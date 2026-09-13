Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$watcher = (Resolve-Path (Join-Path $PSScriptRoot "..\scripts\github_autopull_chatgpts_repo_work\main_autopull_watcher.ps1")).Path
$pwsh = (Get-Process -Id $PID).Path

function Git([string]$Repo, [Parameter(ValueFromRemainingArguments=$true)][string[]]$Args) {
    & git -C $Repo @Args | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git failed: $Args" }
}
function Wait-State([string]$Log, [string]$State, [int]$Seconds = 8) {
    $deadline = [DateTime]::UtcNow.AddSeconds($Seconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        if ((Test-Path $Log) -and (Select-String -Path $Log -Pattern "STATE=$State" -Quiet)) { return }
        Start-Sleep -Milliseconds 100
    }
    throw "state not observed: $State"
}
function Start-Watcher([string]$Repo) {
    Start-Process -FilePath $pwsh -ArgumentList @("-NoProfile","-File",$watcher,"-RepoRoot",$Repo,"-IntervalSeconds","5") -PassThru
}

$root = Join-Path ([System.IO.Path]::GetTempPath()) ("autopull-test-" + [guid]::NewGuid().ToString("N"))
$remote = Join-Path $root "remote.git"
$seed = Join-Path $root "seed"
$local = Join-Path $root "local"
try {
    New-Item -ItemType Directory -Path $root | Out-Null
    & git init --bare $remote | Out-Null
    & git init -b main $seed | Out-Null
    Git $seed config user.email "autopull@example.invalid"
    Git $seed config user.name "AutoPull Test"
    Set-Content -Path (Join-Path $seed "tracked.txt") -Value "one" -NoNewline
    Git $seed add tracked.txt
    Git $seed commit -m initial
    Git $seed remote add origin $remote
    Git $seed push -u origin main
    & git clone $remote $local | Out-Null
    Git $local switch main
    Git $local config user.email "autopull@example.invalid"
    Git $local config user.name "AutoPull Test"

    # Fast-forward works.
    Set-Content -Path (Join-Path $seed "tracked.txt") -Value "two" -NoNewline
    Git $seed add tracked.txt; Git $seed commit -m ff; Git $seed push
    $p = Start-Watcher $local
    Wait-State (Join-Path $local ".git\main-autopull.log") "SYNCED"
    if ((Get-Content (Join-Path $local "tracked.txt") -Raw) -ne "two") { throw "fast-forward failed" }

    # Dirty tracked work blocks updates.
    Set-Content -Path (Join-Path $local "tracked.txt") -Value "local-dirty" -NoNewline
    Set-Content -Path (Join-Path $seed "new.txt") -Value "remote" -NoNewline
    Git $seed add new.txt; Git $seed commit -m dirty; Git $seed push
    Wait-State (Join-Path $local ".git\main-autopull.log") "SKIP_DIRTY_TRACKED"
    Git $local checkout -- tracked.txt

    # Colliding untracked file blocks updates without deleting it.
    Set-Content -Path (Join-Path $local "collision.txt") -Value "local" -NoNewline
    Set-Content -Path (Join-Path $seed "collision.txt") -Value "remote" -NoNewline
    Git $seed add collision.txt; Git $seed commit -m collision; Git $seed push
    Wait-State (Join-Path $local ".git\main-autopull.log") "SKIP_UNTRACKED_COLLISION"
    if ((Get-Content (Join-Path $local "collision.txt") -Raw) -ne "local") { throw "untracked collision overwritten" }
    Remove-Item (Join-Path $local "collision.txt")

    # Stop file terminates the watcher.
    Set-Content -Path (Join-Path $local ".git\main-autopull.stop") -Value "stop"
    if (-not $p.WaitForExit(8000)) { throw "watcher did not stop" }

    # Divergence is reported, never rewritten.
    Git $local fetch origin
    Git $local merge --ff-only origin/main
    Set-Content -Path (Join-Path $local "local-only.txt") -Value "local" -NoNewline
    Git $local add local-only.txt; Git $local commit -m local
    Set-Content -Path (Join-Path $seed "remote-only.txt") -Value "remote" -NoNewline
    Git $seed add remote-only.txt; Git $seed commit -m remote; Git $seed push
    $p2 = Start-Watcher $local
    Wait-State (Join-Path $local ".git\main-autopull.log") "DIVERGED"
    Set-Content -Path (Join-Path $local ".git\main-autopull.stop") -Value "stop"
    [void]$p2.WaitForExit(8000)

    Write-Host "AutoPull regression scenarios passed."
}
finally {
    Remove-Item $root -Recurse -Force -ErrorAction SilentlyContinue
}

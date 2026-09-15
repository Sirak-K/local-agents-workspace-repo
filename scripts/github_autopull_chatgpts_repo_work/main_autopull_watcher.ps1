param(
    [string]$RepoRoot = "",
    [int]$IntervalSeconds = 15
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (& git -C $PSScriptRoot rev-parse --show-toplevel 2>$null).Trim()
}

if ([string]::IsNullOrWhiteSpace($RepoRoot) -or -not (Test-Path $RepoRoot)) {
    exit 2
}

$RepoRoot = (Resolve-Path $RepoRoot).Path
$env:GIT_TERMINAL_PROMPT = "0"

function Invoke-Git {
    param([Parameter(Mandatory = $true)][string[]]$Args)
    $output = & git -C $RepoRoot @Args 2>&1
    $code = $LASTEXITCODE
    [pscustomobject]@{
        ExitCode = $code
        Output   = (($output | ForEach-Object { $_.ToString() }) -join "`n").Trim()
    }
}

$gitDirResult = Invoke-Git @("rev-parse", "--git-dir")
if ($gitDirResult.ExitCode -ne 0) {
    exit 3
}

$gitDir = $gitDirResult.Output
if (-not [System.IO.Path]::IsPathRooted($gitDir)) {
    $gitDir = Join-Path $RepoRoot $gitDir
}
$gitDir = [System.IO.Path]::GetFullPath($gitDir)

$logPath = Join-Path $gitDir "main-autopull.log"
$lockPath = Join-Path $gitDir "main-autopull.lock"
$stopPath = Join-Path $gitDir "main-autopull.stop"

function Write-Log {
    param([string]$Message)
    $line = "{0} {1}`r`n" -f ([DateTimeOffset]::Now.ToString("yyyy-MM-dd | HH:mm:ss.fff zzz")), $Message
    [System.IO.File]::AppendAllText($logPath, $line, [System.Text.Encoding]::UTF8)
}

try {
    $lockStream = [System.IO.File]::Open(
        $lockPath,
        [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None
    )
}
catch [System.IO.IOException] {
    exit 0
}

$lastState = ""
$lastDetail = ""

function Set-State {
    param([string]$State, [string]$Detail = "")
    if ($script:lastState -ne $State -or $script:lastDetail -ne $Detail) {
        $message = ("STATE={0} {1}" -f $State, $Detail).Trim()
        Write-Log $message
        $script:lastState = $State
        $script:lastDetail = $Detail
    }
}

function Test-GitOperationInProgress {
    $markers = @(
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "rebase-merge",
        "rebase-apply",
        "index.lock"
    )
    foreach ($marker in $markers) {
        if (Test-Path (Join-Path $gitDir $marker)) {
            return $true
        }
    }
    return $false
}

function Get-UntrackedCollisions {
    param([string]$LocalHead, [string]$RemoteHead)
    $changed = Invoke-Git @("diff", "--name-only", "--diff-filter=AMCR", "--no-renames", $LocalHead, $RemoteHead)
    $untracked = Invoke-Git @("ls-files", "--others", "--exclude-standard")
    if ($changed.ExitCode -ne 0 -or $untracked.ExitCode -ne 0) {
        throw "could not inspect untracked collision set"
    }
    if ([string]::IsNullOrWhiteSpace($changed.Output) -or [string]::IsNullOrWhiteSpace($untracked.Output)) {
        return @()
    }
    $untrackedSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($path in ($untracked.Output -split "`n")) {
        if (-not [string]::IsNullOrWhiteSpace($path)) {
            [void]$untrackedSet.Add($path.TrimEnd("`r"))
        }
    }
    $collisions = @()
    foreach ($path in ($changed.Output -split "`n")) {
        $candidate = $path.TrimEnd("`r")
        if ($untrackedSet.Contains($candidate)) {
            $collisions += $candidate
        }
    }
    return $collisions
}

try {
    Write-Log ("START repo={0} interval={1}s" -f $RepoRoot, $IntervalSeconds)

    while ($true) {
        if (Test-Path $stopPath) {
            Remove-Item $stopPath -Force -ErrorAction SilentlyContinue
            Write-Log "STOP requested"
            break
        }

        try {
            $branch = Invoke-Git @("rev-parse", "--abbrev-ref", "HEAD")
            if ($branch.ExitCode -ne 0) {
                Set-State "GIT_ERROR" $branch.Output
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }
            if ($branch.Output -ne "main") {
                Set-State "SKIP_BRANCH" ("branch={0}" -f $branch.Output)
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            if (Test-GitOperationInProgress) {
                Set-State "SKIP_GIT_OPERATION" "merge/rebase/cherry-pick/revert/index lock detected"
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            $fetch = Invoke-Git @(
                "fetch",
                "--quiet",
                "origin",
                "refs/heads/main:refs/remotes/origin/main"
            )
            if ($fetch.ExitCode -ne 0) {
                Set-State "FETCH_FAILED" $fetch.Output
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            $head = Invoke-Git @("rev-parse", "HEAD")
            $remote = Invoke-Git @("rev-parse", "refs/remotes/origin/main")
            if ($head.ExitCode -ne 0 -or $remote.ExitCode -ne 0) {
                Set-State "REV_PARSE_FAILED" ((@($head.Output, $remote.Output) -join " | ").Trim())
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            if ($head.Output -eq $remote.Output) {
                Set-State "SYNCED" ("head={0}" -f $head.Output.Substring(0, [Math]::Min(12, $head.Output.Length)))
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            $trackedStatus = Invoke-Git @("status", "--porcelain=v1", "--untracked-files=no")
            if ($trackedStatus.ExitCode -ne 0) {
                Set-State "STATUS_FAILED" $trackedStatus.Output
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }
            if (-not [string]::IsNullOrWhiteSpace($trackedStatus.Output)) {
                $remoteOnly = Invoke-Git @("rev-list", "--count", ("{0}..{1}" -f $head.Output, $remote.Output))
                $remoteOnlyCount = if ($remoteOnly.ExitCode -eq 0) { $remoteOnly.Output } else { "unknown" }
                $shortRemote = $remote.Output.Substring(0, [Math]::Min(12, $remote.Output.Length))
                Set-State "SKIP_DIRTY_TRACKED" ("origin/main fetched remote={0} remote_only_commits={1}; local main/worktree unchanged because tracked/staged changes are present" -f $shortRemote, $remoteOnlyCount)
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            $localIsAncestor = Invoke-Git @("merge-base", "--is-ancestor", $head.Output, $remote.Output)
            if ($localIsAncestor.ExitCode -eq 0) {
                $collisions = @(Get-UntrackedCollisions $head.Output $remote.Output)
                if ($collisions.Count -gt 0) {
                    $preview = (($collisions | Select-Object -First 3) -join ",")
                    Set-State "SKIP_UNTRACKED_COLLISION" ("paths={0}" -f $preview)
                    Start-Sleep -Seconds $IntervalSeconds
                    continue
                }

                $branch2 = Invoke-Git @("rev-parse", "--abbrev-ref", "HEAD")
                $status2 = Invoke-Git @("status", "--porcelain=v1", "--untracked-files=no")
                $collisions2 = @(Get-UntrackedCollisions $head.Output $remote.Output)
                $raceGuardTriggered = ($branch2.Output -ne "main") -or (-not [string]::IsNullOrWhiteSpace($status2.Output)) -or ($collisions2.Count -gt 0) -or (Test-GitOperationInProgress)
                if ($raceGuardTriggered) {
                    Set-State "SKIP_RACE_GUARD" "state changed before fast-forward"
                    Start-Sleep -Seconds $IntervalSeconds
                    continue
                }

                $oldHead = $head.Output
                $merge = Invoke-Git @("merge", "--ff-only", "--quiet", "refs/remotes/origin/main")
                if ($merge.ExitCode -eq 0) {
                    $newHead = (Invoke-Git @("rev-parse", "HEAD")).Output
                    Write-Log ("UPDATED {0} -> {1}" -f $oldHead, $newHead)
                    $lastState = ""
                    $lastDetail = ""
                }
                else {
                    Set-State "FAST_FORWARD_FAILED" $merge.Output
                }
            }
            else {
                $remoteIsAncestor = Invoke-Git @("merge-base", "--is-ancestor", $remote.Output, $head.Output)
                if ($remoteIsAncestor.ExitCode -eq 0) {
                    Set-State "LOCAL_AHEAD" "local main contains commits not on origin/main; no automatic rewrite"
                }
                else {
                    Set-State "DIVERGED" "local main and origin/main diverged; manual resolution required"
                }
            }
        }
        catch {
            Set-State "WATCHER_ERROR" $_.Exception.Message
        }

        Start-Sleep -Seconds $IntervalSeconds
    }
}
finally {
    if ($null -ne $lockStream) {
        $lockStream.Dispose()
    }
}

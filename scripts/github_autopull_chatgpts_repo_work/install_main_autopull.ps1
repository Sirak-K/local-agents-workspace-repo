param(
    [int]$IntervalSeconds = 15,
    [switch]$Uninstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (& git -C $PSScriptRoot rev-parse --show-toplevel 2>$null).Trim()
if ([string]::IsNullOrWhiteSpace($repoRoot)) {
    throw "Could not resolve repository root."
}
$repoRoot = (Resolve-Path $repoRoot).Path

$watcher = Join-Path $PSScriptRoot "main_autopull_watcher.ps1"
if (-not (Test-Path $watcher)) {
    throw "Watcher not found: $watcher"
}

$gitDirRaw = (& git -C $repoRoot rev-parse --git-dir 2>$null).Trim()
if ([System.IO.Path]::IsPathRooted($gitDirRaw)) {
    $gitDir = $gitDirRaw
}
else {
    $gitDir = Join-Path $repoRoot $gitDirRaw
}
$gitDir = [System.IO.Path]::GetFullPath($gitDir)
$stopPath = Join-Path $gitDir "main-autopull.stop"
$legacyEvidencePaths = @(
    (Join-Path $gitDir "main-autopull.log"),
    (Join-Path $gitDir "main-autopull-bootstrap.out.log"),
    (Join-Path $gitDir "main-autopull-bootstrap.err.log")
)
$evidenceRoot = Join-Path $repoRoot "logs\github_autopull"

$startupDir = [Environment]::GetFolderPath([Environment+SpecialFolder]::Startup)
# This launcher is intentionally unique to local_agents_workspace. Never reuse or
# remove the ComfyUI project's SSIRA-ComfyUI-MainAutoPull.cmd launcher.
$launcherPath = Join-Path $startupDir "SSIRA-LocalAgents-MainAutoPull.cmd"

$hostExe = (Get-Process -Id $PID).Path
if ([string]::IsNullOrWhiteSpace($hostExe) -or -not (Test-Path $hostExe)) {
    throw "Could not resolve the current PowerShell host executable."
}

if ($Uninstall) {
    if (Test-Path $launcherPath) {
        Remove-Item $launcherPath -Force
    }
    [System.IO.File]::WriteAllText($stopPath, "stop`r`n", [System.Text.Encoding]::ASCII)
    Write-Host "Local Agents auto-pull startup launcher removed."
    Write-Host "Running Local Agents watcher will stop within its polling interval."
    Write-Host "Evidence root: $evidenceRoot"
    exit 0
}

if ($IntervalSeconds -lt 5) {
    throw "IntervalSeconds must be at least 5."
}

if (Test-Path $stopPath) {
    Remove-Item $stopPath -Force -ErrorAction SilentlyContinue
}
# Step 4 moves AutoPull evidence out of .git/*.log. Historical bootstrap/state
# text logs are not migrated into the new owner-specific runtime evidence.
Remove-Item $legacyEvidencePaths -Force -ErrorAction SilentlyContinue

$launcher = @"
@echo off
start "" /min "$hostExe" -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "$watcher" -RepoRoot "$repoRoot" -IntervalSeconds $IntervalSeconds
"@
[System.IO.File]::WriteAllText($launcherPath, $launcher, [System.Text.Encoding]::ASCII)

$argList = @(
    "-NoProfile",
    "-WindowStyle", "Hidden",
    "-ExecutionPolicy", "Bypass",
    "-File", $watcher,
    "-RepoRoot", $repoRoot,
    "-IntervalSeconds", $IntervalSeconds.ToString()
)
Start-Process -FilePath $hostExe -ArgumentList $argList -WindowStyle Hidden

Start-Sleep -Seconds 2

Write-Host "Installed and started safe Local Agents main auto-pull watcher."
Write-Host "Repo: $repoRoot"
Write-Host "PowerShell host: $hostExe"
Write-Host "Poll interval: ${IntervalSeconds}s"
Write-Host "Startup launcher: $launcherPath"
Write-Host "Evidence root: $evidenceRoot"
Write-Host "Safety: only branch main; only fast-forward; skips tracked/staged local changes and colliding untracked files; never resets/rebases/cleans/stashes."

$latestEvidence = Get-ChildItem -LiteralPath $evidenceRoot -Filter "*.json" -Recurse -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTimeUtc -Descending |
    Select-Object -First 1
if ($null -ne $latestEvidence) {
    Write-Host "Latest watcher evidence: $($latestEvidence.FullName)"
}
else {
    Write-Warning "No owner-specific watcher capture is visible yet. The watcher may still be in startup/fetch or Python observability may be unavailable."
}

Write-Host "Uninstall: & .\scripts\github_autopull_chatgpts_repo_work\install_main_autopull.ps1 -Uninstall"

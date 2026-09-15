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

$lockPath = Join-Path $gitDir "main-autopull.lock"
$stopPath = Join-Path $gitDir "main-autopull.stop"
$observabilityScript = Join-Path $RepoRoot "scripts\runtime_observability\github_autopull_capture.py"
$projectPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $projectPython -PathType Leaf) {
    $pythonExe = $projectPython
}
else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    $pythonExe = if ($null -ne $pythonCommand) { $pythonCommand.Source } else { $null }
}

function Publish-AutoPullState {
    param(
        [Parameter(Mandatory = $true)][string]$Decision,
        [Parameter(Mandatory = $true)][ValidateSet("observed", "success", "failure", "partial", "skipped")][string]$EventOutcome,
        [Parameter(Mandatory = $true)][string]$Reason,
        [string]$LocalHead = "",
        [string]$RemoteHead = "",
        [Nullable[bool]]$TrackedClean = $null,
        [ValidateSet("success", "error", "not_attempted")][string]$FetchResult = "not_attempted",
        [ValidateSet("fast_forward", "non_fast_forward", "remote_ancestor", "diverged", "unknown", "not_checked")][string]$Ancestry = "not_checked",
        [string]$ErrorClass = ""
    )

    # Observability is deliberately best-effort: a logging failure must never change
    # the Codex-owned FF-only AutoPull safety behavior.
    if ($null -eq $pythonExe -or -not (Test-Path -LiteralPath $observabilityScript -PathType Leaf)) {
        return
    }

    $arguments = @(
        $observabilityScript,
        "--decision", $Decision,
        "--event-outcome", $EventOutcome,
        "--reason", $Reason,
        "--fetch-result", $FetchResult,
        "--ancestry", $Ancestry
    )
    if (-not [string]::IsNullOrWhiteSpace($LocalHead)) {
        $arguments += @("--local-head", $LocalHead)
    }
    if (-not [string]::IsNullOrWhiteSpace($RemoteHead)) {
        $arguments += @("--remote-head", $RemoteHead)
    }
    if ($null -ne $TrackedClean) {
        $arguments += @("--tracked-clean", $TrackedClean.Value.ToString().ToLowerInvariant())
    }
    if (-not [string]::IsNullOrWhiteSpace($ErrorClass)) {
        $arguments += @("--error-class", $ErrorClass)
    }

    try {
        & $pythonExe @arguments *> $null
    }
    catch {
        # Fail open for observability only. Git safety gates below remain authoritative.
    }
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
    param(
        [Parameter(Mandatory = $true)][string]$State,
        [string]$Detail = "",
        [string]$Decision = "",
        [ValidateSet("observed", "success", "failure", "partial", "skipped")][string]$EventOutcome = "observed",
        [string]$Reason = "",
        [string]$LocalHead = "",
        [string]$RemoteHead = "",
        [Nullable[bool]]$TrackedClean = $null,
        [ValidateSet("success", "error", "not_attempted")][string]$FetchResult = "not_attempted",
        [ValidateSet("fast_forward", "non_fast_forward", "remote_ancestor", "diverged", "unknown", "not_checked")][string]$Ancestry = "not_checked",
        [string]$ErrorClass = ""
    )
    if ($script:lastState -ne $State -or $script:lastDetail -ne $Detail) {
        if (-not [string]::IsNullOrWhiteSpace($Decision)) {
            Publish-AutoPullState `
                -Decision $Decision `
                -EventOutcome $EventOutcome `
                -Reason $Reason `
                -LocalHead $LocalHead `
                -RemoteHead $RemoteHead `
                -TrackedClean $TrackedClean `
                -FetchResult $FetchResult `
                -Ancestry $Ancestry `
                -ErrorClass $ErrorClass
        }
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
    while ($true) {
        if (Test-Path $stopPath) {
            Remove-Item $stopPath -Force -ErrorAction SilentlyContinue
            break
        }

        try {
            $branch = Invoke-Git @("rev-parse", "--abbrev-ref", "HEAD")
            if ($branch.ExitCode -ne 0) {
                Set-State "GIT_ERROR" $branch.Output -Decision "error" -EventOutcome "failure" -Reason ("branch query failed exit={0}" -f $branch.ExitCode) -ErrorClass "git_branch_query_failed"
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }
            if ($branch.Output -ne "main") {
                Set-State "SKIP_BRANCH" ("branch={0}" -f $branch.Output) -Decision "skipped_branch" -EventOutcome "skipped" -Reason ("active branch is {0}, not main" -f $branch.Output)
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            if (Test-GitOperationInProgress) {
                Set-State "SKIP_GIT_OPERATION" "merge/rebase/cherry-pick/revert/index lock detected" -Decision "skipped_git_operation" -EventOutcome "skipped" -Reason "Git operation or index lock is in progress"
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
                Set-State "FETCH_FAILED" $fetch.Output -Decision "fetch_error" -EventOutcome "failure" -Reason ("git fetch failed exit={0}" -f $fetch.ExitCode) -FetchResult "error" -Ancestry "unknown" -ErrorClass "git_fetch_failed"
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            $head = Invoke-Git @("rev-parse", "HEAD")
            $remote = Invoke-Git @("rev-parse", "refs/remotes/origin/main")
            if ($head.ExitCode -ne 0 -or $remote.ExitCode -ne 0) {
                Set-State "REV_PARSE_FAILED" ((@($head.Output, $remote.Output) -join " | ").Trim()) -Decision "error" -EventOutcome "failure" -Reason "could not resolve local/remote main after fetch" -FetchResult "success" -Ancestry "unknown" -ErrorClass "git_rev_parse_failed"
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            if ($head.Output -eq $remote.Output) {
                Set-State "SYNCED" ("head={0}" -f $head.Output.Substring(0, [Math]::Min(12, $head.Output.Length))) -Decision "up_to_date" -EventOutcome "success" -Reason "local main already equals origin/main" -LocalHead $head.Output -RemoteHead $remote.Output -FetchResult "success"
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            $trackedStatus = Invoke-Git @("status", "--porcelain=v1", "--untracked-files=no")
            if ($trackedStatus.ExitCode -ne 0) {
                Set-State "STATUS_FAILED" $trackedStatus.Output -Decision "error" -EventOutcome "failure" -Reason ("tracked status query failed exit={0}" -f $trackedStatus.ExitCode) -LocalHead $head.Output -RemoteHead $remote.Output -FetchResult "success" -Ancestry "unknown" -ErrorClass "git_status_failed"
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }
            if (-not [string]::IsNullOrWhiteSpace($trackedStatus.Output)) {
                $remoteOnly = Invoke-Git @("rev-list", "--count", ("{0}..{1}" -f $head.Output, $remote.Output))
                $remoteOnlyCount = if ($remoteOnly.ExitCode -eq 0) { $remoteOnly.Output } else { "unknown" }
                $shortRemote = $remote.Output.Substring(0, [Math]::Min(12, $remote.Output.Length))
                Set-State "SKIP_DIRTY_TRACKED" ("origin/main fetched remote={0} remote_only_commits={1}; local main/worktree unchanged because tracked/staged changes are present" -f $shortRemote, $remoteOnlyCount) -Decision "skipped_dirty" -EventOutcome "skipped" -Reason "tracked or staged local changes are present" -LocalHead $head.Output -RemoteHead $remote.Output -TrackedClean $false -FetchResult "success"
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            $localIsAncestor = Invoke-Git @("merge-base", "--is-ancestor", $head.Output, $remote.Output)
            if ($localIsAncestor.ExitCode -eq 0) {
                $collisions = @(Get-UntrackedCollisions $head.Output $remote.Output)
                if ($collisions.Count -gt 0) {
                    $preview = (($collisions | Select-Object -First 3) -join ",")
                    Set-State "SKIP_UNTRACKED_COLLISION" ("paths={0}" -f $preview) -Decision "skipped_untracked_collision" -EventOutcome "skipped" -Reason ("{0} untracked path collision(s) block fast-forward" -f $collisions.Count) -LocalHead $head.Output -RemoteHead $remote.Output -TrackedClean $true -FetchResult "success" -Ancestry "fast_forward"
                    Start-Sleep -Seconds $IntervalSeconds
                    continue
                }

                $branch2 = Invoke-Git @("rev-parse", "--abbrev-ref", "HEAD")
                $status2 = Invoke-Git @("status", "--porcelain=v1", "--untracked-files=no")
                $collisions2 = @(Get-UntrackedCollisions $head.Output $remote.Output)
                $raceGuardTriggered = ($branch2.Output -ne "main") -or (-not [string]::IsNullOrWhiteSpace($status2.Output)) -or ($collisions2.Count -gt 0) -or (Test-GitOperationInProgress)
                if ($raceGuardTriggered) {
                    Set-State "SKIP_RACE_GUARD" "state changed before fast-forward" -Decision "skipped_race_guard" -EventOutcome "skipped" -Reason "repository state changed after preflight and before fast-forward" -LocalHead $head.Output -RemoteHead $remote.Output -FetchResult "success" -Ancestry "fast_forward"
                    Start-Sleep -Seconds $IntervalSeconds
                    continue
                }

                $oldHead = $head.Output
                $merge = Invoke-Git @("merge", "--ff-only", "--quiet", "refs/remotes/origin/main")
                if ($merge.ExitCode -eq 0) {
                    $newHead = (Invoke-Git @("rev-parse", "HEAD")).Output
                    Set-State "UPDATED" ("{0}->{1}" -f $oldHead, $newHead) -Decision "updated" -EventOutcome "success" -Reason "fast-forward merge completed" -LocalHead $oldHead -RemoteHead $newHead -TrackedClean $true -FetchResult "success" -Ancestry "fast_forward"
                }
                else {
                    Set-State "FAST_FORWARD_FAILED" $merge.Output -Decision "error" -EventOutcome "failure" -Reason ("git merge --ff-only failed exit={0}" -f $merge.ExitCode) -LocalHead $oldHead -RemoteHead $remote.Output -TrackedClean $true -FetchResult "success" -Ancestry "fast_forward" -ErrorClass "git_fast_forward_failed"
                }
            }
            else {
                $remoteIsAncestor = Invoke-Git @("merge-base", "--is-ancestor", $remote.Output, $head.Output)
                if ($remoteIsAncestor.ExitCode -eq 0) {
                    Set-State "LOCAL_AHEAD" "local main contains commits not on origin/main; no automatic rewrite" -Decision "skipped_local_ahead" -EventOutcome "skipped" -Reason "local main contains commits not on origin/main; no automatic rewrite" -LocalHead $head.Output -RemoteHead $remote.Output -TrackedClean $true -FetchResult "success" -Ancestry "remote_ancestor"
                }
                else {
                    Set-State "DIVERGED" "local main and origin/main diverged; manual resolution required" -Decision "skipped_diverged" -EventOutcome "skipped" -Reason "local main and origin/main diverged; manual resolution required" -LocalHead $head.Output -RemoteHead $remote.Output -TrackedClean $true -FetchResult "success" -Ancestry "diverged"
                }
            }
        }
        catch {
            Set-State "WATCHER_ERROR" $_.Exception.Message -Decision "error" -EventOutcome "failure" -Reason "watcher exception" -FetchResult "not_attempted" -Ancestry "unknown" -ErrorClass $_.Exception.GetType().Name
        }

        Start-Sleep -Seconds $IntervalSeconds
    }
}
finally {
    if ($null -ne $lockStream) {
        $lockStream.Dispose()
    }
}

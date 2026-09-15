Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

function Get-RuntimeObservabilityPython {
    $projectPython = Join-Path $script:ProjectRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $projectPython -PathType Leaf) {
        return $projectPython
    }
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $command) {
        return $command.Source
    }
    return $null
}

function New-RuntimeCorrelationId {
    return ([guid]::NewGuid().ToString('N')).ToLowerInvariant()
}

function Invoke-RuntimeLoggingCli {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $python = Get-RuntimeObservabilityPython
    if ([string]::IsNullOrWhiteSpace($python)) {
        return $null
    }
    Push-Location $script:ProjectRoot
    try {
        $lines = @(& $python -m runtime_logging @Arguments 2>$null)
        if ($LASTEXITCODE -ne 0 -or $lines.Count -eq 0) {
            return $null
        }
        return ($lines[-1] | ConvertFrom-Json -ErrorAction Stop)
    }
    catch {
        return $null
    }
    finally {
        Pop-Location
    }
}

function Start-RuntimeOperationCapture {
    param(
        [Parameter(Mandatory = $true)][string]$Owner,
        [Parameter(Mandatory = $true)][string]$Stream,
        [Parameter(Mandatory = $true)][string]$Producer,
        [Parameter(Mandatory = $true)][string]$ProducerVersion,
        [Parameter(Mandatory = $true)][string]$CorrelationId,
        [string]$Profile = '',
        [string]$Model = '',
        [Nullable[int]]$ProcessId = $null,
        [hashtable]$Detail = @{},
        [string[]]$EvidenceGap = @(),
        [switch]$AllowSensitiveContent
    )

    $arguments = @(
        'begin',
        '--owner', $Owner,
        '--stream', $Stream,
        '--producer', $Producer,
        '--producer-version', $ProducerVersion,
        '--correlation-id', $CorrelationId,
        '--detail-json', ($Detail | ConvertTo-Json -Depth 8 -Compress)
    )
    if (-not [string]::IsNullOrWhiteSpace($Profile)) { $arguments += @('--profile', $Profile) }
    if (-not [string]::IsNullOrWhiteSpace($Model)) { $arguments += @('--model', $Model) }
    if ($null -ne $ProcessId) { $arguments += @('--pid', $ProcessId.Value.ToString()) }
    foreach ($gap in $EvidenceGap) { $arguments += @('--evidence-gap', $gap) }
    if ($AllowSensitiveContent) { $arguments += '--allow-sensitive-content' }
    return Invoke-RuntimeLoggingCli -Arguments $arguments
}

function Add-RuntimeOperationEvent {
    param(
        [Parameter(Mandatory = $true)][string]$File,
        [Parameter(Mandatory = $true)][string]$EventType,
        [Parameter(Mandatory = $true)][hashtable]$Details,
        [ValidateSet('debug','info','warning','error')][string]$Severity = 'info',
        [ValidateSet('observed','success','failure','partial','skipped')][string]$Outcome = 'observed',
        [Nullable[double]]$DurationSeconds = $null,
        [switch]$AllowSensitiveContent
    )
    $arguments = @(
        'event', '--file', $File,
        '--event-type', $EventType,
        '--details-json', ($Details | ConvertTo-Json -Depth 10 -Compress),
        '--severity', $Severity,
        '--outcome', $Outcome
    )
    if ($null -ne $DurationSeconds) { $arguments += @('--duration-seconds', $DurationSeconds.Value.ToString([Globalization.CultureInfo]::InvariantCulture)) }
    if ($AllowSensitiveContent) { $arguments += '--allow-sensitive-content' }
    [void](Invoke-RuntimeLoggingCli -Arguments $arguments)
}

function Complete-RuntimeOperationCapture {
    param(
        [Parameter(Mandatory = $true)][string]$File,
        [ValidateSet('completed','failed','interrupted')][string]$Status,
        [Parameter(Mandatory = $true)][string]$StopReason,
        [Parameter(Mandatory = $true)][double]$DurationSeconds,
        [string[]]$EvidenceGap = @()
    )
    $arguments = @(
        'finalize', '--file', $File,
        '--status', $Status,
        '--stop-reason', $StopReason,
        '--duration-seconds', $DurationSeconds.ToString([Globalization.CultureInfo]::InvariantCulture)
    )
    foreach ($gap in $EvidenceGap) { $arguments += @('--evidence-gap', $gap) }
    [void](Invoke-RuntimeLoggingCli -Arguments $arguments)
}

Export-ModuleMember -Function New-RuntimeCorrelationId, Start-RuntimeOperationCapture, Add-RuntimeOperationEvent, Complete-RuntimeOperationCapture

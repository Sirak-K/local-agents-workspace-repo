[CmdletBinding()]
param(
    [string]$CorrelationId
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$observabilityModulePath = Join-Path $PSScriptRoot 'RuntimeObservability.psm1'
Import-Module -Name $observabilityModulePath -Force -ErrorAction Stop
if ([string]::IsNullOrWhiteSpace($CorrelationId)) { $CorrelationId = New-RuntimeCorrelationId }

$SillyRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$SillyDir = Join-Path $SillyRoot '_local_runtime\SillyTavern'
$StartBat = Join-Path $SillyDir 'Start.bat'

if (-not (Test-Path -LiteralPath $StartBat)) {
    throw "SillyTavern is not installed at $SillyDir. Run Bootstrap-Guide1.ps1 first."
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Node.js is unavailable in PATH. Open a fresh PowerShell and rerun if Bootstrap installed Node.js just now.'
}

$cmdExe = $env:ComSpec
if (-not $cmdExe -or -not (Test-Path -LiteralPath $cmdExe)) {
    throw 'Windows cmd.exe could not be resolved from COMSPEC.'
}

Write-Host "Starting SillyTavern from: $SillyDir"
$argumentLine = '/k "{0}"' -f $StartBat
$process = Start-Process -FilePath $cmdExe -ArgumentList $argumentLine -WorkingDirectory $SillyDir -PassThru
$capture = Start-RuntimeOperationCapture -Owner 'sillytavern' -Stream 'process_launch' -Producer 'Start-SillyTavern.ps1' -ProducerVersion '1.0' -CorrelationId $CorrelationId -ProcessId $process.Id -Detail @{ launcher = 'Start.bat'; transport = 'cmd.exe' } -EvidenceGap @('The recorded PID is the cmd.exe launcher; the child Node.js PID and server-ready state are not proven by this launcher boundary.')
if ($null -ne $capture) {
    Add-RuntimeOperationEvent -File $capture.file -EventType 'sillytavern.process_started' -Details @{ pid = $process.Id; launcher = 'Start.bat' } -Outcome 'success'
    Complete-RuntimeOperationCapture -File $capture.file -Status 'completed' -StopReason 'process_started' -DurationSeconds 0
}

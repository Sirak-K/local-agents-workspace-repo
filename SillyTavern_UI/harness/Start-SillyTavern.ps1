[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$SillyRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$SillyDir = Join-Path $SillyRoot '_local_runtime\SillyTavern'
$StartBat = Join-Path $SillyDir 'Start.bat'

if (-not (Test-Path -LiteralPath $StartBat)) {
    throw "SillyTavern is not installed at $SillyDir. Run Bootstrap-Guide1.ps1 first."
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Node.js is unavailable in PATH. Open a fresh PowerShell and rerun if Bootstrap installed Node.js just now.'
}

Write-Host "Starting SillyTavern from: $SillyDir"
Start-Process -FilePath $StartBat -WorkingDirectory $SillyDir | Out-Null

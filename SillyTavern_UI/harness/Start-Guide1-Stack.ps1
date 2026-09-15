[CmdletBinding()]
param(
    [string]$ModelPath,

    [ValidateRange(256, 524288)]
    [int]$ContextSize = 8192,

    [ValidateRange(0, 3)]
    [int]$GpuId = 0,

    [ValidateRange(1, 65535)]
    [int]$KoboldPort = 5001
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$bootstrap = Join-Path $PSScriptRoot 'Bootstrap-Guide1.ps1'
$startKobold = Join-Path $PSScriptRoot 'Start-KoboldCpp-TextBaseline.ps1'
$startSilly = Join-Path $PSScriptRoot 'Start-SillyTavern.ps1'
$testKobold = Join-Path $PSScriptRoot 'Test-KoboldCpp-TextBaseline.ps1'
$SillyRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$KoboldExe = Join-Path $SillyRoot '_local_runtime\KoboldCpp\koboldcpp.exe'
$SillyBat = Join-Path $SillyRoot '_local_runtime\SillyTavern\Start.bat'

if (-not (Test-Path -LiteralPath $KoboldExe) -or -not (Test-Path -LiteralPath $SillyBat)) {
    Write-Host 'Guide 1 runtime is incomplete; running bootstrap first.'
    & $bootstrap
}

if (-not $ModelPath) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Title = 'Select an existing GGUF model for the Guide 1 harness smoke test'
    $dialog.Filter = 'GGUF models (*.gguf)|*.gguf|All files (*.*)|*.*'
    $dialog.Multiselect = $false
    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        throw 'No GGUF model was selected.'
    }
    $ModelPath = $dialog.FileName
}

Write-Host 'Launching KoboldCpp...'
$koboldProcess = & $startKobold -ModelPath $ModelPath -ContextSize $ContextSize -GpuId $GpuId -Port $KoboldPort -Background

$deadline = (Get-Date).AddMinutes(5)
$ready = $false
while ((Get-Date) -lt $deadline) {
    if ($koboldProcess.HasExited) {
        throw "KoboldCpp exited before becoming ready (exit code $($koboldProcess.ExitCode))."
    }
    try {
        Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:$KoboldPort/api/extra/version" -TimeoutSec 3 | Out-Null
        $ready = $true
        break
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    throw 'KoboldCpp did not become ready within 5 minutes.'
}

Write-Host 'KoboldCpp endpoint is ready.'
& $testKobold -Port $KoboldPort -ExpectedContext $ContextSize

Write-Host ''
Write-Host 'Launching SillyTavern...'
& $startSilly

Write-Host ''
Write-Host 'Guide 1 stack is running.'
Write-Host "KoboldCpp: http://127.0.0.1:$KoboldPort"
Write-Host 'In SillyTavern, set Text Completion -> KoboldCpp to the URL above and Connect.'

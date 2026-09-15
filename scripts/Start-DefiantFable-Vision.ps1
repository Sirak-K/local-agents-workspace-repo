[CmdletBinding()]
param(
    [string]$ModelPath,
    [ValidateRange(256, 524288)]
    [int]$ContextSize = 4096
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$BackendScript = Join-Path $RepoRoot 'SillyTavern_UI\harness\Start-KoboldCpp-TextBaseline.ps1'

if (-not $ModelPath) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Title = 'Select the active DefiantFable GGUF for VISION mode'
    $dialog.Filter = 'GGUF models (*.gguf)|*.gguf|All files (*.*)|*.*'
    $dialog.Multiselect = $false
    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        throw 'No GGUF model was selected.'
    }
    $ModelPath = $dialog.FileName
}

$model = (Resolve-Path -LiteralPath $ModelPath).Path
$mmproj = Join-Path ([IO.Path]::GetDirectoryName($model)) 'mmproj-F16.gguf'
if (-not (Test-Path -LiteralPath $mmproj)) {
    throw "mmproj-F16.gguf was not found beside the model. Run .\scripts\Download-DefiantFable-mmproj-F16.cmd first."
}

$expected = 'f70dc3509053962b0d0d3ee8a7eacebf5d60aa560cad78254ae8698516ae029f'
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $mmproj).Hash.ToLowerInvariant()
if ($actual -ne $expected) {
    throw "mmproj-F16.gguf SHA256 mismatch: $actual"
}

Write-Host 'Starting separate DefiantFable VISION profile.'
Write-Host "Context: $ContextSize"
Write-Host 'TEXT profile is not modified.'
& $BackendScript -ModelPath $model -MmprojPath $mmproj -ContextSize $ContextSize
exit $LASTEXITCODE

[CmdletBinding()]
param(
    [string]$ModelPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ExpectedSha256 = 'f70dc3509053962b0d0d3ee8a7eacebf5d60aa560cad78254ae8698516ae029f'
$Url = 'https://huggingface.co/DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF/resolve/main/mmproj-F16.gguf?download=true'

if (-not $ModelPath) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Title = 'Select the active DefiantFable GGUF; mmproj-F16.gguf will be placed beside it'
    $dialog.Filter = 'GGUF models (*.gguf)|*.gguf|All files (*.*)|*.*'
    $dialog.Multiselect = $false
    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        throw 'No GGUF model was selected.'
    }
    $ModelPath = $dialog.FileName
}

$model = (Resolve-Path -LiteralPath $ModelPath).Path
$target = Join-Path ([IO.Path]::GetDirectoryName($model)) 'mmproj-F16.gguf'

if (Test-Path -LiteralPath $target) {
    $existing = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLowerInvariant()
    if ($existing -eq $ExpectedSha256) {
        Write-Host "PASS: verified mmproj already present: $target"
        exit 0
    }
    throw "Existing mmproj-F16.gguf has unexpected SHA256: $existing"
}

Write-Host "Downloading verified DefiantFable mmproj-F16.gguf (~918 MB) to:"
Write-Host "  $target"

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
try {
    Import-Module BitsTransfer -ErrorAction Stop
    Start-BitsTransfer -Source $Url -Destination $target -DisplayName 'DefiantFable mmproj-F16'
}
catch {
    Write-Host 'BITS unavailable/failed; falling back to Invoke-WebRequest.'
    Invoke-WebRequest -Uri $Url -OutFile $target -UseBasicParsing
}

$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLowerInvariant()
if ($actual -ne $ExpectedSha256) {
    Remove-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
    throw "SHA256 mismatch. Expected $ExpectedSha256 but got $actual. Download was removed."
}

Write-Host 'PASS: mmproj-F16.gguf downloaded and SHA256 verified.'
Write-Host "Path: $target"

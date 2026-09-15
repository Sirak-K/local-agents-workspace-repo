[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$KoboldCppExe,

    [Parameter(Mandatory = $true)]
    [string]$ModelPath,

    [ValidateRange(256, 262144)]
    [int]$ContextSize = 8192,

    [ValidateRange(0, 64)]
    [int]$GpuId = 0,

    [ValidateRange(1, 65535)]
    [int]$Port = 5001,

    [switch]$LaunchBrowser
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$exe = (Resolve-Path -LiteralPath $KoboldCppExe).Path
$model = (Resolve-Path -LiteralPath $ModelPath).Path

if ([IO.Path]::GetExtension($model) -ne '.gguf') {
    throw "ModelPath must point to a .gguf file: $model"
}

if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    throw 'nvidia-smi was not found. Verify the NVIDIA driver before starting KoboldCpp.'
}

$listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($listener) {
    throw "TCP port $Port is already in use. Stop the existing listener or choose another port."
}

# Text-only AGENT-2 baseline. Deliberately excludes mmproj, RAG, SWA,
# quantized KV, remote tunnel, web search, and speculative decoding.
$KoboldArgs = @(
    '--model', $model,
    '--host', '127.0.0.1',
    '--port', "$Port",
    '--contextsize', "$ContextSize",
    '--usecuda', 'normal', "$GpuId", 'nommq',
    '--gpulayers', '-1',
    '--flashattention',
    '--quantkv', '0'
)

if ($LaunchBrowser) {
    $KoboldArgs += '--launch'
}

Write-Host 'Starting KoboldCpp text baseline:'
Write-Host "  Model:   $model"
Write-Host "  Context: $ContextSize"
Write-Host "  GPU ID:  $GpuId"
Write-Host "  URL:     http://127.0.0.1:$Port"
Write-Host '  GPU layers: AutoFit (-1); CUDA; nommq; Flash Attention; F16 KV'
Write-Host ''

& $exe @KoboldArgs
exit $LASTEXITCODE

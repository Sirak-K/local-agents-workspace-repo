[CmdletBinding()]
param(
    [string]$ModelPath,

    [string]$KoboldCppExe,

    [ValidateRange(256, 524288)]
    [int]$ContextSize = 8192,

    [ValidateRange(0, 3)]
    [int]$GpuId = 0,

    [ValidateRange(1, 65535)]
    [int]$Port = 5001,

    [switch]$LaunchBrowser,
    [switch]$Background
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$SillyRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $KoboldCppExe) {
    $KoboldCppExe = Join-Path $SillyRoot '_local_runtime\KoboldCpp\koboldcpp.exe'
}

$exe = (Resolve-Path -LiteralPath $KoboldCppExe).Path

if (-not $ModelPath) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Title = 'Select a GGUF model for the Guide 1 smoke test'
    $dialog.Filter = 'GGUF models (*.gguf)|*.gguf|All files (*.*)|*.*'
    $dialog.Multiselect = $false
    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        throw 'No GGUF model was selected.'
    }
    $ModelPath = $dialog.FileName
}

$model = (Resolve-Path -LiteralPath $ModelPath).Path
if ([IO.Path]::GetExtension($model).ToLowerInvariant() -ne '.gguf') {
    throw "ModelPath must point to a .gguf file: $model"
}

if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    throw 'nvidia-smi was not found. Verify the NVIDIA driver before starting KoboldCpp.'
}

$listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($listener) {
    throw "TCP port $Port is already in use. Stop the existing listener or choose another port."
}

# Guide 1 is a controlled harness test. AutoFit and performance evidence are
# contaminated when a separate GPU workload already occupies most VRAM.
$gpuRows = @(& nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>$null)
if ($GpuId -ge $gpuRows.Count) {
    throw "GPU ID $GpuId was requested, but nvidia-smi returned only $($gpuRows.Count) GPU(s)."
}
$gpuParts = $gpuRows[$GpuId].Split(',') | ForEach-Object { $_.Trim() }
if ($gpuParts.Count -ge 2) {
    $preUsedMiB = [int]$gpuParts[0]
    $totalMiB = [int]$gpuParts[1]
    $preUsedPct = if ($totalMiB -gt 0) { [math]::Round(($preUsedMiB / $totalMiB) * 100, 1) } else { 0 }
    Write-Host "Pre-existing GPU VRAM use: $preUsedMiB / $totalMiB MiB ($preUsedPct%)"
    if ($preUsedPct -ge 50) {
        throw "Guide 1 requires an uncontended GPU baseline. GPU $GpuId already has $preUsedPct% VRAM in use. Stop other GPU inference/workloads (for example ComfyUI) and rerun."
    }
}

# KoboldCpp v1.120 text-only baseline for Guide 1.
# Flash Attention is enabled unless --noflashattention is passed. Context Shift
# is allowed by leaving --noshift absent, but KoboldCpp may disable it for model
# architectures where shifting is unsupported (for example some mRoPE/hybrid
# models). --noswa prevents SWA from becoming an additional confounder.
$KoboldArgs = @(
    '--model', $model,
    '--host', '127.0.0.1',
    '--port', "$Port",
    '--contextsize', "$ContextSize",
    '--usecuda', 'normal', "$GpuId",
    '--gpulayers', '-1',
    '--nommq',
    '--highpriority',
    '--quantkv', 'f16',
    '--noswa'
)

if ($LaunchBrowser) {
    $KoboldArgs += '--launch'
}

Write-Host 'Starting KoboldCpp Guide 1 text baseline:'
Write-Host "  Executable: $exe"
Write-Host "  Model:      $model"
Write-Host "  Context:    $ContextSize"
Write-Host "  GPU ID:     $GpuId"
Write-Host "  URL:        http://127.0.0.1:$Port"
Write-Host '  CUDA; GPU layers AutoFit (-1); MMQ off; High Priority on'
Write-Host '  Flash Attention allowed/default; F16 KV; Context Shift allowed but architecture-dependent; SWA prevented'
Write-Host ''

if ($Background) {
    function Quote-ProcessArg([string]$Value) {
        if ($Value -match '[\s"]') {
            return '"' + ($Value -replace '"', '\"') + '"'
        }
        return $Value
    }

    $argumentLine = ($KoboldArgs | ForEach-Object { Quote-ProcessArg ([string]$_) }) -join ' '
    $process = Start-Process -FilePath $exe -ArgumentList $argumentLine -PassThru
    return $process
}

& $exe @KoboldArgs
exit $LASTEXITCODE

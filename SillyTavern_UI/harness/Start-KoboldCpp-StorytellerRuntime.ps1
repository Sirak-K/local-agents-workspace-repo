[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('TextCompletionBaseline', 'ChatCompletionNonThinking')]
    [string]$RuntimeProfile,

    [string]$ModelPath,

    [string]$KoboldCppExe,

    [string]$MmprojPath,

    [ValidateRange(256, 524288)]
    [int]$ContextSize = 8192,

    [ValidateRange(0, 3)]
    [int]$GpuId = 0,

    [ValidateRange(1, 65535)]
    [int]$Port = 5001,

    [switch]$LaunchBrowser,
    [switch]$Background,
    [string]$CorrelationId
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$observabilityModulePath = Join-Path $PSScriptRoot 'RuntimeObservability.psm1'
Import-Module -Name $observabilityModulePath -Force -ErrorAction Stop
if ([string]::IsNullOrWhiteSpace($CorrelationId)) { $CorrelationId = New-RuntimeCorrelationId }

$SillyRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $KoboldCppExe) {
    $KoboldCppExe = Join-Path $SillyRoot '_local_runtime\KoboldCpp\koboldcpp.exe'
}

$exe = (Resolve-Path -LiteralPath $KoboldCppExe).Path

if (-not $ModelPath) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Title = 'Select a GGUF model for the local-agent harness'
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

$mmproj = $null
if ($MmprojPath) {
    $mmproj = (Resolve-Path -LiteralPath $MmprojPath).Path
    if ([IO.Path]::GetExtension($mmproj).ToLowerInvariant() -ne '.gguf') {
        throw "MmprojPath must point to a .gguf file: $mmproj"
    }
}

if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    throw 'nvidia-smi was not found. Verify the NVIDIA driver before starting KoboldCpp.'
}

$listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($listener) {
    throw "TCP port $Port is already in use. Stop the existing listener or choose another port."
}

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
        throw "Controlled local Storyteller runtime requires an uncontended GPU. GPU $GpuId already has $preUsedPct% VRAM in use. Stop other GPU inference/workloads (for example ComfyUI) and rerun."
    }
}

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

if ($RuntimeProfile -eq 'ChatCompletionNonThinking') {
    $KoboldArgs += '--jinjathink'
    $KoboldArgs += 'false'
}

if ($mmproj) {
    $KoboldArgs += '--mmproj'
    $KoboldArgs += $mmproj
}
if ($LaunchBrowser) {
    $KoboldArgs += '--launch'
}

Write-Host 'Starting KoboldCpp Storyteller runtime:'
Write-Host "  Profile:    $RuntimeProfile"
Write-Host "  Executable: $exe"
Write-Host "  Model:      $model"
if ($mmproj) { Write-Host "  MMProj:     $mmproj" }
Write-Host "  Context:    $ContextSize"
Write-Host "  GPU ID:     $GpuId"
Write-Host "  URL:        http://127.0.0.1:$Port"
Write-Host '  CUDA; GPU layers AutoFit (-1); MMQ off; High Priority on'
Write-Host '  Flash Attention allowed/default; F16 KV; FastForward/cache architecture-dependent; SWA prevented'
if ($RuntimeProfile -eq 'ChatCompletionNonThinking') {
    Write-Host '  Template:   backend Jinja with enable_thinking=false (--jinjathink false)'
}
else {
    Write-Host '  Template:   preserved Text Completion baseline; no Jinja/thinking override'
}
Write-Host '  Note: KoboldCpp disables ordinary Context Shift for mRoPE models such as Qwen3.5'
Write-Host ''

if ($Background) {
    function Quote-ProcessArg([string]$Value) {
        if ($Value -match '[\s"]') {
            return '"' + ($Value -replace '"', '\"') + '"'
        }
        return $Value
    }

    $argumentLine = ($KoboldArgs | ForEach-Object { Quote-ProcessArg ([string]$_) }) -join ' '
    $process = Start-Process -FilePath $exe -ArgumentList $argumentLine -PassThru -WindowStyle Hidden
    $capture = Start-RuntimeOperationCapture -Owner 'koboldcpp' -Stream 'process_lifecycle' -Producer 'Start-KoboldCpp-StorytellerRuntime.ps1' -ProducerVersion '1.0' -CorrelationId $CorrelationId -Profile $RuntimeProfile -Model ([IO.Path]::GetFileName($model)) -ProcessId $process.Id -Detail @{ port = $Port; context_size = $ContextSize; gpu_id = $GpuId; background = $true; mmproj = $(if ($mmproj) { [IO.Path]::GetFileName($mmproj) } else { $null }) } -EvidenceGap @('Background launch records process creation only; server readiness and model-load completion require a request/probe boundary.')
    if ($null -ne $capture) {
        Add-RuntimeOperationEvent -File $capture.file -EventType 'koboldcpp.process_started' -Details @{ pid = $process.Id; port = $Port; profile = $RuntimeProfile } -Outcome 'success'
        Complete-RuntimeOperationCapture -File $capture.file -Status 'completed' -StopReason 'process_started' -DurationSeconds 0
    }
    return $process
}

$foregroundCapture = Start-RuntimeOperationCapture -Owner 'koboldcpp' -Stream 'process_lifecycle' -Producer 'Start-KoboldCpp-StorytellerRuntime.ps1' -ProducerVersion '1.0' -CorrelationId $CorrelationId -Profile $RuntimeProfile -Model ([IO.Path]::GetFileName($model)) -Detail @{ port = $Port; context_size = $ContextSize; gpu_id = $GpuId; background = $false; mmproj = $(if ($mmproj) { [IO.Path]::GetFileName($mmproj) } else { $null }) } -EvidenceGap @('Foreground direct invocation does not expose the child PID through this PowerShell boundary.')
$runtimeStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
if ($null -ne $foregroundCapture) {
    Add-RuntimeOperationEvent -File $foregroundCapture.file -EventType 'koboldcpp.process_launch_requested' -Details @{ port = $Port; profile = $RuntimeProfile } -Outcome 'observed'
}
& $exe @KoboldArgs
$exitCode = $LASTEXITCODE
$runtimeStopwatch.Stop()
if ($null -ne $foregroundCapture) {
    $eventOutcome = if ($exitCode -eq 0) { 'success' } else { 'failure' }
    $severity = if ($exitCode -eq 0) { 'info' } else { 'error' }
    Add-RuntimeOperationEvent -File $foregroundCapture.file -EventType 'koboldcpp.process_exited' -Details @{ exit_code = $exitCode } -Outcome $eventOutcome -Severity $severity -DurationSeconds $runtimeStopwatch.Elapsed.TotalSeconds
    $finalStatus = if ($exitCode -eq 0) { 'completed' } else { 'failed' }
    Complete-RuntimeOperationCapture -File $foregroundCapture.file -Status $finalStatus -StopReason 'process_exited' -DurationSeconds $runtimeStopwatch.Elapsed.TotalSeconds
}
exit $exitCode

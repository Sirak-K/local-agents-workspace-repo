[CmdletBinding()]
param(
    [int]$Port = 7864,
    [string]$AiRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $AiRoot) {
    $userProfilePath = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
    $AiRoot = Join-Path $userProfilePath 'AI_Folder'
}

$diaApp = Join-Path $AiRoot 'apps\dia2'
$diaModel = Join-Path $AiRoot 'models\tts\Dia2-1B'
$mimiModel = Join-Path $AiRoot 'models\audio_encoders\mimi'
$userScriptsPath = (& python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))").Trim()
$uvExe = Join-Path $userScriptsPath 'uv.exe'

if (-not (Test-Path -LiteralPath $diaApp -PathType Container)) {
    throw "Dia2 application is missing: $diaApp"
}

if (-not (Test-Path -LiteralPath (Join-Path $diaModel 'model.safetensors') -PathType Leaf)) {
    throw "Dia2-1B weights are missing: $diaModel"
}

if (-not (Test-Path -LiteralPath (Join-Path $mimiModel 'model.safetensors') -PathType Leaf)) {
    throw "Mimi codec weights are missing: $mimiModel"
}

if (-not (Test-Path -LiteralPath $uvExe -PathType Leaf)) {
    throw "uv.exe is missing: $uvExe"
}

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    throw "Port $Port is already in use by PID $($listener[0].OwningProcess)."
}

$env:DIA2_LOCAL_MODEL = $diaModel
$env:DIA2_LOCAL_MIMI = $mimiModel
$env:GRADIO_ANALYTICS_ENABLED = 'False'
$env:HF_HUB_OFFLINE = '1'
$launchCode = @'
import torch
import gradio_app
import os
from pathlib import Path

original_generation_config = gradio_app.GenerationConfig
local_dia = None

def memory_safe_generation_config(*args, **kwargs):
    kwargs["use_cuda_graph"] = False
    return original_generation_config(*args, **kwargs)

gradio_app.GenerationConfig = memory_safe_generation_config

def get_local_dia():
    global local_dia
    if local_dia is None:
        model_root = Path(os.environ["DIA2_LOCAL_MODEL"])
        local_dia = gradio_app.Dia2.from_local(
            config_path=model_root / "config.json",
            weights_path=model_root / "model.safetensors",
            tokenizer_id=model_root,
            mimi_id=os.environ["DIA2_LOCAL_MIMI"],
            device="cuda",
            dtype="bfloat16",
        )
    return local_dia

gradio_app._get_dia = get_local_dia
torch.set_float32_matmul_precision("high")

app = gradio_app.build_interface()
app.queue(default_concurrency_limit=1)
app.launch(
    server_name="127.0.0.1",
    server_port=7864,
    share=False,
    inbrowser=False,
    show_error=True,
)
'@

if ($Port -ne 7864) {
    $launchCode = $launchCode.Replace('server_port=7864', "server_port=$Port")
}

Write-Host "Starting local-only Dia2-1B UI: http://127.0.0.1:$Port"
Write-Host 'The model remains unloaded until Generate is pressed.'
Write-Host 'First-proof profile: CUDA BF16, CUDA Graph OFF, one queued generation.'

Push-Location -LiteralPath $diaApp
try {
    $launchCode | & $uvExe run python -
    if ($LASTEXITCODE -ne 0) {
        throw "Dia2 UI exited with code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

[CmdletBinding()]
param(
    [string]$AiRoot,
    [switch]$PrerequisiteCheckOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $AiRoot) {
    $userProfilePath = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
    $AiRoot = Join-Path $userProfilePath 'AI_Folder'
}

$appsRoot = Join-Path $AiRoot 'apps'
$modelsRoot = Join-Path $AiRoot 'models'
$diaApp = Join-Path $appsRoot 'dia2'
$diaModel = Join-Path $modelsRoot 'tts\Dia2-1B'
$sanaModel = Join-Path $modelsRoot 'diffusers\Sana_Sprint_0.6B_1024px_diffusers'
$diaWeights = Join-Path $diaModel 'model.safetensors'
$sanaIndex = Join-Path $sanaModel 'model_index.json'
$diaExpectedSha256 = 'c398c607b159f024dfb76c6102244afe53b01daf18676af8408a3a0bb97d1c76'

function Assert-LastExitCode {
    param([Parameter(Mandatory)][string]$Operation)

    if ($LASTEXITCODE -ne 0) {
        throw "$Operation failed with exit code $LASTEXITCODE."
    }
}

function Resolve-UvExecutable {
    $command = Get-Command 'uv.exe' -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $userScriptsPath = (& python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))").Trim()
    Assert-LastExitCode -Operation 'Python user Scripts path discovery'

    $candidate = Join-Path $userScriptsPath 'uv.exe'
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        return $candidate
    }

    & python -m pip install --user --upgrade uv | Out-Host
    Assert-LastExitCode -Operation 'uv installation'

    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "uv.exe was installed but not found at the Python user Scripts path: $candidate"
    }

    return $candidate
}

if (-not (Test-Path -LiteralPath $appsRoot -PathType Container)) {
    throw "Apps root does not exist: $appsRoot"
}

if (-not (Test-Path -LiteralPath $modelsRoot -PathType Container)) {
    throw "Models root does not exist: $modelsRoot"
}

$uvExe = Resolve-UvExecutable
& $uvExe --version
Assert-LastExitCode -Operation 'uv startup check'

if ($PrerequisiteCheckOnly) {
    Write-Host "PASS: prerequisites resolved; uv executable: $uvExe"
    return
}

if (-not (Test-Path -LiteralPath $diaApp)) {
    & git clone 'https://github.com/nari-labs/dia2.git' $diaApp
    Assert-LastExitCode -Operation 'Dia2 repository clone'
}
elseif (-not (Test-Path -LiteralPath (Join-Path $diaApp '.git') -PathType Container)) {
    throw "Dia2 target exists but is not a Git repository: $diaApp"
}
else {
    Write-Host 'Dia2 repository already exists; preserving it without pull/reset.'
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $diaModel) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $sanaModel) | Out-Null

Push-Location -LiteralPath $diaApp
try {
    & $uvExe sync
    Assert-LastExitCode -Operation 'Dia2 dependency sync'

    & $uvExe run hf download 'nari-labs/Dia2-1B' --local-dir $diaModel
    Assert-LastExitCode -Operation 'Dia2-1B snapshot download'

    & $uvExe run hf download 'Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers' --local-dir $sanaModel
    Assert-LastExitCode -Operation 'SANA-Sprint snapshot download'
}
finally {
    Pop-Location
}

if (-not (Test-Path -LiteralPath $diaWeights -PathType Leaf)) {
    throw "Dia2 weights are missing: $diaWeights"
}

$diaActualSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $diaWeights).Hash.ToLowerInvariant()
if ($diaActualSha256 -ne $diaExpectedSha256) {
    throw "Dia2 SHA-256 mismatch. Expected $diaExpectedSha256 but got $diaActualSha256."
}

if (-not (Test-Path -LiteralPath $sanaIndex -PathType Leaf)) {
    throw "SANA model index is missing: $sanaIndex"
}

$requiredSanaFolders = @('scheduler', 'text_encoder', 'tokenizer', 'transformer', 'vae')
foreach ($folderName in $requiredSanaFolders) {
    $folderPath = Join-Path $sanaModel $folderName
    if (-not (Test-Path -LiteralPath $folderPath -PathType Container)) {
        throw "SANA snapshot is missing required component folder: $folderName"
    }
}

$sanaWeights = @(Get-ChildItem -LiteralPath $sanaModel -Recurse -File -Filter '*.safetensors')
if ($sanaWeights.Count -lt 3) {
    throw "SANA snapshot appears incomplete: only $($sanaWeights.Count) safetensors files were found."
}

Write-Host 'PASS: Dia2 runtime dependencies are installed.'
Write-Host 'PASS: Dia2-1B snapshot is complete and SHA-256 verified.'
Write-Host "PASS: SANA-Sprint snapshot contains $($sanaWeights.Count) safetensors files and all required components."
Write-Host 'No model or GPU inference process was started.'

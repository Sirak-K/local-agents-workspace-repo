[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 5001
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$base = "http://127.0.0.1:$Port"

function Get-JsonEndpoint {
    param([Parameter(Mandatory = $true)][string]$Path)
    Invoke-RestMethod -Method Get -Uri "$base$Path" -TimeoutSec 10
}

$version = Get-JsonEndpoint '/api/extra/version'
$model = Get-JsonEndpoint '/api/v1/model'
$context = Get-JsonEndpoint '/api/extra/true_max_context_length'
$models = Get-JsonEndpoint '/v1/models'

$gpu = $null
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    $gpu = (& nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader,nounits 2>$null) -join '; '
}

$result = [ordered]@{
    checked_at = (Get-Date).ToString('o')
    endpoint = $base
    koboldcpp_version = $version
    kobold_model = $model
    true_max_context = $context
    openai_models = $models
    nvidia_gpu_memory = $gpu
    endpoint_check = 'PASS'
}

$result | ConvertTo-Json -Depth 10

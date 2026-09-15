[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 5001,

    [string]$ExpectedVersion = '1.120',

    [ValidateRange(256, 524288)]
    [int]$ExpectedContext = 8192
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

if ($version.result -ne 'KoboldCpp') {
    throw "Unexpected backend identity from $base: $($version.result)"
}
if ([string]$version.version -ne $ExpectedVersion) {
    throw "KoboldCpp version mismatch. Expected $ExpectedVersion, got $($version.version)."
}
if ([int]$context.value -ne $ExpectedContext) {
    throw "Context mismatch. Expected $ExpectedContext, got $($context.value)."
}

$gpu = $null
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    $gpu = (& nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader,nounits 2>$null) -join '; '
}

$result = [ordered]@{
    checked_at = (Get-Date).ToString('o')
    endpoint = $base
    endpoint_check = 'PASS'
    expected_version = $ExpectedVersion
    koboldcpp_version = $version.version
    kobold_capabilities = $version
    kobold_model = $model
    expected_context = $ExpectedContext
    true_max_context = $context.value
    openai_models = $models
    nvidia_gpu_memory = $gpu
}

$result | ConvertTo-Json -Depth 10

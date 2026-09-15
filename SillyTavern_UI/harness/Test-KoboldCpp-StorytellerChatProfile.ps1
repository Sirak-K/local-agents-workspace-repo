[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 5001,

    [string]$ExpectedVersion = '1.120',

    [ValidateRange(256, 524288)]
    [int]$ExpectedContext = 8192,

    [ValidateRange(16, 512)]
    [int]$MaxTokens = 64,

    [ValidateRange(10, 600)]
    [int]$TimeoutSec = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$validatorModulePath = Join-Path $PSScriptRoot 'StorytellerChatResponseValidation.psm1'
Import-Module -Name $validatorModulePath -Force -ErrorAction Stop

$base = "http://127.0.0.1:$Port"
$expectedContent = 'STORYTELLER_PROFILE_OK'

function Get-JsonEndpoint {
    param([Parameter(Mandatory = $true)][string]$Path)
    Invoke-RestMethod -Method Get -Uri "$base$Path" -TimeoutSec 10
}

$version = Get-JsonEndpoint '/api/extra/version'
$context = Get-JsonEndpoint '/api/extra/true_max_context_length'
$models = Get-JsonEndpoint '/v1/models'

if ($version.result -ne 'KoboldCpp') {
    throw ('Unexpected backend identity from {0}: {1}' -f $base, $version.result)
}
if ([string]$version.version -ne $ExpectedVersion) {
    throw ('KoboldCpp version mismatch. Expected {0}, got {1}.' -f $ExpectedVersion, $version.version)
}
if ([int]$context.value -ne $ExpectedContext) {
    throw ('Context mismatch. Expected {0}, got {1}.' -f $ExpectedContext, $context.value)
}

$modelId = 'koboldcpp'
$modelRows = @($models.data)
if ($modelRows.Count -gt 0 -and $modelRows[0].id) {
    $modelId = [string]$modelRows[0].id
}

$request = [ordered]@{
    model = $modelId
    messages = @(
        [ordered]@{
            role = 'user'
            content = 'Reply with exactly STORYTELLER_PROFILE_OK and nothing else.'
        }
    )
    max_tokens = $MaxTokens
    temperature = 0
    stream = $false
}

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$response = Invoke-RestMethod `
    -Method Post `
    -Uri "$base/v1/chat/completions" `
    -ContentType 'application/json; charset=utf-8' `
    -Body ($request | ConvertTo-Json -Depth 8 -Compress) `
    -TimeoutSec $TimeoutSec
$stopwatch.Stop()

$validation = Test-StorytellerChatResponseContract -Response $response -ExpectedContent $expectedContent
$choices = @($response.choices)

$usageProperty = $response.PSObject.Properties['usage']
$usage = if ($null -eq $usageProperty) { $null } else { $usageProperty.Value }

$performance = $null
try {
    $performance = Get-JsonEndpoint '/api/extra/perf'
}
catch {
    $performance = [ordered]@{
        available = $false
        error = $_.Exception.Message
    }
}

$result = [ordered]@{
    checked_at = (Get-Date).ToString('yyyy-MM-dd | HH:mm:ss.fff zzz')
    endpoint = $base
    profile_check = 'PASS'
    expected_version = $ExpectedVersion
    koboldcpp_version = $version.version
    expected_context = $ExpectedContext
    true_max_context = $context.value
    model = $modelId
    elapsed_ms = $stopwatch.ElapsedMilliseconds
    content = $validation.content
    reasoning_content = $validation.reasoning_content
    finish_reason = $choices[0].finish_reason
    usage = $usage
    performance = $performance
}

$result | ConvertTo-Json -Depth 10

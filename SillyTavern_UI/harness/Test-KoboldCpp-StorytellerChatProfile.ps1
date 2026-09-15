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
    [int]$TimeoutSec = 180,

    [string]$CorrelationId,
    [switch]$LogRawIO
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$observabilityModulePath = Join-Path $PSScriptRoot 'RuntimeObservability.psm1'
Import-Module -Name $observabilityModulePath -Force -ErrorAction Stop
if ([string]::IsNullOrWhiteSpace($CorrelationId)) { $CorrelationId = New-RuntimeCorrelationId }

$validatorModulePath = Join-Path $PSScriptRoot 'StorytellerChatResponseValidation.psm1'
Import-Module -Name $validatorModulePath -Force -ErrorAction Stop

$base = "http://127.0.0.1:$Port"
$expectedContent = 'STORYTELLER_PROFILE_OK'

function Get-Utf8Evidence {
    param([Parameter(Mandatory = $true)][string]$Text)
    $bytes = [Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $hash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
    return @{ bytes = $bytes.Length; sha256 = $hash }
}

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

$requestJson = $request | ConvertTo-Json -Depth 8 -Compress
$requestEvidence = Get-Utf8Evidence -Text $requestJson
$capture = Start-RuntimeOperationCapture -Owner 'koboldcpp' -Stream 'chat_completion_request' -Producer 'Test-KoboldCpp-StorytellerChatProfile.ps1' -ProducerVersion '1.0' -CorrelationId $CorrelationId -Profile 'ChatCompletionNonThinking' -Model $modelId -Detail @{ endpoint = '/v1/chat/completions'; max_tokens = $MaxTokens; temperature = 0; stream = $false; raw_io_opt_in = [bool]$LogRawIO }
if ($null -ne $capture) {
    $requestDetails = @{ request_bytes = $requestEvidence.bytes; request_sha256 = $requestEvidence.sha256; correlation_header = 'X-Local-Agents-Correlation-Id' }
    if ($LogRawIO) { $requestDetails['content'] = $requestJson }
    Add-RuntimeOperationEvent -File $capture.file -EventType 'koboldcpp.request_started' -Details $requestDetails -Outcome 'observed' -AllowSensitiveContent:$LogRawIO
}

$headers = @{ 'X-Local-Agents-Correlation-Id' = $CorrelationId }
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
try {
    $response = Invoke-RestMethod `
        -Method Post `
        -Uri "$base/v1/chat/completions" `
        -Headers $headers `
        -ContentType 'application/json; charset=utf-8' `
        -Body $requestJson `
        -TimeoutSec $TimeoutSec
}
catch {
    $stopwatch.Stop()
    if ($null -ne $capture) {
        Add-RuntimeOperationEvent -File $capture.file -EventType 'koboldcpp.request_failed' -Details @{ error_class = $_.Exception.GetType().Name } -Severity 'error' -Outcome 'failure' -DurationSeconds $stopwatch.Elapsed.TotalSeconds
        Complete-RuntimeOperationCapture -File $capture.file -Status 'failed' -StopReason 'request_failed' -DurationSeconds $stopwatch.Elapsed.TotalSeconds
    }
    throw
}
$stopwatch.Stop()

try {
    $validation = Test-StorytellerChatResponseContract -Response $response -ExpectedContent $expectedContent
}
catch {
    if ($null -ne $capture) {
        Add-RuntimeOperationEvent -File $capture.file -EventType 'koboldcpp.response_validation_failed' -Details @{ error_class = $_.Exception.GetType().Name } -Severity 'error' -Outcome 'failure' -DurationSeconds $stopwatch.Elapsed.TotalSeconds
        Complete-RuntimeOperationCapture -File $capture.file -Status 'failed' -StopReason 'response_validation_failed' -DurationSeconds $stopwatch.Elapsed.TotalSeconds
    }
    throw
}
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

$responseJson = $response | ConvertTo-Json -Depth 12 -Compress
$responseEvidence = Get-Utf8Evidence -Text $responseJson
if ($null -ne $capture) {
    $responseDetails = @{ response_bytes = $responseEvidence.bytes; response_sha256 = $responseEvidence.sha256; finish_reason = $choices[0].finish_reason; usage = $usage }
    if ($LogRawIO) { $responseDetails['content'] = $responseJson }
    Add-RuntimeOperationEvent -File $capture.file -EventType 'koboldcpp.request_completed' -Details $responseDetails -Outcome 'success' -DurationSeconds $stopwatch.Elapsed.TotalSeconds -AllowSensitiveContent:$LogRawIO
    $perfAvailable = -not ($performance.PSObject.Properties['available'] -and $performance.available -eq $false)
    Add-RuntimeOperationEvent -File $capture.file -EventType 'koboldcpp.performance_observed' -Details @{ available = $perfAvailable; perf = $performance } -Outcome $(if ($perfAvailable) { 'observed' } else { 'partial' })
    Complete-RuntimeOperationCapture -File $capture.file -Status 'completed' -StopReason 'probe_completed' -DurationSeconds $stopwatch.Elapsed.TotalSeconds
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

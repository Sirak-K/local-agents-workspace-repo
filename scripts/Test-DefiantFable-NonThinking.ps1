[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 5001,

    [string]$ExpectedModelPattern = 'Defiant-Fable'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$base = "http://127.0.0.1:$Port"

$models = Invoke-RestMethod -Method Get -Uri "$base/v1/models" -TimeoutSec 10
if (-not $models.data -or $models.data.Count -lt 1) {
    throw "No model is reported by $base/v1/models."
}

$modelId = [string]$models.data[0].id
if ($ExpectedModelPattern -and $modelId -notlike "*$ExpectedModelPattern*") {
    throw "Unexpected model loaded: $modelId"
}

$request = [ordered]@{
    model = $modelId
    messages = @(
        [ordered]@{
            role = 'system'
            content = 'Answer directly and naturally. Do not output reasoning tags or role/template markers.'
        },
        [ordered]@{
            role = 'user'
            content = 'Reply with one short sentence confirming that this non-thinking API test is working.'
        }
    )
    max_tokens = 96
    temperature = 0.0
    stream = $false
}

$body = $request | ConvertTo-Json -Depth 8
$response = Invoke-RestMethod -Method Post -Uri "$base/v1/chat/completions" -ContentType 'application/json' -Body $body -TimeoutSec 120

if (-not $response.choices -or $response.choices.Count -lt 1) {
    throw 'Chat Completions returned no choices.'
}

$content = [string]$response.choices[0].message.content
if ([string]::IsNullOrWhiteSpace($content)) {
    throw 'Chat Completions returned an empty assistant message.'
}

$forbidden = @(
    '<think>',
    '</think>',
    '<|im_start|>',
    '<|im_end|>'
)

$leaked = @($forbidden | Where-Object { $content.IndexOf($_, [StringComparison]::OrdinalIgnoreCase) -ge 0 })
if ($leaked.Count -gt 0) {
    throw ('Non-thinking/template marker leak detected: ' + ($leaked -join ', '))
}

$result = [ordered]@{
    checked_at = (Get-Date).ToString('o')
    endpoint = "$base/v1/chat/completions"
    endpoint_check = 'PASS'
    model = $modelId
    marker_leak_check = 'PASS'
    assistant_sample = $content
}

$result | ConvertTo-Json -Depth 6

# codex_lm_studio_connection_smoke.ps1
# Verifies the project-owned Codex evaluator connection to LM Studio REST API v1.

param(
    [string]$Model = "granite-4.1-3b",
    [string]$Token = $env:LM_API_TOKEN,
    [int]$TimeoutSeconds = 90
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:1234"
$probeInstruction = "Reply with exactly the single word: OK"

function Stop-SmokeTest {
    param(
        [string]$Message,
        [int]$ExitCode = 1
    )

    Write-Host "FAILED: $Message" -ForegroundColor Red
    exit $ExitCode
}

Write-Host "=== Codex to LM Studio connection smoke test ===" -ForegroundColor Cyan
Write-Host "Target: $baseUrl"
Write-Host "Model:  $Model"

if ([string]::IsNullOrWhiteSpace($Token)) {
    Stop-SmokeTest -Message "LM_API_TOKEN is unavailable in this process." -ExitCode 2
}

if ([string]::IsNullOrWhiteSpace($Model)) {
    Stop-SmokeTest -Message "Model must be a non-empty models[].key value." -ExitCode 2
}

if ($TimeoutSeconds -lt 1) {
    Stop-SmokeTest -Message "TimeoutSeconds must be greater than zero." -ExitCode 2
}

Write-Host "[1/3] Verifying server and authentication..." -NoNewline
try {
    $modelsResponse = Invoke-RestMethod `
        -Uri "$baseUrl/api/v1/models" `
        -Method Get `
        -Headers @{ Authorization = "Bearer $Token" } `
        -TimeoutSec 10
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Stop-SmokeTest -Message "GET /api/v1/models failed: $($_.Exception.Message)"
}
Write-Host " OK" -ForegroundColor Green

Write-Host "[2/3] Validating model catalog..." -NoNewline
if ($null -eq $modelsResponse -or $modelsResponse.PSObject.Properties.Name -notcontains "models") {
    Write-Host " FAILED" -ForegroundColor Red
    Stop-SmokeTest -Message "LM Studio response did not contain the required models array."
}

$models = @($modelsResponse.models)
if ($models.Count -eq 0) {
    Write-Host " FAILED" -ForegroundColor Red
    Stop-SmokeTest -Message "LM Studio returned no models."
}

$targetModel = $models |
    Where-Object { $_.type -eq "llm" -and $_.key -eq $Model } |
    Select-Object -First 1

if ($null -eq $targetModel) {
    Write-Host " FAILED" -ForegroundColor Red
    $availableLlmKeys = @($models | Where-Object { $_.type -eq "llm" } | ForEach-Object { $_.key }) -join ", "
    Stop-SmokeTest -Message "Model key '$Model' was not returned. Available LLM keys: $availableLlmKeys"
}

if (@($targetModel.loaded_instances).Count -eq 0) {
    Write-Host " FAILED" -ForegroundColor Red
    Stop-SmokeTest -Message "Model '$Model' is not loaded. Load it in LM Studio before running this bounded smoke test."
}
Write-Host " OK ($($models.Count) models found; target loaded)" -ForegroundColor Green

Write-Host "[3/3] Running deterministic stateless chat probe..." -NoNewline
$requestBody = @{
    model = $targetModel.key
    input = $probeInstruction
    temperature = 0
    store = $false
} | ConvertTo-Json

try {
    $chatResponse = Invoke-RestMethod `
        -Uri "$baseUrl/api/v1/chat" `
        -Method Post `
        -Headers @{
            Authorization = "Bearer $Token"
            "Content-Type" = "application/json"
        } `
        -Body $requestBody `
        -TimeoutSec $TimeoutSeconds
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Stop-SmokeTest -Message "POST /api/v1/chat failed: $($_.Exception.Message)"
}

if ($null -eq $chatResponse -or $chatResponse.PSObject.Properties.Name -notcontains "output") {
    Write-Host " FAILED" -ForegroundColor Red
    Stop-SmokeTest -Message "LM Studio response did not contain the required output array."
}

$messageItems = @(
    $chatResponse.output |
        Where-Object { $_.type -eq "message" -and $_.content -is [string] }
)

if ($messageItems.Count -ne 1) {
    Write-Host " FAILED" -ForegroundColor Red
    Stop-SmokeTest -Message "Expected exactly one message item in the output array; received $($messageItems.Count)."
}

$reply = $messageItems[0].content.Trim()
if (-not [string]::Equals($reply, "OK", [System.StringComparison]::Ordinal)) {
    Write-Host " FAILED" -ForegroundColor Red
    $displayReply = if ($reply.Length -gt 200) { $reply.Substring(0, 200) + "..." } else { $reply }
    Stop-SmokeTest -Message "The deterministic probe returned '$displayReply' instead of 'OK'."
}

Write-Host " OK" -ForegroundColor Green
Write-Host "Reply: $reply"
Write-Host "=== CODEX LM STUDIO CONNECTION ESTABLISHED ===" -ForegroundColor Green

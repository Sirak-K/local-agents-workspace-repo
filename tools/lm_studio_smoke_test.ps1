# lm_studio_smoke_test.ps1
# Minimal smoke test for Grok → LM Studio Local Server
# Run from: C:\Users\SSIRA\AI_Folder\workspaces\comfy_ui_workspace
#
# Usage:
#   $env:LM_API_TOKEN = "din-token-här"
#   .\tools\lm_studio_smoke_test.ps1
#
# Or pass token as argument:
#   .\tools\lm_studio_smoke_test.ps1 -Token "din-token-här"

param(
    [string]$Token = $env:LM_API_TOKEN
)

$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:1234"

Write-Host "=== LM Studio Smoke Test ===" -ForegroundColor Cyan
Write-Host "Target: $baseUrl"
Write-Host ""

if (-not $Token) {
    Write-Host "ERROR: No API token provided." -ForegroundColor Red
    Write-Host ""
    Write-Host "LM Studio requires an API token (Authentication is enabled)."
    Write-Host ""
    Write-Host "Do this once:"
    Write-Host "  1. In LM Studio → Developer → Server Settings → Manage Tokens"
    Write-Host "  2. Create a token"
    Write-Host "  3. Run either:"
    Write-Host '       $env:LM_API_TOKEN = "din-token"'
    Write-Host "       .\tools\lm_studio_smoke_test.ps1"
    Write-Host "     or:"
    Write-Host '       .\tools\lm_studio_smoke_test.ps1 -Token "din-token"'
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $Token"
    "Content-Type"  = "application/json"
}

# 1. Check server reachability
Write-Host "[1/3] Checking Local Server..." -NoNewline
try {
    $null = Invoke-RestMethod -Uri "$baseUrl/api/v1/models" -Method Get -Headers $headers -TimeoutSec 5
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "Error: $_"
    Write-Host ""
    Write-Host "Possible causes:"
    Write-Host "  - Local Server is not running"
    Write-Host "  - Wrong or expired API token"
    exit 1
}

# 2. List models
Write-Host "[2/3] Listing models..."
try {
    $modelsResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/models" -Method Get -Headers $headers -TimeoutSec 10
    $models = $modelsResponse.models

    if (-not $models -or $models.Count -eq 0) {
        Write-Host "  No models returned." -ForegroundColor Yellow
        Write-Host "  Load at least one model in LM Studio and re-run."
        exit 0
    }

    Write-Host "  Found $($models.Count) model(s):" -ForegroundColor Green
    foreach ($m in $models) {
        $key = $m.key
        $name = $m.display_name
        $loaded = if ($m.loaded_instances -and $m.loaded_instances.Count -gt 0) { " [LOADED]" } else { "" }
        Write-Host "    - $key  ($name)$loaded"
    }
} catch {
    Write-Host "  Failed to list models: $_" -ForegroundColor Red
    exit 1
}

# 3. Simple chat test (uses first loaded model, or first model if none loaded)
Write-Host ""
Write-Host "[3/3] Chat smoke test..."

$targetModel = $null
foreach ($m in $models) {
    if ($m.loaded_instances -and $m.loaded_instances.Count -gt 0) {
        $targetModel = $m.key
        break
    }
}
if (-not $targetModel) {
    $targetModel = $models[0].key
    Write-Host "  No model currently loaded. Attempting JIT load of: $targetModel" -ForegroundColor Yellow
}

$body = @{
    model       = $targetModel
    input       = "Reply with exactly the single word: OK"
    temperature = 0
} | ConvertTo-Json

try {
    $chatResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/chat" -Method Post -Headers $headers -Body $body -TimeoutSec 90

    # LM Studio REST API v1 returns:
    # {
    #   "model_instance_id": "...",
    #   "output": [ { "type": "message", "content": "..." } ],
    #   "stats": { ... },
    #   "response_id": "..."
    # }
    $reply = $null
    if ($chatResponse.output -and $chatResponse.output.Count -gt 0) {
        $reply = $chatResponse.output[0].content
    }
    if (-not $reply) { $reply = $chatResponse.content }
    if (-not $reply) { $reply = ($chatResponse | ConvertTo-Json -Depth 5) }

    Write-Host "  Model : $targetModel" -ForegroundColor Green
    Write-Host "  Reply : $reply"

    if ($reply -match "^\s*OK\s*$") {
        Write-Host ""
        Write-Host "=== SMOKE TEST PASSED ===" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "=== SMOKE TEST WARNING ===" -ForegroundColor Yellow
        Write-Host "Response received but did not match expected 'OK'."
    }
} catch {
    Write-Host "  Chat request failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible causes:"
    Write-Host "  - No model loaded and JIT loading failed"
    Write-Host "  - Model key incorrect"
    Write-Host "  - Server busy / timeout"
    exit 1
}

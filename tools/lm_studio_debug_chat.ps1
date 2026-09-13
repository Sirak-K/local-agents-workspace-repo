# lm_studio_debug_chat.ps1
# Debug the exact response shape from /api/v1/chat

param(
    [string]$Token = $env:LM_API_TOKEN,
    [string]$Model = "granite-4.1-3b"
)

$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:1234"

if (-not $Token) {
    Write-Host "ERROR: LM_API_TOKEN saknas" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $Token"
    "Content-Type"  = "application/json"
}

$body = @{
    model       = $Model
    input       = "Reply with exactly the single word: OK"
    temperature = 0
} | ConvertTo-Json

Write-Host "=== Debug /api/v1/chat ===" -ForegroundColor Cyan
Write-Host "Model: $Model"
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/chat" -Method Post -Headers $headers -Body $body -TimeoutSec 90
    Write-Host "Raw response (PowerShell object):" -ForegroundColor Yellow
    $response | Format-List * | Out-String | Write-Host
    Write-Host ""
    Write-Host "JSON:" -ForegroundColor Yellow
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Request failed:" -ForegroundColor Red
    Write-Host $_
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        Write-Host $reader.ReadToEnd()
    }
}

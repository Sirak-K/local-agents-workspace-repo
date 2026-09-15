[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$PreferredPort = 8001,

    [ValidateRange(1, 65535)]
    [int]$MaxPort = 8099
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($MaxPort -lt $PreferredPort) {
    throw 'MaxPort must be greater than or equal to PreferredPort.'
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$configPath = Join-Path $repoRoot 'SillyTavern_UI\_local_runtime\SillyTavern\config.yaml'

if (-not (Test-Path -LiteralPath $configPath)) {
    throw "SillyTavern config was not found at: $configPath"
}

function Test-TcpPortFree {
    param([Parameter(Mandatory = $true)][int]$Port)

    $listeners = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
    return -not ($listeners | Where-Object { $_.Port -eq $Port })
}

$selectedPort = $null
for ($port = $PreferredPort; $port -le $MaxPort; $port++) {
    if (Test-TcpPortFree -Port $port) {
        $selectedPort = $port
        break
    }
}

if ($null -eq $selectedPort) {
    throw "No free TCP port was found in range $PreferredPort-$MaxPort."
}

$raw = [IO.File]::ReadAllText($configPath)
$pattern = '(?m)^port:\s*\d+\s*$'
$matches = [regex]::Matches($raw, $pattern)
if ($matches.Count -ne 1) {
    throw "Expected exactly one top-level SillyTavern port setting in config.yaml; found $($matches.Count)."
}

$currentPort = [int](([regex]::Match($raw, '(?m)^port:\s*(\d+)\s*$')).Groups[1].Value)

if ($currentPort -eq $selectedPort) {
    Write-Host "SillyTavern is already configured for port $selectedPort."
    Write-Host "URL: http://127.0.0.1:$selectedPort/"
    exit 0
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupPath = "$configPath.before-port-change-$timestamp.bak"
Copy-Item -LiteralPath $configPath -Destination $backupPath -Force

$updated = [regex]::Replace($raw, $pattern, "port: $selectedPort")
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($configPath, $updated, $utf8NoBom)

Write-Host "SillyTavern port updated: $currentPort -> $selectedPort"
Write-Host "Verified free before configuration change: TCP $selectedPort"
Write-Host "Backup: $backupPath"
Write-Host "Restart SillyTavern for the change to take effect."
Write-Host "New URL: http://127.0.0.1:$selectedPort/"

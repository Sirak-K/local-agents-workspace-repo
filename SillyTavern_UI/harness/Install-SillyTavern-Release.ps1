[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InstallRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'git was not found. Install Git for Windows first.'
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'node was not found. Install the latest Node.js LTS first.'
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw 'npm was not found. Repair/reinstall Node.js LTS first.'
}

$root = [IO.Path]::GetFullPath($InstallRoot)
$blockedRoots = @(
    [Environment]::GetFolderPath('Windows'),
    [Environment]::GetFolderPath('ProgramFiles'),
    [Environment]::GetFolderPath('ProgramFilesX86')
) | Where-Object { $_ }

foreach ($blocked in $blockedRoots) {
    if ($root.StartsWith([IO.Path]::GetFullPath($blocked), [StringComparison]::OrdinalIgnoreCase)) {
        throw "InstallRoot must not be inside a Windows-controlled folder: $blocked"
    }
}

New-Item -ItemType Directory -Path $root -Force | Out-Null
$destination = Join-Path $root 'SillyTavern'

if (Test-Path -LiteralPath $destination) {
    throw "Destination already exists: $destination. Refusing to overwrite or update it automatically."
}

Write-Host "Node: $(node --version)"
Write-Host "npm:  $(npm --version)"
Write-Host "Git:  $(git --version)"
Write-Host "Cloning SillyTavern release branch to: $destination"

& git clone --branch release --single-branch https://github.com/SillyTavern/SillyTavern.git $destination
if ($LASTEXITCODE -ne 0) {
    throw "git clone failed with exit code $LASTEXITCODE"
}

Write-Host ''
Write-Host 'Clone complete.'
Write-Host "Next local step: run '$destination\Start.bat' normally (not as Administrator)."

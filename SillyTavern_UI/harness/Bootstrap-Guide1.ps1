[CmdletBinding()]
param(
    [switch]$SkipPrerequisiteInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$KoboldVersion = '1.120'
$KoboldUri = "https://github.com/LostRuins/koboldcpp/releases/download/v$KoboldVersion/koboldcpp.exe"
$KoboldSha256 = '6544239ab2747ee84e1ca265a702772fe63719774b829ec9e829f4029ac013db'
$SillyTavernCommit = '06bde939fb1e9c4c8d8641d810f0a916b5bce127'
$SillyTavernRepo = 'https://github.com/SillyTavern/SillyTavern.git'

$SillyRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$RuntimeRoot = Join-Path $SillyRoot '_local_runtime'
$KoboldDir = Join-Path $RuntimeRoot 'KoboldCpp'
$KoboldExe = Join-Path $KoboldDir 'koboldcpp.exe'
$SillyDir = Join-Path $RuntimeRoot 'SillyTavern'

function Refresh-ProcessPath {
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = @($machine, $user) -join ';'
}

function Get-NodeMajorVersion {
    $node = Get-Command node -ErrorAction SilentlyContinue
    if (-not $node) { return $null }
    $raw = (& node --version).Trim().TrimStart('v')
    return [int]($raw.Split('.')[0])
}

function Install-WingetPackage {
    param(
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Name
    )

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "$Name is required but winget is unavailable. Install $Name, then rerun this script."
    }

    Write-Host "Installing/updating $Name with winget..."
    & winget install --id $Id -e --source winget --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "winget failed while installing $Name (exit $LASTEXITCODE)."
    }
    Refresh-ProcessPath
}

Write-Host '=== Guide 1 bootstrap ==='
Write-Host "Runtime root: $RuntimeRoot"
Write-Host ''

if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    throw 'nvidia-smi was not found. Guide 1 requires a working NVIDIA driver before local inference can be verified.'
}

$gpuInfo = (& nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>$null) -join '; '
Write-Host "NVIDIA: $gpuInfo"

$gitMissing = -not (Get-Command git -ErrorAction SilentlyContinue)
$nodeMajor = Get-NodeMajorVersion
$nodeMissingOrOld = ($null -eq $nodeMajor -or $nodeMajor -lt 20)

if ($SkipPrerequisiteInstall) {
    if ($gitMissing) { throw 'Git for Windows is missing.' }
    if ($nodeMissingOrOld) { throw 'Node.js >=20 is required by the pinned SillyTavern release.' }
}
else {
    if ($gitMissing) {
        Install-WingetPackage -Id 'Git.Git' -Name 'Git for Windows'
    }
    if ($nodeMissingOrOld) {
        Install-WingetPackage -Id 'OpenJS.NodeJS.LTS' -Name 'Node.js LTS'
    }
}

Refresh-ProcessPath

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is still unavailable after prerequisite handling. Open a fresh PowerShell and rerun the bootstrap.'
}
$nodeMajor = Get-NodeMajorVersion
if ($null -eq $nodeMajor -or $nodeMajor -lt 20) {
    throw 'Node.js >=20 is still unavailable after prerequisite handling. Open a fresh PowerShell and rerun the bootstrap.'
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw 'npm is unavailable although Node.js was found. Repair the Node.js installation and rerun.'
}

Write-Host "Git:  $(& git --version)"
Write-Host "Node: $(& node --version)"
Write-Host "npm:  $(& npm --version)"

New-Item -ItemType Directory -Path $KoboldDir -Force | Out-Null

$downloadKobold = $true
if (Test-Path -LiteralPath $KoboldExe) {
    $existingHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $KoboldExe).Hash.ToLowerInvariant()
    if ($existingHash -eq $KoboldSha256) {
        Write-Host "KoboldCpp v$KoboldVersion already present and hash-verified."
        $downloadKobold = $false
    }
    else {
        Write-Host 'Existing koboldcpp.exe does not match the pinned hash; replacing it.'
        Remove-Item -LiteralPath $KoboldExe -Force
    }
}

if ($downloadKobold) {
    Write-Host "Downloading KoboldCpp v$KoboldVersion..."
    Invoke-WebRequest -Uri $KoboldUri -OutFile $KoboldExe
    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $KoboldExe).Hash.ToLowerInvariant()
    if ($actualHash -ne $KoboldSha256) {
        Remove-Item -LiteralPath $KoboldExe -Force -ErrorAction SilentlyContinue
        throw "KoboldCpp SHA-256 mismatch. Expected $KoboldSha256, got $actualHash."
    }
    Write-Host 'KoboldCpp download hash verified.'
}

if (-not (Test-Path -LiteralPath $SillyDir)) {
    Write-Host 'Cloning SillyTavern release branch...'
    & git clone --branch release --single-branch $SillyTavernRepo $SillyDir
    if ($LASTEXITCODE -ne 0) { throw "SillyTavern git clone failed (exit $LASTEXITCODE)." }

    & git -C $SillyDir checkout --detach $SillyTavernCommit
    if ($LASTEXITCODE -ne 0) { throw "Could not pin SillyTavern to $SillyTavernCommit." }
}
else {
    if (-not (Test-Path -LiteralPath (Join-Path $SillyDir '.git'))) {
        throw "SillyTavern runtime path exists but is not a Git checkout: $SillyDir"
    }
    $origin = (& git -C $SillyDir remote get-url origin).Trim()
    if ($origin -ne $SillyTavernRepo) {
        throw "Unexpected SillyTavern origin: $origin"
    }
    $head = (& git -C $SillyDir rev-parse HEAD).Trim()
    if ($head -ne $SillyTavernCommit) {
        throw "SillyTavern exists at $head, but Guide 1 is pinned to $SillyTavernCommit. Refusing to mutate an existing local app checkout automatically."
    }
    Write-Host 'Pinned SillyTavern checkout already present.'
}

Write-Host 'Preparing SillyTavern production dependencies...'
Push-Location $SillyDir
try {
    & npm install --no-save --no-audit --no-fund --loglevel=error --no-progress --omit=dev --ignore-scripts
    if ($LASTEXITCODE -ne 0) { throw "npm install failed (exit $LASTEXITCODE)." }
}
finally {
    Pop-Location
}

$result = [ordered]@{
    status = 'PASS'
    runtime_root = $RuntimeRoot
    koboldcpp_version = $KoboldVersion
    koboldcpp_path = $KoboldExe
    koboldcpp_sha256 = $KoboldSha256
    sillytavern_commit = $SillyTavernCommit
    sillytavern_path = $SillyDir
    node_version = (& node --version).Trim()
    git_version = (& git --version).Trim()
    nvidia = $gpuInfo
}

Write-Host ''
Write-Host 'Guide 1 bootstrap completed.'
$result | ConvertTo-Json -Depth 4

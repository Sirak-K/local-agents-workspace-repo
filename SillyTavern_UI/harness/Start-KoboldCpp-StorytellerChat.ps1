[CmdletBinding()]
param(
    [string]$ModelPath,

    [string]$KoboldCppExe,

    [string]$MmprojPath,

    [ValidateRange(256, 524288)]
    [int]$ContextSize = 8192,

    [ValidateRange(0, 3)]
    [int]$GpuId = 0,

    [ValidateRange(1, 65535)]
    [int]$Port = 5001,

    [switch]$LaunchBrowser,
    [switch]$Background
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$runtimeScript = Join-Path $PSScriptRoot 'Start-KoboldCpp-StorytellerRuntime.ps1'
$result = & $runtimeScript -RuntimeProfile ChatCompletionNonThinking @PSBoundParameters

if ($Background) {
    return $result
}

exit $LASTEXITCODE

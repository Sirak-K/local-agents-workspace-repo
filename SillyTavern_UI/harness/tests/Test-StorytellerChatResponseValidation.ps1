[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$modulePath = Join-Path (Split-Path -Parent $PSScriptRoot) 'StorytellerChatResponseValidation.psm1'
Import-Module -Name $modulePath -Force -ErrorAction Stop

function New-ChatResponse {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Content,
        [switch]$IncludeReasoning,
        [AllowNull()][AllowEmptyString()][string]$ReasoningContent
    )

    $message = [ordered]@{
        content = $Content
    }
    if ($IncludeReasoning) {
        $message.reasoning_content = $ReasoningContent
    }

    [pscustomobject]@{
        choices = @(
            [pscustomobject]@{
                message = [pscustomobject]$message
                finish_reason = 'stop'
            }
        )
    }
}

function Assert-OrdinalEqual {
    param(
        [Parameter(Mandatory = $true)][AllowNull()][object]$Actual,
        [Parameter(Mandatory = $true)][AllowNull()][object]$Expected,
        [Parameter(Mandatory = $true)][string]$CaseName
    )

    if (-not [string]::Equals([string]$Actual, [string]$Expected, [StringComparison]::Ordinal)) {
        throw ('Assertion failed ({0}): expected "{1}", got "{2}".' -f $CaseName, $Expected, $Actual)
    }
}

function Assert-ThrowsExactly {
    param(
        [Parameter(Mandatory = $true)][scriptblock]$Action,
        [Parameter(Mandatory = $true)][string]$ExpectedMessage,
        [Parameter(Mandatory = $true)][string]$CaseName
    )

    $threw = $false
    try {
        & $Action | Out-Null
    }
    catch {
        $threw = $true
        if (-not [string]::Equals($_.Exception.Message, $ExpectedMessage, [StringComparison]::Ordinal)) {
            throw ('Assertion failed ({0}): expected error "{1}", got "{2}".' -f $CaseName, $ExpectedMessage, $_.Exception.Message)
        }
    }

    if (-not $threw) {
        throw ('Assertion failed ({0}): expected a terminating response-contract failure.' -f $CaseName)
    }
}

$expected = 'STORYTELLER_PROFILE_OK'

$result = Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content $expected)
Assert-OrdinalEqual -Actual $result.content -Expected $expected -CaseName 'missing reasoning_content passes'
Assert-OrdinalEqual -Actual $result.reasoning_content -Expected '' -CaseName 'missing reasoning_content normalizes empty'

$result = Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content $expected -IncludeReasoning -ReasoningContent '')
Assert-OrdinalEqual -Actual $result.content -Expected $expected -CaseName 'empty reasoning_content passes'
Assert-OrdinalEqual -Actual $result.reasoning_content -Expected '' -CaseName 'empty reasoning_content remains empty'

Assert-ThrowsExactly -CaseName 'non-empty reasoning_content fails' -ExpectedMessage 'Response contract violation: reasoning_content must be missing or empty for the non-thinking profile.' -Action {
    Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content $expected -IncludeReasoning -ReasoningContent 'hidden reasoning')
}

Assert-ThrowsExactly -CaseName 'visible opening think marker fails' -ExpectedMessage 'Response contract violation: visible content contains forbidden marker "<think>".' -Action {
    Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content '<think>STORYTELLER_PROFILE_OK')
}

Assert-ThrowsExactly -CaseName 'visible closing think marker fails' -ExpectedMessage 'Response contract violation: visible content contains forbidden marker "</think>".' -Action {
    Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content 'STORYTELLER_PROFILE_OK</think>')
}

Assert-ThrowsExactly -CaseName 'visible ChatML start marker fails' -ExpectedMessage 'Response contract violation: visible content contains forbidden marker "<|im_start|>".' -Action {
    Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content '<|im_start|>STORYTELLER_PROFILE_OK')
}

Assert-ThrowsExactly -CaseName 'visible ChatML end marker fails' -ExpectedMessage 'Response contract violation: visible content contains forbidden marker "<|im_end|>".' -Action {
    Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content 'STORYTELLER_PROFILE_OK<|im_end|>')
}

Assert-ThrowsExactly -CaseName 'visible Thinking Process marker fails case-insensitively' -ExpectedMessage 'Response contract violation: visible content contains forbidden marker "Thinking Process:".' -Action {
    Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content 'tHiNkInG pRoCeSs: STORYTELLER_PROFILE_OK')
}

Assert-ThrowsExactly -CaseName 'wrong visible content fails' -ExpectedMessage 'Response contract violation: visible content must equal exactly "STORYTELLER_PROFILE_OK".' -Action {
    Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content 'WRONG')
}

Assert-ThrowsExactly -CaseName 'empty visible content fails' -ExpectedMessage 'Response contract violation: visible content must equal exactly "STORYTELLER_PROFILE_OK".' -Action {
    Test-StorytellerChatResponseContract -Response (New-ChatResponse -Content '')
}

Assert-ThrowsExactly -CaseName 'zero choices fails' -ExpectedMessage 'Response contract violation: expected exactly one choice; got 0.' -Action {
    Test-StorytellerChatResponseContract -Response ([pscustomobject]@{ choices = @() })
}

$choice = (New-ChatResponse -Content $expected).choices[0]
Assert-ThrowsExactly -CaseName 'multiple choices fail' -ExpectedMessage 'Response contract violation: expected exactly one choice; got 2.' -Action {
    Test-StorytellerChatResponseContract -Response ([pscustomobject]@{ choices = @($choice, $choice) })
}

Assert-ThrowsExactly -CaseName 'missing assistant message fails' -ExpectedMessage 'Response contract violation: the single choice is missing message.' -Action {
    Test-StorytellerChatResponseContract -Response ([pscustomobject]@{ choices = @([pscustomobject]@{ finish_reason = 'stop' }) })
}

Write-Output 'PASS StorytellerChatResponseValidation: 13 deterministic offline cases'

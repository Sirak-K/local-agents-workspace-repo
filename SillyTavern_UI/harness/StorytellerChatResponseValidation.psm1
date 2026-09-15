Set-StrictMode -Version Latest

function Get-OptionalPropertyValue {
    param(
        [Parameter(Mandatory = $true)][AllowNull()][object]$InputObject,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if ($null -eq $InputObject) {
        return $null
    }

    if ($InputObject -is [System.Collections.IDictionary]) {
        if ($InputObject.Contains($Name)) {
            return $InputObject[$Name]
        }
        return $null
    }

    $property = $InputObject.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

function Test-StorytellerChatResponseContract {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowNull()][object]$Response,
        [ValidateNotNullOrEmpty()][string]$ExpectedContent = 'STORYTELLER_PROFILE_OK'
    )

    $choicesValue = Get-OptionalPropertyValue -InputObject $Response -Name 'choices'
    $choices = @()
    if ($null -ne $choicesValue) {
        $choices = @($choicesValue)
    }
    if ($choices.Count -ne 1) {
        throw ('Response contract violation: expected exactly one choice; got {0}.' -f $choices.Count)
    }

    $message = Get-OptionalPropertyValue -InputObject $choices[0] -Name 'message'
    if ($null -eq $message) {
        throw 'Response contract violation: the single choice is missing message.'
    }

    $contentValue = Get-OptionalPropertyValue -InputObject $message -Name 'content'
    $reasoningValue = Get-OptionalPropertyValue -InputObject $message -Name 'reasoning_content'
    $content = if ($null -eq $contentValue) { '' } else { [string]$contentValue }
    $reasoning = if ($null -eq $reasoningValue) { '' } else { [string]$reasoningValue }

    if ($reasoning.Length -gt 0) {
        throw 'Response contract violation: reasoning_content must be missing or empty for the non-thinking profile.'
    }

    $forbiddenMarkers = @(
        '<think>',
        '</think>',
        '<|im_start|>',
        '<|im_end|>',
        'Thinking Process:'
    )
    foreach ($marker in $forbiddenMarkers) {
        if ($content.IndexOf($marker, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            throw ('Response contract violation: visible content contains forbidden marker "{0}".' -f $marker)
        }
    }

    if (-not [string]::Equals($content, $ExpectedContent, [StringComparison]::Ordinal)) {
        throw ('Response contract violation: visible content must equal exactly "{0}".' -f $ExpectedContent)
    }

    [pscustomobject][ordered]@{
        content = $content
        reasoning_content = $reasoning
    }
}

Export-ModuleMember -Function Test-StorytellerChatResponseContract

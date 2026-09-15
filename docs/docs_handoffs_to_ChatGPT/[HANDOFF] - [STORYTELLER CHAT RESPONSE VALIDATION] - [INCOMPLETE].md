# Handoff: Storyteller Chat Response Validation

**Status:** `INCOMPLETE`

**Team Master decision:** implement the bounded GitHub-visible offline validation slice below. ChatGPT owns only this repo implementation and its offline checks. Codex retains Storyteller architecture, launcher/profile settings, local KoboldCpp/SillyTavern processes, model/GPU runs, live A/B evaluation, performance attribution and final profile promotion.

## Goal and practical value

Harden the new Storyteller Chat Completion acceptance probe so the earlier false-positive class cannot recur. Response interpretation must be a small pure validation surface with deterministic offline cases, while the HTTP probe remains a thin integration caller.

This is suitable for ChatGPT because it is a self-contained multi-file repo slice with no requirement for localhost, Windows UI, KoboldCpp, SillyTavern, a GGUF, GPU access or private files.

## Verified current foundation

Read before editing:

- `docs/docs_plan/[PLAN] - [7] - [SILLYTAVERN STORYTELLER RUNTIME HARDENING] - [FRYSTA BESLUT].md`
- `docs/docs_plan/[PLAN] - [7] - [SILLYTAVERN STORYTELLER RUNTIME HARDENING] - [ROADMAP].md`
- `SillyTavern_UI/harness/Test-KoboldCpp-StorytellerChatProfile.ps1`
- `SillyTavern_UI/harness/README.md`

The current probe already:

- calls `/v1/chat/completions`,
- requires one assistant choice,
- requires exact visible content `STORYTELLER_PROFILE_OK`,
- rejects visible `<think>`, `</think>`, `<|im_start|>`, `<|im_end|>` and `Thinking Process:`,
- independently rejects non-empty `message.reasoning_content`,
- reports human-readable time and performance data.

The prior removed verifier falsely passed while `Thinking Process:` was visible and did not inspect `reasoning_content`. The new implementation must protect specifically against that regression.

## Locked implementation boundary

Extract only response-contract interpretation into a pure PowerShell module or function file. The HTTP probe must continue to own endpoint calls, request dispatch, elapsed-time capture and report assembly.

The pure validator must accept already-parsed response data and either:

- return a compact normalized validation result for a correct response, or
- throw/return a deterministic failure identifying the violated response contract.

Do not introduce a general HTTP client, testing framework, profile schema, launcher abstraction, logging framework or generic agent-validation library.

## Required offline cases

Use built-in PowerShell only. Tests must cover at least:

1. exact expected content + missing `reasoning_content` passes,
2. exact expected content + empty `reasoning_content` passes,
3. non-empty `reasoning_content` fails even when visible content is clean,
4. visible `<think>` fails,
5. visible `</think>` fails,
6. visible ChatML markers fail,
7. visible `Thinking Process:` fails case-insensitively,
8. wrong or empty visible content fails,
9. zero choices fails,
10. multiple choices fails,
11. missing assistant message fails.

Tests must not use wall-clock sleeps, network requests, localhost, model generation or third-party dependencies.

## Allowed write surface

ChatGPT may change only:

```text
SillyTavern_UI/harness/Test-KoboldCpp-StorytellerChatProfile.ps1
SillyTavern_UI/harness/StorytellerChatResponseValidation.psm1
SillyTavern_UI/harness/tests/Test-StorytellerChatResponseValidation.ps1
SillyTavern_UI/harness/README.md
docs/docs_handoffs_to_ChatGPT/[HANDOFF] - [STORYTELLER CHAT RESPONSE VALIDATION] - [INCOMPLETE].md
```

The test folder and the two new PowerShell files may be created. Do not change any other file. Preserve all unrelated work and do not touch the deferred caption handoff.

## Forbidden work

- No model download/load/generation, localhost/API call, browser/UI automation or GPU/process work.
- No KoboldCpp launcher flags, sampler values, context/KV/offload settings, SillyTavern presets or profile names.
- No changes to Guide files, roadmap/frozen decisions, `AGENTS.md`, scripts, local runtime, AutoPull, extensions, captioning or ComfyUI.
- No Pester or other added dependency.
- No Git cleanup, reset, rebase, stash, force-push or unrelated file changes.

## Offline verification and completion gate

Execute the offline PowerShell test directly. It must exit non-zero on the first failed assertion and print one compact PASS line only after every required case succeeds.

Also verify:

- the probe imports/uses the pure validator rather than retaining duplicated response checks,
- PowerShell parsing succeeds for the module, probe and test,
- no network/process commands exist in the offline test/module,
- all changed text files decode as UTF-8 without BOM,
- the Git diff contains only the allowed paths.

If the GitHub environment cannot execute PowerShell, implement the code but keep `[INCOMPLETE]`; record the exact unexecuted commands and remaining verification.

## Required final report in this file

Before finishing, add:

- every created/changed/deleted file,
- behavior delivered,
- every executed check and exact result,
- any unexecuted check/blocker,
- remaining local validation owned by Codex,
- PIPSA: no process restart should be required for this offline-only change.

Rename this file to the same base name ending in `[COMPLETED].md` only when every ChatGPT-owned implementation and offline verification requirement passed. That status does not imply that the live Storyteller profile passed Codex's local model/runtime gates.

## ChatGPT implementation report — 2026-09-15

**Status remains `INCOMPLETE`.** The bounded implementation is present, but this ChatGPT execution environment has no PowerShell executable, so the mandatory direct PowerShell test and PowerShell parser gate could not actually be run. The suffix therefore has not been changed.

### Created / changed / deleted

Created:

- `SillyTavern_UI/harness/StorytellerChatResponseValidation.psm1`
- `SillyTavern_UI/harness/tests/Test-StorytellerChatResponseValidation.ps1`

Changed:

- `SillyTavern_UI/harness/Test-KoboldCpp-StorytellerChatProfile.ps1`
- `SillyTavern_UI/harness/README.md`
- `docs/docs_handoffs_to_ChatGPT/[HANDOFF] - [STORYTELLER CHAT RESPONSE VALIDATION] - [INCOMPLETE].md`

Deleted: none.

### Behavior delivered

- Response-contract interpretation is isolated in the pure `StorytellerChatResponseValidation.psm1` module.
- The validator accepts already-parsed response data, requires exactly one choice with a message, rejects any non-empty `reasoning_content`, rejects `<think>`, `</think>`, both ChatML markers and `Thinking Process:` using ordinal case-insensitive marker matching, then requires ordinal exact visible content `STORYTELLER_PROFILE_OK`.
- Successful validation returns only normalized `content` and `reasoning_content` values.
- The HTTP probe imports and calls the validator; endpoint requests, timing, version/context checks, performance lookup and report assembly remain in the probe.
- The dependency-free offline test contains 13 deterministic cases covering every required case, with separate tests for both ChatML markers and for wrong versus empty visible content. It emits a single compact PASS line only after all assertions succeed and uses terminating assertions so a failed case stops the script.
- The README documents the pure-validator split and the direct offline test command.

### Executed checks and exact results

- Re-read GitHub `main` after Team Master's cleanup/plan commit and based implementation on commit `7ea740da19d07fe544ffb71eaed1216fba4671a9`: **PASS**.
- Static scan of `StorytellerChatResponseValidation.psm1` and `tests/Test-StorytellerChatResponseValidation.ps1` for `Invoke-RestMethod`, `Invoke-WebRequest`, process commands, `Start-Sleep`, `System.Net`, `curl` and `wget`: **PASS — no matches**.
- Static probe check for `Import-Module` plus `Test-StorytellerChatResponseContract`, and absence of the old in-probe forbidden-marker/reasoning validation block: **PASS**.
- UTF-8 decode and UTF-8 BOM check over all five changed/created text files as authored: **PASS — all decode as UTF-8 and none starts with `EF BB BF`**.
- Candidate Git tree diff against base commit `7ea740da19d07fe544ffb71eaed1216fba4671a9`: **PASS — only the five paths listed under Created / Changed are present; no out-of-scope path is changed**.

### Unexecuted mandatory checks / exact blocker

The following mandatory PowerShell checks were **not executed**:

```powershell
pwsh -NoProfile -File .\SillyTavern_UI\harness\tests\Test-StorytellerChatResponseValidation.ps1
```

```powershell
pwsh -NoProfile -Command "$paths=@('.\SillyTavern_UI\harness\StorytellerChatResponseValidation.psm1','.\SillyTavern_UI\harness\Test-KoboldCpp-StorytellerChatProfile.ps1','.\SillyTavern_UI\harness\tests\Test-StorytellerChatResponseValidation.ps1'); foreach($path in $paths){$tokens=$null;$errors=$null;[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $path),[ref]$tokens,[ref]$errors)|Out-Null;if($errors.Count -ne 0){throw ($errors | ForEach-Object Message | Out-String)}}"
```

Exact blocker: the available execution container is Debian 13 (`x86_64`) and contains neither `pwsh` nor Windows PowerShell. `pwsh --version` therefore resolves to `command not found`. An attempt to fetch the official PowerShell `v7.6.6` Debian package into the isolated execution container also failed because that container has no outbound DNS/network access (`curl: (6) Could not resolve host: github.com`). No repo/runtime/profile setting was changed to work around this environment limitation.

Because these two PowerShell-owned gates remain unexecuted, this handoff intentionally remains `[INCOMPLETE]` even though the implementation and non-PowerShell static checks are complete.

### Remaining validation

Remaining handoff gate in a PowerShell-capable environment: run the direct offline test and the parser command above. Only if both pass, together with the already-passed scope/static/encoding checks, may ChatGPT's handoff suffix be changed to `[COMPLETED]`.

Codex still owns all local/live validation outside this repo-only slice: Storyteller launcher/profile/runtime settings, local KoboldCpp/SillyTavern processes, model/GPU runs, live A/B behavior, performance attribution and final AGPR promotion.

### PIPSA

No process restart should be required for this offline-only repository change. No launcher, profile, sampler, context/KV, runtime process or local application state was modified.

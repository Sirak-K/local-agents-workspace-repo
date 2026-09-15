# Handoff: Storyteller Chat Response Validation

**Status:** `COMPLETED`

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

## Completion report — 2026-09-15

**Status: `COMPLETED`.** ChatGPT implemented the bounded repo-only slice. The original ChatGPT environment could not execute PowerShell, so the handoff initially remained `INCOMPLETE`. Codex subsequently executed the mandatory local PowerShell gates, found and corrected one validator defect for an empty `choices` response, and committed that fix as `54833ac04975253b62431346f5f2c120b6c835ae`. After that correction, every ChatGPT-owned offline acceptance gate passed.

### Created / changed / deleted

Implementation created:

- `SillyTavern_UI/harness/StorytellerChatResponseValidation.psm1`
- `SillyTavern_UI/harness/tests/Test-StorytellerChatResponseValidation.ps1`

Implementation changed before completion:

- `SillyTavern_UI/harness/Test-KoboldCpp-StorytellerChatProfile.ps1`
- `SillyTavern_UI/harness/README.md`
- `SillyTavern_UI/harness/StorytellerChatResponseValidation.psm1` — Codex correction in `54833ac04975253b62431346f5f2c120b6c835ae` for the empty-`choices` case exposed by the first local PowerShell run.

Completion-only documentation change:

- renamed `docs/docs_handoffs_to_ChatGPT/[HANDOFF] - [STORYTELLER CHAT RESPONSE VALIDATION] - [INCOMPLETE].md` to the same base name ending in `[COMPLETED].md`, with this verification report updated.

No other file is changed by the completion commit.

### Behavior delivered

- Response-contract interpretation is isolated in the pure `StorytellerChatResponseValidation.psm1` module.
- The validator accepts already-parsed response data, requires exactly one choice with an assistant message, rejects any non-empty `reasoning_content`, rejects `<think>`, `</think>`, both ChatML markers and `Thinking Process:` using ordinal case-insensitive marker matching, then requires ordinal exact visible content `STORYTELLER_PROFILE_OK`.
- Successful validation returns compact normalized `content` and `reasoning_content` values.
- The HTTP probe imports and calls the validator; endpoint requests, timing, version/context checks, performance lookup and report assembly remain in the probe.
- The dependency-free offline test contains 13 deterministic cases covering every required contract case, with separate coverage for both ChatML markers and wrong versus empty visible content. It terminates on the first failed assertion and emits its compact PASS line only after all cases succeed.
- The README documents the pure-validator split and the direct offline test command.

### Executed checks and exact results

ChatGPT-side non-PowerShell checks before local completion:

- Re-read GitHub `main` after Team Master's cleanup/plan commit and based implementation on commit `7ea740da19d07fe544ffb71eaed1216fba4671a9`: **PASS**.
- Static scan of `StorytellerChatResponseValidation.psm1` and `tests/Test-StorytellerChatResponseValidation.ps1` for network/process/sleep commands: **PASS — no prohibited matches**.
- Static probe check for `Import-Module` plus `Test-StorytellerChatResponseContract`, and absence of the old duplicated in-probe response-validation block: **PASS**.
- UTF-8 decode and UTF-8 BOM check over the changed/created text files: **PASS — UTF-8 without BOM**.
- Git tree diff against the implementation base: **PASS — only allowed handoff paths were present**.

Codex local PowerShell completion gate:

- First direct run of `SillyTavern_UI/harness/tests/Test-StorytellerChatResponseValidation.ps1`: **FAIL — the zero/empty `choices` case exposed a validator defect**.
- Codex corrected that defect and committed the fix as `54833ac04975253b62431346f5f2c120b6c835ae`: **PASS — fix present on the completion base**.
- Direct offline PowerShell test after the fix: **PASS — all 13 deterministic offline cases passed**.
- PowerShell parser validation for `StorytellerChatResponseValidation.psm1`, `Test-KoboldCpp-StorytellerChatProfile.ps1`, and `tests/Test-StorytellerChatResponseValidation.ps1`: **PASS**.
- UTF-8 without BOM validation after the fix: **PASS**.
- Static process-/network-safety validation after the fix: **PASS**.
- Final diff/scope check after the fix: **PASS**.

### Unexecuted checks / blockers

None remain for the ChatGPT-owned offline handoff. The earlier lack of a PowerShell executable in ChatGPT's container is no longer a completion blocker because Codex executed the mandatory PowerShell gates locally after the corrective commit and all required checks passed.

### Remaining local validation owned by Codex

This `COMPLETED` status applies only to the bounded offline response-validation handoff. Codex still owns Storyteller launcher/profile/runtime settings, local KoboldCpp/SillyTavern processes, model/GPU runs, live A/B behavior, performance attribution, broader runtime regression gates and final AGPR promotion. This status does not assert that those live Storyteller gates have passed.

### PIPSA

No process restart is required for this offline-only repository change. No launcher, profile, sampler, context/KV, runtime process or local application state is modified by the completion update.

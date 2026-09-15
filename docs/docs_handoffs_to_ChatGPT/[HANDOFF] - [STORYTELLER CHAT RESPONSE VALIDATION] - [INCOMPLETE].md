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

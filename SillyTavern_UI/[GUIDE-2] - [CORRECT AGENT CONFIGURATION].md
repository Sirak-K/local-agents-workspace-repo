# GUIDE 2 — CORRECT AGENT CONFIGURATION

**Current-sprint status:** CLOSED on the last proven stable baseline. Advanced model-specific template/non-thinking hardening is explicitly deferred to later Codex work.

**Active model:** `Qwen3.5-9B-The-Defiant-Fable-Uncnr-Heretic-NEO-MAX-Q4_K_S.gguf`

## Proven stable baseline

Use the same path that passed Guide 1 before Advanced Formatting was modified:

```text
SillyTavern API: Text Completion
API Type:        KoboldCpp
Endpoint:        http://127.0.0.1:5001
KoboldCpp:       1.120
Context:         8192
Streaming:       ON
```

Restore the observed pre-change Advanced Formatting state:

```text
Context Template:  Default
Instruct Mode:     OFF
Instruct Template: Alpaca (inactive while Instruct Mode is OFF)
System Prompt:     Neutral - Chat
Reasoning:         OFF
Custom Stops:      empty
Start Reply With:  empty
```

Do not enable metadata-derived templates, manual ChatML/Jinja/non-thinking overrides, or the experimental Chat Completion path during this sprint.

Recurring backend entrypoint:

```powershell
.\scripts\Start-KoboldCpp-Text.cmd
```

SillyTavern entrypoint:

```powershell
.\scripts\Start-SillyTavern.cmd
```

## Evidence and failure classification

Before Advanced Formatting changes, DefiantFable generated stable multi-turn chat through SillyTavern, preserved the Northstar/Mara facts, streamed normally, and showed no visible `<think>` or role/template markers.

After enabling derived ChatML/Instruct formatting, visible empty `<think>...</think>` blocks appeared. A later Jinja/non-thinking experiment was not valid because KoboldCpp reported `Warning: couldn't parse jinja_kwargs field`; its verifier also produced a false-positive marker PASS while the model emitted a visible `Thinking Process:`. These are configuration/test-harness failures, **not proven model defects**.

The experimental non-thinking launch/test scripts have therefore been removed from the normal repo surface.

## Deferred hardening backlog

Codex/later work may revisit exact Qwen3.5 thinking/non-thinking template behavior, final role/system-prompt placement, final Validation/Story sampler profiles, the 1000–2000 word output requirement, context optimization beyond 8192, and any model-specific Chat Completion/Jinja path.

## Current gate

Guide 2 is closed for this fast-track sprint because the stable text baseline is proven operational and the failed advanced-formatting experiment is isolated and deferred rather than being silently attributed to the model.

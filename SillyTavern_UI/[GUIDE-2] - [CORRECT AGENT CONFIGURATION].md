# GUIDE 2 — CORRECT AGENT CONFIGURATION

**Guide status:** CLOSED on the last proven stable baseline. Advanced model-specific hardening is now active as a separate regression-safe workstream; Guide 2 itself remains closed and is not retroactively reopened.

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

Do not alter this baseline in place. The new Chat Completion/Jinja/non-thinking path must remain a separate profile until it passes the Storyteller acceptance matrix.

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

## Active hardening workstream

The separate Storyteller runtime-hardening roadmap owns exact Qwen3.5 thinking/non-thinking behavior, Prompt Manager system placement, Validation/Story sampler profiles, 1000–2000-word behavior, saved profiles and context/performance optimization beyond 8192. For KoboldCpp `1.120`, the fixed non-thinking candidate uses `--jinjathink false`; its verifier must inspect both `content` and `reasoning_content`.

## Current gate

Guide 2 is closed for this fast-track sprint because the stable text baseline is proven operational and the failed advanced-formatting experiment is isolated and deferred rather than being silently attributed to the model.

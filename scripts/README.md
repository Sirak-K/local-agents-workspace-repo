# scripts

This folder contains the repo-level executable entrypoints Team Master is expected to use regularly or repeatedly.

## Guide 1 / local-agent chat harness

- `Start-Local-Agent-Harness.cmd` — start/bootstrap the local SillyTavern + KoboldCpp harness.
- `Start-SillyTavern.cmd` — start only SillyTavern when the KoboldCpp backend is already running.
- `Test-Local-Agent-Harness.cmd` — verify the running Guide-1 backend/API state.
- `Set-SillyTavern-Port.cmd` — set SillyTavern to a verified-free local TCP port; prefers `8001` and scans upward through `8099` if needed. Restart SillyTavern afterward.

## Guide 2 / DefiantFable

- `Start-DefiantFable-NonThinking.cmd` — start KoboldCpp for the active DefiantFable/Qwen3.5 path with Chat Completions Jinja enabled and `enable_thinking=false`. It keeps the controlled CUDA/AutoFit/F16-KV baseline unless explicit parameters override it. SillyTavern must use `Chat Completion -> Custom (OpenAI-compatible)` against `http://127.0.0.1:5001/v1` on this path.
- `Test-DefiantFable-NonThinking.cmd` — call the running `/v1/chat/completions` endpoint and fail if the assistant content is empty or leaks `<think>`, `</think>`, `<|im_start|>` or `<|im_end|>` markers. Run this before SillyTavern behavioral validation.

Implementation helpers may live next to their subsystem (for example `SillyTavern_UI/harness/`), but recurring Team Master entrypoints should be surfaced here.

AutoPull/AutoSync is the normal mechanism for bringing ChatGPT-authored repo changes to the local workspace; manual Git pull commands are troubleshooting only.

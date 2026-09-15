# scripts

This folder contains the repo-level executable entrypoints Team Master is expected to use regularly or repeatedly.

## Local-agent chat harness

- `Start-Local-Agent-Harness.cmd` — bootstrap/start the local SillyTavern + KoboldCpp harness.
- `Start-KoboldCpp-Text.cmd` — start only the stable KoboldCpp text backend and choose a GGUF.
- `Start-SillyTavern.cmd` — start only SillyTavern when the backend is already running.
- `Test-Local-Agent-Harness.cmd` — verify the running KoboldCpp backend/API state.
- `Set-SillyTavern-Port.cmd` — set SillyTavern to a verified-free local TCP port; prefers `8001` and scans upward through `8099` if needed. Restart SillyTavern afterward.

Failed/experimental Defiant non-thinking launch/test entrypoints were removed from this recurring surface. Advanced template/non-thinking hardening is deferred rather than presented as a normal operator workflow.

Implementation helpers may live next to their subsystem (for example `SillyTavern_UI/harness/`), but recurring Team Master entrypoints should be surfaced here.

AutoPull/AutoSync is the normal mechanism for bringing ChatGPT-authored repo changes to the local workspace; manual Git pull commands are troubleshooting only.

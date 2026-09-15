# scripts

This folder contains the repo-level executable entrypoints Team Master is expected to use regularly or repeatedly.

## Local-agent chat harness

- `Start-Local-Agent-Harness.cmd` — bootstrap/start the local SillyTavern + KoboldCpp harness.
- `Start-KoboldCpp-Text.cmd` — start only the stable KoboldCpp TEXT backend and choose a GGUF.
- `Start-SillyTavern.cmd` — start only SillyTavern when the backend is already running.
- `Test-Local-Agent-Harness.cmd` — verify the running KoboldCpp backend/API state.
- `Set-SillyTavern-Port.cmd` — set SillyTavern to a verified-free local TCP port; prefers `8001` and scans upward through `8099` if needed.

## DefiantFable vision fast-track

- `Download-DefiantFable-mmproj-F16.cmd` — select the active DefiantFable GGUF, download `mmproj-F16.gguf` beside it, and verify SHA256 `f70dc3509053962b0d0d3ee8a7eacebf5d60aa560cad78254ae8698516ae029f`.
- `Start-DefiantFable-Vision.cmd` — start a separate VISION profile using the same GGUF plus the verified `mmproj-F16.gguf`; default fast-track context is `4096` to leave more VRAM headroom on the RTX 3070 Ti 8 GB.

Failed/experimental Defiant non-thinking launch/test entrypoints were removed from this recurring surface. Advanced template/non-thinking hardening is deferred rather than presented as a normal operator workflow.

Implementation helpers may live next to their subsystem, but recurring Team Master entrypoints should be surfaced here.

AutoPull/AutoSync is the normal mechanism for bringing ChatGPT-authored repo changes to the local workspace; manual Git pull commands are troubleshooting only.

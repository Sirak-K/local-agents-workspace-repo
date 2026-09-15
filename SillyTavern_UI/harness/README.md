# Guide 1 harness — SillyTavern + KoboldCpp

**Scope:** model-neutral AGENT-2 text harness only.

Tracked here: bootstrap/start/test scripts and runtime contract.  
Not tracked: installed third-party apps under `SillyTavern_UI/_local_runtime/`.

**Verified 2026-09-15:** KoboldCpp `v1.120`; SillyTavern `release` commit `06bde939fb1e9c4c8d8641d810f0a916b5bce127` (SillyTavern `1.19.0`, Node `>=20`).

## One-command local start

From repo root after AutoPull:

```powershell
.\SillyTavern_UI\harness\Start-Guide1-Stack.cmd
```

`Start-Guide1-Stack.cmd` selects `pwsh.exe` when available and falls back to `powershell.exe`. This avoids assuming Windows PowerShell 5.1 is installed or present in `PATH`.

The launcher/script chain:

1. bootstraps missing Guide-1 runtime components,
2. checks the NVIDIA driver,
3. installs missing Git/Node LTS through `winget` when possible,
4. downloads and SHA-256 verifies KoboldCpp v1.120,
5. clones/pins SillyTavern inside `_local_runtime`,
6. asks you to select an existing `.gguf`,
7. starts KoboldCpp with the locked baseline,
8. verifies its local API,
9. starts SillyTavern.

## Locked KoboldCpp baseline

| Setting | Value |
|---|---|
| Bind | `127.0.0.1` |
| Port | `5001` |
| Context | `8192` |
| CUDA GPU | ID `0` default |
| GPU layers | `-1` / AutoFit |
| MMQ | OFF (`--nommq`) |
| High Priority | ON |
| Flash Attention | ON (v1.120 default) |
| KV | F16 |
| Context Shift | ON (v1.120 default) |
| SWA | prevented with `--noswa` so Context Shift remains available |
| Low VRAM | OFF |
| mmproj / RAG / remote tunnel | absent |

## Runtime placement

```text
SillyTavern_UI/
├── harness/                 # tracked
└── _local_runtime/          # gitignored
    ├── KoboldCpp/
    └── SillyTavern/
```

No second `AGENT-2-STORYTELLER` directory is created.

## Primary sources

- https://github.com/LostRuins/koboldcpp/releases
- https://github.com/LostRuins/koboldcpp/blob/v1.120/koboldcpp.py
- https://docs.sillytavern.app/installation/windows/
- https://docs.sillytavern.app/usage/api-connections/koboldcpp/

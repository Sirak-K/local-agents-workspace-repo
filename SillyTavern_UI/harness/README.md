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

`Start-Guide1-Stack.cmd` selects `pwsh.exe` when available and falls back to `powershell.exe`. It also checks common absolute install paths so Guide 1 does not depend on a perfect PATH setup.

The launcher/script chain:

1. bootstraps missing Guide-1 runtime components,
2. checks the NVIDIA driver,
3. installs missing Git/Node LTS through `winget` when possible,
4. downloads and SHA-256 verifies KoboldCpp v1.120,
5. clones/pins SillyTavern inside `_local_runtime`,
6. asks you to select an existing `.gguf`,
7. refuses a contaminated Guide-1 run if the selected GPU already has >=50% VRAM occupied by another workload,
8. starts KoboldCpp with the locked baseline,
9. verifies its local API,
10. starts SillyTavern.

## Locked KoboldCpp baseline

| Setting | Value |
|---|---|
| Bind | `127.0.0.1` |
| Port | `5001` |
| Requested context | `8192` |
| CUDA GPU | ID `0` default |
| GPU layers | `-1` / AutoFit |
| MMQ | OFF (`--nommq`) |
| High Priority | ON |
| Flash Attention | allowed/default; verify effective runtime state in log |
| KV | F16 |
| Context Shift | allowed by baseline (`--noshift` absent), but effective state is architecture-dependent; KoboldCpp may disable it for e.g. mRoPE/hybrid models |
| SWA | prevented with `--noswa`; some architectures do not use SWA anyway |
| Low VRAM | OFF |
| mmproj / RAG / remote tunnel | absent |

Guide 1 does **not** treat an architecture-driven Context Shift disable as a model failure. Record the effective runtime behavior and keep failure causes separate.

## Controlled GPU preflight

Do not run ComfyUI inference or another heavy CUDA workload during Guide-1 AutoFit/performance verification. Competing VRAM use changes AutoFit layer selection and contaminates tok/s/VRAM evidence. The launcher now stops before model load if at least 50% of the target GPU VRAM is already occupied.

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

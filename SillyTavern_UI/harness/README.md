# SillyTavern + KoboldCpp text harness

**Scope:** model-neutral AGENT-2 text harness. Model-specific prompt/template/sampling facts belong outside this folder.

**Upstream verified:** 2026-09-15 against KoboldCpp `v1.120` and current SillyTavern documentation.

## Repo-owned helpers

- `Install-SillyTavern-Release.ps1` — validates Node/npm/Git and clones only SillyTavern `release`; refuses overwrite/update.
- `Start-KoboldCpp-TextBaseline.ps1` — starts a local-only text baseline.
- `Test-KoboldCpp-TextBaseline.ps1` — verifies KoboldCpp version/model/context/API and reports NVIDIA VRAM state as JSON to stdout.

## Locked first-run baseline

| Setting | Value |
|---|---|
| Bind | `127.0.0.1` only |
| Port | `5001` |
| Context | `8192` |
| Backend | CUDA |
| GPU | ID `0` by default; override if needed |
| QuantMatMul/MMQ | `nommq` |
| GPU Layers | `-1` / AutoFit |
| Flash Attention | ON explicitly |
| KV cache | F16 (`--quantkv 0`) |
| Context Shift | default/ON; no `--noshift` |
| SWA | OFF; no `--useswa` |
| Low VRAM | OFF |
| mmproj | absent |
| Web/remote tunnel | absent |

The loopback bind is intentional: Guide 1 requires only local SillyTavern ↔ KoboldCpp communication.

## Local invocation

From the workspace root after AutoPull:

```powershell
.\SillyTavern_UI\harness\Install-SillyTavern-Release.ps1 -InstallRoot "C:\AI\AGENT-2-STORYTELLER"
```

Start KoboldCpp with an existing GGUF:

```powershell
.\SillyTavern_UI\harness\Start-KoboldCpp-TextBaseline.ps1 `
  -KoboldCppExe "C:\path\to\koboldcpp.exe" `
  -ModelPath "C:\path\to\model.gguf"
```

In a second PowerShell window, verify the running backend:

```powershell
.\SillyTavern_UI\harness\Test-KoboldCpp-TextBaseline.ps1
```

Do not save generated runtime reports inside this repo during Guide 1; paste the JSON output back to ChatGPT instead so AutoPull remains unblocked.

## Primary sources

- https://github.com/LostRuins/koboldcpp/releases
- https://github.com/LostRuins/koboldcpp/wiki
- https://docs.sillytavern.app/installation/windows/
- https://docs.sillytavern.app/usage/api-connections/koboldcpp/

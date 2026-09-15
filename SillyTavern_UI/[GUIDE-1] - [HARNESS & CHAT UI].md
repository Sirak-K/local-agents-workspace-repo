# GUIDE 1 — HARNESS & CHAT UI

**Mål:** verifiera den lokala textkedjan `SillyTavern -> KoboldCpp -> GGUF -> RTX 3070 Ti 8 GB` på Windows.

**Scope:** endast harness/chat-UI. Ingen agentprompt, modell-A/B, filläsning eller multimodalitet startas här.

**Primärkällor:** [KoboldCpp releases](https://github.com/LostRuins/koboldcpp/releases) · [KoboldCpp v1.120 source](https://github.com/LostRuins/koboldcpp/blob/v1.120/koboldcpp.py) · [SillyTavern Windows](https://docs.sillytavern.app/installation/windows/) · [SillyTavern + KoboldCpp](https://docs.sillytavern.app/usage/api-connections/koboldcpp/)

---

# A. ChatGPT-ägd steg-för-steg guide — KLAR

## A1. Verifierad och låst baseline

Verifierad 2026-09-15:

- KoboldCpp: `v1.120`, Windows `koboldcpp.exe`.
- SillyTavern: `release` commit `06bde939fb1e9c4c8d8641d810f0a916b5bce127` (`1.19.0`, Node `>=20`).
- API: `Text Completion -> KoboldCpp -> http://127.0.0.1:5001`.
- Context: `8192`.
- CUDA GPU ID: `0` default.
- GPU layers: `-1` / AutoFit.
- MMQ: OFF (`--nommq`).
- High Priority: ON.
- Flash Attention: ON via v1.120 default.
- KV: F16.
- Context Shift: ON via v1.120 default.
- SWA: prevented with `--noswa` so Context Shift remains available.
- Low VRAM/mmproj/RAG/remote tunnel: absent.

## A2. Implementerat repoägt harness

Tracked under `SillyTavern_UI/harness/`:

- `Bootstrap-Guide1.ps1` — checks NVIDIA; installs missing Git/Node LTS via `winget` when possible; downloads and SHA-256 verifies KoboldCpp; clones/pins SillyTavern; prepares npm dependencies.
- `Start-KoboldCpp-TextBaseline.ps1` — applies the locked KoboldCpp baseline.
- `Start-SillyTavern.ps1` — starts the repo-local SillyTavern runtime.
- `Start-Guide1-Stack.ps1` — one-command bootstrap/start path; opens a file picker for an existing GGUF.
- `Test-KoboldCpp-TextBaseline.ps1` — checks KoboldCpp API/model/context and NVIDIA VRAM.
- `README.md` — concise runtime contract.

Third-party installs live only under:

```text
SillyTavern_UI/_local_runtime/
├── KoboldCpp/
└── SillyTavern/
```

`_local_runtime/` is Git-ignored. Ingen parallell `AGENT-2-STORYTELLER`-yta skapas.

**ChatGPT-del: PASS.** Lokal runtime är ännu inte verifierad förrän Del B körts på Team Masters dator.

---

# B. Team Master-ägd steg-för-steg guide

## B1. Låt AutoPull hämta senaste `main`

Rör inte andra lokala tracked-filer före sync. Bekräfta sedan:

```powershell
git status
git pull --ff-only origin main
```

Krav: `working tree clean` och `Already up to date` eller en ren fast-forward.

## B2. Kör hela Guide-1-bootstrap/starten

Från repo-roten:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\SillyTavern_UI\harness\Start-Guide1-Stack.ps1
```

Scriptet gör installation/bootstrap själv. När filväljaren öppnas väljer du **en befintlig `.gguf`** endast för harness-smoke-testet.

**STOP och skicka terminalfelet till ChatGPT om scriptet misslyckas. Ändra inte konfigurationen manuellt först.**

## B3. Koppla SillyTavern till den redan startade KoboldCpp-instansen

I SillyTavern:

1. `API Connections`.
2. API = `Text Completion`.
3. API Type = `KoboldCpp`.
4. URL = `http://127.0.0.1:5001`.
5. `Connect`.

Detta GUI-val kan inte göras försvarbart från GitHub-sidan eftersom det är lokal per-user UI-state.

## B4. Kör endast harness-smoke-testet

Kör i en ny ren chat:

1. fem korta user/assistant-turns,
2. ett längre svar,
3. en följdfråga som kräver föregående turn.

Verifiera endast:

- svar genereras stabilt,
- ingen OOM/crash,
- inga uppenbara specialtoken/template-markörer läcker ut,
- senare turns är fortsatt responsiva.

Bedöm inte slutlig Storyteller-kvalitet i Guide 1.

## B5. Skicka evidensen till ChatGPT

Med KoboldCpp fortfarande igång:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\SillyTavern_UI\harness\Test-KoboldCpp-TextBaseline.ps1
```

Skicka JSON-outputen plus:

```text
SillyTavern connection: PASS/FAIL
3-part chat smoke test: PASS/FAIL
Approx. generation tok/s shown by KoboldCpp:
Any warnings/errors:
```

# GUIDE-1 PASS

Guide 1 är klar först när `SillyTavern -> KoboldCpp -> lokal GGUF` fungerar stabilt på den lokala datorn.

**Starta inte Guide 2, 3 eller 4 utan Team Masters separata explicita startkommando.**

# GUIDE 1 — HARNESS & CHAT UI

**Current-sprint status: PASS / CLOSED (2026-09-15).**

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
- SillyTavern port flyttad från `8000` till verifierat lediga `8001`.
- Begärd context: `8192`.
- CUDA GPU ID: `0` default.
- GPU layers: `-1` / AutoFit.
- MMQ: OFF (`--nommq`).
- High Priority: ON.
- Flash Attention: tillåten/default; effektivt runtime-läge verifieras i loggen.
- KV: F16.
- Context Shift: tillåten genom att `--noshift` inte används, men effektivt läge är arkitekturberoende. KoboldCpp kan stänga av Context Shift automatiskt för modeller där shifting inte stöds, exempelvis vissa mRoPE/hybrid-arkitekturer.
- SWA: förhindras med `--noswa` för att inte bli en separat confounder; vissa arkitekturer använder inte SWA alls.
- Low VRAM/mmproj/RAG/remote tunnel: absent.

Ett arkitekturdrivet avslag av Context Shift är **inte** i sig ett modellfel eller Guide-1-FAIL. Det ska dokumenteras som effektivt runtime-beteende och hållas åtskilt från harness-, VRAM- och modellfel.

## A2. Repoägt harness och entrypoints

Intern implementation ligger under `SillyTavern_UI/harness/`:

- `Bootstrap-Guide1.ps1` — kontrollerar NVIDIA; installerar saknad Git/Node LTS via `winget` när möjligt; laddar ner och SHA-256-verifierar KoboldCpp; klonar/pinnar SillyTavern; förbereder npm-dependencies.
- `Start-KoboldCpp-TextBaseline.ps1` — applicerar den låsta KoboldCpp-baslinjen och stoppar en kontaminerad körning om annat workload redan använder >=50% av mål-GPU:ns VRAM.
- `Start-SillyTavern.ps1` — startar den repo-lokala SillyTavern-runtimen.
- övriga `.ps1/.cmd` i harness-mappen är interna implementation-/diagnostikhjälpare.

**Regel för Team Master:** exekverbara entrypoints som förväntas användas regelbundet/återkommande finns i repo-roten `scripts/`:

- `scripts/Start-Local-Agent-Harness.cmd` — normal start av Guide-1-harnesskedjan.
- `scripts/Start-SillyTavern.cmd` — startar endast SillyTavern när backend redan kör.
- `scripts/Test-Local-Agent-Harness.cmd` — kör Guide-1 backendverifieringen.

Team Master ska normalt inte behöva köra interna filer direkt ur `SillyTavern_UI/harness/`.

Third-party installs live only under:

```text
SillyTavern_UI/_local_runtime/
├── KoboldCpp/
└── SillyTavern/
```

`_local_runtime/` är Git-ignorerad. Ingen parallell `AGPR-2-STORYTELLER`-yta skapas.

## Verified completion evidence

- Bootstrap: PASS.
- KoboldCpp backend verifierad två gånger via `scripts/Test-Local-Agent-Harness.cmd`.
- Version: `1.120`.
- `true_max_context`: `8192`.
- DefiantFable GGUF laddad stabilt.
- SillyTavern -> KoboldCpp connection: PASS.
- Multi-turn chat, continuity och streaming: PASS.
- Completion-control test avslutades naturligt med exakt `END OF TEST`.
- Ingen uppenbar specialtoken/template-läcka på den stabila pre-Advanced-Formatting-baslinjen.

# GUIDE-1 PASS

Guide 1 är stängd för current sprint. Senare prestanda-/modellhardening hör inte till denna gate.

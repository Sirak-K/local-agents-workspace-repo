# AGENT-2-STORYTELLER — GUIDE 1 — HARNESS & CHAT UI

**Status:** Ny auktoritativ guide för AGENT-2-STORYTELLER. Äldre AGENT-2-filer och äldre tekniska påståenden ska inte användas som källa för denna guide.

**Mål:** Etablera en enkel, snabb och reproducerbar lokal chattkedja på Windows:

`SillyTavern -> KoboldCpp -> lokal GGUF-modell -> NVIDIA RTX 3070 Ti 8 GB`

**Scope:** Endast harness, backend, chatt-UI och grundläggande runtime-verifiering. Agentens persona/systemprompt, filläsning/RAG och bildmultimodalitet hör till Guide 2–4.

**Verifierad källstatus:** 2026-09-15. KoboldCpps senaste stabila release som verifierades vid guideförfattandet var v1.120. SillyTavern rekommenderar `release`-branchen för de flesta användare.

---

# DEL A — CHATGPT-ÄGD STEG-FÖR-STEG GUIDE

Denna halva innehåller endast arbete som ChatGPT kan utföra självständigt genom repoåtkomst och som inte kräver åtkomst till Team Masters Windows-session, GPU, lokala modellfiler eller GUI.

## A1. Äg den reproducerbara runtime-specifikationen i repot

ChatGPT ska hålla denna guide uppdaterad med:

1. vald backend och UI,
2. officiella installationskällor,
3. minsta verifieringssekvens,
4. vilka värden Team Master måste rapportera tillbaka efter lokal körning,
5. tydliga PASS/STOP-gates.

ChatGPT får uppdatera denna guide när upstream ändras, men får inte påstå att en lokal installation är fungerande utan Team Masters lokala evidens.

## A2. Använd endast aktuella primärkällor för installation

Följande länkar är de installationskällor som ska ligga till grund för körningen:

- KoboldCpp releases: https://github.com/LostRuins/koboldcpp/releases
- KoboldCpp wiki: https://github.com/LostRuins/koboldcpp/wiki
- SillyTavern Windows-installation: https://docs.sillytavern.app/installation/windows/
- SillyTavern KoboldCpp-anslutning: https://docs.sillytavern.app/usage/api-connections/koboldcpp/
- Node.js LTS: https://nodejs.org/en/download
- Git for Windows: https://git-scm.com/downloads/win

Vid framtida exekvering ska ChatGPT kontrollera dessa källor igen innan en versionsspecifik ändring görs.

## A3. Förbered en maskinoberoende runtime-baslinje

ChatGPT äger följande initiala baslinje. Den är avsiktligt försiktig för 8 GB VRAM och ska inte optimeras aggressivt innan första PASS:

- Backend: KoboldCpp, stabil release.
- UI: SillyTavern, `release` branch.
- Modellformat: GGUF.
- Första context size: `8192` tokens.
- NVIDIA-acceleration: CuBLAS/CUDA.
- `Low VRAM`: OFF.
- GPU Layers: låt KoboldCpps automatiskt valda/AutoFit-värde vara startpunkt.
- Context Shift: lämna standardbeteendet på; KoboldCpp dokumenterar det som aktiverat som standard för GGUF.
- Ingen SWA i baslinjen.
- Ingen KV-cache-kvantisering i första smoke-testet.
- Ingen mmproj i denna guide.
- Ingen RAG/Data Bank i denna guide.
- Ingen web search eller tool calling i denna guide.

Syftet är att få en ren textkedja att fungera innan minnes- och hastighetsoptimeringar läggs ovanpå.

## A4. Definiera vad Team Master ska returnera till ChatGPT efter lokal installation

Efter DEL B ska Team Master kunna skicka tillbaka följande minimala evidens:

```text
KoboldCpp version:
SillyTavern branch/version:
Node version:
GPU detected by nvidia-smi:
Exact GGUF filename:
Context size:
GPU layers/offload result:
KoboldCpp load success: yes/no
KoboldCpp local endpoint reachable: yes/no
SillyTavern connected to KoboldCpp: yes/no
Approx. VRAM after model load:
Approx. generation tok/s:
Any visible errors:
```

ChatGPT kan därefter göra nästa repoägda arbete: analysera evidensen, föreslå endast motiverade ändringar och dokumentera en reproducerbar kandidatprofil.

## A5. ChatGPT-gate före Guide 2

Guide 2 får inte betraktas som tekniskt verifierad förrän Team Master har bekräftat att:

- KoboldCpp laddar en GGUF-modell,
- `http://localhost:5001` fungerar,
- SillyTavern kan ansluta till KoboldCpp,
- en enkel flerturnschatt kan genereras.

ChatGPT ska vid fel först klassificera felet som installation/backend/UI/template/model/runtime i stället för att automatiskt skylla på modellen.

---

# DEL B — TEAM MASTER-ÄGD STEG-FÖR-STEG GUIDE

Följande kräver lokal Windows-, GPU-, filsystem- eller GUI-åtkomst och måste därför utföras av Team Master.

## B1. GPU-preflight

Öppna PowerShell eller CMD och kör:

```powershell
nvidia-smi
```

Kontrollera att RTX 3070 Ti syns och att inget onödigt program redan använder en stor del av de 8 GB VRAM som behövs för modellen.

**STOP om:** `nvidia-smi` inte fungerar eller GPU:n inte känns igen korrekt. Fixa NVIDIA-drivrutinen innan resten fortsätter.

Officiell NVIDIA-drivrutinssida vid behov:
https://www.nvidia.com/en-us/drivers/

## B2. Installera KoboldCpp

1. Öppna: https://github.com/LostRuins/koboldcpp/releases
2. Hämta den senaste stabila Windows-binären `koboldcpp.exe` för NVIDIA-användning.
3. Lägg den i en egen lokal mapp, exempelvis:

```text
C:\AI\AGENT-2-STORYTELLER\koboldcpp\
```

4. Starta `koboldcpp.exe`.

KoboldCpp distribueras som en självständig Windows-binär; någon separat CUDA Toolkit-installation ska inte läggas till enbart för att få standardbinären att fungera.

**PASS:** launchern öppnas utan blockerande fel.

## B3. Välj en befintlig kompatibel GGUF endast för harness-smoke-test

Guide 1 väljer inte slutmodell. Använd en redan tillgänglig Qwen3.5-9B-baserad GGUF eller annan fungerande text-GGUF för att verifiera kedjan.

Om den tidigare nämnda Huihui-Qwen3.5-9B-abliterated redan finns lokalt i GGUF-format kan den användas här utan att detta räknas som ett slutligt modellbeslut.

**Viktigt:** ladda ingen `mmproj` ännu.

## B4. Starta första KoboldCpp-baslinjen

I KoboldCpp launcher:

1. välj GGUF-modellen,
2. sätt Context Size till `8192`,
3. välj CuBLAS/CUDA för NVIDIA,
4. kontrollera att rätt GPU-ID motsvarar RTX 3070 Ti,
5. lämna automatiskt GPU Layers/AutoFit-värde som startpunkt,
6. håll `Low VRAM` avstängt,
7. håll SWA avstängt,
8. använd inte KV-kvantisering i första smoke-testet,
9. starta modellen.

SillyTaverns aktuella KoboldCpp-guide rekommenderar CuBLAS på NVIDIA, `Low VRAM` av och att det automatiskt valda GPU-layer-värdet lämnas som startpunkt.

**PASS:** KoboldCpp visar att modellen laddats och exponerar servern på port 5001.

## B5. Verifiera backend utan SillyTavern

Öppna:

```text
http://localhost:5001
```

Kör minst 5–10 enkla textturns i Kobold Lite.

Kontrollera samtidigt:

```powershell
nvidia-smi
```

Notera ungefärlig VRAM-användning och generationstakt.

**PASS:** modellen svarar flera turns utan crash, OOM eller extrema pauser.

## B6. Installera Node.js LTS och Git

Node.js:
https://nodejs.org/en/download

Alternativt via WinGet:

```powershell
winget install --id OpenJS.NodeJS.LTS -e
```

Git for Windows:
https://git-scm.com/downloads/win

Alternativt:

```powershell
winget install --id Git.Git -e --source winget
```

Verifiera:

```powershell
node -v
npm -v
git --version
```

**PASS:** alla tre kommandon returnerar giltig version.

## B7. Installera SillyTavern från `release`

Följ den officiella Windows-guiden:
https://docs.sillytavern.app/installation/windows/

Installera i en användarägd mapp, inte i `Program Files` eller `System32`.

Exempel:

```powershell
cd C:\AI\AGENT-2-STORYTELLER
git clone https://github.com/SillyTavern/SillyTavern -b release
```

Starta sedan:

```text
SillyTavern\Start.bat
```

Kör inte `Start.bat` som Administrator.

**PASS:** SillyTavern öppnas i webbläsaren.

## B8. Koppla SillyTavern till KoboldCpp

Med KoboldCpp fortfarande igång:

1. öppna API Connections i SillyTavern,
2. välj KoboldCpp under den relevanta Text Completion-anslutningen,
3. använd endpoint:

```text
http://localhost:5001
```

4. anslut.

KoboldCpp exponerar både sitt Kobold API och OpenAI-kompatibelt API på port 5001; SillyTaverns egen KoboldCpp-guide anger `http://localhost:5001` som anslutningsadress.

**PASS:** SillyTavern visar fungerande anslutning.

## B9. Genomför harness-smoke-testet

Kör en ny ren chatt och kontrollera minst:

1. fem korta user/assistant-turns,
2. ett längre svar,
3. en uppföljningsfråga som kräver föregående tur,
4. inga läckta specialtokens eller uppenbart trasig formatering,
5. ingen OOM/crash.

Bedöm ännu inte Storyteller-kvalitet. Detta test mäter endast om kedjan fungerar.

## B10. Rapportera tillbaka och stoppa här

Skicka tillbaka checklistan från A4 till ChatGPT.

**Guide 1 är PASS först när:**

- GPU fungerar,
- KoboldCpp kör modellen lokalt,
- backend svarar på `localhost:5001`,
- SillyTavern är installerat från `release`,
- SillyTavern ansluter till KoboldCpp,
- enkel flerturnschatt fungerar.

Gå därefter till **[GUIDE-2] - [CORRECT AGENT CONFIGURATION].md**. Ingen RAG, ingen mmproj och ingen avancerad VRAM-optimering ska introduceras före denna gate.
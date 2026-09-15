# GUIDE 1 — HARNESS & CHAT UI

**Mål:** Implementera den lokala textkedjan `SillyTavern -> KoboldCpp -> GGUF -> RTX 3070 Ti 8 GB` på Windows.

**Källor:** [KoboldCpp releases](https://github.com/LostRuins/koboldcpp/releases) · [KoboldCpp wiki](https://github.com/LostRuins/koboldcpp/wiki) · [SillyTavern Windows](https://docs.sillytavern.app/installation/windows/) · [SillyTavern + KoboldCpp](https://docs.sillytavern.app/usage/api-connections/koboldcpp/)

---

# A. ChatGPT-ägd steg-för-steg guide

## A1. Lås baslinjen

ChatGPT äger följande startkonfiguration tills lokal evidens motiverar ändring:

| Del | Baslinje |
|---|---|
| Backend | senaste stabila `koboldcpp.exe` |
| UI | SillyTavern `release` branch |
| API | Text Completion -> KoboldCpp |
| URL | `http://localhost:5001` |
| Modellformat | GGUF |
| Context | `8192` |
| GPU | CuBLAS/CUDA, RTX 3070 Ti |
| GPU Layers | KoboldCpp AutoFit/autodetect först |
| Low VRAM | OFF |
| QuantMatMul/MMQ | OFF på RTX 3070 Ti |
| High Priority | ON |
| Flash Attention | ON |
| Context Shift | ON/default |
| SWA | OFF |
| Quantized KV | OFF initialt |
| mmproj | OFF |

Context Shift lämnas aktivt för lång flerturnschatt. `--quantkv` och SWA införs inte samtidigt i baslinjen eftersom de ändrar KV/context-beteendet; de testas endast vid konkret VRAM-behov.

## A2. Definiera verifieringsdata

Efter Team Masters lokala steg ska följande returneras till ChatGPT:

```text
KoboldCpp version:
SillyTavern version/branch:
Exact GGUF filename:
Context size:
GPU layers offloaded:
VRAM after load:
Prompt processing speed:
Generation tok/s:
Kobold Lite 10-turn test: PASS/FAIL
SillyTavern connection: PASS/FAIL
Errors/warnings:
```

## A3. Nästa ChatGPT-åtgärd

När datan finns ska ChatGPT:

1. skilja backend-, VRAM-, template- och modellproblem åt,
2. justera högst en resursparameter åt gången,
3. dokumentera den fungerande runtimeprofilen,
4. först därefter öppna Guide 2.

**Gate:** Guide 1 är inte PASS förrän SillyTavern kan genomföra stabil flerturnschatt via KoboldCpp.

---

# B. Team Master-ägd steg-för-steg guide

## B1. GPU-preflight

Kör:

```powershell
nvidia-smi
```

RTX 3070 Ti ska synas. Stäng onödiga GPU-tunga program.

Vid drivrutinsproblem: [NVIDIA Drivers](https://www.nvidia.com/en-us/drivers/).

## B2. Installera KoboldCpp

1. Hämta senaste stabila `koboldcpp.exe`: [Releases](https://github.com/LostRuins/koboldcpp/releases).
2. Lägg den t.ex. i `C:\AI\AGENT-2-STORYTELLER\koboldcpp\`.
3. Starta `.exe`-filen.

Windows NVIDIA-binären har CUDA-stödet paketerat; installera inte CUDA Toolkit enbart för denna standardinstallation.

## B3. Ladda smoke-testmodellen

Välj en fungerande GGUF som redan finns lokalt. Detta är ännu inte slutligt modellval.

I KoboldCpp:

1. välj modellen,
2. `Context Size = 8192`,
3. `Use CuBLAS/CUDA = ON`,
4. verifiera rätt GPU ID,
5. lämna automatiskt GPU Layers-värde,
6. `Low VRAM = OFF`,
7. `QuantMatMul/MMQ = OFF`,
8. `High Priority = ON`,
9. `Flash Attention = ON`,
10. Context Shift lämnas på/default,
11. SWA och Quantized KV lämnas av,
12. spara KoboldCpp-konfigurationen och Launch.

**PASS:** loggen visar `Load Model OK: True` och server på port `5001`.

## B4. Verifiera KoboldCpp ensamt

Öppna `http://localhost:5001` och kör 10 sammanhängande turns i Kobold Lite.

Kontrollera samtidigt `nvidia-smi` och notera VRAM samt tok/s.

**STOP vid:** OOM, crash, trasig output eller extrem CPU/RAM-spill. Ändra inte flera inställningar samtidigt; rapportera utfallet till ChatGPT.

## B5. Installera SillyTavern

Installera först:

- [Node.js senaste LTS](https://nodejs.org/en/download)
- [Git for Windows](https://git-scm.com/downloads/win)

Verifiera:

```powershell
node -v
npm -v
git --version
```

Installera sedan SillyTavern utanför Windows-kontrollerade mappar:

```powershell
cd C:\AI\AGENT-2-STORYTELLER
git clone https://github.com/SillyTavern/SillyTavern -b release
```

Starta `SillyTavern\Start.bat` normalt, **inte som Administrator**.

## B6. Koppla SillyTavern till KoboldCpp

I SillyTavern:

1. `API Connections`,
2. API = `Text Completion`,
3. API Type = `KoboldCpp`,
4. URL = `http://localhost:5001`,
5. `Connect`.

## B7. Smoke-test hela kedjan

Kör minst:

1. fem korta dialogturns,
2. ett längre svar,
3. en fråga som kräver föregående tur,
4. kontroll att inga specialtokens/template-markörer läcker ut.

Returnera A2-checklistan till ChatGPT.

**PASS:** `SillyTavern -> KoboldCpp -> GPU-modell` fungerar stabilt. Fortsätt därefter till Guide 2.
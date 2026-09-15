# GUIDE 2 — CORRECT AGENT CONFIGURATION

**Mål:** konfigurera och verifiera AGENT-2-STORYTELLER korrekt ovanpå Guide 1 med **DefiantFable som enda aktiva modellkandidat**.

**Aktivt modellspecifikt scope:**
- `LOCAL_AGENTS/AGENT-2-STORYTELLER/AG-2-MODEL-DefiantFable/`

Huihui och andra kandidater är inte del av aktiv Guide 2 och får inte testas eller konfigureras utan Team Masters separata beslut.

Gemensam SillyTavern/KoboldCpp-konfiguration hör till `SillyTavern_UI/`.

**Förutsättning:** Guide 1 = PASS.

---

# A. ChatGPT-ägd guide

## A1. Lås verifierad DefiantFable-identitet

Aktuell verifierad runtimekandidat:

`Qwen3.5-9B-The-Defiant-Fable-Uncnr-Heretic-NEO-MAX-Q4_K_S.gguf`

Verifierat från faktisk KoboldCpp-runtime:

- arkitektur/familj: `qwen35`, 9B-klass,
- parametrar: cirka 8.95B,
- quant: `Q4_K_S`,
- training context rapporterad i modellmetadata: `262144`,
- aktuell Guide-2 baseline context: `8192`,
- mRoPE/hybrid/recurrent-egenskaper finns,
- KoboldCpp stänger Context Shift automatiskt i observerad runtime,
- modellen laddar och genererar stabilt genom KoboldCpp 1.120,
- streaming genom SillyTavern fungerar.

Exakt publicerad GGUF-källa är verifierad som DavidAU:s DefiantFable GGUF-repository. Filnamn/marknadsföring är inte i sig evidens för kvalitet eller beteende.

## A2. Template-gate — korrigerad efter faktisk FAIL-evidens

Första metadata-derived försöket via `Text Completion -> KoboldCpp` auto-valde `ChatML`. Grundläggande rolltaggar såg korrekta ut, men den rena smoke-chatten producerade ett synligt tomt `<think>...</think>`-block före **varje** assistant-svar.

Detta klassas som **template/configuration FAIL, inte modellfel**.

Qwen3.5 tänker som default. Officiell non-thinking-path använder chat-template-parametern:

```json
{"enable_thinking": false}
```

Qwen3.5:s Jinja lägger då in ett tomt `<think>\n\n</think>\n\n`-block i den kompilerade generation-prompten efter `<|im_start|>assistant`. Om den prefilling-delen saknas kan modellen själv generera think-taggarna som synlig output, vilket är exakt vad vår första smoke visade.

Aktiv Guide-2-väg är därför:

1. starta KoboldCpp med `--jinja`,
2. starta med `--chat-template-kwargs '{"enable_thinking":false}'`,
3. använd KoboldCpp OpenAI-compatible Chat Completions,
4. anslut SillyTavern via `Chat Completion -> Custom (OpenAI-compatible)` mot `http://127.0.0.1:5001/v1`,
5. låt backend-Jinja sköta Qwen3.5-formattering,
6. använd inte SillyTavern Text Completion Instruct Mode som aktiv template-path i denna konfiguration.

Repo-entrypoint:

```powershell
.\scripts\Start-DefiantFable-NonThinking.cmd
```

Automatisk backend-gate efter start:

```powershell
.\scripts\Test-DefiantFable-NonThinking.cmd
```

Testet anropar `/v1/chat/completions` och FAIL:ar om assistant-output innehåller `<think>`, `</think>`, `<|im_start|>` eller `<|im_end|>`.

**Viktigt:** SillyTavern Reasoning `Auto-Parse` ska inte användas som kosmetisk lösning för denna baseline. Vi vill stoppa felaktig generering, inte bara dölja den i UI:t.

## A3. Systemprompt v1 — rätt promptlager för Chat Completion

Baseline:

```text
You are the user's private English-speaking conversational and storytelling partner.
Be natural, imaginative, specific, and responsive to the user's intent. Maintain continuity within the current chat and follow the requested tone, characters, setting, perspective, and level of detail. Treat fictional scenarios as fiction and avoid unsolicited moralizing or generic assistant boilerplate. Never claim access to files, images, tools, or memories you were not actually given. Do not claim persistent memory across separate chats.
```

På den korrigerade Chat Completion-pathen ska prompten läggas i **Chat Completion Prompt Manager / Main Prompt**. Advanced Formatting `System Prompt` är Text Completion-yta och får inte antas vara den aktiva systemprompten efter API-bytet.

Ingen Story Creator-, MCP-, WORKER-, kod- eller filskrivningslogik ska läggas till i Guide 2.

## A4. Validation-sampler efter corrected template-PASS

Officiell Qwen3.5 non-thinking API-baseline ger:

- Temperature `0.7`
- Top-P `0.80`
- Top-K `20`
- Presence penalty `1.5`

Håll repetition penalty neutral på `1.0` tills exakt DefiantFable-evidens motiverar annat. Samplerprofilen låses först efter att corrected non-thinking template smoke har PASS.

Ändra aldrig flera samplerparametrar samtidigt vid felsökning.

## A5. DefiantFable-funktionstest

Efter corrected template-PASS och systemprompt:

1. minst 10 turns vanlig engelsk dialog,
2. två längre story-prompts,
3. ett kontinuitetstest som kräver tidigare fakta,
4. samma context/outputbudget genom testet,
5. logga observerad tok/s, VRAM, repetition, stopp/truncering och eventuella template-/reasoning-markörer.

1000–2000 ord per agentsvar är ett slutkrav men optimeras inte ännu; tidigare observerad truncering är inte bevisat modellfel och hålls separat från template/runtime-verifieringen.

## A6. Context-/VRAM-optimering senare

Efter kvalitets-PASS:

`8192 -> 12288 -> 16384`

En variabel åt gången. För denna mRoPE/hybrid-runtime ska Context Shift inte antas vara tillgängligt; effektivt runtimebeteende gäller.

---

# B. Team Master-ägd guide

## B1. Byt backend till corrected Defiant non-thinking profile

1. Stoppa **endast den nuvarande KoboldCpp-processen**.
2. SillyTavern får vara igång.
3. Kör från repo-roten:

```powershell
.\scripts\Start-DefiantFable-NonThinking.cmd
```

4. Välj samma exakta DefiantFable GGUF när filväljaren öppnas.
5. Vänta tills KoboldCpp rapporterar att API:n kör på `127.0.0.1:5001`.

ComfyUI får vara öppet men kör inte tung GPU-inferens under kontrollerade Guide-2-tester.

## B2. Verifiera non-thinking backend före SillyTavern

I en separat terminal, med nya KoboldCpp-processen igång:

```powershell
.\scripts\Test-DefiantFable-NonThinking.cmd
```

**PASS:** JSON visar `endpoint_check = PASS` och `marker_leak_check = PASS`.

Vid FAIL: ändra inga SillyTavern-inställningar ännu; skicka testoutput + relevant KoboldCpp-output.

## B3. Byt SillyTavern API-path

I API Connections:

```text
API:                    Chat Completion
Chat Completion Source: Custom (OpenAI-compatible)
Custom Endpoint/Base:   http://127.0.0.1:5001/v1
```

Den pinnade SillyTavern-versionens Custom Chat Completion-källa är keyless-capable, så lokal baseline behöver ingen API-nyckel. Refresh/select exakt modell-ID från backend om modellfält visas, sedan Connect/Test Message.

**Advanced Formatting Instruct Mode är inte den aktiva template-pathen här.**

## B4. Flytta baseline-systemprompten till Chat Completion Prompt Manager

Öppna Chat Completion Prompt Manager och sätt **Main Prompt** till exakt A3-texten. Håll extra jailbreak/NSFW/auxiliary prompts av eller tomma under validation om UI-presettet tillåter det; målet är en attribution-ren baseline.

Starta sedan en helt ny chat.

## B5. Rerun clean 5-turn smoke

Kör samma fem turns:

1. `Introduce yourself naturally in two sentences.`
2. `Remember this fact for this chat: the old manor is called Blackthorn House.`
3. `Who am I talking to, and what is the manor called?`
4. `Write one short atmospheric paragraph about arriving at Blackthorn House at midnight.`
5. `Continue naturally from the previous scene, but do not repeat the setup.`

**PASS:** inga synliga `<think>`, `</think>`, `<|im_start|>`, `<|im_end|>`; korrekta roller; `Blackthorn House` minns; normal streaming/stopp; naturlig continuation.

Vid FAIL: ändra inget mer; skicka screenshot + relevant ST/KoboldCpp-output.

## B6. Fortsättning efter PASS

ChatGPT låser därefter Validation-samplers och leder DefiantFable-funktionstestet.

**Guide 3 eller 4 får inte startas utan Team Masters separata explicita startkommando.**

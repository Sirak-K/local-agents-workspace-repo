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
- quant enligt filnamn: `Q4_K_S`,
- training context rapporterad i modellmetadata: `262144`,
- aktuell Guide-2 baseline context: `8192`,
- mRoPE/hybrid/recurrent-egenskaper finns,
- KoboldCpp stänger därför Context Shift automatiskt i den observerade runtime-konfigurationen,
- modellen laddar och genererar stabilt genom KoboldCpp 1.120,
- streaming genom SillyTavern fungerar.

Exakt publicerad GGUF-källa är verifierad som DavidAU:s DefiantFable GGUF-repository. Filnamn eller modellnamnets marknadsföring är fortfarande inte i sig evidens för kvalitet/beteende.

## A2. Template-gate — korrigerad efter faktisk smoke-evidens

Första metadata-derived försöket via `Text Completion -> KoboldCpp` auto-valde `ChatML` och gav korrekta grundläggande rolltaggar, men smoke-testet producerade synliga tomma `<think>...</think>`-block före varje svar.

Detta är **inte modellfel**. Qwen3.5:s riktiga non-thinking generation prompt kräver modellens Jinja med `enable_thinking=false`; då läggs det tomma think-blocket i själva prompten före generation i stället för att modellen behöver generera det som synlig output. Generisk SillyTavern ChatML representerade inte denna del.

Därför är aktiv Guide-2-väg nu:

1. starta KoboldCpp med Jinja,
2. sätt `chat_template_kwargs = {"enable_thinking":false}` på backendnivå,
3. använd KoboldCpp OpenAI-compatible Chat Completions,
4. anslut SillyTavern via `Chat Completion -> Custom (OpenAI-compatible)` mot `http://127.0.0.1:5001/v1`,
5. låt Chat Completion-pathen sköta roll/template-formattering; SillyTavern Instruct Mode hör till Text Completion och ska inte användas för denna path,
6. starta en helt ny chat och rerun template/systemprompt-smoke.

Repo-entrypoint:

```powershell
.\scripts\Start-DefiantFable-NonThinking.cmd
```

Denna startar den aktiva KoboldCpp-baslinjen med `--jinja --chat-template-kwargs '{"enable_thinking":false}'` ovanpå samma kontrollerade Guide-1 runtimeprofil.

**PASS:** inga synliga `<think>`, `</think>`, `<|im_start|>`, `<|im_end|>` eller felvända roller; normal streaming/stopp och stabil kontinuitet.

**Viktigt:** slå inte bara på SillyTavern `Auto-Parse` för att kosmetiskt dölja råa think-taggar. Baseline ska i första hand använda modellens avsedda non-thinking template-path så tokenbeteendet också blir korrekt.

## A3. Systemprompt v1

Använd följande korta modellneutrala baseline:

```text
You are the user's private English-speaking conversational and storytelling partner.
Be natural, imaginative, specific, and responsive to the user's intent. Maintain continuity within the current chat and follow the requested tone, characters, setting, perspective, and level of detail. Treat fictional scenarios as fiction and avoid unsolicited moralizing or generic assistant boilerplate. Never claim access to files, images, tools, or memories you were not actually given. Do not claim persistent memory across separate chats.
```

Ingen Story Creator-, MCP-, WORKER-, kod- eller filskrivningslogik ska läggas till i Guide 2.

## A4. Validation-sampler efter template-PASS

Verifierade source/model-cardvärden för **Instruct / non-thinking** används som första Validation-profil:

- Temperature `0.7`
- Top-P `0.80`
- Top-K `20`
- Min-P `0.0`
- Presence penalty `1.5`
- Repetition penalty `1.0`

Ändra aldrig flera samplerparametrar samtidigt vid felsökning. Samplerprofilen låses först efter att corrected non-thinking template smoke har PASS.

## A5. DefiantFable-funktionstest

Efter corrected template-PASS och systemprompt:

1. minst 10 turns vanlig engelsk dialog,
2. två längre story-prompts,
3. ett kontinuitetstest som kräver tidigare fakta,
4. samma context/outputbudget genom testet,
5. logga observerad tok/s, VRAM, repetition, stopp/truncering och eventuella template-markörer.

1000–2000 ord per agentsvar är ett slutkrav men optimeras inte ännu; tidigare observerad truncering är inte bevisat modellfel och hålls separat från template/runtime-verifieringen.

## A6. Context-/VRAM-optimering senare

Efter kvalitets-PASS:

`8192 -> 12288 -> 16384`

En variabel åt gången. För denna mRoPE/hybrid-runtime ska Context Shift inte antas vara tillgängligt bara för att baseline tillåter det; effektivt runtimebeteende gäller.

---

# B. Team Master-ägd guide

## B1. Byt backend till corrected Defiant non-thinking profile

1. Stoppa den nuvarande KoboldCpp-processen.
2. Låt SillyTavern vara igång.
3. Kör från repo-roten:

```powershell
.\scripts\Start-DefiantFable-NonThinking.cmd
```

4. Välj samma exakta DefiantFable GGUF när filväljaren öppnas.
5. Vänta tills KoboldCpp API är ready på `127.0.0.1:5001`.

## B2. Byt SillyTavern API-path

I API Connections:

```text
API:                    Chat Completion
Chat Completion Source: Custom (OpenAI-compatible)
Custom Endpoint:        http://127.0.0.1:5001/v1
```

API key lämnas tom om UI:t tillåter detta för den lokala endpointen. Refresh/select exakt modell-ID från `/v1/models` om modell-dropdown visas. Använd Test Message/Connect.

## B3. Rerun clean smoke

Starta helt ny chat. Kör samma 5-turn validation som tidigare.

PASS = inga synliga think-/specialtokens, korrekta roller, normal streaming/stopp, `Blackthorn House`-kontinuitet och naturlig continuation.

Vid FAIL: ändra inget mer; skicka screenshot + relevant ST/KoboldCpp-output.

## B4. Fortsättning efter PASS

ChatGPT låser därefter Validation-samplers och leder DefiantFable-testet.

**Guide 3 eller 4 får inte startas utan Team Masters separata explicita startkommando.**

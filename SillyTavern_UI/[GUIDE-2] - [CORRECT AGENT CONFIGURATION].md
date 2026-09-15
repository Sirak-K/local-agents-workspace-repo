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

Exakt upstream-repository, merge/finetune-lineage, inbäddad Jinja/template och modellkortets samplerrekommendationer ska betraktas som **öppna tills de verifierats från källa eller modellmetadata**. Filnamnet ensam räcker inte som bevis.

## A2. Template-gate — nästa aktiva steg

Primär väg:

1. SillyTavern API = `Text Completion -> KoboldCpp`.
2. Instruct Mode = ON.
3. `Derive templates` / metadata-derived template för både Context och Instruct = ON.
4. Reconnect till redan laddad DefiantFable.
5. Starta helt ny chat.
6. Kör 5 korta turns.

**PASS:** inga råa `<|...|>`-tokens, rolltaggar, trasiga stopp eller felvända user/assistant-turns.

**STOP:** om SillyTavern inte kan härleda en template eller väljer en uppenbart generisk/felaktig template. Gissa inte manuellt ännu.

Fallback först vid verifierat derive-FAIL:

- låt KoboldCpp använda modellens Jinja,
- använd KoboldCpps OpenAI-kompatibla Chat Completions-endpoint,
- anslut SillyTavern via Chat Completion/Custom mot lokal `/v1`.

## A3. Systemprompt v1 — efter template-PASS

Använd följande korta modellneutrala baseline:

```text
You are the user's private English-speaking conversational and storytelling partner.
Be natural, imaginative, specific, and responsive to the user's intent. Maintain continuity within the current chat and follow the requested tone, characters, setting, perspective, and level of detail. Treat fictional scenarios as fiction and avoid unsolicited moralizing or generic assistant boilerplate. Never claim access to files, images, tools, or memories you were not actually given. Do not claim persistent memory across separate chats.
```

Ingen Story Creator-, MCP-, WORKER-, kod- eller filskrivningslogik ska läggas till i Guide 2.

## A4. Validation-sampler först

Template/runtime verifieras först med en konservativ Validation-profil. Modellkortets exakta rekommendationer ska användas när de är verifierade; tills dess ska vi inte låsa modellspecifika samplerpåståenden.

Ändra aldrig flera samplerparametrar samtidigt vid felsökning.

## A5. DefiantFable-funktionstest

Efter template-PASS och systemprompt:

1. minst 10 turns vanlig engelsk dialog,
2. två längre story-prompts,
3. ett kontinuitetstest som kräver tidigare fakta,
4. samma context/outputbudget genom testet,
5. logga observerad tok/s, VRAM, repetition, stopp/truncering och eventuella template-markörer.

1000–2000 ord per agentsvar är ett slutkrav men **optimeras inte ännu**; tidigare observerad truncering är inte bevisat modellfel och hålls separat från template/runtime-verifieringen.

## A6. Context-/VRAM-optimering senare

Efter kvalitets-PASS:

`8192 -> 12288 -> 16384`

En variabel åt gången. För denna mRoPE/hybrid-runtime ska Context Shift inte antas vara tillgängligt bara för att baseline tillåter det; effektivt runtimebeteende gäller.

---

# B. Team Master-ägd guide

## B1. Starta SillyTavern efter Guide-1-portbytet

Normal entrypoint från repo-roten:

```powershell
.\scripts\Start-SillyTavern.cmd
```

Aktuell lokal SillyTavern-port är konfigurerad bort från `8000`; använd den URL som startup-terminalen rapporterar.

KoboldCpp ska fortsatt vara `http://127.0.0.1:5001` för aktuell baseline.

## B2. Gör endast template-gaten nu

I SillyTavern:

1. öppna Advanced Formatting / Instruct-inställningarna,
2. slå på Instruct Mode,
3. slå på metadata-derived/Derive Templates för Context + Instruct,
4. reconnect till KoboldCpp,
5. starta en helt ny ren chat.

Skicka screenshot av Advanced Formatting-sektionen **efter derive/reconnect**, så verifierar ChatGPT exakt vilken template ST faktiskt valt innan systemprompt/samplers ändras.

## B3. Template smoke

Efter ChatGPT-verifiering: kör fem korta turns.

PASS = inga synliga specialtokens/rolltaggar, normala stopp, korrekt user/assistant-riktning och stabil generation.

Vid FAIL: ändra ingenting mer; skicka screenshot + relevant ST/KoboldCpp-output.

## B4. Fortsättning efter PASS

ChatGPT ger därefter exakt systemprompt- och Validation-sampler-konfiguration och leder DefiantFable-testet.

**Guide 3 eller 4 får inte startas utan Team Masters separata explicita startkommando.**
# GUIDE 2 — CORRECT AGENT CONFIGURATION

**Mål:** Konfigurera AGENT-2-STORYTELLER korrekt ovanpå Guide 1.

**Modellspecifika ytor — enda tillåtna:**
- `LOCAL_AGENTS/AGENT-2-STORYTELLER/AG-2-MODEL-Huihui/`
- `LOCAL_AGENTS/AGENT-2-STORYTELLER/AG-2-MODEL-DefiantFable/`

Gemensam SillyTavern/KoboldCpp-konfiguration hör till `SillyTavern_UI/`.

**Källor:** [SillyTavern Advanced Formatting](https://docs.sillytavern.app/usage/core-concepts/advancedformatting/) · [Instruct Mode](https://docs.sillytavern.app/usage/core-concepts/instructmode/) · [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) · [KoboldCpp wiki](https://github.com/LostRuins/koboldcpp/wiki)

**Förutsättning:** Guide 1 = PASS.

---

# A. ChatGPT-ägd steg-för-steg guide

## A1. Verifiera varje modell separat

Team Master skickar exakt GGUF-fil/repository för Huihui respektive DefiantFable. ChatGPT verifierar för varje modell:

- lineage/base model,
- quant,
- chat template/Jinja,
- contextgräns,
- thinking/non-thinking-regler,
- modellkortets samplerrekommendationer,
- eventuell mmproj-information för Guide 4.

Fakta för Huihui får endast skrivas mot `AG-2-MODEL-Huihui/`; fakta för DefiantFable endast mot `AG-2-MODEL-DefiantFable/`.

## A2. Lås template-strategin

Primär väg:

1. SillyTavern API = `Text Completion -> KoboldCpp`.
2. Instruct Mode = ON.
3. `Derive templates` = ON för Context + Instruct.
4. Reconnect efter modellbyte.
5. Bekräfta att rätt template faktiskt härleds från modellmetadata.

**STOP:** om SillyTavern inte hittar rätt template. Gissa inte en närliggande template.

Fallback om korrekt modelltemplate inte kan representeras via Text Completion:

- starta KoboldCpp med modellens Jinja (`--jinja`),
- använd KoboldCpps OpenAI-kompatibla Chat Completions-endpoint,
- anslut SillyTavern via Chat Completion/Custom mot `http://localhost:5001/v1`.

## A3. Systemprompt v1

ChatGPT äger en kort modellneutral prompt:

```text
You are the user's private English-speaking conversational and storytelling partner.
Be natural, imaginative, specific, and responsive to the user's intent. Maintain continuity within the current chat and follow the requested tone, characters, setting, perspective, and level of detail. Treat fictional scenarios as fiction and avoid unsolicited moralizing or generic assistant boilerplate. Never claim access to files, images, tools, or memories you were not actually given. Do not claim persistent memory across separate chats.
```

Ingen Story Creator-, MCP-, WORKER-, kod- eller filskrivningslogik ska läggas till.

## A4. Skapa två samplerprofiler

ChatGPT definierar:

**Validation:** nära modellkortets rekommenderade standardvärden; används för template/runtime-test.

**Story:** kreativ profil som A/B-testas efter Validation-PASS.

Ändra inte flera samplingparametrar samtidigt när ett problem felsöks.

## A5. Definiera Huihui ↔ DefiantFable A/B-test

Båda kör exakt samma:

1. 5-turn vanlig dialog,
2. 2 längre story-prompts,
3. 1 kontinuitetstest efter minst 10 turns,
4. samma systemprompt,
5. samma context och outputbudget,
6. respektive korrekta template,
7. samma Validation-profil först.

Bedöm: naturalitet, prosa, kontinuitet, instruktionsefterlevnad, repetition, onödiga refusals i tillåten fiktion, tok/s och VRAM.

ChatGPT sammanställer resultatet och väljer primär modell först efter evidens. Modellnamn som `abliterated`, `uncensored` eller `heretic` är inte resultatbevis.

## A6. Context-/VRAM-optimering efter kvalitets-PASS

Ordning:

`8192 -> 12288 -> 16384`

En variabel åt gången. Context Shift prioriteras för lång chatt. Om 8 GB VRAM kräver KV-kvantisering testas `Q8 KV` separat; verifiera då installerad KoboldCpp-version eftersom Quantized KV och Context Shift har haft kompatibilitetsförändringar mellan versioner. SWA används inte samtidigt med Context Shift.

---

# B. Team Master-ägd steg-för-steg guide

## B1. Testa template först

För aktuell modell:

1. starta KoboldCpp med Guide-1-profilen,
2. anslut SillyTavern,
3. aktivera Instruct Mode + Derive templates,
4. reconnect,
5. starta en helt ny chatt.

Kör 5 turns.

**PASS:** inga `<|...|>`, rolltaggar, trasiga stopp eller uppenbart felvända user/assistant-turns syns.

Vid FAIL: stoppa och skicka modellfilnamn + relevant KoboldCpp/SillyTavern-output till ChatGPT.

## B2. Lägg in systemprompten

Använd exakt A3-prompten som baslinje. Lägg inte till gamla AGENT-2-prompter.

Kör minst 10 turns vanlig engelskspråkig dialog.

**PASS:** naturlig chatt, relevant kontinuitet och inget uppenbart prompt-/templatefel.

## B3. Kör Huihui-testet

Kör A5-testet med Huihui. Rapportera:

```text
Exact GGUF:
Template used:
Context:
Sampler profile:
VRAM:
tok/s:
Dialogue:
Prose:
Continuity:
Repetition:
Refusals/boilerplate:
Errors:
```

## B4. Kör DefiantFable-testet

Byt endast modell och dess verifierade modellspecifika template/config. Kör samma A5-test och samma rapportformat.

## B5. Låt ChatGPT välja kandidat innan context höjs

Skicka båda resultaten. Höj inte context, aktivera inte RAG och lägg inte till mmproj innan ChatGPT jämfört utfallet.

## B6. Verifiera vald modell vid längre context

Efter ChatGPT:s val:

1. testa `12288`,
2. kontrollera VRAM/tok/s/stabilitet,
3. endast vid PASS testa `16384`,
4. gör därefter en verklig längre chatt mot ungefär 50 user-turns.

**PASS:** vald modell har korrekt template, bra Storyteller-beteende och acceptabel flerturnslatens. Fortsätt till Guide 3.
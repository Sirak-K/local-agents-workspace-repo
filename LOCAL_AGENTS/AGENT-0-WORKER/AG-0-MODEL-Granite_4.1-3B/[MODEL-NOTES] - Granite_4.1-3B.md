# Granite — modellanteckningar inför praktisk EVAL

Detta är ett modellfamiljsorienterat, teoretiskt underlag. Varje utsaga nedan gäller den angivna Granite-releasen och stöds av IBM:s publicerade modellmaterial; IBM:s benchmarkvärden är **rapporterade mätningar av upstream-modellerna**, inte resultat från vår lokala agentkandidat. Lokal installationsidentitet, LM Studio-inställningar och vald men ännu inte applicerad första baseline hör till [[MODEL-CONFIG-BASELINE] - Granite_4.1-3B.md](<./[MODEL-CONFIG-BASELINE] - Granite_4.1-3B.md>), inte hit.

## Granite 4.1 Instruct: träning, kontrakt och avsedd användning

- IBM beskriver Granite 4.1 Instruct som vidaretränad från Granite 4.1 Base med supervised fine-tuning och reinforcement learning. Den angivna SFT-datamixen består av öppet tillgängliga dataset med tillåtande licenser, intern syntetisk data och utvald människokurerad data. IBM beskriver förbättringsarbetet som riktat mot instruktionsefterlevnad, tool calling och chatt. [IBM:s modellkort](https://huggingface.co/ibm-granite/granite-4.1-3b).
- IBM avser Granite 4.1 Instruct för generella instruktioner, AI-assistenter och agenter med verktyg. Modellkortet listar sammanfattning, klassificering, extraktion, frågesvar, RAG, kodrelaterade uppgifter, funktionsanrop och flerspråkig dialog som användningsområden. Det är **avsedd användning och upstream-underlag**, inte ett lokalt godkännande för autonomt WORKER-arbete. [IBM:s modellkort](https://huggingface.co/ibm-granite/granite-4.1-3b).
- Granite 4.1:s publicerade språklista omfattar engelska, tyska, spanska, franska, japanska, portugisiska, arabiska, tjeckiska, italienska, koreanska, nederländska och kinesiska. Svenska finns inte på listan. IBM anger dessutom att instruction-finetuning huvudsakligen använder engelska instruktion/svar-par. Detta är ett konkret skäl att mäta svensk användbarhet separat; frånvaron på listan är inte ett misslyckat svenskt test. [IBM:s modellkort](https://huggingface.co/ibm-granite/granite-4.1-3b).
- Den [publicerade Granite 4.1 3B-chattemplaten](https://huggingface.co/ibm-granite/granite-4.1-3b/blob/main/chat_template.jinja) serialiserar roller med `<|start_of_role|>`/`<|end_of_role|>` och `<|end_of_text|>`. När verktyg ges placeras deras scheman i `<tools>`; assistentens anrop använder `<tool_call>` och verktygssvar `<tool_response>` i ett användarmeddelande. Templaten kan också lägga dokument i `<documents>`. Dessa är fakta om **publicerad 4.1-template**, inte bevis på vilka tools LM Studio exponerar eller vilken template en viss inference faktiskt använder. En lokal granskningskopia finns i [chat-template-snapshot.jinja](./chat-template-snapshot.jinja).
- Den publicerade 4.1-templaten visar ingen särskild `<think>`-gren eller `enable_thinking`-styrning. Det belägger inte att modellen saknar vanlig flerstegslogisk förmåga. [IBM:s chattemplate](https://huggingface.co/ibm-granite/granite-4.1-3b/blob/main/chat_template.jinja).
- IBM:s [`generation_config.json` för Granite 4.1 3B](https://huggingface.co/ibm-granite/granite-4.1-3b/blob/main/generation_config.json) innehåller token-ID:n men inga föreskrivna `temperature`-, `top_k`- eller `top_p`-värden. Ett samplerval från en annan Granite-release eller kvantiserare är därför inte en officiell 4.1-standard för denna modellfamilj.

## Storleksjämförelse — Granite 4.1 Dense

IBM:s modellkort namnger **3B, 8B och 30B**, inte en separat 9B-variant. Tabellen återger IBM:s upstream-arkitektur och ett litet urval av dess publicerade EVAL-resultat; alla tre har angiven maximal sekvenslängd 131 072 token. Detta är inte laddad LM Studio-kontext eller en lokal hastighets-/minnesmätning. [IBM:s modellkort, arkitektur och resultat](https://huggingface.co/ibm-granite/granite-4.1-3b).

| Granite 4.1 Dense | Lager | IFEval Avg | BFCL v3, tool calling | HumanEval pass@1 |
| --- | ---: | ---: | ---: | ---: |
| 3B | 40 | 82,30 | 60,80 | 81,71 |
| 8B | 40 | 87,06 | 68,27 | 85,37 |
| 30B | 64 | 89,65 | 73,68 | 88,41 |

På just dessa tre rapporterade mätningar är de större varianternas värden högre. Tabellen bevisar inte att en större variant är snabbare, får plats på projektets GPU eller är mer pålitlig i LM Studio. Val av WORKER kräver samma rollrelevanta, kontrollerade lokala EVAL för varje kandidat.

## Gräns mot praktiska slutsatser

Publicerad träning, template och benchmarkdata motiverar **vilka förmågor som är värda att pröva**, inte att ett tool-anrop, en filändring, svensk instruktion eller lång kontext fungerar i vår agentprofil. Lokalt observerade modellutdata och effektiva konfigurationsvillkor finns i [[MODEL-CONFIG-BASELINE] - Granite_4.1-3B.md](<./[MODEL-CONFIG-BASELINE] - Granite_4.1-3B.md>); plattformens tool-dispatch dokumenteras i LM Studio-anslutningen och uppgiftsutfall i WORKER-evalen. Dessa lokala observationer är inte IBM:s benchmarkresultat och bevisar inget skriv-/svensk-/långkontextutfall. Senare Granite-releaser får egna avgränsade fakta.

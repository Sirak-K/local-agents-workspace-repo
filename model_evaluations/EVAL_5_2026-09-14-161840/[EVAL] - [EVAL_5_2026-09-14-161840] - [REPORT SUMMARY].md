# EVAL 5 — Qwen vs Granite: introducerande native read-jämförelse

## 1. Beslutssammanfattning

**Qwen2.5-7B-Instruct Q4_K_M klarade den faktiska read-uppgiften via native SDK-dispatch.** Toolen läste rätt fil, handler-receipt styrker läsningen, modellen återgav båda filvärdena korrekt och filen var oförändrad. Ingen Granite-adapter, formatcoaching eller projektägd systemprompt användes.

Granite 4.1 3B Q4_K_M klarade inte samma introducerande uppgift i den aktuella jämförelsen: svaret innehöll tool-liknande text, men ingen native toolrequest/handler/receipt eller de efterfrågade filvärdena. Detta är **ett praktiskt installationsutfall**, inte bevis för ensam modellorsak.

**Nästa prioritet är fortsatt Qwen-kvalificering för 0-WORKER**, inte fler oförändrade Granite-runs. Det finns nu en verifierat fungerande native read-väg i vår LM Studio-harness. Det avgränsade målet för jämförelsen är uppnått; intern parser-/cache-/kernelorsak behöver inte förklaras för att denna väg ska få prövas vidare.

Detta var ett begränsat jämförelse-/kompatibilitetspass, **inte en full 8×3-kandidat-eval**, bekräftad write-förmåga, ComfyUI-expertis eller beslut om permanent modellval. Qwen är redan Team Masters prioriterade nästa kandidat, men bättre generell rollprestation är fortsatt arbetshypotes.

## 2. Vad kördes, i verklig ordning?

| Ordning | Arbete | Verifierat utfall | Evidens |
| --- | --- | --- | --- |
| 1 | SDK-inventering med giltig, ogiltig och åter giltig token | Giltig accepterades, ogiltig nekades; ingen inferens | `LiveSdkAuthenticationTest`: 1 live-test PASS, 3 autentiseringsfall |
| 2 | Qwen-generering med separat begärt stopp och disponibelt processarbete | `verified_cancel`, serverns `userStopped`, inga aktiva ägda processer | `5c86395ef8b9405e90577a7bc68cd7fa/evidence.json` |
| 3 | Qwen: normal kort avslutning | Exakt `OK`, naturligt EOS, ingen cancel | `c0b769a4967443a48cadf925578215bf/evidence.json` |
| 4 | Qwen: faktisk native read | Uppgiften klarad, 1 completed tool, 0 active, korrekt slutleverans | `ce818313c0ba35951370550996bdf7e7/evidence.json` |
| 5 | Efter terminalt Qwen-avslut: unload Qwen, load Granite, samma read-recept | Uppgiften inte klarad, 0 completed/active tools, naturligt EOS | `6fc298caf45398d7949ee36008773ddb/evidence.json` |
| 6 | Efter terminalt Granite-avslut: unload Granite och stoppa servern | Inga laddade modeller, server stoppad | CLI-slutkontroll och separat lifecycle-capture |

De två första Qwen-genereringarna var obligatorisk avgränsad säkerhets-/transportpreflight för aktuell kandidat, inte förmågepoäng eller extra försök att få read-PASS. Genereringsstoppreceipt kom 0,016 s efter stoppbegäran. Ägt disponibelt processarbete verifierades utan sena writes; detta är inte i sig ett test av avbrott inne i den riktiga read-handlern.

Två read-försök utfördes, ett per installation, inom jämförelseplanens budget. Inga likadana read-retries, full-evals, templateändringar, omladdningsstudier eller ComfyUI-genereringar startades.

## 3. Uppgiften och låsta operativa villkor

Exakt instruktion för båda armarna:

> Read project/config/service.json using the available file tool. Tell me the queue_name and retry_limit from that file. Do not guess values or modify files.

Fixturen innehöll `queue_name=render-diagnostic`, `retry_limit=3` samt de befintliga service-/note-fälten. Den levererades endast på disk i respektive unik disponibel workspace, inte som facit i instruktionen.

Gemensamt: officiell JavaScript-SDK 1.5.0 med befintlig godkänd auth-anpassning; färsk Chat; ingen projektägd systemprompt/rollkontext/skill; endast befintlig `read_workspace_text`; temperature 0; högst 512 tokens/prediction, 2 prediction-rounds, 2 toolanrop; inga parallella tools; 30 s körbudget och 5 s stoppbudget. Effektiv load: context 4096, GPU-offload 1, parallel sessions 1, draft MTP false. Capture anger ingen dold draftmodell; native lifecycle-konfiguration redovisar även speculative draft simple false.

Samma exakta instruktion, fixturebytes, projekt-source-set och installerade SDK/Node/Zod-identitet verifierades för båda read-runs. Load-config har samma fältnycklar och endast den modellberoende prompt-templaten skiljer i de fångade värdena. Båda använder sin egen effektiva template, inte ett påtvingat Granite-format.

## 4. Hur presterade installationerna på uppgiften?

| Observation | Qwen2.5-7B-Instruct Q4_K_M | Granite 4.1 3B Q4_K_M |
| --- | --- | --- |
| Uppgiften slutförd | **Ja** | **Nej** |
| Native toolrequest-events | Start, namn, argument, parsed/finalized | Inga |
| Guard och handler | Allowed, rätt read-handler körd | Ingen körning |
| Read-receipt | Completed, rätt filhash | Saknas |
| Slutleverans | Båda rätta filvärdena | Tool-liknande text, inga filvärden |
| Fixtureintegritet | Oförändrad | Oförändrad |
| Prediction-rounds | 2: `toolCalls` → `eosFound` | 1: `eosFound` |
| End-to-end runner-evidens | 1,160 s till verifierad leverans | 0,547 s till svar utan slutförd uppgift |
| Tillåten negativ modellspecifik slutsats | Ingen sådan behövs | **Ingen modellspecifik negativ slutsats möjlig** |

Qwens exakta slutleverans:

> From the `project/config/service.json` file, the `queue_name` is `render-diagnostic` and the `retry_limit` is `3`.

Granites exakta sluttext:

```text
<tool_call>{
  "name": "read_workspace_text",
  "arguments": {
    "path": "project/config/service.json"
  }
}
```

Den avslutande tool-taggen saknas i den observerade Granite-texten. Predictionen slutade naturligt vid 31 genererade tokens, inte vid 512-tokenbudgeten. Detta är en rå observation; den bevisar inte om den avgörande orsaken ligger i vikter, template, stopptolkning eller samspelet med backend/harness.

## 5. Vad avslöjar jämförelsen om harness och eval?

### Verifierat

- En faktisk native toolkedja fungerar för Qwen-installationen: publikt toolrequest-event → allowed guard → read-handler → completed receipt → modellens korrekta slutleverans.
- Gemensam autentisering, SDK-anslutning, read-tool, pathscope, fixture och handler är inte generellt oförmögna att utföra denna read. Ett obegränsat påstående att vår hela harness inte kan köra tools är därmed fel.
- Qwen kunde fullfölja den tvåstegskedja som 0-WORKER behöver: begära extern filinformation och använda faktiskt toolresultat. Detta är smal verifierad förmåga under angiven installation, inte generell autonomi.
- Den fångade Granite-runnens publika avvikelse ligger före native parsed request/guard/handler; ett handler-/permission-avslag observerades inte. Exakt intern felägare förblir öppen.

### Viktiga rapporteringsfällor som undveks

- Qwens slutliga `prediction_config.tools` är `type=none`, medan Granites är `toolArray`. Det gäller **sista predictionen**: Qwen kom till finalround efter genomförd tool, Granite stannade i första round. Skillnaden är inte bevis för att Qwen från början fick ett annat eller saknat tool-schema.
- Qwens finalized request har separat namn `read_workspace_text`, rätt argument och `raw_content={"path": "project/config/service.json"}`. Den publika råsträngen är här argumenttext, **inte hela ursprungliga genererade envelope-texten**. Dess SHA får inte användas som bevis för komplett jämförbar modelloutput.
- Ingen projektägd systemprompt betyder inte noll effektiv konditionering. Qwens standardtemplate lägger till sin vanliga assistant-/toolvägledning; Granites egen template har annan modellberoende roll-/toolserialisering. Detta är en korrekt native installationsjämförelse, inte en okonditionerad vikter-ensam-A/B.

## 6. Jämförbarhet och kvarstående luckor

Armarna är käll-/receptmatchade men **inte fullständigt positions-/tillståndskontrollerade**. Qwen hade cancellation och normal-completion-prober före readen: dess read började vid tredje genereringsanropet på instansen. Granite-readen var första anropet efter dess färska laddning. Därför isolerar kontrasten inte modellfamiljen från första-anrop-/tillståndseffekter.

Detta förhindrar ensamorsakspåståenden men gör inte Qwens faktiska native read-PASS ogiltigt. För projektets nästa praktiska beslut räcker fyndet: en prioriterad installation kan nu utföra uppgiften. Ingen ytterligare Granite-serie behövs för att Qwen ska få kvalificeras vidare. Om ett framtida beslut verkligen kräver kausal positionskontroll ska det utformas separat och förhandsmotiveras, inte smygas in som fler retries här.

Storlek, modellvikter, tokenizer, template och modellberoende tooltolkning skiljer samtidigt. Backendens exakta build är inte identifierad genom klienternas dependency-hashar. SDK/Node/Zod-artefaktidentitet och effektiva fångade configvärden är kontrollerade; full backend-byte-identitet får inte påstås.

Den historiska EVAL 4 är separat referens, inte aktuell kontrollarm. EVAL 2:s äldre read-PASS har inte retroaktivt kompletterats eller presenterats som reproducerad.

## 7. Praktisk hastighet och resurskostnad

Qwen gav en användbar verifierad read-leverans på cirka **1,16 s** från runnerns created till finished. Predictiontiderna var 0,519404 s för toolround och 0,394516 s för finalround; det senare ensamt är inte hela uppgiftstiden.

Granites 0,547 s till ofullbordat uppgiftsutfall är inte en snabbare användbar leverans. Dess högre observerade tokens/s motiverar inte att Qwen nedprioriteras. Ett prov är inte generell latency-/reliabilitetsranking.

CLI rapporterade loadtid/allokering: Qwen 3,26 s och 4,36 GiB; Granite 1,94 s och 1,96 GiB. Dessa är appens rapporterade loadvärden, inte maximal uppmätt GPU-kostnad under alla agentuppgifter. Efter Qwen-load observerades GPU-total 5598/8192 MiB och 2420 MiB ledigt. Båda kördes en åt gången; ingen resursöverskridning observerades i detta bounded pass.

## 8. Evidens och observability

- Evalhem: `model_evaluations/EVAL_5_2026-09-14-161840/`; de fyra genereringsrunsen i tabellen ovan äger sina original och partiell evidens. Det finns ingen redundant `frontier_evaluations/`-wrapper.
- Qwen-read evidence SHA-256: `8f0285349ad11305a2bd2ab0a65778c6d1f468383cab19b48fa606fff1a428aa`.
- Granite-read evidence SHA-256: `1b59eb9a59e341cbecd4fbd209b51d146f844237470c32ceed8265f54f8a53b0`.
- Gemensam projekt-source-set SHA-256: `c604eb36c04bcbf2927fc25b51f54c9bca78c9d3aa678738f771b4f43fc4f0c4`.
- SDK 1.5.0, Node v24.11.1; installerade SDK-/Zod-entrypoint-hashar och rekonstruerbara bounded projektkällbytes finns i varje read-run, inte bara i rapporten.
- Separat generell lifecycle-capture: `LM-Studio_logs/model_lifecycle_events/20260914_161933531_de596fa7-ec81-425f-b6dd-6f80d345534f.json`, 90 s bounded, 45 polls, 6 events. Den började efter Qwen-load och kan därför inte bevisa dess ursprungliga loadhändelse.
- Capturen är `completed_with_errors`/partial: efter avsiktlig serverstopp gav sista polls anslutningsfel/timeout. Detta är observability efter shutdown, inte ett observerat inferensfel eller modell-FAIL. Capture-originalets luckor och status är bevarade; ingen redundant generell fellogg skapades.
- Modellfilens distributionsstorlek/metadata och hard-link-registrering är dokumenterade i jämförelseplanen. Lokal fullfilshash har inte uppmätts; distributionshash är inte ett fabricerat lokalt integritetsbevis.

Två förberedelsekommandon korrigerades utan inferens: tokenmodulens faktiska ägare var `tools/`, och lifecycle-funktionsanropet behövde explicit `base_url`. Det var lokala förberedelse-/anropsmissar, inte kandidat- eller harnessruntimefel; inget read-försök gjordes om på grund av dem.

## 9. Nästa beslut och tydlig exit

**Jämförelsepasset avslutas här.** Qwen behåller första prioritet. Nästa kandidatförmågearbete är dess egen modellneutrala screening och därefter minsta säkert verifierbara read/write/readback-uppgift; Granites screeningpoäng ärvs inte. Vid mutation följer scoped JSON-/workflowarbete mot det redan förberedda playground-materialet, inte produktionsändringar eller checkpoint-/bildgenerering.

Ordinarie kandidat-toolrunners kräver fortfarande aktuell tre-read-transportreview för samma laddade instans samt klasspecifikt scope-/stoppbevis. En read-PASS från detta pass låser inte upp dem och ersätter inte verkligt stopp inne i den specifika toolen. Ny modellload kräver aktuell instanskontroll; detta ska hanteras som avgränsad startverifiering, inte fler full-evals eller kandidatpoäng.

Ingen mer Granite-rabbit-hole, ny parser, ny plattform eller motorstudie är motiverad av detta resultat. Ett framtida negativt Qwen-utfall ska först utredas hos rätt config-/harness-/evalägare; ingen ensam modellorsak antas. Kandidaten lämnas utan ytterligare generering tills Team Master tar ställning till sammanfattningen.

## 10. ERQER — extern granskning av framtida förbättringar

1. **Vad kunde jag, Codex, gjort mycket bättre eller annorlunda?** Särskilt: borde de nödvändiga säkerhetsprobernas anropsposition ha matchats i Granite-armen före körning, eller räcker den tydligt avgränsade praktiska kontrollen för installationsvalet? En positionsskillnad ska inte döljas som perfekt A/B.
2. **Hur kan framtida utvärderade agenter ge mer lönsamma, användbara och försvarsbara resultat/insikter på modellspecifik och modellneutral nivå?** Föreslå minsta rollrelevanta vidare uppgift som skiljer verklig read/write-förmåga från fungerande read-transport, utan att frångå Qwens prioritet eller blanda tool-/modellorsaker.
3. **Hur kan framtida EVALS förbättras icke-kosmetiskt och icke-trivialt?** Bedöm om nuvarande tre-read/startgate och instansfärskhet ger proportionerligt värde, samt hur första respektive sista predictionens effektiva tools-config kan rapporteras utan felaktig interfacejämförelse. Inga overifierade parserhooks förutsätts.
4. **Vilka övriga mycket höga/höga ROI-insikter bör Codex adressera eller implementera?** Fokusera på nästa verifierade WORKER-förmåga och ComfyUI-workflownytta. Ange konkret ändring, rätt ägare, tidigare bra beteende som ska bevaras och vilket beslut ändringen påverkar—inte en obegränsad intern orsaksjakt.

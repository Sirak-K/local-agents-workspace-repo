# EVAL REPORT SUMMARY — EVAL_1_2026-09-13-204437

## Rapportidentitet

| Fält                      | Värde                                                             |
| ------------------------- | ----------------------------------------------------------------- |
| Eval-id                   | `EVAL_1_2026-09-13-204437`                                        |
| Kandidat                  | Granite 4.1 3B, `Q4_K_M`                                          |
| Aktiv agentroll           | `0-WORKER`                                                        |
| Frontier-evaluator        | Codex                                                             |
| Primär bedömd del         | Round 1, verktygsfri IMSLE, tre ERST                              |
| Första giltiga ERST start | 2026-09-13 \| 20:44:37.949 +02:00                                 |
| Rapport skapad            | 2026-09-13 \| 23:29:10 +02:00                                     |
| Rapportversion            | 1.0                                                               |
| Rapportstatus             | Sammanställd för extern förbättringsgranskning av Grok och Claude |

Denna fil sammanfattar den första och hittills enda fullständigt genomförda evalrundan. EVAL 1-hemmet innehåller även förkontroller, ett ogiltigt föregångsförsök och efterföljande filläsnings-/avbrottsdiagnostik. Endast de tre uttryckligt namngivna IMSLE-körningarna ingår i resultatet `3/3`. Övriga körningar används som process-, kompatibilitets- eller säkerhetsevidens och får inte räknas som ytterligare godkända ERST.

Rapporten är en syntes, inte ny rå evidens eller en ny grader. Vid konflikt väger immutable `evidence.json`, hashbunden `assessment.json` och faktisk tool-/diskevidens tyngre än rapporttexten.

## Läsinstruktion för externa reviewers

Granska fyra lager separat innan en orsak tillskrivs:

1. **Modellspecifikt:** vad Granite faktiskt genererade under namngivna villkor.
2. **Plattform/harness:** vad LM Studio, SDK, template, parser, controller och tools faktiskt dispatchade, exekverade och kvitterade.
3. **Uppgiftsutfall:** om den avsedda 0-WORKER-uppgiften faktiskt slutfördes och verifierades.
4. **Evaluatorprocess:** hur Codex utformade, avgränsade, observerade, bedömde och korrigerade EVALEN.

Ett samband mellan två lager är inte automatiskt en bevisad ensamorsak. Särskilt viktigt: en korrekt textgenererad tool-begäran är inte samma sak som exekverad tool, och en harness-anpassad framgång är inte retroaktiv framgång i originalgränssnittet.

## Executive summary

- Granite klarade de tre låsta, verktygsfria IMSLE-uppgifterna: exakt record transformation, korrekt prioriterad routing och korrekt grundad vägran att avgöra hastighet från prisdata. Detta är **smal preliminär 3/3-evidens**, inte bekräftad generell 0-WORKER-förmåga.
- De tre giltiga körningarna använde färsk chat, en enda user-instruktion, tom projektägd System Prompt, inga tools, inga rollfiler, inga skills, ingen projektkontext och `temperature: 0`. LM Studios/Granites effektiva Jinja-template var fortfarande aktiv; utfallet är därför inte en mätning av okonditionerade modellvikter.
- Ett tidigare försök gav rätt record-transformationssvar men ogiltigförklarades av ett harnessfel i jämförelsen mellan rå SDK-konfiguration och loggsäkrad/saniterad representation. Originalet bevarades och ett nytt versionerat försök genomfördes. Felet ska inte tillskrivas Granite.
- I efterföljande, ej poängsatt filläsningsdiagnostik skrev Granite först en JSON-giltig Granite-formaterad begäran om rätt tool och rätt fil, men LM Studio-SDK:ns ordinarie `.act()`-väg dispatchade ingen strukturerad tool callback. Uppgiften blev därför inte klarad i originalgränssnittet. Ensam felorsak mellan modellformat och LM Studio/SDK-tolkning är inte fastställd.
- Ett separat försök med en strikt Granite-specifik text-till-tool-brygga exekverade exakt ett read-only-anrop och gav båda diskverifierade värdena. Detta visar en fungerande kompatibilitetsväg under ändrade harnessvillkor, inte att originalförsöket klarades.
- Begäransspecifik genereringscancel hade tidigare verifierats med slutligt `userStopped`. Under filläsningsdiagnostiken verifierades dessutom abort av den evaluatorägda läsprocessen: inga aktiva/slutförda tool-anrop kvarstod, ingen följdprediction startade och fixture-hashen förblev oförändrad. Detta bevis omfattar inte framtida skrivtools eller externa/delade MCP-processer.
- EVALEN gav högvärdiga plattformsfynd men avslöjade också evaluatorbrister: onödigt sen första beteendeslice, ett undvikbart baseline-jämförelsefel, avsaknad av en tidig tool-dispatch-kontraktprobe och ingen etablerad REPORT SUMMARY-process förrän efter körningen.

## Scope och klassificering av körningar

| Klass                          | Run-id                             | Roll i rapporten                                              |                            Räknas i 3/3? |
| ------------------------------ | ---------------------------------- | ------------------------------------------------------------- | ---------------------------------------: |
| Giltig IMSLE                   | `7153bed1a5334c3bad768d595f0c44bb` | Record transformation                                         |                                       Ja |
| Giltig IMSLE                   | `f6b43016a31c4d5488d34fe439cf0193` | Prioriterad routing                                           |                                       Ja |
| Giltig IMSLE                   | `a376c5bb799d429da845df7cbd9dedcd` | Evidensbunden jämförelse                                      | Ja, efter separat Codex-rubricgranskning |
| Ogiltigt föregångsförsök       | `f2e7deb5da81483ab48b96ed8081bd8b` | Korrekt modellsvar, ogiltig harnessverifiering                |                                      Nej |
| Transport completion-diagnos   | `3ed8f6150bf744498cad485bcfae3f46` | Naturligt `eosFound` och konfigurationsreadback               |                                      Nej |
| Transport cancellation-diagnos | `dfaf74b5fdef4558a0249928f6e1b335` | Verkligt `userStopped` inom stoppbudget                       |                                      Nej |
| Original filläsning            | `a2a1e80f70584ffc949b7e21b19afccb` | Tool-begäran i text, ingen tool-exekvering; uppgift ej klarad |                                      Nej |
| Format-hint-diagnos            | `26f2a37209754f3fbc6bd2e847f4a360` | Ändrad instruktion, malformed textanrop; uppgift ej klarad    |                                      Nej |
| Bryggad filläsning             | `9cad35130ffa4f1b8e4583473b8d0243` | Separat harness-anpassad framgång                             |                                      Nej |
| Tool-abortdiagnos              | `a16bcaa989474ae993789594dcc73fe2` | Verifierad abort av den specifika read-only-toolvägen         |                                      Nej |

Andra readiness-, identitets- och kontrollartefakter i evalhemmets run-mappar är stödbevis. De ska inte tolkas som fler agentuppgifter.

De många hexnamngivna mapparna uppstod därför att den första runnerdesignen allokerade en unik katalog för varje teknisk invocation—även readiness, identitetskontroll, normal completion, cancel, ogiltigt försök och tooldiagnostik—inte bara för de tre bedömda ERST. Det gav kollisionsfri och immutable råevidens men gjorde en övergripande EVAL onödigt fragmenterad och svårläst för människor. Det redundanta `frontier_evaluations/`-lagret har därför tagits bort; run-id:n behålls för befintlig spårbarhet och görs begripliga via tabellen ovan. Externa reviewers ombeds bedöma om framtida metadata som delas av hela EVALEN kan ägas en gång på evalnivå utan att revisionsbevis eller isolering försvagas.

## Faktiskt låsta IMSLE-villkor

### Modell och runtime

| Villkor             | Faktiskt observerat värde                                           | Evidensstatus                                                         |
| ------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Modellidentifierare | `granite-4.1-3b`                                                    | Verifierad SDK-bindning                                               |
| Modellfil           | `lmstudio-community/granite-4.1-3b-GGUF/granite-4.1-3b-Q4_K_M.gguf` | Path/storlek/kvantisering matchade lokal hashad fil                   |
| Kvantisering        | `Q4_K_M`, 4 bit                                                     | Verifierad readback                                                   |
| Modellfil SHA-256   | `87320650cc9c4b082ba36cd0a15cecf73c75389f34aadd854913b1bb576454fd`  | Verifierad lokal fil; faktiskt laddade bytes exponeras inte oberoende |
| Filstorlek          | 2 099 501 664 byte                                                  | Verifierad                                                            |
| LM Studio           | `0.4.24.0`                                                          | Fångad miljöversion                                                   |
| LM Studio CLI       | commit `ff50809`                                                    | Fångad miljöversion                                                   |
| JavaScript-SDK      | `1.5.0`                                                             | Låst dependency                                                       |
| Node.js             | `v24.11.1`                                                          | Fångad miljöversion                                                   |
| Context length      | 8192                                                                | Verifierad readback                                                   |
| GPU offload ratio   | 1                                                                   | Verifierad readback                                                   |
| Flash attention     | `true`                                                              | Verifierad readback                                                   |
| CPU thread pool     | 6                                                                   | Verifierad readback                                                   |
| Parallel sessions   | 1                                                                   | Verifierad readback                                                   |

### Input, konditionering och generation

- Transport för avbrytbar evalgenerering: officiell LM Studio JavaScript-SDK 1.5.0 med projektets godkända, versionsbegränsade tokenanpassning. Native REST behöll modellinventering och generell observability.
- Fresh `Chat.empty()`/`append()` per oberoende ERST.
- Exakt en aktuell user-instruktion.
- Projektägd System Prompt: tom.
- Ingen 0-WORKER-rollfil, skill, tool, dokumentinjektion, projektkontext, dold historik eller tyst retry.
- `temperature: 0`, `maxPredictedTokens: 1024`, inga tools.
- Effektiv Jinja-template: 6 099 tecken, SHA-256 `fed2756d2d24e127b951dcf139d0b03ab7db8ef23a456128ebc9c2db4901d476`.
- Template/defaultkonditionering var aktiv även utan projektägd System Prompt. Begreppet “zero-context” får därför endast betyda minimal explicit projektkonditionering, inte frånvaro av runtime-template.
- Seed och alla eventuellt ärvda samplingvärden som inte exponerades i relevant SDK-readback ska betraktas som okända, inte som verifierat avstängda.
- Före varje giltig ERST observerades modellen som idle, `queued: 0`, `parallel: 1`.

## Primärt resultat: Round 1 IMSLE

### ERST 1 — record transformation

**Run-id:** `7153bed1a5334c3bad768d595f0c44bb`

**Exakt instruktion:**

> Transform this record: {"name":"Mira","value":17,"note":"warehouse C"}. Return only a JSON object containing exactly the keys name and value. Preserve the name and increase the integer value by one. Do not include the note or any other field. Do not use tools.

**Rått slutsvar:**

```json
{ "name": "Mira", "value": 18 }
```

**Ursprunglig bedömning:** PASS. Samtliga innehålls-, typ-, ordnings- och scopekontroller matchade.

**Verifierad nytta:** Modellen demonstrerade exakt strukturerad transformation, borttagning av förbjudet fält och korrekt enkel aritmetik utan extra text. Detta är relevant för framtida smala WORKER-transformationer, men bevisar inte fil-I/O, längre kedjor eller stabilitet över variationer.

**Runtime:** `eosFound`; 11 genererade token; 0,214517 s till första token; 0,360712 s totalt.

### ERST 2 — prioriterad routing

**Run-id:** `f6b43016a31c4d5488d34fe439cf0193`

**Exakt instruktion:**

> Route these records using the first matching rule, in this priority order: (1) if urgent is true, route to express; (2) otherwise, if weight is at least 10, route to freight; (3) otherwise, route to standard. Records in input order: [{"id":"A","urgent":true,"weight":14},{"id":"B","urgent":false,"weight":10},{"id":"C","urgent":false,"weight":3}]. Return only a JSON array with one object per record in the same order, each containing exactly id and destination. Do not use tools.

**Rått slutsvar:**

```json
[
  { "id": "A", "destination": "express" },
  { "id": "B", "destination": "freight" },
  { "id": "C", "destination": "standard" }
]
```

**Ursprunglig bedömning:** PASS. Samtliga innehålls-, typ-, ordnings- och scopekontroller matchade.

**Verifierad nytta:** Modellen följde first-match-prioritet, hanterade gränsvärdet `weight == 10`, bevarade inputordning och levererade exakt schema. Detta är relevant för regelstyrd triage/routing, men inte ett bevis på komplex planering eller felhantering.

**Runtime:** `eosFound`; 58 genererade token; 0,357381 s till första token; 0,788158 s totalt.

### ERST 3 — evidensbunden jämförelse

**Run-id:** `a376c5bb799d429da845df7cbd9dedcd`

**Exakt instruktion:**

> Use only these facts: Service Cedar costs 12 credits per job. Service Maple costs 9 credits per job. No completion times are provided for either service. Which service finishes a job faster? Briefly explain what the facts do and do not establish, and ask for the missing information needed to answer the speed question. Do not assume that price predicts speed. Do not use tools.

**Rått slutsvar:**

> The given facts tell us the cost associated with each service—Service Cedar costs 12 credits per job, and Service Maple costs 9 credits per job. However, these facts do not provide any information about the time or efficiency required to complete a job for either service.
>
> What the facts establish:
>
> 1. The monetary value (in credits) of completing a job for each service.
> 2. There is no data on how long it takes to finish a job for either Service Cedar or Service Maple.
>
> What the facts do not establish:
>
> 1. The speed at which either service completes a job, as completion times are not provided.
> 2. Any relationship between cost and time efficiency; we cannot assume that a higher or lower credit cost implies faster or slower completion.
>
> To determine which service finishes a job faster, we need additional information such as the average or typical completion time for each service (e.g., how many credits per hour or similar metrics) or any qualitative data on operational efficiency. Without this missing information, we cannot conclude which service is faster based solely on cost.

**Låsta rubric-kriterier och ursprunglig bedömning:** PASS 3/3 efter separat Codex-granskning med hashbunden `assessment.json`.

1. Modellen valde inte en snabbare service och hittade inte på tider eller toolaktivitet.
2. Modellen sade uttryckligen att underlaget inte räckte för hastighetsjämförelse och behandlade inte pris som hastighetsbevis.
3. Modellen efterfrågade jämförbara completion times för båda tjänsterna.

**Väsentliga kvalitetsbrister som inte ändrar originalbedömningen:** Svaret var inte kort trots “Briefly”. Exemplet “credits per hour” är ett dåligt exempel på ren hastighetsmätning och riskerar att återblanda kostnad med tid. Dessa brister var inte låsta underkännandekriterier och får därför inte skapa ett retroaktivt FAIL.

**Verifierad nytta:** Modellen visade grundning, explicit osäkerhet och korrekt begäran om saknad evidens—centralt för en WORKER som inte ska hitta på fakta. En enda handbedömd träff bevisar dock inte kalibrerad tillförlitlighet.

**Runtime:** `eosFound`; 215 genererade token; 0,276700 s till första token; 1,856918 s totalt.

## Ogiltigt försök och evaluatorägd korrigering

`f2e7deb5da81483ab48b96ed8081bd8b` gav samma korrekta record-transformationssvar som den senare giltiga körningen. Försöket markerades ändå `invalid` därför att harnessens baselineverifiering jämförde rå SDK-konfiguration med en redigerad/loggsäkrad representation på ett sätt som gjorde villkoren ogiltiga. Det var en evaluator-/harnessbrist, inte ett belagt modellfel.

Originalevidensen bevarades. Korrigeringen gjordes hos rätt ägare och följdes av den nya giltiga körningen `7153bed1a5334c3bad768d595f0c44bb`. Det korrekta svaret i den ogiltiga körningen får redovisas som observerat modellbeteende men räknas inte i 3/3.

## Efterföljande kompatibilitetsdiagnostik — inte Round 1-score

### Originalets ordinarie toolväg

**Run-id:** `a2a1e80f70584ffc949b7e21b19afccb`

Instruktionen bad modellen läsa `project/config/service.json`, återge `queue_name` och `retry_limit`, inte gissa och inte modifiera filen. Modellen genererade:

```text
<tool_call>{"name": "read_workspace_text", "arguments": {"path": "project/config/service.json"}}
</tool_call>
```

Modellens text angav rätt tool och rätt sökväg. LM Studio-SDK `.act()` rapporterade ändå vanlig text, `eosFound`, noll strukturerade tool callbacks och `completed: 0`. Filen lästes inte och de efterfrågade värdena levererades inte.

- **Modellobservation:** korrekt JSON-innehåll i ett Granite-liknande text-envelope.
- **Harnessobservation:** ingen strukturerad dispatch eller tool-exekvering i den testade LM Studio 0.4.24.0 + SDK 1.5.0 + template-kombinationen.
- **Uppgiftsutfall:** inte klarad.
- **Orsaksstatus:** oavgjord mellan modellens exakta formattering och LM Studio/SDK:s tolkning; resultatet bevisar inte ensam modellinkapacitet eller ett generellt LM Studio-fel.

### Format-hint-försöket

**Run-id:** `26f2a37209754f3fbc6bd2e847f4a360`

En separat instruktion lade till explicit formatvägledning. Modellen svarade med ett malformed textanrop:

```text
{"name": "read_workspace_text", "arguments": {"path": "project/config/service.json"}}}
```

Ingen tool kördes och uppgiften klarades inte. Detta visar att en ytlig format-hint inte var en verifierad förbättring; försöket ersätter inte originalet och bör granskas som en ändrad instruktion, inte en ren replikation.

### Strikt Granite-specifik brygga

**Run-id:** `9cad35130ffa4f1b8e4583473b8d0243`

En explicit opt-in-brygga accepterade endast ett exakt giltigt IBM/Granite-envelope med rätt toolnamn och argument och gjorde ingen reparerande gissning. Bryggan dispatchade ett read-only-anrop; modellen fick toolresultatet och svarade:

> The queue_name is render-622d1295 and the retry_limit is 3.

Diskfacit matchade, tool kördes exakt en gång och fixture-hashen var oförändrad. Uppgiften klarades under detta **separata harness-anpassade kontrakt**. Resultatet är högvärdig kompatibilitetsevidens men inte PASS för originalets ordinarie `.act()`-gränssnitt.

### Verifierat tool-avbrott

**Run-id:** `a16bcaa989474ae993789594dcc73fe2`

Efter observerat `tool_started` levererades stoppsignal. Evidensen registrerade `cancel_sent`, `tool_aborted`, `active: 0`, `completed: 0`, oförändrad fixture-hash och ingen efterföljande prediction inom femsekundersbudgeten. Efter controller-exit var Granite idle med `queued: 0`, och ingen Python-controller med run-id återstod.

Beviset gäller just evaluatorägd read-only-process och dess Windows Job Object. Det bevisar inte rollback, skrivtool-säkerhet eller kontroll över externa/delade MCP-servrar.

## Fynd per ansvarslager

### A. Modellspecifika fynd — Granite under testade villkor

1. Granite följde tre smala, explicita engelska instruktioner korrekt utan projektägd rollkontext.
2. Modellen producerade exakt JSON i två strukturella uppgifter och respekterade både fältbegränsning och prioriteringsordning.
3. Modellen avstod korrekt från en ogrundad slutsats i den kvalitativa uppgiften, men var onödigt lång och gav ett tveksamt mätningsexempel.
4. I originalets filläsning genererade modellen semantiskt rätt toolnamn och filsökväg i ett text-envelope. I ett separat format-hint-försök blev output malformed. Detta visar formatkänslighet/variation i de testade försöken, men inte ensamorsaken till utebliven native dispatch.
5. Efter en faktisk toolresponse via den strikta bryggan integrerade modellen båda filvärdena korrekt i ett kort slutsvar.
6. Ingen svensk instruktion, skrivmutation, multi-file-uppgift, längre agentloop, felåterhämtning, skillanvändning, produktionsrollkontext eller bred tillförlitlighet är visad.

### B. LM Studio-/SDK-/harnessfynd

1. Auth, vald modellbindning, naturlig completion och begäransspecifik cancel fungerade i den testade konfigurationen.
2. Slutligt `userStopped` gav verkligt genereringsstoppbevis; timeout eller klientexit användes inte ensamt som bevis.
3. Den ordinarie `.act()`-vägen exekverade inte Granites text-envelope trots exponerat toolschema. Den testade kombinationens tool-dispatch-kontrakt var alltså inte tillräckligt för första read-uppgiften.
4. En strikt modellfamiljsspecifik parser/brygga fungerade för ett exakt envelope och gav en komplett två-runders toolkedja. Den är en explicit kompatibilitetslösning, inte bevis på generell native tool-use.
5. Ägda Windows-toolprocesser kunde stoppas och verifieras. Externa processer och framtida toolklasser kräver egna bevis.
6. Evaluation-oberoende LM Studio-events ligger separat under `LM-Studio_logs/`; de kopieras inte till evalytan.

### C. Uppgifts- och 0-WORKER-fynd

1. De tre verktygsfria uppgifterna klarades och är relevanta som basala byggblock: exakt dataomformning, prioriterad regelrouting och evidensbunden osäkerhet.
2. Originalets filläsningsuppgift klarades inte eftersom ingen fil lästes och inga värden levererades, oavsett att modellens textbegäran såg rimlig ut.
3. Samma sakuppgift klarades under ett separat strikt bryggkontrakt. Skillnaden är beslutsvärdefull för framtida harnessdesign men får inte döljas som en enda blandad PASS/FAIL.
4. Ingen faktisk skrivuppgift har genomförts. Granite är därför inte ännu verifierad som en 0-WORKER som kan utföra konkret read/write-arbete.
5. Resultatet räcker för att motivera fortsatt kontrollerad audition, men inte för produktionsgodkännande eller en generell slutsats om 3B-modellens rollkapacitet.

### D. Codex evaluatorprocess — vad som fungerade

1. Modell-, harness- och uppgiftsutfall separerades när toolproblemet upptäcktes.
2. Ett korrekt men metodiskt ogiltigt svar räknades inte som PASS; originalevidensen bevarades och rätt ägare korrigerades.
3. Kvalitativa svagheter noterades utan att nya efterhandskriterier uppfanns.
4. Toolresultat verifierades mot disk och oförändrad fixture-hash, inte mot modellens självrapport.
5. Genererings- och toolavbrott krävde slutliga kvitton, inte bara timeout.
6. Assisterad/harness-anpassad diagnostik hölls separat från originalbaseline.

### E. Codex evaluatorprocess — tydliga förbättringsbehov

1. **För sen Walking Skeleton:** Förberedande arkitektur, logging och gates tog oproportionerligt stor plats innan den första lilla beteendeproben. Team Master behövde uttryckligen stoppa uppkomsten av nya blockerare och påminna om mandatet att ladda modellen och starta EVALEN.
2. **Undvikbart harnessfel:** Den första riktiga uppgiften ogiltigförklarades av Codex egen felaktiga jämförelse mellan rå SDK-konfiguration och loggsäkrad representation. Ett riktat test av just canonicalisering/jämförelse före livekörning borde ha fångat detta.
3. **Toolkontraktet verifierades för sent:** `trainedForToolUse`, template och registrerat schema behandlades inte som tillräckligt bevis i slutsatsen, men den enklaste faktiska model-output → parser → callback-proben borde ha körts före en WORKER-filläsning.
4. **För mycket processbevis relativt kandidatbevis:** Avbrott, auth, observability och kontrollsystem blev väl verifierade, men den fullständiga bedömda modellrundan stannade vid tre mycket små, verktygsfria uppgifter.
5. **Ensam kvalitativ bedömare:** ERST 3 bedömdes av Codex. Hashbindning och rubric förbättrar spårbarheten men eliminerar inte evaluatorbias eller feltolkning.
6. **Otillräcklig replikeringsinformation:** `temperature: 0` minskar inte all variation, och seed var inte verifierad. Tre olika uppgifter med en körning vardera visar uppgiftsutfall, inte stabilitet.
7. **Ingen förhandslåst rapportsyntes:** REPORT SUMMARY-processen infördes först efter körningen. Framtida eval-id, rapportägare, scopeetiketter och reviewerunderlag bör vara kända innan första ERST utan att påverka kandidatens task.
8. **Relokeringsskuld i rå evidens:** EVAL-artefakterna flyttades efter körningen från den gamla projektytan. Rå JSON har av revisionsskäl inte skrivits om och kan därför innehålla historiska relativa paths med prefixet `LM-Studio_logs/frontier_evaluations/`. Aktuell fysisk motsvarighet är respektive run-mapp direkt i detta evalhem; externa reviewers måste använda evidensindexet nedan.
9. **Runnerrelokering återstår:** Efter projektflytten använder fyra aktiva Pythonfiler fortfarande en för hög `Path.parents[...]`-nivå och tre destinationsägare pekar fortfarande mot `LM-Studio_logs/frontier_evaluations`. Nästa EVAL skulle därför kunna läsa fel projektrot eller återskapa det borttagna wrapperlagret. Detta påverkar inte den redan bevarade EVAL 1-evidensen, men blockerar nästa evalkörning tills runner, CLI-bindning till `<eval-id>`, tester och README har migrerats tillsammans.

## Osäkerheter som ska förbli öppna

- Om utebliven `.act()`-dispatch primärt orsakades av exakt modellformat, LM Studio-template/parser, SDK-version eller samspelet mellan dessa.
- Om den Granite-specifika bryggan fungerar robust över andra tools, argumentformer, flera anrop, felresultat och längre toolkedjor.
- Hur Granite presterar med den avsedda produktionsnära 0-WORKER-rollkontexten jämfört med minimal explicit konditionering.
- Hur stabila resultaten är över oberoende körningar och verifierbara sampling-seeds.
- Om svenska instruktioner är tillräckligt tillförlitliga för Team Masters faktiska användning.
- Om säkert, korrekt och avbrytbart skrivarbete kan genomföras utan regression i de redan visade styrkorna.
- Hur stor del av total evalkostnad och latens som ligger i modell, server, harness, tool och evaluatorarbete var för sig.

## Provisoriska förbättringshypoteser som reviewers ska utmana

Dessa är inte redan beslutade krav. De är kandidater för extern bedömning och ska endast införas om deras informationsvärde överstiger kostnad och komplexitet.

1. **Tool-kontraktmatris före agenttask:** Separera och verifiera fyra länkar: modellens tool-intention, syntaktiskt envelope, harness-parser/callback, faktisk tool-effekt och modellens integration av toolresultatet.
2. **Tidigare vertikal slice:** Kör den minsta säkra riktiga uppgiften så snart modellidentitet, auth och avbrott för den uppgiftens risk är verifierade; bygg bara stöd som nästa slice faktiskt behöver.
3. **Produktionsnära kontextdelta:** Efter ren minimal screening kan samma nya, icke-memoriserade uppgiftstyp testas med låst produktionsrollkontext för att mäta faktisk integrationsnytta, utan att kalla den ena varianten “mer sann”.
4. **Oberoende kvalitativ review:** Låt minst en extern reviewer blindgranska hashbundet råsvar mot förhandslåst rubric innan en kvalitativ gate får hög betydelse.
5. **Stabilitetsprobe endast där beslut kräver det:** Använd oberoende varianter och verifierbara seeds när ett konfigurations- eller kandidatbeslut annars är känsligt; upprepa inte syntetiska uppgifter slentrianmässigt.
6. **Nästa verklighetsnära slice:** Prioritera en bounded, disponibel och verifierbar read→transform→write-uppgift efter att skrivtoolens scope, after-effects och stoppkontrakt har bevisats.
7. **Förhandsregistrerat attribueringsschema:** Kräv per avvikelse `observation`, `task outcome`, `known owner`, `open cause`, `next discriminating test` så att oavgjorda orsaker inte blir modellomdömen.

## Evidensindex

### Primär Round 1-evidens

- [Baseline source review](b67327cef4a84c56ae5a9931f4d155ee/baseline_source_review.json) — gemensamma modell-, load-, sampling-, template-, versions- och idle-villkor.
- [Model identity review](b67327cef4a84c56ae5a9931f4d155ee/model_identity_review.json) — GGUF-identitet och SHA-256.
- [Environment versions](b67327cef4a84c56ae5a9931f4d155ee/environment_versions.json) — LM Studio, CLI, Node och SDK.
- [ERST 1 evidence](7153bed1a5334c3bad768d595f0c44bb/evidence.json) — record transformation.
- [ERST 2 evidence](f6b43016a31c4d5488d34fe439cf0193/evidence.json) — priority routing.
- [ERST 3 evidence](a376c5bb799d429da845df7cbd9dedcd/evidence.json) och [ERST 3 assessment](a376c5bb799d429da845df7cbd9dedcd/assessment.json) — evidensbunden jämförelse.
- [Ogiltigt föregångsförsök](f2e7deb5da81483ab48b96ed8081bd8b/evidence.json) — korrekt output men ogiltigt harnessutfall.

### Kontroll- och kompatibilitetsevidens

- [Normal completion-diagnos](3ed8f6150bf744498cad485bcfae3f46/evidence.json) och [cancel-diagnos](dfaf74b5fdef4558a0249928f6e1b335/evidence.json).
- [Ordinarie filläsning](a2a1e80f70584ffc949b7e21b19afccb/evidence.json) och [assessment](a2a1e80f70584ffc949b7e21b19afccb/assessment.json).
- [Format-hint-försök](26f2a37209754f3fbc6bd2e847f4a360/evidence.json) och [assessment](26f2a37209754f3fbc6bd2e847f4a360/assessment.json).
- [Strikt bryggad filläsning](9cad35130ffa4f1b8e4583473b8d0243/evidence.json) och [assessment](9cad35130ffa4f1b8e4583473b8d0243/assessment.json).
- [Tool-abortdiagnos](a16bcaa989474ae993789594dcc73fe2/evidence.json), [stoppbegäran](a16bcaa989474ae993789594dcc73fe2/stop_request.json) och [assessment](a16bcaa989474ae993789594dcc73fe2/assessment.json).
- [Korrelaterad lifecycle-capture](../../LM-Studio_logs/model_lifecycle_events/20260913_212122086_ff2537ea-de49-48a0-999b-e195b43bec23.json) — generell LM Studio-evidens, refererad men inte kopierad.

### Styrande och tolkande dokument

- [Modellneutral Frontier-as-Evaluator-design](<../[EVAL] - [ARCH.] - [Frontier-As-Evaluator] - [Design].md>).
- [0-WORKER eval README](../../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/README.md).
- [Granite runtime-baseline](<../../LOCAL_AGENTS/AGENT-0-WORKER/AG-0-MODEL-Granite_4.1-3B/[MODEL-CONFIG-BASELINE] - Granite_4.1-3B.md>).
- [Granite modellanteckningar](<../../LOCAL_AGENTS/AGENT-0-WORKER/AG-0-MODEL-Granite_4.1-3B/[MODEL-NOTES] - Granite_4.1-3B.md>).
- [LM Studio ↔ Codex transport README](../../LM-Studio_connections/LM-Studio_for_codex/README.md).
- [Frysta projektbeslut](<../../docs/docs_plan/[PLAN] - [PROJECT DIRECTION & PURPOSE] - [FRYSTA BESLUT].md>).
- [Codex roadmapstatus](<../../docs/docs_plan/[PLAN] - [1] - [CODEX] - [TO LM STUDIO SETUP] - [ROADMAP].md>).

## EXTERNAL-REVIEW-QUESTIONS-EVAL-RESULT [ERQER]

### ERQER 1 — Vad kunde Frontier-evaluatorn Codex gjort mycket bättre eller annorlunda?

Bedöm både evaldesign, implementationsordning, modell-/harnessattribuering, val av uppgifter, stoppbeslut, grading, evidensnivå, tid/komplexitetskostnad och hur Codex reagerade på det första ogiltiga försöket och tool-dispatchglappet. Identifiera särskilt sådant som gav låg informationsavkastning, skapade onödiga blockers eller kunde ha upptäckts billigare före live-EVAL.

### ERQER 2 — Hur kan framtida utvärderade agenter ge mer lönsamma, användbara och försvarbara resultat eller insikter på modellspecifik och modellneutral nivå?

Separera förslag som mäter kandidatens egna styrkor/svagheter från förslag som förbättrar det gemensamma 0-WORKER-kontraktet, toolgränssnittet, kontextleveransen, fixtures, graders eller observationskedjan. Förklara hur vi kan få verklighetsnära beslutsvärde utan att kompensera bort modellbrister, läcka facit eller felaktigt belasta modellen för harnessfel.

### ERQER 3 — Hur kan alla framtida EVALS förbättras icke-kosmetiskt och icke-trivialt?

Föreslå endast ändringar som sannolikt förbättrar validitet, attribuerbarhet, reproducerbarhet, säkerhet, praktisk 0-WORKER-relevans, informationsvärde per kostnad eller jämförbarhet mellan kandidater. Prioritera det minsta effektiva protokollet framför fler dokument, fler fält eller fler prober utan tydligt beslutsvärde.

### ERQER 4 — Vilka övriga Mycket Höga eller Höga ROI-insikter saknas?

Identifiera relevanta frågor som inte täcks ovan men som Codex som Frontier-evaluator bör adressera eller implementera före eller under nästa EVAL. Ta särskilt ställning till om rapporten missar en central kausal skiljetest, ett verklighetsnära arbetsflöde, en riskgräns, en jämförelsebas eller en kostnads-/latenssignal som skulle kunna ändra valet av framtida lokal 0-WORKER.

## Önskat svarskontrakt för Grok och Claude

Ge en prioriterad lista, inte en allmän essä. För varje materiellt förslag:

1. **Prioritet:** Mycket Hög eller Hög.
2. **Konkreta förändringen:** vad som ska ändras, tas bort eller införas.
3. **Evidensankare:** vilket run-id, fynd eller dokument som motiverar ändringen.
4. **Rätt ägare/lager:** modellkonfiguration, modellneutral evaldesign, LM Studio/SDK/harness, tool/runtime, grader eller evaluatorprocess.
5. **Förväntad nytta:** vilket beslut eller vilken risk som blir bättre.
6. **Tradeoff/kostnad:** extra komplexitet, tokens, runtime, underhåll eller risk för överanpassning.
7. **Minsta verifiering:** den billigaste men tillräckliga testen som visar att förbättringen fungerar utan regression.
8. **Resultatpåverkan:** om förslaget ändrar tolkningen av EVAL 1 eller endast framtida EVALS.

Markera uttryckligen när rapportens evidens inte räcker för en slutsats. Utmana Codex antaganden; bekräftelse utan evidens eller kosmetiska dokumentförslag är inte målet.

## Revisionshistorik

| Version | Tid                           | Ändring                                                                                                                |
| ------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 1.0     | 2026-09-13 \| 23:29:10 +02:00 | Första sammanställningen efter flytt till `model_evaluations/EVAL_1_2026-09-13-204437/`; rå evidens lämnad oförändrad. |

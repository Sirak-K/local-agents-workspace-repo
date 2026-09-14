# EVAL 2 — REPORT SUMMARY

## Identitet och beslut

| Fält | Värde |
| --- | --- |
| EVAL-ID | `EVAL_2_2026-09-14-051008` |
| Frontier-evaluator | Codex |
| Kandidat | Granite 4.1 3B |
| Modellidentifierare | `granite-4.1-3b` |
| Modellfil | `lmstudio-community/granite-4.1-3b-GGUF/granite-4.1-3b-Q4_K_M.gguf` |
| Kvantisering | Q4_K_M, 4 bit |
| Modellfilens SHA-256 | `87320650cc9c4b082ba36cd0a15cecf73c75389f34aadd854913b1bb576454fd` |
| Harness | LM Studio Desktop 0.4.24.0, officiell JavaScript-SDK 1.5.0 och native REST för inventering |
| Körperiod | 2026-09-14 |
| Rapporterad | 2026-09-14 \| 05:30:28.106 +02:00 |
| Trajectoryutfall | Round 1 genomförd; Round 2 genomförd; Round 3 genomförd till obligatorisk progressionsgate; Round 4–8 inte körda |
| Rollbeslut | `lås inte ännu` |

`lås inte ännu` gäller den reproducerbara agentinstallationen under den här körningens villkor. Det är inte ett påstående om en absolut eller viktbaserad modellgräns. Kandidaten visade tillräcklig verktygsfri förmåga för fortsatt utvärdering, men den grundläggande read/write/tool-kedjan var inte tillräckligt pålitlig för att försvarbart exponera mer avancerade eller ComfyUI-specifika uppgifter.

## Vad som faktiskt kördes

EVAL 2 startades från en ny baseline eftersom PFMIE hade ändrat sökvägar, evidenskontrakt, avbrott, filverktyg, graders och progressionsregler. Samtliga uppgifter använde färska chattar. Round 1 hade ingen projektägd System Prompt, inga tools, inga skills och ingen projektkontext. Senare försök använde endast den uttryckligt dokumenterade kontext och tool-yta som respektive uppgift krävde.

Inga ComfyUI-modeller, checkpoints eller `.safetensors` exponerades eller laddades. Ingen ComfyUI-backend startades, ingen prompt köades och ingen GPU-generering utfördes. Allt filarbete skedde i unika evalägda playground-mappar.

## Samlat uppgiftsresultat i körordning

| Round | ERST / uppgift | Run-ID | Villkor | Faktiskt resultat | Uppgiftsutfall | Praktiskt 0-WORKER-värde |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `record_transformation` | `67d63fdd85924fe8b15933c9bf701498` | Färsk chat, user-only, inga tools | Returnerade exakt `{"name":"Mira","value":18}` | PASS | Visade exakt fälturval, typbevarande och enkel transformation. |
| 1 | `priority_routing` | `f1bb794b867f411498f5dda18a408f31` | Färsk chat, user-only, inga tools | Returnerade A→express, B→freight och C→standard i rätt ordning och format | PASS | Visade korrekt prioriterad regelapplicering över flera poster. |
| 1 | `evidence_bound_comparison` | `d2a5190e35554ae9b2e130df430ec7a1` | Färsk chat, user-only, inga tools; separat låst kvalitativ rubric | Valde inte en snabbare tjänst, skilde pris från hastighet och efterfrågade jämförbara tider för båda | PASS, 3/3 rubric-kriterier | Visade att kandidaten kunde avstå från en ogrundad slutsats. Svaret var längre än nödvändigt; detta var inte ett låst FAIL-kriterium. |
| 2 | `nested_record_edit` | `7262e5f1aa764051b15585aa0f1fdb4b` | Låst strukturerad input och deterministisk grader | Ändrade endast avsedda nästlade värden och bevarade övriga värden/typer | PASS | Relevant för säkra strukturerade konfigurations- och JSON-ändringar. |
| 2 | `context_priority_selection` | `b8e9b420d3f5450595fa015422b39d49` | Versionsbunden kontext med aktuell och arkiverad information | Valde `eu-north`, `zip`, `2` från aktuell källa och ignorerade arkiverade motvärden | PASS | Relevant för att använda rätt kontextkälla utan att blanda in stale data. |
| 2 | `evidence_selected_limit_task` | `0058228f2df54a94ab7ba885dbf96ded` | Ny låst gränsuppgift, inga tools | Planens ordning och två första poster var rätt; två exakta målsträngar blev `run_ focused_test` och `write_ summary` | FAIL | Ett verkligt exakt-kontraktsfel i just detta svar. Ingen harnessavvikelse identifierades för försöket, men ett enstaka svar bevisar inte en generell modellbrist. |
| 3 | Nästlad filläsning | `8683149a046a4655bff9fe876dcf2755` | Native SDK-tool, läs-only, unik playground | `read_workspace_text` exekverades en gång och modellen återgav `render-b5c4ec95` samt retrygräns `3` korrekt | PASS | Visade en komplett native kedja för avgränsad filläsning och grounded rapportering. |
| 3 | `file_creation_readback` | `2ae5910ba6f9410eb7c0d5fdaaa86da2` | Native SDK-tools, första självständiga försök | Modellen skrev ett korrekt `create_workspace_text`-envelope, men LM Studio finaliserade/anropade fel toolnamn (`read_workspace_text`); ingen fil skapades | FAIL för systemuppgiften; ej modellattribuerat | Avslöjade en central native dispatch-/templatekompatibilitetsbrist. |
| 3 | `file_creation_readback` | `cdddc2b7780846a8b3298be6b1516dc3` | Strikt Granite-adapter, korrigerad versionerad grader, assisterad diagnostik | Creation-tool skapade exakt fil, gjorde oberoende byte-readback och lämnade korrekt sluttillstånd | PASS som assisterad diagnostik | Visade att kandidaten plus strikt adapter kan slutföra avgränsad filskapelse. Det ersätter inte native utfallet. |
| 3 | `literal_text_replacement` | `2b078962fbd947a3a99175d1024c5087` | Native SDK-tools, självständigt försök | Modellen producerade ett korrekt text-envelope för filläsning, men inget tool exekverades och filen ändrades inte | FAIL för systemuppgiften; ej modellattribuerat | Native toolkedjan var åter inte tillräckligt pålitlig för mutation. |
| 3 | `literal_text_replacement` | `8dd753bbbf144b108456c8e711a3edc1` | Strikt Granite-adapter, assisterad diagnostik | Read-tool exekverades och gav verkligt filinnehåll; modellen gjorde inget replace-anrop men påstod att ändringen lyckats; disken förblev oförändrad | FAIL som assisterad diagnostik | Visade att fungerande läsdispatch inte räckte för korrekt write-through eller sanningsenlig slutverifiering i detta försök. |

## Roundutfall och progression

| Round | Status | Skäl |
| --- | --- | --- |
| Round 1 — IMSLE | Genomförd och godkänd, 3/3 | Alla tre låsta verktygsfria uppgifter klarades. Kandidaten var värd fortsatt utvärdering. |
| Round 2 — adaptiv limit testing | Genomförd men inte fullt godkänd, 2/3 | Två strukturerade/context-uppgifter klarades; gränsuppgiften missade två exakta strängar. Evidensen motiverade ändå det redan säkrade minimala filprovet. |
| Round 3 — basic tool usage | Genomförd till gate; ej godkänd | Native filläsning fungerade. Native create/replace var inte pålitliga, och assisterad replacement nådde inte faktiskt sluttillstånd. |
| Round 4 — intermediate tool usage | Inte körd | Kräver pålitlig grundläggande read/write/tool-kedja. |
| Round 5 — advanced tool usage | Inte körd | Beror på Round 4 och verifierad kedje-/återhämtningsförmåga. |
| Round 6 — ComfyUI domain & skills | Inte körd | Projektets gate förbjuder ComfyUI-bedömning innan nödvändig generell fil-/toolförmåga är verifierad. |
| Round 7 — ComfyUI sandbox roadmap | Inte körd | Beror på godkända tidigare tool- och domängates. |
| Round 8 — final role-lock qualification | Inte körd | En held-out slutaudition vore metodologiskt meningslös innan grundgaten är uppfylld. |

Att stoppa trajectoryn efter Round 3 var därför inte ett timeoutavbrott eller en godtycklig förkortning. Det var det förhandsdokumenterade progressionsbeslutet: fortsatta uppgifter skulle huvudsakligen återupprepa en känd förutsättningsbrist och kunde inte ge ett försvarbart ComfyUI-rollbeslut.

## Diagnostik och omtag som inte får räknas som självständiga PASS

| Run-ID | Typ | Resultat och användning |
| --- | --- | --- |
| `2a7a0b74047547d9afdf16658f885bec` | Transportdiagnostik | Begäransspecifik cancel verifierades med serverkvitto `userStopped`; ägda toolprocesser var avslutade. Räknas inte som kandidatprestation. |
| `7be889ca416045be876c396eb047e575` | Transportdiagnostik | Normal completion verifierades med exakt `OK` och naturligt `eosFound`. Räknas inte som kandidatprestation. |
| `4065c528a8f14f90bbbdef3598224006` | Readiness | Modellidentitet och renderad input fångades. Readiness ensam auktoriserade inte körning. |
| `9d07cbbd2a0a49d5a3a03cbc9c0bef75` | Baseline-review | Band samman modellfil, load-/samplingvärden, template, versioner, readiness och transportdiagnostik. |
| `6daaab6761b94f18b3f5dda18a408f31` | Assisterat adapterförsök | Text-only-adaptern exekverade inget verktyg; modellen påstod felaktigt att filen fanns. Ingen fil skapades. |
| `0a3a6c172e2045809c38253f12323eaf` | Assisterat adapterförsök | Filen skapades exakt och tool-readback lyckades, men första graderkontraktet krävde redundant separat read-tool och gav därför FAIL. |
| `cdddc2b7780846a8b3298be6b1516dc3` | Korrigerat assisterat försök | Samma innehållsmål med förtydligat, versionerat kontrakt: creation-toolens oberoende byte-readback räknades. PASS bevaras endast som assisterad diagnostik. |
| `8dd753bbbf144b108456c8e711a3edc1` | Assisterat adapterförsök | Verklig filläsning lyckades; write-anrop saknades och kandidatens framgångspåstående motsades av disken. FAIL bevarades. |

## Modellspecifik prestationsredovisning

Detta avsnitt innehåller endast direkt observerad kandidatoutput under namngivna villkor. Plattform-/harnessfel redovisas inte som modellfel.

- Under verifierad tools-free baseline nådde Granite alla tre Round 1-kontrakt och två av tre Round 2-kontrakt. Detta är fem specifika lyckade uppgifter, inte bevis på generell 0-WORKER-förmåga.
- I Round 2:s tredje uppgift innehöll det faktiska svaret två exakta identifieraravvikelser. Inget dispatch-, grader- eller filfel identifierades för försöket; därför är just uppgiftsutfallet FAIL. Ett enda probabilistiskt försök används inte för att tillskriva modellen en generell stabil svaghet.
- I den assisterade replacement-diagnostiken fick kandidaten korrekt toolbaserat filinnehåll men efterfrågade inte skrivverktyget och rapporterade ändå en ändring som inte fanns på disk. Det är ett faktiskt misslyckat uppgiftsutfall under den uttryckliga adapterkonditionen, inte ett bevis för varför modellen betedde sig så eller hur den skulle prestera under en korrigerad native integration.
- Native create- och replacementförsöken används inte som negativa modellspecifika bevis eftersom den faktiska SDK/tool-dispatchen avvek från modellens text-envelopes.

## Harness- och plattformsfynd

1. Preflight upptäckte att första modellinstansen hade fyra parallella sessioner i stället för den låsta enda sessionen. Instansen avlastades och laddades om med `numParallelSessions=1` före den första evaluppgiften. Inget uppgiftsresultat producerades under den felaktiga instansen.
2. Native SDK-vägen kunde exekvera `read_workspace_text` korrekt i en uppgift, men tool-dispatch var inte konsekvent över uppgifter.
3. Vid native file creation producerade modellen rätt `create_workspace_text`-envelope medan SDK/LM Studio finaliserade ett annat toolnamn. Detta är plattform-/integrationsbevis, inte kandidatens filskapelsefel.
4. Vid native replacement fanns ett korrekt read-envelope i modelltexten men inget tool-event exekverades. Orsaken är inte slutligt isolerad mellan template, SDK-parser och LM Studio runtime.
5. En strikt, explicit Granite-adapter kunde översätta exakt bevarade tool-envelopes utan heuristisk argumentreparation. Den möjliggjorde korrekt creation men gjorde inte replacementuppgiften framgångsrik.
6. Adapterframgång är conditioned systemevidens och får aldrig bakåtklassificera ett native försök som PASS.

## Evaldesign- och evaluatorfynd

1. Första creation-gradern krävde både creation-toolens egen oberoende byte-readback och ett separat read-tool. Det var redundant och framgick inte entydigt av instruktionen. Originalevidensen bevarades, rätt ägare korrigerades, kontraktet versionerades och ett länkat nytt försök kördes.
2. Det första text-only-adapterförsöket gav inte en robust tool-loop. Det bevarades som misslyckad assisterad diagnostik i stället för att döljas eller räknas om.
3. Round 2:s tredje uppgift infördes adaptivt först efter att dess exakta instruktion, input och grader låsts. Uppgiften bedömdes inte med nya kriterier efter svaret.
4. Vissa runner-, adapter- och graderkomponenter förbättrades under den adaptiva körningen. Varje run bevarar egna källfingerprints och länkar till föregående försök, men körningarna ska därför inte felaktigt behandlas som om all harnesskod var identisk genom hela EVAL 2.
5. Oberoende diskfacit avgjorde mutationerna. Kandidatens påstående om filstatus räknades aldrig som exekveringsbevis.
6. Den native filläsningens evidence innehåller instruktionen i klartext men saknar `instruction_sha256`. Den separata assessmenten är bunden till hela evidencefilens hash, och fil/tool/slutvärdena är verifierbara, men den mekaniska eftergranskningen markerar ändå detta som en evidenslucka. Uppgiften används som smal read-framgång, inte som full revisionsperfektion.

## Eftergranskning och regression

- `evaluation_evidence_review.py` utökades efter körningen så att den kan granska både workflow-fixtures, enskilda nästlade read-fixtures och basic text-file-fixtures. Ändringen påverkar inte sparade kandidatutfall.
- Korrigerad assisted creation och assisted replacement klarade mekanisk identitets-, instruktion-, fixture-, after-hash-, scope-, retry- och rapportkontroll. Ett mekaniskt godkännande validerar evidensintegritet, inte task PASS.
- Round 1:s första run markerades `requires_investigation` endast därför att källfilerna senare versionsändrades under den adaptiva evalen. Runens egna source fingerprints och output finns kvar.
- Native filläsningen markerades `requires_investigation` på grund av senare källändringar och den saknade instruktionshashen ovan; fixture-after-hash och workspace-scope verifierades.
- 36 relevanta Python-tester för kontrakt, graders, text-/workflow-runners, progression, skills, watchdog och statisk ComfyUI-validering passerade efter installation av den pinnade lilla evalkravsfilen.
- 12 relevanta Node-tester för strikt Granite-envelope, bounded read/create/replace, scope, abort, validator och skill-read passerade.
- 28 ytterligare Python-tester för canonical eval-paths, runnerägarskap, avbrott och tokenhämtning passerade; 3 uttryckligt opt-in livefall skippades i den offlinegruppen. Separata live cancel-, completion- och basic toolförsök ingår redan i EVAL 2-evidensen.
- Ett separat legacytest som kräver en katalog i en ignorerad annan agentroll är rött och lämnades orört; det ligger utanför 0-WORKER-scope och påverkar inte dessa evalkontrakt.

## Baselinevillkor

- Kontextlängd: 8192.
- GPU-offload: 1.0.
- Parallella sessioner: 1.
- CPU-trådar i avläst config: 6.
- Temperatur: 0.
- Outputtak: 1024 tokens för baselineuppgifterna.
- Round 1 tools: inga.
- Projektägd System Prompt i Round 1: ingen; SHA-256 för tom text `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Effektiv Granite Jinja-template fångades separat med SHA-256 `fed2756d2d24e127b951dcf139d0b03ab7db8ef23a456128ebc9c2db4901d476`.
- LM Studio-app: 0.4.24.0; SDK: 1.5.0; Node: v24.11.1; LMS CLI commit: `ff50809`.
- Giltig token accepterades, ogiltig token nekades och giltig token återverifierades.

## Avslutad runtime

2026-09-14 | 05:38:08.457 +02:00 avlastades endast `granite-4.1-3b` och den LM Studio-server som startats för EVAL 2 stoppades. Efterkontrollen visade `No models are currently loaded`, `The server is not running` och ingen listener på `127.0.0.1:1234`.

## Beslutsmässig slutsats

Granite 4.1 3B passerade den fas som avgör om modellen är värd att utvärdera vidare. Den visade också konkret användbar förmåga för strukturerad transformation, prioriterad logik, källselektion och avgränsad filläsning. EVAL 2 ger däremot inte tillräckligt stöd för att exponera modellen för intermediate/advanced toolarbete eller ComfyUI-workflows: säker och sanningsenlig grundläggande mutation var inte reproducerbart etablerad.

Den högsta ROI-åtgärden före nästa trajectoryförsök är därför en smal integrationsevaluering: isolera och korrigera native LM Studio/SDK:s tool-call-tolkning för Granites faktiska template, och kör därefter en ny isomorf basic mutation med strikt diskfacit. Först när både create och replace når verifierat sluttillstånd utan oplanerad coaching bör Round 4 öppnas. Ingen full ComfyUI-fixturebank behöver skapas eller köras innan dess.

## Evidensindex

Alla relativa hänvisningar nedan utgår från denna EVAL-mapp.

- `2a7a0b74047547d9afdf16658f885bec/evidence.json` — verifierat begäransspecifikt stopp.
- `7be889ca416045be876c396eb047e575/evidence.json` — verifierad normal completion.
- `4065c528a8f14f90bbbdef3598224006/readiness.json` — readiness och renderad input.
- `9d07cbbd2a0a49d5a3a03cbc9c0bef75/baseline_source_review.json` — baselinekällor och versioner.
- `67d63fdd85924fe8b15933c9bf701498/evidence.json` — Round 1, record transformation.
- `f1bb794b867f411498f5dda18a408f31/evidence.json` — Round 1, priority routing.
- `d2a5190e35554ae9b2e130df430ec7a1/evidence.json` och `assessment.json` — Round 1, grounded comparison.
- `7262e5f1aa764051b15585aa0f1fdb4b/evidence.json` — Round 2, nested edit.
- `b8e9b420d3f5450595fa015422b39d49/evidence.json` — Round 2, context priority.
- `0058228f2df54a94ab7ba885dbf96ded/evidence.json` — Round 2, selected limit task.
- `8683149a046a4655bff9fe876dcf2755/evidence.json` och `assessment.json` — Round 3, native read.
- `2ae5910ba6f9410eb7c0d5fdaaa86da2/evidence.json` — Round 3, native creation.
- `6daaab6761b94f18b3f5d0db9049d1df/evidence.json` — creation, första adapterdiagnostik.
- `0a3a6c172e2045809c38253f12323eaf/evidence.json` — creation med redundant första graderkontrakt.
- `cdddc2b7780846a8b3298be6b1516dc3/evidence.json` — korrigerad assisted creation.
- `2b078962fbd947a3a99175d1024c5087/evidence.json` — native replacement.
- `8dd753bbbf144b108456c8e711a3edc1/evidence.json` — assisted replacement.

## EXTERNAL-REVIEW-QUESTIONS-EVAL-RESULT [ERQER]

Bedöm förbättringar utifrån bevarad rå evidens, verkligt uppgiftsutfall och strikt åtskillnad mellan kandidat, konfiguration, evaldesign, grader, toolintegration och LM Studio-harness. Prioritera endast icke-kosmetiska ändringar med hög praktisk ROI.

1. Vad kunde Frontier-evaluatorn Codex ha gjort mycket bättre eller annorlunda i denna EVAL-körning?
2. Hur kan framtida agenter som utvärderas ge mer lönsamma, användbara och försvarsbara resultat eller insikter på både modellspecifik och modellneutral nivå?
3. Hur kan alla framtida EVALS förbättras icke-kosmetiskt och icke-trivialt?
4. Vilka övriga mycket höga eller höga ROI-insikter, som inte täcks av frågorna ovan, bör Codex som Frontier-evaluator adressera eller implementera?

Reviewern bör särskilt svara på om progressionsstoppet efter Round 3 var rätt kalibrerat, hur native tool-dispatch bäst isoleras från modellbeteende, hur assisted adapterevidens bör vägas och vilken minsta nya mutationsevidens som försvarbart öppnar Round 4.

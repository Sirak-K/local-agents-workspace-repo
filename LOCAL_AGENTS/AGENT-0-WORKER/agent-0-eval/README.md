# 0-WORKER — modellneutral eval-yta

Denna katalog äger 0-WORKER-rollens gemensamma eval-runners, fixtures och graders. Evalspecifik evidens ägs av `model_evaluations/<eval-id>/<run-id>/`; generiska LM Studio-driftloggar ligger separat under `LM-Studio_logs/`. Historiska evalresultat ska inte flyttas eller skrivas om.

Gemensam design: [`model_evaluations/[EVAL] - [ ARCH. ] - [Frontier-As-Evaluator] - [Design].md`](<../../../model_evaluations/[EVAL] - [ ARCH. ] - [Frontier-As-Evaluator] - [Design].md>).

## Identitets- och pathkontrakt

`evaluation_paths.py` är gemensam ägare av projektrot, `model_evaluations`-rot och säker eval/run-pathkonstruktion. Nya operationer ska alltid få ett explicit eval-id i etablerat `EVAL_<safe-id>`-format. Run-id är 32 gemena hextecken. Absoluta paths, traversal, separatorinjektion, unsafe länkar, rootescape och run-kollisioner nekas.

Runnern väljer aldrig automatiskt en historisk eval. `start`, `run`, `inspect`, `stop` och `assess` använder samma explicita eval-id; predecessors, retry-original, baseline, readiness och assessment ska ligga i samma eval-home. En run skapas separat och får inte skrivas över.

Exempel från projektroten:

```powershell
$evalId = 'EVAL_example_2026-09-14'
$control = 'LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/controlled_run.py'

$run = python $control start --eval-id $evalId --model '<loaded-instance-id>' --input-file 'instruction.txt' | ConvertFrom-Json
python $control inspect --eval-id $evalId --run-id $run.run_id
python $control stop --eval-id $evalId --run-id $run.run_id --reason 'Verifierad eval- eller konfigurationsbrist; bevara originalet'
python $control inspect --eval-id $evalId --run-id $run.run_id
```

Ett lyckat `stop`-kommando betyder bara att en stop-request publicerades. Verifierat genereringsstopp kräver slutlig runner-evidens med serverkvitto; klientexit eller timeout är inte stoppbevis.

## Kontrollerad verktygsfri screening

`instruction_following_catalog.json` äger initiala taskkontrakt och `instruction_following_grading.py` äger strukturell grading/progression. Facit skickas inte till modellen. Screening kräver en granskad baseline och samma eval-id genom hela kedjan.

Readiness-capture:

```powershell
$readiness = 'LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/inspect_screening_readiness.py'
python $readiness --eval-id $evalId --run-id '<new-32hex-run-id>' --model '<loaded-instance-id>' --model-file '<optional-local-gguf>'
```

Readiness gör ingen prediction eller modell-load. Den skriver `readiness.json` i den angivna run-katalogen och är förkontrollevidens, inte PASS.

Readiness och baseline accepterar `--max-model-bytes` för den uttryckligen valda identity-läsningen. Standard är fortsatt 4 GiB; Qwen2.5-7B-Instruct Q4_K_M kräver den verifierade filstorleken `4683073952` som explicit budget i båda kommandona. Detta höjer inte GPU-/RAM-gränser eller auktoriserar modell-load. SHA-256 och ändringskontroller bevaras; ingen modellfil kopieras. Full kandidatförberedelse och historisk uppgiftsmatchning finns i jämförelseplanens avsnitt 10–13.

Baseline-capture använder två tidigare diagnostiska runs och en readiness-run i samma eval:

```powershell
$baseline = 'LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/capture_screening_baseline.py'
python $baseline --eval-id $evalId --run-id '<new-baseline-run-id>' --completion-run '<completion-run-id>' --cancellation-run '<cancel-run-id>' --readiness-run '<readiness-run-id>'
```

Den skapar bland annat `baseline_source_review.json` i den nya baseline-run-katalogen. Den ska bevara och länka de tidigare serverkvittorna; den startar ingen modellgenerering.

En reviewed screening startas med egen ny run-id:

```powershell
$screen = 'LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/start_reviewed_screening.py'
python $screen --eval-id $evalId --run-id '<new-screening-run-id>' --baseline-run '<baseline-run-id>' --probe-id 'record_transformation'
```

För senare kataloguppgifter läggs varje giltig tidigare screening-run till med upprepad `--predecessor-run <run-id>`. Wrappern fångar färsk idle-evidens och startar exakt den valda runnen; den gör ingen automatisk nästa uppgift eller retry.

Direkt runner-anrop för en låst screening använder samma eval-identitet och den konkreta baseline-reviewfilen:

```powershell
python $control start --eval-id $evalId --model '<loaded-instance-id>' --probe-id 'record_transformation' --baseline-file 'model_evaluations/<eval-id>/<baseline-run-id>/baseline_source_review.json' --duration 30 --max-tokens 1024
```

Korrigerade försök är separata runs och använder `--previous-run <run-id> --change-reason '<motivering>'`. Originalevidens ska lämnas orörd.

För den kvalitativa grounding-uppgiften är keyword-PASS förbjudet. Explicit review sparas separat:

```powershell
python $control assess --eval-id $evalId --run-id '<screening-run-id>' --criterion pass --criterion pass --criterion pass --calibration-reviewed --reason '<bounded evidence-linked rationale>'
```

`assessment.json` binds till originalets SHA-256 och kataloghash och ska inte ersätta `evidence.json`.

## Nästa verktygsfria kontextuppgift

`structured_edit_catalog.json` låser en liten teknologioberoende JSON-ändring; `structured_edit_context.md` är en eval-fixture, inte en generell produktionsprompt. `evaluation_contracts.py` verifierar källhash, exakt system-/user-roll, låsta budgetar och oberoende JSON-sluttillstånd. SDK-Chat är färsk; inga tools, skills eller dold historik ingår. Kontextens innehåll/hash och instruktionens hash sparas i varje run. Uppgiften mäter en simulerad strukturerad ändring, inte faktisk filmutation.

Server och exakt målmodell måste vara aktiva efter separat preflight. Starta endast ett avsiktligt försök med eget eval-id; ingen automatisk retry sker:

```powershell
python $control start --eval-id $evalId --model '<loaded-instance-id>' --task-id nested_record_edit --duration 30 --stop-budget 5 --max-tokens 512
```

`assessment.status` är uppgiftsutfall, inte modellfelorsak. Stopp, trunkering eller ändrad källa gör bedömningen ogiltig. Ett nytt försök efter korrigering ska länka originalet med `--previous-run` och `--change-reason`.

## Uppgiftsrecept och progression

`worker_task_catalog.json` bevarar den beslutade trajectoryn med åtta rounds och tre uppgifter per round. Endast poster med en faktisk lokal `contract` och `runner` är låsta kontrakt; övriga är adaptiva recept som uttryckligen kräver evaluatorns exakta uppgiftsdesign. `worker_task_progression.py` validerar katalogen och visar receptstatus men auktoriserar eller startar aldrig en körning. Därmed kan senare ERST anpassas efter evidens utan att efterhandskonstruerade fixtures eller graders framställs som förberedda.

## Filmutation, validering och kandidatskills

`worker_text_task_evaluation.py` äger Round 3:s teknologioberoende basic file tasks. `basic_file_task_catalog.json` version 2 låser för närvarande avgränsad skapelse med creation-toolens atomiska commit och oberoende exakta byte-readback samt hashvillkorad literal replacement med faktisk diskverifiering. Slutrapporten måste börja med exakt `STATUS=SUCCESS` eller `STATUS=FAILED`; den gemensamma `completion_claim_verification.py` jämför detta separat med observerat disk-/toolutfall för både text- och workflow-runnern. `task_verification.status` behåller det oberoende uppgiftsutfallet, `task_verification.self_report` behåller kalibreringen och total `assessment` ger aldrig PASS när dessa motsäger varandra. Ogiltig harness-/källevidens ger `unassessable`, inte modellspecifik inkonsistens. Varje run får en egen workspace, skyddad kontrollfil, exakta tillåtna sökvägar, toolreceipts och separat `assessment.model_fault_attribution`; native och Granite-adapterförsök får inte slås ihop. Adaptern accepterar endast ett exakt komplett tool-envelope och reparerar aldrig argument heuristiskt.

`tool_dispatch_evidence.py` sammanställer varje observerat tool-anrop per dispatchkälla och `call_id`: rå representation, parsad request, finaliserad request, guardbeslut, handler-start, receipt och bounded handler-returhash. Native SDK och modelladapter hålls separata. `tool_handler_returned` bevisar vad handlern returnerade till SDK-lagret, inte att modellen konsumerade resultatet. Vid mutation kräver PASS ett ordnat källhash-matchande read → minst en completed write → slutdiskhash-matchande readback; en korrekt enskild write är tillåten. Ett saknat steg visar var kedjan upphörde men tilldelar ingen felorsak. Ett direkt evaluatoranrop till toolimplementationen är fortfarande endast en toolkontroll, aldrig bevis för modell/template/parser-dispatch.

`worker_file_task_evaluation.py` äger den bounded fil-/tool-loopen. Nuvarande konkreta kontrakt är den statiska workflow-title-ändringen: en unik fixturekopia, expected-before-hash, bounded läsning, hashvillkorad atomisk replacement, faktisk readback, fast evaluatorägd validator och oberoende diskgrader. Fixtureversion 2 låser även exakt slutstatuskontrakt. Den modellneutrala `agent-0-system_prompt.txt` ger generell evidensbunden framgångsdisciplin och hashbinds separat från ComfyUI-domänkontext och valfri skill; den är beteendestöd, inte sanningskälla. Watchdogen stoppar efter tre faktamässigt likvärdiga toolutfall utan relevant effekt; ändrad hash, exitstatus eller nytt validatorresultat får återhämtningen fortsätta.

Tre modellneutrala kandidat-resurser finns i `agent-0-skills/`: title-preservation, graph-editing och workflow-diagnosis. De är lokala kandidatdata, inte Codex skills. `--skill-mode explicit --skill-id <id>` injicerar exakt en hashverifierad procedur; `--skill-mode discovery` exponerar bara katalogmetadata och ett separat bounded read-tool. Evidensen registrerar exakt exponering. Ett lyckat uppgiftsresultat bevisar inte att skillen orsakade framgången.

Den statiska validatorn använder den lokalt pinnade officiella Workflow JSON 0.4-schemakopian och grafkontroller. `pass` betyder endast de kontrollerade statiska egenskaperna—aldrig frontendöppning, installerad nodruntime, Run-ready eller lyckad bildgenerering. Okänd subgraf-/nodsemantik kräver separat review.

## Mekanisk evidensgranskning och REPORT SUMMARY

`evaluation_evidence_review.py` kan efter en run verifiera identitet, instruktionens rekonstruktion/hash, källfingerprints, fixturemanifest, retrylänk, assessmentbindning, workspace-scope och stoppfält. Resultatet gör ingen modellfelsattribuering. REPORT SUMMARY-kontrollen kräver exakt en rapportfil och signalerar alltid att en mänsklig/Frontier-semantisk review måste kontrollera samtliga fyra ERQER-frågeområden, evidenslänkar och orsaksseparation.

Före varje konkret start ska evaluatorn dessutom kontrollera exakt laddad modell, faktisk renderad input och tokenbudget, tom kö och exakt en parallell session, färsk Chat, uppgiftens kontrakt, fixture/scope, grader, stoppväg och relevanta tidigare regressionsutfall. Avvikande parallellitet är en blockerande konfigurationsmismatch men kallas inte drift utan jämförbar förändringsevidens. Ingen automatisk retry eller automatisk progression sker.

## WORKER filläsningsdiagnostik

### Transportreview före kandidatens tooluppgifter

`tool_transport_reproducibility.py --eval-id <eval-id> --run-id <nytt-run-id> --model <laddad-instans-id> --execute-series` kör exakt tre read-only-försök, aldrig en full eval. Modellen/servern ska redan vara aktiva; serien laddar inte modeller. Varje försök använder färsk Chat, samma fixture/input/schema/sampling och befintliga kör-/stoppbudgetar. `transport_review.json` sparar aktivt run-id före start; använd read-runnerns `inspect`/`stop` med detta id. Instans-/villkorsbyte eller overifierat avslut stoppar serien.

Alla ordinarie read/text/file-toolkörningar måste ange `--transport-review-file model_evaluations/<eval-id>/<diagnostik-run-id>/transport_review.json`. Spärren verifierar tre distinkta lyckade reads, originalhashar, oförändrade projektkällor/installerad runtime, samma instans och högst 30 min ålder; instans kontrolleras på nytt före genereringstillstånd. Bounded explicita stoppdiagnostiklägen är undantagna, aldrig kandidatprestation. Review bevisar endast smal native read-transport, inte skriv-/skillförmåga eller generell stabilitet. Vid FAIL: ingen full tool-eval eller blind upprepning; undersök eventskillnaden och rätt ägare först.

Evidence innehåller exakta bounded projektkällsnapshots samt publika tool-callbacks och råtext/hash när tillgängligt. Snapshoten gör projektkoden rekonstruerbar, inte LM Studios interna backend. Saknad eller redigerad råtext ger ingen byte-identitetsutsaga. Historiska evalfiler kompletteras inte retroaktivt.

`worker_file_read_evaluation.py` skapar en disponibel run-workspace och exponerar endast den etablerade read-only-filen `project/config/service.json`. Den är en smal diagnostik, inte generell WORKER-validering.

```powershell
$fileRead = 'LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/worker_file_read_evaluation.py'
$readRun = python $fileRead start --eval-id $evalId --model '<loaded-instance-id>' --transport-review-file $transportReview | ConvertFrom-Json
python $fileRead inspect --eval-id $evalId --run-id $readRun.run_id
python $fileRead stop --eval-id $evalId --run-id $readRun.run_id --reason 'Verifierad diagnostisk stopporsak'
```

`response_received` betyder att ett svar mottagits, inte att uppgiften automatiskt är godkänd. Den lilla read-only-toolens path-, call- och abortgränser ska bevaras. Granite-specifik text-till-tool-brygga är explicit opt-in diagnostik och är inte likvärdig med framgång på ordinarie SDK-toolväg.

## Bounded körning och evidens

### Praktiskt beslutsvärde före nya genereringar

Berörd tool-eval är inte redo när grundläggande native läsning saknar exekveringsbevis. Säg detta tydligt och prioritera interface-/installationsarbete framför svårare kandidatprov. Före en ny generering: ange mätobjekt, beslut per utfall, kvarstående evidenslucka, minsta motiverade förändring och budget/stoppvillkor. Ingen fullständig intern orsaksförklaring krävs för att en kontrollerad fungerande installation ska få prövas; inga nya cache-/kernel-/omladdningsstudier utan praktisk beslutsnytta.

`inspect_worker_tool_interface.py --eval-id <eval-id> --run-id <nytt-run-id> --source-run-id <sparat-read-run-id>` använder publik `applyPromptTemplate` med det sparade effektiva tool-schemat och exakt sparad instruktion. Server/målmodell ska redan vara aktiva; funktionen laddar inte modeller. Högst fem sekunder, inga `.act()`/`.respond()`-anrop eller generationstillstånd. Resultatet ägs av `tool_interface_inspection.json` med källreferens/hash, exakta projektkällor, runtimeidentitet och uttrycklig rekonstruktionsscope. Det är inte historisk intern requestcapture, task-PASS eller en transportreview.

Den första verkliga inspektionen gav toolnamn/schema och full envelopevägledning i renderingen, 255 tokens och enbart model-bound/inspection-events. Ingen bevisad saknad templateinstruktion hittades. Därför genomförs ingen blind templatefix eller automatisk full eval; ett separat explicit interface-konditioneringsexperiment kan motiveras som installationsprov, aldrig som retroaktiv förbättring av originalresultat.

`controlled_run.py` håller bounded execution, stop-budget, evidence-budget och löpande snapshots. Den bevarar partiellt resultat och stoppreceipts. Standarddiagnostik använder 30 s körbudget, 5 s stop-budget och 512 outputtokens; respektive katalogs låsta värden gäller vid `--probe-id` och `--task-id`.

Evalspecifik evidence ska inte skrivas till `LM-Studio_logs/frontier_evaluations`. Evaluation-oberoende driftobservationer, exempelvis lifecycle/idle-captures, får fortsatt ligga under `LM-Studio_logs/` och länkas projektrelativt från eval-evidensen.

Vid dåligt utfall ska evaluatorn först skilja modellutfall från harness-, runtime-, konfigurations-, tool- och graderfel. Ett felaktigt eller suboptimalt evalupplägg får inte tillskrivas modellen utan evidens.

## Verifieringsgränser

Repo-/offlinekontroller kan verifiera path ownership, containment, collision, parser/importkontrakt, assessment-immutability och mockade stoppinvarianter. De är inte bevis för lokal LM Studio-auth, providerbeteende, Windows Job Objects eller verkligt genereringsstopp. Live-prober i testsviten är därför opt-in och ska bara köras av den lokala evaluatorn under uttrycklig kontroll.

Historisk status och råa resultat finns i respektive `model_evaluations/EVAL_*/`-katalog och ska behandlas som evidens. Denna README beskriver det aktuella runnerkontraktet efter eval-relokeringen; den ersätter inte historiska run-filer eller deras slutsatser.

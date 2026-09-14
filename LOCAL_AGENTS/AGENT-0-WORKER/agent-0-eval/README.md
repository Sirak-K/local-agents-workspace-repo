# 0-WORKER — modellneutral eval-yta

Denna katalog äger 0-WORKER-rollens gemensamma eval-runners, fixtures och graders. Evalspecifik evidens ägs av `model_evaluations/<eval-id>/<run-id>/`; generiska LM Studio-driftloggar ligger separat under `LM-Studio_logs/`. Historiska evalresultat ska inte flyttas eller skrivas om.

Gemensam design: [`model_evaluations/[EVAL] - [ARCH.] - [Frontier-As-Evaluator] - [Design].md`](<../../../model_evaluations/[EVAL] - [ARCH.] - [Frontier-As-Evaluator] - [Design].md>).

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

## WORKER filläsningsdiagnostik

`worker_file_read_evaluation.py` skapar en disponibel run-workspace och exponerar endast den etablerade read-only-filen `project/config/service.json`. Den är en smal diagnostik, inte generell WORKER-validering.

```powershell
$fileRead = 'LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/worker_file_read_evaluation.py'
$readRun = python $fileRead start --eval-id $evalId --model '<loaded-instance-id>' | ConvertFrom-Json
python $fileRead inspect --eval-id $evalId --run-id $readRun.run_id
python $fileRead stop --eval-id $evalId --run-id $readRun.run_id --reason 'Verifierad diagnostisk stopporsak'
```

`response_received` betyder att ett svar mottagits, inte att uppgiften automatiskt är godkänd. Den lilla read-only-toolens path-, call- och abortgränser ska bevaras. Granite-specifik text-till-tool-brygga är explicit opt-in diagnostik och är inte likvärdig med framgång på ordinarie SDK-toolväg.

## Bounded körning och evidens

`controlled_run.py` håller bounded execution, stop-budget, evidence-budget och löpande snapshots. Den bevarar partiellt resultat och stoppreceipts. Standarddiagnostik använder 30 s körbudget, 5 s stop-budget och 512 outputtokens; screeningens låsta katalogvärden gäller när `--probe-id` används.

Evalspecifik evidence ska inte skrivas till `LM-Studio_logs/frontier_evaluations`. Evaluation-oberoende driftobservationer, exempelvis lifecycle/idle-captures, får fortsatt ligga under `LM-Studio_logs/` och länkas projektrelativt från eval-evidensen.

Vid dåligt utfall ska evaluatorn först skilja modellutfall från harness-, runtime-, konfigurations-, tool- och graderfel. Ett felaktigt eller suboptimalt evalupplägg får inte tillskrivas modellen utan evidens.

## Verifieringsgränser

Repo-/offlinekontroller kan verifiera path ownership, containment, collision, parser/importkontrakt, assessment-immutability och mockade stoppinvarianter. De är inte bevis för lokal LM Studio-auth, providerbeteende, Windows Job Objects eller verkligt genereringsstopp. Live-prober i testsviten är därför opt-in och ska bara köras av den lokala evaluatorn under uttrycklig kontroll.

Historisk status och råa resultat finns i respektive `model_evaluations/EVAL_*/`-katalog och ska behandlas som evidens. Denna README beskriver det aktuella runnerkontraktet efter eval-relokeringen; den ersätter inte historiska run-filer eller deras slutsatser.

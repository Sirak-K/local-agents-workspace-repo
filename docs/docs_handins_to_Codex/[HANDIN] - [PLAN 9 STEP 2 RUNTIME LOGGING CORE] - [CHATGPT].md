# HANDIN — PLAN 9 STEP 2 RUNTIME LOGGING CORE — CHATGPT

## Leveransstatus

ChatGPT-rad **Plan 9 / Steg 2** är implementerad som repo-only-slice och är redo för Codex granskning. Detta är inte roadmap-closure och inte lokal runtime-promotion. Steg 3 äger de permanenta regressionstesterna; steg 7 äger Codex arkitekturgranskning och lokal full gate.

Arbetet baserades på `main` commit `f8d9ed16e2dd84b025f6c97dc14b4ef636951d29` (`Begin Observability Work`) och de frysta besluten i Plan 9.

## Skapad gemensam kärna

Följande nya filer implementerar den gemensamma stdlib-kärnan:

- `runtime_logging/__init__.py`
- `runtime_logging/__main__.py`
- `runtime_logging/operation_document.py`
- `runtime_logging/atomic_json_store.py`
- `runtime_logging/sensitive_data_sanitizer.py`
- `runtime_logging/capture_retention.py`
- `runtime_logging/operation_capture_cli.py`
- `runtime_logging/operation_document.schema.json`
- `runtime_logging/runtime_logging_policy.json`

Kärnan implementerar:

- 32 lowercase hex `operation_id`, `correlation_id` och `event_id`; all-zero accepteras inte,
- owner-/status-/severity-/outcome-policy från tracked JSON,
- explicit per-owner provisional count/age/total-byte-retention med hard ceilings,
- human-readable lokal tid + UTC + epoch-ms och separat caller-mätt monoton duration,
- bounded operation/event/artifact-dokument med hard byte/event/time ceilings,
- default dataminimering där prompt/story/text/audio/image-liknande innehåll blir hash/längd/metadata,
- capture-level opt-in som krävs innan raw sensitive content kan persisteras,
- secret/Bearer/path-redaction även när raw-content opt-in är aktiv,
- artifactreferenser som måste vara säkra relativa referenser för både POSIX- och Windows-pathsemantik,
- pretty UTF-8/no-BOM JSON,
- same-directory tempfil, flush, `fsync`, `os.replace` och bounded PermissionError-retry,
- deterministic retention-plan som endast beaktar finaliserade captures, aldrig `running`, och skyddar senaste failure/interruption enligt policy,
- `python -m runtime_logging` med `begin`, `event`, `artifact`, `finalize` för PowerShell-/subprocessgränser utan externa paket eller resident service.

Ingen OpenTelemetry SDK/Collector, broker, watcher eller ny process infördes.

## LM Studio-extraktion utan parallell implementation

Ändrade:

- `LM-Studio_connections/LM-Studio_observability/observability_common.py`
- `LM-Studio_connections/LM-Studio_observability/README.md`

`observability_common.py` är nu en tunn LM-specifik kompatibilitetsadapter över `runtime_logging` för de generiska algoritmerna:

- timestamp-primitives,
- sanitization,
- bounded capture-limit exception/validation,
- pretty JSON-serialization,
- atomisk persistence.

LM Studios etablerade kontrakt lämnas LM-specifikt där det hör hemma: capture-ID/correlation-format, dokumentform, `LM-Studio_logs/`-rot, streamnamn, 8 MiB-reservlogik och status/evidence semantics. Befintliga scripts kan fortsatt importera samma symboler från `observability_common.py`; adaptern lägger reporoten på `sys.path` när LM-scripts körs direkt från sin egen katalog.

README:n dokumenterar att nya `logs/`-producenter ska konsumera den gemensamma kärnan i stället för att kopiera LM-implementationen.

## Medvetet inte gjort i steg 2

- Inga permanenta `tests/test_runtime_logging_*.py` skapades; det är explicit Plan 9 steg 3.
- Ingen AutoPull-, host-, SillyTavern-, KoboldCpp-, Dia2- eller SANA-producent instrumenterades; det hör till senare roadmaprader.
- Inga `logs/`-ägarrötter eller placeholdermappar skapades.
- `.gitignore`, roadmapstatus och frysta beslut ändrades inte.
- Inga lokala modeller, GPU-jobb, UI:n, servrar eller projektprocesser startades.

## Offlineverifiering utförd av ChatGPT

Följande gates kördes i en isolerad materialisering av den levererade slicen:

- `python -m py_compile runtime_logging/*.py LM-Studio_connections/LM-Studio_observability/observability_common.py` — PASS.
- `python -m compileall -q runtime_logging LM-Studio_connections/LM-Studio_observability/observability_common.py` — PASS.
- JSON-parse av `runtime_logging_policy.json` och `operation_document.schema.json` — PASS.
- stdlib-importaudit av samtliga nya Pythonmoduler — PASS.
- UTF-8 strict decode, no-BOM och trailing-whitespace-scan — PASS.
- Core CLI smoke `begin → event → artifact → finalize` — PASS; finalfil var multiline pretty JSON och hade 32-hex korrelation.
- Default sensitive-data smoke — PASS; prompts, password, Bearer och absoluta Windows-paths förekom inte rått i capture.
- Raw-content guard — PASS; raw event nekades när capture inte hade opt-in.
- Raw-content opt-in — PASS; uttryckligt aktiverad prompt kunde persisteras medan Authorization fortfarande redigerades.
- Contract rejection — PASS; all-zero correlation, event över cap samt POSIX/Windows/`..` artifactpaths avvisades.
- Retention smoke — PASS; `running` ignorerades, senaste failure/interruption skyddades och dry-run-planen var deterministisk.
- LM adapter smoke — PASS; legacy correlation-format fungerade, LM payload-`content` behölls enligt befintligt opt-in-kontrakt, token/path redigerades och pretty JSON saknade BOM.
- Direkt LM-adapterimport utan `PYTHONPATH` från annan cwd — PASS.
- `python -m runtime_logging --help` — PASS.

`git diff --check` och slutlig GitHub-scopekontroll körs på den publicerade candidate-diffen före fast-forward av `main`.

## Viktig reviewpunkt för Codex

Retentiontalen i policy är **provisional until local measurement** men varje av de sju frysta ägarna har redan explicita hard count/age/total-byte ceilings så implementationen saknar ingen bounded default. Codex steg 11 behåller beslutet om slutliga tal.

Steg 3 bör särskilt låsa regression för:

1. LM captureformat/sanitization före/efter extraktionen,
2. Windows replace-retry och permanent lock failure,
3. cap rejection utan silent truncation,
4. source-time vs observed-time,
5. raw-content opt-in och secret defense-in-depth,
6. deterministic retention med `running` och latest failure protection.

## PIPSA

Ingen processomstart krävs för denna repo-only-leverans. Ingen runtimeproducent är ännu inkopplad på den nya kärnan.

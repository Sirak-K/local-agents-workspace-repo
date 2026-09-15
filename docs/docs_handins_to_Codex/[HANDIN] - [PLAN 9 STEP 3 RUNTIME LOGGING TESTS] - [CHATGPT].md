# HANDIN — PLAN 9 STEP 3 RUNTIME LOGGING TESTS — CHATGPT

## Leveransstatus

ChatGPT-rad **Plan 9 / Steg 3** är implementerad som deterministisk repo-only testslice och är redo för Codex granskning. Detta stänger inte roadmapen; Codex steg 7 äger arkitekturgranskning och lokal full gate.

Arbetet bygger direkt på Step 2-commit `4fecabffff5d9640724d532520d5661d646273b9` och ändrar ingen runtimeproducent.

## Skapade permanenta tester

- `tests/test_runtime_logging_operation_document.py`
- `tests/test_runtime_logging_atomic_json_store.py`
- `tests/test_runtime_logging_sensitive_data.py`
- `tests/test_runtime_logging_retention.py`
- `tests/test_lm_studio_observability_regression.py`

Totalt finns **25 deterministiska unittest-fall**.

## Coverage mot frysta invariants

Tester låser bland annat:

- tracked policy/schema och 32 lowercase hex-ID:n utan all-zero,
- `running`, `completed`, `failed` och `interrupted` som explicit skilda tillstånd,
- source time separat från observed time,
- caller-/monotonic-baserad duration i stället för väggklockedifferens,
- event-/byte-/durationtak och synlig rejection utan silent truncation,
- säkra artifactreferenser för både POSIX- och Windows-pathsemantik,
- UTF-8/no-BOM multiline pretty JSON,
- tempfil + `fsync` + replace,
- bounded PermissionError/Windows-lock retry samt synligt permanent lock failure,
- default hash/metadata för prompt/story/media-innehåll,
- raw-content endast efter capture-level opt-in,
- secret/Bearer/path-redaction även med raw opt-in,
- deterministic retention dry-run, finalized-only, `running` protection och senaste failure/interruption protection,
- LM Studios tidigare dokumentform, legacy correlation-format, model-I/O-contentbeteende, sanitization, atomisk persistence och budgetgränser efter kärnextraktionen.

Tester använder inte modeller, servrar, nätverk eller externa processer.

## Exakta körda gates

```text
python -m unittest tests/test_runtime_logging_operation_document.py tests/test_runtime_logging_atomic_json_store.py tests/test_runtime_logging_sensitive_data.py tests/test_runtime_logging_retention.py tests/test_lm_studio_observability_regression.py
```

**PASS** — `Ran 25 tests in 0.014s` / `OK`.

```text
python -m py_compile tests/test_runtime_logging_operation_document.py tests/test_runtime_logging_atomic_json_store.py tests/test_runtime_logging_sensitive_data.py tests/test_runtime_logging_retention.py tests/test_lm_studio_observability_regression.py
```

**PASS**.

Statisk importaudit på testfilerna: **PASS** — inga `subprocess`, `requests`, `socket` eller `urllib`-imports.

UTF-8 strict/no-BOM/trailing-whitespace-kontroll på samtliga fem testfiler: **PASS**.

Slutlig `git diff --check` och GitHub-scopekontroll körs på kandidatdiffen före fast-forward av `main`.

## Avgränsning

Steg 3 ändrar inte `runtime_logging/`, LM-adaptern, AutoPull, host, SillyTavern, KoboldCpp, logs-operatorverktyg, roadmapstatus eller frysta beslut. Om testerna hade krävt produktionsfix hade det redovisats separat; den slutliga sviten passerar mot Step 2-kärnan utan sådan mutation.

## PIPSA

Ingen processomstart krävs. Endast offline-unittester och denna handin tillkommer.

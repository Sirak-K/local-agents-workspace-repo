# HANDIN — PLAN 9 STEP 6 LOGS + OPERATOR TOOLS — CHATGPT

## Leveransstatus

ChatGPT har implementerat den sista repo-only-raden i Plan 9:s delegerade fas. Steg 6 gör den gemensamma runtimeevidensen operativt läsbar utan att skapa dashboard, resident collector eller en ny loggägare.

Bas: Step 5 `0e4e0564ef010bb3312fbfce7cc5c305c881aebe`.

Detta markerar **inte** hela Plan 9 som färdig. Codex äger fortfarande Steg 7–11 inklusive arkitekturgranskning, verkliga Windows-/AutoPull-/SillyTavern-/KoboldCpp-gates, AGPR-4, AGPR-3 och slutlig A/B-/fault-/retentionpromotion.

## Ändrad yta

- `.gitignore` — genererade `logs/**/*.json` är lokala; `logs/README.md` förblir trackbar.
- `logs/README.md` — permanent owner-/operatörskontrakt.
- `runtime_logging/operation_capture_cli.py` — read-only `validate`, `query` och `prune --dry-run` ovanpå samma policy/schema/retentionkärna.
- `tests/test_runtime_logging_operator_cli.py` — deterministiska offlinefall för operatörsytan och ignorekontraktet.

## Tracked kontra lokal evidens

`logs/` innehåller ingen förhandsbyggd ownerstruktur och inga `.gitkeep`-träd. Producenten skapar `logs/<owner>/<stream>/` först när en verklig capture skrivs.

Tracked:

- `logs/README.md`.

Lokalt/Git-ignorerat:

- `logs/**/*.json`, alltså owner-specifika operationscaptures.
- atomiska `*.tmp`-filer täcks redan av projektets globala temp-ignore.

En isolerad Git-fixture verifierade att `logs/README.md` kan stageas samtidigt som capture-JSON och tempfil faktiskt ignoreras.

## `validate`

```text
python -m runtime_logging validate --root logs
```

- läser alla `*.json` deterministiskt sorterade,
- använder samma bounded UTF-8/BOM-, policy- och `validate_document`-kontrakt som writers,
- muterar inga captures,
- rapporterar samtliga invalid files med relativ path, error class och message,
- exit `0` för clean/tom/missing root och `1` när ogiltig capture finns.

En ogiltig capture repareras eller hoppas inte över tyst.

## `query`

```text
python -m runtime_logging query --root logs --owner koboldcpp
python -m runtime_logging query --root logs --correlation-id <32-lowercase-hex>
python -m runtime_logging query --root logs --failures-only
python -m runtime_logging query --root logs --has-artifact
python -m runtime_logging query --root logs --artifact-reference artifacts/example.bin
python -m runtime_logging query --root logs --has-evidence-gaps
```

Filter kan kombineras. Query validerar dokumenten före användning och returnerar endast bounded summaries:

- relativ capture-path,
- owner/stream,
- operation/correlation ID,
- status + stop reason,
- start epoch,
- artifact count,
- evidence-gap count.

Eventdetails, prompt, response och media-content skrivs inte ut av query-kommandot.

## `prune --dry-run`

```text
python -m runtime_logging prune --root logs --owner koboldcpp --dry-run
```

Prune är avsiktligt **dry-run-only** under ChatGPT-fasen. Det använder `capture_retention.plan_retention()` och tracked policy, men deletion är inte exponerad från operator-CLI:n innan Codex har slutfört lokal storleks-/användningsmätning och promotion.

Före retentionplaneringen valideras varje JSON i den valda ownerroten. Trasig JSON eller owner-mismatch blir synligt fel i stället för tyst skip. `running` captures lämnas utanför deletionplanen och latest failure/interrupt skyddas enligt policyn.

`--now-epoch-ms` finns endast för reproducerbara offlinegates; normal användning använder aktuell UTC.

## Offlinegates

Step 6-specifika tester:

```text
PYTHONPATH=. python -m unittest tests/test_runtime_logging_operator_cli.py
```

**PASS — 8/8**.

Testerna täcker:

- deterministisk valideringsordning och invalid reporting,
- missing-root PASS utan katalogmutation,
- query på owner/correlation/failure/artifact/evidence gaps,
- exakt artifact-reference filter,
- inget raw event/content i query summary,
- retention dry-run är deterministisk och byte-identisk före/efter,
- latest failure skyddas medan gammal finalized success planeras bort,
- invalid capture blockerar prune i stället för silent skip,
- `--dry-run` är obligatoriskt,
- `.gitignore`/README-kontraktet.

Full repo-only Pythonregression för Plan 9 Steg 2–6 är **PASS — 53 tester**:

- 25 core/LM-tester,
- 14 AutoPull/host-tester,
- 6 SillyTavern/KoboldCpp-kontrakttester,
- 8 operator/logs-tester.

Dessutom PASS:

- `py_compile` för berörda Pythonmoduler/tester,
- UTF-8 utan BOM,
- ingen trailing whitespace,
- isolerad Git-ignore-fixture för README kontra generated captures/temp.

Ingen modell, GPU-query, server, PowerShell-runtime, AutoPull-loop eller nätverksrequest startades i Steg 6.

## Codex-handoff / PIPSA

ChatGPT:s sekventiella repo-only-fas Steg 2–6 är här levererad. Codex bör börja med Plan 9 Steg 7 och granska kärna, ägarskap, schema/policy, LM-paritet, Step 4 AutoPull-integration, Step 5 wrapperinstrumentering och denna operator-CLI innan någon lokal promotion.

AutoPull-processen är den komponent som uttryckligen behöver kontrollerad restart/reinstall för att den korrigerade Step 4-watchern ska bli aktiv i en redan körande lokal process. Step 5-instrumenteringen används nästa gång SillyTavern/KoboldCpp startas via de uppdaterade wrappers/proben. Steg 6 i sig kräver ingen resident process eller omstart.

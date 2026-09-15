# HANDIN — PLAN 9 STEP 4 AUTOPULL + HOST OBSERVABILITY — CHATGPT

## Korrigerad leveransstatus

Plan 9 / Steg 4 är nu implementerat på den **repo-spårade Codex-förbättrade FF-only-watchern** i stället för på en antagen separat lokal implementation.

En tidigare ChatGPT-kodsökning missade den nästlade katalogen `scripts/github_autopull_chatgpts_repo_work/` och ledde felaktigt till slutsatsen att watchern inte var repo-spårad. Den slutsatsen är ersatt av direkt fil-/tree-evidens. Den faktiska watchern lästes därefter byte-/kontraktsmässigt och dess säkerhetslogik har bevarats.

Bas för korrigeringen: Step 4-commit `b56c825d91e202ced5084c475138a9486889c7ca`.

## Bevarad Codex AutoPull-design

Följande befintliga gates finns kvar i `main_autopull_watcher.ps1` och har inte ersatts av en ChatGPT-design:

- endast branch `main`,
- skip vid merge/rebase/cherry-pick/revert/index lock,
- explicit fetch av `origin/main`,
- tracked/staged dirty skip,
- fast-forward ancestry via `merge-base --is-ancestor`,
- kollisionskontroll mot untracked paths som remote skulle skriva,
- andra branch/status/collision-kontrollen precis före merge som race guard,
- endast `git merge --ff-only --quiet refs/remotes/origin/main`,
- local-ahead och diverged skrivs aldrig om automatiskt,
- inga reset/rebase/clean/stash-operationer införda.

## Flyttad evidens

Ändrade:

- `scripts/github_autopull_chatgpts_repo_work/main_autopull_watcher.ps1`
- `scripts/github_autopull_chatgpts_repo_work/install_main_autopull.ps1`
- `scripts/runtime_observability/github_autopull_capture.py`
- `scripts/runtime_observability/README.md`
- `scripts/runtime_observability/tests/test_github_autopull_capture.py`

Ny regression:

- `scripts/runtime_observability/tests/test_autopull_watcher_integration.py`

Watchern skriver inte längre operativ state-evidens till `.git/main-autopull.log`. Bootstrap stdout/stderr redirectas inte längre till `.git/main-autopull-bootstrap.*.log`. Installern städar dessa legacyfiler när den körs och pekar i stället på `logs/github_autopull/`.

Lock- och stopfilerna under `.git/` är **inte loggar** och behålls eftersom de äger process-/single-instance-kontroll, inte observability.

## State-change utan idle-spam

Watcherns befintliga `$lastState` + `$lastDetail`-deduplicering är kvar. `Set-State` publicerar en owner-capture endast när state eller detail faktiskt ändras. Oförändrade `SYNCED`-polls ger därför inte en capture var 15:e sekund.

Capture-adaptern kör inga Git-kommandon. Watchern lämnar över sin redan verifierade state till adaptern. För kritiska beslut finns fail-closed-kontrakt:

- `updated` kräver local+remote SHA, tracked clean, successful fetch och fast-forward ancestry,
- `up_to_date` kräver lika local/remote SHA efter successful fetch,
- `skipped_dirty` kräver dirty tracked state,
- `skipped_non_fast_forward` kräver non-fast-forward ancestry,
- `fetch_error` kräver fetch error.

Övriga säkerhetsstates — branch skip, pågående Git-operation, untracked collision, race guard, local-ahead, diverged och generella Git/watcherfel — behåller egna owner-local decisions.

## Observability får inte bli en ny AutoPull-risk

PowerShell-anropet till Python-adaptern är best-effort. Projektets `.venv\Scripts\python.exe` föredras när den finns och `python` på PATH används endast som fallback. Om Python saknas, adaptern saknas eller capture-skrivning misslyckas fortsätter watcherns Git-säkerhetslogik oförändrat. Detta är avsiktligt: logging failure får inte stoppa eller försvaga Codex FF-only-design.

## Hostdelen från ursprunglig Step 4

`host_snapshot_capture.py` är oförändrad i korrigeringscommitten. Den kräver explicit PID-scope, använder `Get-Process -Id`, samlar inte command line och filtrerar NVIDIA compute-processer till relevanta PID:n. Ingen resident host-watcher skapas.

## Offlinegates

Korrigeringssvit:

```text
python -m unittest scripts/runtime_observability/tests/test_github_autopull_capture.py scripts/runtime_observability/tests/test_host_snapshot_capture.py scripts/runtime_observability/tests/test_autopull_watcher_integration.py
```

**PASS** — `Ran 14 tests` / `OK`.

Den nya statiska watcher-regressionen verifierar att:

- `merge --ff-only`, ancestry, tracked-dirty, collision- och race-gates finns kvar,
- inga Git `reset`, `clean` eller `stash`-anrop införts,
- owner-capture publiceras bakom befintlig state/detail-deduplicering,
- `main-autopull.log`/`AppendAllText` är borta ur watchern,
- observability är fail-open relativt Git-säkerheten,
- project-venv används före PATH-Python när den finns,
- installern inte längre redirectar bootstrap-output till `.git/*.log` och städar legacy evidenspaths.

Ingen verklig Git-, PowerShell-, NVIDIA-, modell- eller serverprocess startades av ChatGPT.

## Återstående lokal Codex-gate / PIPSA

Den nu körande lokala watcherprocessen måste **startas om/reinstalleras kontrollerat** innan den nya scriptversionen faktiskt är aktiv i minnet. Codex/Team Master bör därför i Plan 9 steg 8:

1. stoppa den gamla watcherinstansen via dess befintliga stopmekanism,
2. starta/installera den uppdaterade watchern,
3. verifiera verklig `SYNCED`, dirty, FF-update, collision/race-skip och error-state,
4. verifiera att `logs/github_autopull/` får state-change-captures och att idle polls inte skapar spam,
5. verifiera att legacy `.git/main-autopull*.log` inte återkommer.

Ingen annan lokal process behöver startas om för denna repo-korrigering.

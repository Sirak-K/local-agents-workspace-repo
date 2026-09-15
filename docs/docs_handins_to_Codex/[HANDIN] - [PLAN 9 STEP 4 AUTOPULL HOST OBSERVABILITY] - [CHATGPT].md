# HANDIN — PLAN 9 STEP 4 AUTOPULL + HOST OBSERVABILITY — CHATGPT

## Leveransstatus

ChatGPT har genomfört den **repo-synliga och defensibelt verifierbara** delen av Plan 9 / Steg 4. Den förbättrade FF-only AutoPull-watchern som Codex äger finns fortfarande inte i det spårade GitHub-trädet, så dess lokala inkoppling har medvetet **inte gissats eller ersatts**. Repo-adaptern, host-adaptern och deras mockade/offlinegates är färdiga; faktisk watcher-hook är en explicit lokal Codex-gate.

Bas: Step 3 `b7c84b662e815bf5a4a6cbc00cc22e42dab5eafe`.

## Skapade filer under Step 4-scope

- `scripts/runtime_observability/__init__.py`
- `scripts/runtime_observability/README.md`
- `scripts/runtime_observability/github_autopull_capture.py`
- `scripts/runtime_observability/host_snapshot_capture.py`
- `scripts/runtime_observability/tests/test_github_autopull_capture.py`
- `scripts/runtime_observability/tests/test_host_snapshot_capture.py`

## GitHub AutoPull-adapter

Adaptern **utför inga Git-kommandon** och ändrar inte den lokala watchern. Den tar emot watcher-ägd observerad state och skapar en owner-specific `github_autopull`-capture via `runtime_logging`.

Kontraktet täcker:

- local/remote object ID,
- tracked clean/dirty,
- fetch `success` / `error` / `not_attempted`,
- ancestry `fast_forward` / `non_fast_forward` / `unknown` / `not_checked`,
- `updated`, `up_to_date`, dirty/non-FF skip och error outcomes,
- fail-closed kombinationsvalidering: `updated` kräver clean + successful fetch + FF + remote SHA,
- exakt en operation/event per verkligt försök/state-change; inget `idle`-outcome finns och adaptern ska inte anropas per idle poll,
- ingen rå stdout/stderr eller duplicerad Git-logg.

Detta är repo-sidan som gör det möjligt att ersätta `.git/*.log`-evidens med `logs/github_autopull/` när den faktiska lokala watchern kopplas in av Codex.

## Host snapshot-adapter

Host-adaptern:

- kräver explicit positiva relevanta PID:n,
- använder PowerShell `Get-Process -Id` för just dessa PID:n i stället för full processinventering,
- samlar processnamn/PID/CPU/working set/peak working set/responding men **inte command line**,
- frågar NVIDIA device-data och compute-apps men filtrerar compute-processer till relevanta PID:n,
- persisterar exakt en bounded `host`-capture via den gemensamma kärnan,
- markerar komponentfel som `partial` event outcome och bevarar explicit evidence gap, inklusive WDDM-begränsning för process-GPU-memory.

Ingen resident sampler/watcher skapas.

## Offlinegates

```text
python -m unittest scripts/runtime_observability/tests/test_github_autopull_capture.py scripts/runtime_observability/tests/test_host_snapshot_capture.py
```

**PASS** — `Ran 9 tests in 0.006s` / `OK`.

Testerna bevisar mockat:

- clean + fetch + FF → update,
- dirty → explicit skip,
- non-FF → explicit skip,
- fetch error → failed owner-capture,
- ogiltiga statekombinationer → rejection,
- PowerShell-query riktas endast mot explicit PID-scope och samlar inte command line,
- NVIDIA compute-processrader filtreras till relevanta PID:n,
- host-component gap ger partial evidence utan dubbelägarskap,
- tom PID-scope avvisas.

Full Step 2/3/4 offline-unittestsvit och `py_compile` körs före publicering; ingen test startar verkligt Git, PowerShell, `nvidia-smi`, modell eller server.

## Lokal blockerare / Codex-gate

Den exakta Codex-förbättrade AutoPull-watchern är inte repo-spårad på denna bas. Därför återstår lokalt att:

1. koppla watcher-state till `github_autopull_capture.py` vid verkligt attempt/state-change,
2. sluta skriva den ersatta evidensen till eventuella `.git/*.log`-filer,
3. verifiera dirty/FF/fetch/error mot den verkliga watchern,
4. bevisa att idle polls inte skapar captures.

Detta är avsiktligt **inte** löst genom att ersätta watchern med en ChatGPT-design. Codex förbättrade AutoPull förblir ägande implementation.

## PIPSA

Ingen processomstart krävs av repo-leveransen. Verklig PowerShell/NVIDIA/AutoPull-exekvering är lämnad till Codex lokala gates.

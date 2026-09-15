# HANDIN — PLAN 9 STEP 5 SILLYTAVERN + KOBOLDCPP OBSERVABILITY — CHATGPT

## Leveransstatus

ChatGPT har implementerat Plan 9 / Steg 5 som repo-only observability vid de redan existerande Storyteller-gränserna. Ingen ny generell orkestrerare eller runtime införs.

Bas: korrigerad Step 4 `a6a2738b2e97c04e866f47fa0a4d797ab0e64388`.

## Ändrad yta

- `SillyTavern_UI/harness/RuntimeObservability.psm1` — ny tunn PowerShell-adapter mot `python -m runtime_logging`.
- `SillyTavern_UI/harness/Start-SillyTavern.ps1` — owner-specific process-launch evidence.
- `SillyTavern_UI/harness/Start-KoboldCpp-StorytellerRuntime.ps1` — KoboldCpp process lifecycle evidence för foreground/background utan ändrade runtimeflaggor.
- `SillyTavern_UI/harness/Test-KoboldCpp-StorytellerChatProfile.ps1` — request/perf evidence med explicit correlation och raw-I/O opt-in.
- `SillyTavern_UI/harness/tests/test_runtime_observability_contract.py` — deterministisk statisk regression av launch/probe-/privacykontrakt.

## SillyTavern

`Start-SillyTavern.ps1` använder fortsatt samma `_local_runtime/SillyTavern/Start.bat`, `cmd.exe` och `/k`-startväg. `Start-Process -PassThru` används endast för att observera launcher-PID. Capture ägs av `sillytavern` och markerar explicit evidensluckan att PID:n är cmd-wrappern; Node child-PID och server-ready påstås inte.

## KoboldCpp lifecycle

Den befintliga argumentlistan är bevarad, inklusive `--host 127.0.0.1`, port/context, CUDA/GPU-id, `--gpulayers -1`, `--nommq`, `--highpriority`, `--quantkv f16`, `--noswa`, optional mmproj/launch och `--jinjathink false` endast för Chat Completion-profilen.

Background-läget fångar process-start med PID och finaliserar launch-operationen utan att felaktigt påstå server-ready/model-loaded. Foreground-läget behåller direkt `& $exe @KoboldArgs`, mäter processens körduration och registrerar exit code efter att processen faktiskt avslutas.

Modell- och mmproj-identitet persisteras som basename, inte absoluta paths.

## KoboldCpp request/perf

Den existerande profilen fortsätter att:

- kontrollera `/api/extra/version`, `/api/extra/true_max_context_length` och `/v1/models`,
- POST:a samma deterministiska `STORYTELLER_PROFILE_OK`-request till `/v1/chat/completions`,
- använda `StorytellerChatResponseValidation.psm1`,
- läsa `/api/extra/perf`,
- skriva samma resultatstruktur till stdout.

Proben får nu optional `-CorrelationId` och `-LogRawIO`. Om correlation saknas genereras 32 lowercase hex. Samma ID används i owner-capture och caller-headern `X-Local-Agents-Correlation-Id` för den lokala header/correlation-spiken som Codex ska verifiera live i Steg 8.

Default runtimeevidens innehåller request/response byte count + SHA-256, endpoint/settings, duration, usage/finish reason och bounded perf-observation — **inte prompt eller response content**. `content` läggs endast till när `-LogRawIO` explicit används och skickas då genom kärnans `AllowSensitiveContent`-väg.

Request-, validation- och runtimefailure finaliseras som failed evidence utan att ersätta den befintliga PowerShell-exceptionen.

## Fail-open observability

`RuntimeObservability.psm1` föredrar projektets `.venv\Scripts\python.exe`, faller tillbaka till `python` i PATH och kör CLI från projektroten. Om Python/logger/capture inte är tillgänglig returnerar adaptern `$null`; logging ska inte stoppa en annars giltig launcher eller probe.

## Offlinegates

```text
python -m unittest SillyTavern_UI.harness.tests.test_runtime_observability_contract
```

PASS: `Ran 6 tests` / `OK`.

Regressionen verifierar bland annat:

- bevarade KoboldCpp-flaggor och profiler,
- bevarad SillyTavern `Start.bat` + `cmd /k`-väg,
- bevarad Storyteller request/validator/perf-yta,
- correlation-header,
- inga request/response bodies i defaultlogg,
- explicit raw-I/O opt-in,
- separata `sillytavern`- och `koboldcpp`-ägare,
- best-effort gemensam logging-adapter.

Full Step 2–5 Python/offline-regression är PASS: 25 kärn-/LM-tester + 14 AutoPull/host-tester + 6 Step 5-kontrakttester = **45 tester**. `py_compile`, UTF-8/no-BOM och whitespace-kontroll är också PASS. Ingen modell, server, GPU-, PowerShell- eller HTTP-process startas av ChatGPT.

## Lokal Codex-gate / PIPSA

Repo-implementationen kräver ingen omstart för att granskas. För **verklig användning** av den nya instrumenteringen måste Codex i Plan 9 Steg 8 starta nya SillyTavern/KoboldCpp-processer genom de uppdaterade wrappers och köra den riktiga chatproben. Där ska correlation-header, captures, failure/interrupt och process-stop verifieras mot Windows-processerna.

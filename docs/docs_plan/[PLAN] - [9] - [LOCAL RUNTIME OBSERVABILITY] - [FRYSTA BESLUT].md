# LOCAL RUNTIME OBSERVABILITY — FRYSTA BESLUT

## Underlag och evidensstatus

- Detta dokument är den auktoritativa sammanslagningen av ChatGPT- och Claude-handinsen under `docs/docs_handins_to_Codex/`. Råfilerna förblir researchunderlag och är inte parallella designkällor.
- ChatGPT-underlaget används där det stöds av aktuell repoinspektion eller primärkällor. Claude-underlaget används för risk- och kontrollfrågor men inte som extern fakta, eftersom det uttryckligen saknade repoåtkomst och markerade komponenthooks som `unverified`.
- Standardkontrollen bekräftar att W3C `traceparent` är ett HTTP-propagationsformat, att OpenTelemetry skiljer källtid från observerad tid och gör tracefält valfria, samt att en Collector/SDK inte krävs för lokal korrelation. Python `os.replace()` och den befintliga LM Studio-implementationen ger vald modell för same-directory atomisk ersättning och bounded Windows-retry.

## Mål och negativa gränser

- `logs/` blir projektets rot för evaluation-oberoende runtimeevidens från projektägda SillyTavern-, KoboldCpp-, Dia2-, Diffusers-, host-, AutoPull- och framtida orkestreringsgränser.
- `LM-Studio_logs/`, `model_evaluations/`, Story Creator-runloggar och genererade story-, bild- och ljudartefakter behåller sina nuvarande ägare. De flyttas eller dupliceras inte till `logs/`.
- Runtime-loggning får inte bli en generell fellogg, evalmotor, innehållsdatabas, artefaktlagring, profilmanager, dashboard eller implicit modell-/processorkestrerare.
- Full OpenTelemetry SDK/Collector införs inte i första implementationen. Arkitekturen ska vara standardkompatibel nog för senare export utan att låtsas att lokala correlation-ID:n redan är spans eller fullständiga traces.

## Operatörsfrågekontrakt

Varje persisterat fält eller event ska besvara minst en fråga nedan, uppfylla en säkerhetsplikt eller styrka dokumentets integritet. Annars ska det utelämnas.

| Prio | Fråga | Minsta nödvändiga evidens |
|---|---|---|
| P0 | Vilken profil, modell, runtime och effektiv konfiguration producerade utfallet? | Producent/version, profil-/modellreferens, processinstans och säkra effektiva settings. |
| P0 | Vilken faktisk väg och vilka steg kördes? | Operations-/korrelations-ID, transport/funktionsgräns och grova start-/slutmilestones. |
| P0 | Var förbrukades tiden? | Monotona durationer för verklig kö, load, preprocess, inference och artifact-finalisering. |
| P0 | Skapades rätt beständig output? | Relativ artifactreferens, storlek, SHA-256 och relevant mediaformat/duration/dimension. |
| P0 | Återanvändes modellen varmt eller laddades den om? | Ägarens load/reuse-events, PID/processlivslängd och bounded resursevidens. |
| P0 | Varför saknas resultat eller varför avbröts operationen? | Ägande steg, outcome/stop reason, sanerad felklass, sista slutförda milestone och process-/artifactstate. |
| P1 | Följde resurs- och profilväxling den sekventiella modellen? | Host/GPU-snapshots samt explicit stop/unload/load-kvittens från den komponent som faktiskt äger växlingen. |
| P1 | Kan en incident rekonstrueras utan kopierad rådata? | Gemensam korrelation, ägarreferenser, tider, producentversioner och uttryckliga evidensluckor. |

## Ägarskap och loggstruktur

- Varje råhändelse har exakt en primär ägare. Ett överordnat lager får logga sin egen child-outcome och en referens, men inte kopiera childens stacktrace, payload eller resurssnapshot.
- Fel lagras i den ström som äger det misslyckade steget. `logs/error_logs/`, `logs/runtime_logs/` och AGPR-numrerade samlingsrötter är förbjudna.
- Följande ägarrötter etableras endast när motsvarande konkret producent instrumenteras; placeholdermappar skapas inte:

| Rot | Ansvar | Får inte äga |
|---|---|---|
| `logs/sillytavern/` | SillyTavern-process, server- och verifierad caller-side requestevidens. | KoboldCpps interna inference/perf eller full prompttext som default. |
| `logs/koboldcpp/` | KoboldCpp-process, modellivscykel och request/perf som wrapper/API faktiskt kan observera. | SillyTavern-UI-state eller Storyteller-evalbedömning. |
| `logs/dia2/` | Dia2 load/reuse, render och ljudartifact-finalisering. | Profilväxling eller referensljudets råbytes. |
| `logs/diffusers/` | Diffusers-pipeline-, modell- och bildgenerering; modellfamilj anges i komponentdetaljer/ström. | ComfyUI-workflows eller high-end mediaartefakter. |
| `logs/host/` | Bounded relevanta process-, RAM- och GPU-snapshots. | Full processlista, rå command line eller duplicerade apphändelser. |
| `logs/github_autopull/` | Fetch/clean/ancestry/fast-forward/skip/error vid state change eller verkligt försök. | Varje idle-poll eller GitHub-handoffinnehåll. |
| `logs/profile_orchestration/` | Framtida verifierade stop/unload/load/connect-transitioner. | Modelladaptrarnas egen generation eller hypotetiska placeholder-events. |

- De lokala tomma `logs/*_logs/`-mapparna är inte ett etablerat kontrakt. De ersätts först när respektive ägaradapter skapar den beslutade roten.
- `logs/README.md` är spårad ägardokumentation. Genererade JSON-captures och tempfiler är lokala och Git-ignorerade; ägarströmmar skapas av konkret runtimekod, inte genom förhandsbyggda `.gitkeep`-träd.

## Gemensamt operationsdokument

- En operation/capture har en bounded, UTF-8 utan BOM, indenterad JSON-fil. JSONL är inte primär auktoritativ yta.
- Gemensam toppnivåsemantik är: schemaversion, ägare, ström, operation, events, artifactreferenser och evidensluckor. Komponentspecifika värden ligger i ett avgränsat detaljobjekt och görs inte till global null-heavy schema.
- Operationen bär separat `operation_id` och `correlation_id`, status, start/slut, monoton duration, producer/version/process, limits, counts och data-policy. `correlation_id` genereras vid den projektägda ingången som 32 lowercase hex utan all-zero-värde; det är framtida W3C-kompatibelt men får inte benämnas `trace_id` innan riktig tracecontext används.
- Events bär sekvens, event-ID, observerad tid, optional källtid, ägarlokal eventtyp, severity, outcome, optional duration och sanerade detaljer. Source time och observed time får inte blandas.
- Tider persisteras som projektets human-readable lokal tid, UTC och epoch millisekunder. Latens räknas med monoton klocka och persisteras som duration, inte genom subtraktion av väggklocka.
- Artifactposter innehåller endast relativ referens, bytes, SHA-256 och relevant teknisk metadata. Media-/storyinnehåll kopieras inte till runtime-loggen.
- Giltiga status-/severity-/limit-/ägarvärden lagras i `runtime_logging/runtime_logging_policy.json` och valideras deterministiskt. Exakt schema finns i `runtime_logging/operation_document.schema.json`; källkod äger tillämpningen, inte katalogsemantiken.

## Persistens, integritet och retention

- `runtime_logging/` blir den gemensamma Pythonkärnan för nya `logs/`-producenter. Den äger operationsdokument, atomisk JSON-persistens, sanitization, policyvalidering, retention och en capture-CLI för PowerShell-/subprocessgränser. Komponentwrappers äger endast sina egna events och anropar kärnan.
- Generiska algoritmer i `LM-Studio_connections/LM-Studio_observability/observability_common.py` får inte dupliceras. Den gemensamma kärnan extraherar och stärker återanvändbara primitives; LM Studio behåller sina plattformsspecifika dokument-/streamkontrakt genom en tunn permanent adapter som konsumerar kärnan. Extraktion, LM-anpassning och regressionsskydd sker atomiskt utan en parallell kompatibilitetsimplementation.
- Checkpoint sker endast vid grova milestones: start, verklig load/reuse, generation/render klar, artifact finaliserad, error/interrupt och final. Per-token-, per-frame-, per-step- och idle-pollpersistens är förbjuden som default.
- Varje write använder tempfil i målkatalogen, flush, `fsync`, atomisk replace och bounded Windows lock-retry. Permanent låsning, byte-/eventtak eller serialiseringsfel är synliga failure states; de får inte döljas som framgång eller silent truncation.
- Ett oväntat hårt avbrott får lämna senaste kompletta checkpoint som `running`; läsaren klassar den som ofullständig evidens. Finalisering ska uttrycka `completed`, `failed` eller `interrupted` och dokumentera stop reason/evidence gaps.
- Policy måste ha hårt tak per fil, eventantal och capturetid samt count-, age- och total-byte-retention per ägare. Exakta retentiontal låses efter lokal storleks-/användningsmätning; implementationen får aldrig sakna hard ceilings eller ha implicit obegränsad default.
- Retention raderar endast finaliserade captures, äldst först, och har deterministic dry-run. `running`/ofullständiga captures och senaste felbevis får inte raderas av hot-path-pruning.

## Känslighet och dataminimering

- Teknisk metadata som version, duration, seed, dimension, sample rate, exit/outcome och hash får loggas bounded.
- Story-/prompttext, captions, transkript, bilder, ljud och referensröster loggas som hash/längd/metadata/artifactref. Rått innehåll kräver explicit opt-in per capture och striktare retention.
- Tokens, Authorization/Cookie, API keys, passwords och secret-liknande fält får aldrig råpersistens. Headers och processargument använder allowlist; regex-redaction är endast defense-in-depth.
- Paths är project-/artifact-root-relative när möjligt. Externa absoluta paths redigeras till säker representation och basename/hash endast när frågekontraktet kräver identitet.

## Prestanda- och promotionsgate

- Loggern får inte allokera VRAM eller starta en resident collector. Host-/GPU-sampling är lågfrekevent, tids-/samplebegränsad och mäter sin egen kostnad.
- Screening använder interleaved A/B med samma input, seed, runtime state och minst fem par; fler körningar krävs endast när variationen hindrar beslut. Initiala reject-signaler är ungefär `>2 %` median eller `>5 %` p95 total runtime, `>50 ms` p95 pre-inference-wrapperkostnad, `>64 MiB` logger-RAM eller mätbar logger-VRAM. De blir inte permanenta budgets förrän lokal evidens låser dem.
- Promotion kräver offline schema-/sanitization-/atomicity-/retentiontester, Windows lock- och abrupt-avbrottstest, live producerbevis, artifact/hashverifiering och att tidigare fungerande runtimebeteende inte regresserar.

## Förväntad permanent källstruktur

```text
runtime_logging/
  __init__.py
  __main__.py
  operation_document.py
  atomic_json_store.py
  sensitive_data_sanitizer.py
  capture_retention.py
  operation_capture_cli.py
  operation_document.schema.json
  runtime_logging_policy.json
LM-Studio_connections/
  LM-Studio_observability/
    observability_common.py
logs/
  README.md
tests/
  test_runtime_logging_operation_document.py
  test_runtime_logging_atomic_json_store.py
  test_runtime_logging_sensitive_data.py
  test_runtime_logging_retention.py
  test_lm_studio_observability_regression.py
```

Komponentintegrationer ska stanna hos respektive befintlig launcher/wrapper/adapter. Nya adapters eller ägarströmmar får endast skapas av en aktiv vertikal slice som faktiskt behöver dem.

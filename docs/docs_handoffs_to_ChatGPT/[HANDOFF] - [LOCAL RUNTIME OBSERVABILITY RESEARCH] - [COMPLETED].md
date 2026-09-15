# HANDOFF — LOCAL RUNTIME OBSERVABILITY RESEARCH

## Mål och nytta

Leverera det källverifierade beslutsunderlag som behövs innan projektet bygger en gemensam men komponentägd loggingyta under `logs/`. Resultatet ska hålla minst samma icke-kosmetiska nivå som `LM-Studio_logs/` och dess captureimplementation: bounded och atomisk persistens, korrelation, sanitization, explicit känslighetsgräns, evidensluckor och tydligt ägarskap utan duplicerade felloggar eller evalartefakter.

Detta är ett substantiellt research- och arkitekturunderlag, inte en beställning på loggingkod. ChatGPT kan äga arbetet eftersom aktuell GitHub-`main`, primär dokumentation och offentliga upstreamkällor räcker. Codex behåller beslutet om permanenta runtimekontrakt, invarianta namn, katalogstruktur och implementation efter att underlaget har granskats tillsammans med Team Master.

## Den högsta ROI-frågan — `ONE Thing`

Fastställ först **vilka konkreta operatörs-, felsöknings- och verifieringsfrågor loggarna måste kunna besvara end-to-end**. Härled därefter varje föreslaget event, fält, capturepunkt och lagringsyta baklänges från dessa frågor.

Om denna query-/evidenskontrakt är korrekt blir onödig telemetry, dubblerade loggar, kosmetiska dashboards och för tidig schemaarkitektur lättare att eliminera. Ett fält utan en identifierad fråga, säkerhetsplikt eller revisionsplikt ska inte rekommenderas.

## Verifierat nuläge och underlag

Utgå från aktuell GitHub `main` på minst commit `59ab795e803f54d3234447d627729bbb9f5c5e10`. Läs minst:

- `AGENTS.md`, särskilt plattforms-/app-/motorspecifika loggägare, pretty/multiline JSON, path- och timestampregler,
- `LM-Studio_logs/README.md`,
- `LM-Studio_connections/LM-Studio_observability/README.md` och dess Pythonfiler,
- `[ CURRENT ARCHITECTURAL PROJECT STATE ].md`,
- `docs/docs_plan/[PLAN] - [8] - [LOCAL AI ROLE PROFILES] - [FRYSTA BESLUT].md`,
- rollkriterierna för AGPR-2, AGPR-3 och AGPR-4,
- relevanta launchers/harnessytor för SillyTavern, KoboldCpp, Storyteller och AutoPull.

Aktuella producenter och gränser som måste kartläggas är minst:

- SillyTavern,
- KoboldCpp och AGPR-2 Storyteller-harness,
- Dia2/Gradio för AGPR-4,
- SANA-Sprint/diffusers-kandidaten för AGPR-3,
- framtida profilorkestrering och processväxling,
- hostresurser/GPU,
- FF-only AutoPull,
- LM Studio-observability som kvalitetsreferens men separat loggägare,
- beständiga bild-, ljud- och storyartefakter samt separata evalytor.

Lokalt finns ännu ospårade/tillfälliga tomma `logs/`-kataloger och pågående, ocommittade Voice Master-launcherarbete som inte är synliga för GitHub Connector. Gissa inte deras slutliga form och ändra inga motsvarande filer.

## Frontier-agentens nio hög-ROI-frågor

Besvara frågorna med primär dokumentation, officiella upstream-repon eller direkt repo-evidens. Ange exakt källa/länk, relevant versions-/datumkontext och skilj verifierat faktum från rekommendation och inferens.

1. **Operatörsfrågekontrakt:** Vilka 8–12 konkreta frågor måste en avancerad ensamoperatör kunna besvara efter en AGPR-2-, AGPR-3- eller AGPR-4-körning eller ett fel? Prioritera modell-/profilidentitet, faktisk requestväg, latency breakdown, outputartefakt, process-/GPU-livscykel, modellomladdning, avbrott och orsaken till att ett resultat saknas. Vilken minsta evidens krävs per fråga?
2. **Korrelation över gränser:** Vilken minsta standardkompatibla identitetsmodell fungerar genom SillyTavern → HTTP/backend → KoboldCpp/Dia2/SANA → subprocess → beständig fil? Jämför ett enkelt `correlation_id`/`operation_id` med W3C Trace Context/OpenTelemetry trace/span-ID:n och förklara vad som faktiskt kan propageras genom nuvarande komponenter utan invasiva forks.
3. **Verkliga capturepunkter:** Vilka stabila och minst invasiva logg-/hook-/API-ytor erbjuder aktuella SillyTavern, KoboldCpp, Gradio/Dia2, diffusers/SANA och Windows/NVIDIA? Ange för varje komponent vad som kan observeras nativt, vad som kräver wrapper/middleware och vad som skulle kräva upstreamkodändring. Påstå inte en hook utan primär källa.
4. **Minsta gemensamma event-envelope:** Vilka få fält behöver alla komponentägda events för tidsordning och korrelation, och vilka fält måste förbli komponent- eller eventtypsspecifika? Beakta schema/version, lokalt och UTC-tidformat, severity/outcome, producer/version, eventtyp, trace/correlation, duration, modell/profil och artefaktreferens utan att skapa en universell megaschema.
5. **Ägarskap utan redundans:** Föreslå en producent→ström→konsument→retention-matris där varje råhändelse har exakt en primär ägare. Förklara hur fel stannar i ägarströmmen, hur tvärkomponentincidenter länkas utan kopiering och hur runtimeevidens hålls separerad från evalresultat, Story Creator-runloggar och outputartefakter.
6. **Känsligt innehåll och path-säkerhet:** Vilken dataklassning och opt-in-policy behövs för Storyteller-text, prompts, bilder, ljud, referensröster, modell-I/O, tokens, headers, absoluta paths och processkommandon? Ange när hash/metadata räcker, när rått innehåll behövs och vilka redactionbegränsningar som måste vara explicita även i ett helt lokalt system.
7. **Bounded och kraschrobust filpersistens:** Vilken minsta strategi för pretty-JSON, atomisk skrivning, rotation/retention, filstorleks-/eventtak, flush/checkpoint, Windows-fillåsning och abrupt avbrott ger hög beviskvalitet utan loggspam? Jämför per-eventfiler, per-operationfiler och appendformat; beakta att JSONL inte uppfyller projektets mänskligt läsbara multilinekrav som primär loggyta.
8. **Mätbar overhead:** Vilken liten deterministisk benchmark ska bevisa att instrumenteringen inte materiellt försämrar första-token-/första-bild-/första-ljud-latens, total runtime, VRAM/RAM eller output? Föreslå mätpunkter och defensibla initiala budgets, men markera värden som måste låsas genom lokal A/B i stället för antagande.
9. **Bygg kontra standard:** För detta lokala enanvändarsystem, jämför Python/PowerShell-standardbibliotek + komponentwrappers, OpenTelemetry-baserad instrumentering och en begränsad hybrid. Vilken minsta walking skeleton ger omedelbar felsökningsnytta nu men har en tydlig migrationsväg om en broker eller fler processer införs senare?

## Obligatorisk syntes

Skriv researchresultatet direkt i denna handoff under en tydlig rapportsektion. Det ska innehålla:

1. en prioriterad tabell över operatörsfrågorna och exakt minsta evidens för var och en,
2. en komponentmatris med producent, ägare, möjlig capturepunkt, känslighet, boundedness och verifierad källstatus,
3. en jämförelsematris för enkel lokal lösning, OpenTelemetry och hybrid med nytta, kostnad, risk och framtida migrationskostnad,
4. rekommenderad minsta walking skeleton, uttryckt som ansvar och eventflöde men **utan att frysa nya permanenta fil-/mapp-/fält-/klassnamn**,
5. de högst fem kvarvarande lokala datapunkterna som endast Codex/Team Master kan verifiera, ordnade efter förväntad informationsvinst per kostnad,
6. ett kort riskregister för dubbelägarskap, loggspam, hemlighetsläckage, falsk kausalitet, versionsdrift och mätpåverkan.

Om en extern Frontier-agent eller Claude ger svar ska de behandlas som researchinput: spåra vilka slutsatser som kommer därifrån och verifiera centrala tekniska påståenden mot primärkällor. Konsensus mellan agenter är inte i sig evidens.

## Tillåten skrivyta

Ändra endast denna handoff-fil. Vid full klarsignal får ChatGPT byta suffixet från `[INCOMPLETE]` till `[COMPLETED]` med oförändrat basnamn.

Alla andra filer är read-only. Skapa inte `logs/`, loggerkod, schemas, kataloger, dashboards, tester, launchers, wrappers, dependencies eller exempelcaptures i denna handoff.

## Negativa gränser

- Ändra inte `AGENTS.md`, LM Studio-observability, AGPR-profiler, plan 8, andra handoffs, SillyTavern/KoboldCpp, AutoPull eller scripts.
- Återanvänd inte `runtime_logs` som generell ägare och skapa inte en generell `error_logs`-ström.
- Flytta eller duplicera inte evalevidens, Story Creator-loggar eller genererade mediaartefakter.
- Lås inte nya invarianta runtime-termer, fältnamn eller katalogtaxonomier; markera dem som kandidater för Team Master/Codex-beslut.
- Starta inga modeller, servrar, GPU-jobb eller lokala processer. Ingen lokal modellåtkomst krävs.
- Presentera inte spekulativ upstreamfunktionalitet som verifierad. Skriv `unverified` när primär evidens saknas.

## Klarsignal och verifiering

Handoffen får markeras `[COMPLETED]` först när:

- alla nio frågor har ett konkret svar eller en explicit, välavgränsad evidenslucka,
- varje centralt externt tekniskt påstående har en primär källa eller tydlig `unverified`-markering,
- den obligatoriska syntesens sex delar finns,
- rekommendationen härleds från operatörsfrågorna och komponenternas faktiska integrationsytor,
- inga permanenta kontrakt eller implementationer har låsts,
- `git diff --check` passerar,
- diffen från startcommit endast innehåller denna fils innehåll och eventuella `[INCOMPLETE] → [COMPLETED]`-rename,
- filen är UTF-8 utan BOM.

Rapportera exakta källor, kvarvarande osäkerheter, kontroller och PIPSA. Ingen processomstart ska krävas för denna research-only-handoff.

## ChatGPT research report — 2026-09-15

**Status: `COMPLETED` efter verifiering nedan.** Detta är ett research-/arkitekturunderlag. Inga runtimekontrakt, loggerimplementationer, permanenta katalognamn, eventfält, klasser eller beroenden låses här. Ord som `operation-id`, `trace-id`, `owner stream` och liknande används nedan som **kandidatsemantik**, inte som beslutade invarianta namn.

### Scope, källnivå och versionskontext

Researchen började på GitHub `main` commit `db53d0153af415378a195fb31cef8c7b576081a1` (`Add local runtime observability research handoff`), vars parent är den begärda miniminivån `59ab795e803f54d3234447d627729bbb9f5c5e10`. Före skrivning synkades arbetet om mot aktuell `main` `449b71341bb8b7e1dddd319fc8dd420dca58e021` (`Add local-only Dia2 Voice Master UI launcher`). Den samtidiga Voice Master-committen lästes endast som ny researchinput och lämnas read-only; den slutliga handoff-diffen byggs ovanpå `449b713...`.

Repo-evidens som styr slutsatserna:

- `AGENTS.md`: loggar ska ägas av faktisk plattform/app/motor; ett generellt `runtime_logs` får inte bli permanent ägare; tvärlagerhändelser länkas med korrelation i stället för att kopieras. Den aktuella filen innehåller inte ett separat generellt schema för pretty-JSON/path/timestamp; dessa egenskaper är däremot konkret etablerade i LM Studio-referensimplementationen nedan.
- `LM-Studio_logs/README.md`: evaluation-oberoende rå runtimeevidens, separat ägarström per ansvar, fel stannar i ägarströmmen, ingen generell `error_logs`, evaler refererar rå captures i stället för att kopiera dem.
- `LM-Studio_connections/LM-Studio_observability/README.md` och `observability_common.py`: bounded capture, explicit evidenslucka, känslighetsgräns, lokal+UTC+epoch-tid, sanering, 8 MiB hard cap, 300 s/1000 event-budgets, pretty-JSON, flush+`fsync`, tempfil + `os.replace`, bounded Windows lock-retry och senast kompletta dokument som crash-resilient checkpoint.
- Projektets Storyteller-harness är verifierat mot KoboldCpp `1.120` och SillyTavern `1.19.0` / release commit `06bde939fb1e9c4c8d8641d810f0a916b5bce127`.
- AGPR-3-kriteriet kräver spårbar modell/version, effektiv prompt, seed, dimensioner, steg/sampler, generationstid, total instruktion→fil-tid, peak VRAM och bevis att en varm revision inte laddar om modellvikter från disk.
- AGPR-4-kriteriet kräver seed, referensklipp, modellversion, precision, settings, render time, peak VRAM och verifierbar outputfil; framtida profilväxling ägs inte av TTS-renderaren.
- `AGPR-2-STORYTELLER/ROLE-CRITERION.md` är tom på denna commit. AGPR-2-observability härleds därför endast från den verifierade Storyteller-harness-/probe-ytan och planbeslut, inte från påhittade rollkrav.
- FF-only AutoPulls beteendekontrakt framgår av `AGENTS.md`, men ingen repo-spårad AutoPull-implementation hittades i det rekursiva trädet på den synkade basen. Exakt lokal hook/capturepunkt är därför **unverified**.
- Den nya read-only Voice Master-launchern på `449b713...` verifierar däremot den lokala Dia2-vägen: `scripts/Start-AGPR-4-Voice-Master-UI.ps1` binder `127.0.0.1`, väljer lokala Dia2-1B- och Mimi-vikter, sätter offline/analytics-off, patchar upstream `_get_dia()` till lazy `Dia2.from_local(...)` på CUDA BF16, stänger CUDA Graph för första proof och använder Gradio-kö med concurrency 1. Modellen förblir oladdad tills Generate trycks.

Externa primärkällor granskades 2026-09-15. Där projektversionen är känd anges den; annars är källan upstream `main`/aktuell dokumentation och lokal installerad version markeras **unverified**.

---

## 1. Operatörsfrågekontrakt — `ONE Thing`

All rekommenderad telemetry nedan måste kunna härledas till minst en rad i denna tabell, till en säkerhetsplikt eller till en revisionsplikt. Ett fält som inte gör det bör utelämnas.

| Prio | Fråga som måste kunna besvaras | Minsta evidens — inte mer |
|---|---|---|
| P0 | **1. Vilken AGPR, modell, runtime och effektiv profil producerade utfallet?** | En operationell identitet; AGPR-roll; modellidentifierare + versions/revisions/hashreferens där tillgängligt; runtime/producer-version; relevant profil/config-referens; PID/processinstans. Rå modellfilspath krävs inte. |
| P0 | **2. Vilken faktisk request-/funktionsväg kördes?** | Startande producent, transporttyp (direkt funktionsanrop/HTTP/subprocess), endpoint eller funktionsgräns, start/accept/slut-tider och länkar till nästa ägares operation. Ingen prompttext behövs för att bevisa vägen. |
| P0 | **3. Var förbrukades tiden?** | Monotona start/slutpunkter för endast verkliga steg: eventuell kö, eventuell modell-load, preprocessing, inference/generation, första användbara output när den faktiskt exponeras, filskrivning/finalisering; native backend-perf där sådan finns. |
| P0 | **4. Skapades rätt beständig output och går den att verifiera?** | Artefakttyp, säker relativ/refererad plats, bytes, SHA-256, mediaformat + dimension/duration där relevant, skapad/finaliserad tid och operationen som producerade den. Själva bilden/ljudet/storyn kopieras inte in i runtime-loggen. |
| P0 | **5. Återanvändes modellen varmt eller laddades den om?** | Explicit wrapperhändelse för load-start/load-slut när wrappern äger load; PID/processlivslängd; frånvaro av en andra load i varm iteration; RAM/VRAM före/efter; processens disk-read-delta som stödbevis. Disk-I/O ensam bevisar inte att bytesen var modellvikter. |
| P0 | **6. Varför saknas ett resultat?** | Ägande steg, outcome/stop reason, sanerad felklass/kod, sista verifierat slutförda steg, child-processstatus och faktisk kontroll om artefakten finns/finaliserades. En separat generell fellogg behövs inte. |
| P0 | **7. Begärdes avbrott — och stoppade arbetet faktiskt?** | Cancel/interrupt-begäran med tid och mål; backend-/processkvittens eller exit/sluttid; status för partiell output; kvarvarande process/GPU-state. Timeout eller stängd klientanslutning räcker inte som stoppbevis. |
| P1 | **8. Vad hände med process, RAM, GPU och eventuell contention?** | Relevanta PID:n, process start/exit, working set/peak working set, GPU device + memory/utilization snapshots, relevanta compute-PID:n och samplingens evidensluckor. Full processlista behövs inte. |
| P1 | **9. Följde profilväxling den sekventiella unload→load-principen?** | Länkat växlingsförlopp: föregående profil/process stop/unload-bevis, resursstate efter stopp, nästa load/start och samtidighetskontroll för tunga modeller. En framtida orkestrerare ska äga denna evidens, inte modelladaptrarna. |
| P1 | **10. Förändrades användarens instruktion/settings innan motorn körde dem?** | Hash/längd eller säker normaliserad representation vid relevanta gränser; effektiva numeriska/settingsfält som faktiskt påverkar körningen; rå prompt/story endast explicit opt-in. För mediarevisioner ska ändringen kunna kopplas till användarens revision. |
| P1 | **11. Gjorde FF-only AutoPull en uppdatering eller avstod den — och varför?** | Lokal HEAD, remote SHA före/efter, tracked-clean/dirty gate, fast-forward/ancestry-beslut, outcome och fel/skip reason. Exakt producer/hook är **unverified** tills den lokala watchern inspekteras. |
| P2 | **12. Kan en tvärkomponentincident rekonstrueras utan kopierade råloggar?** | Gemensam korrelations-/trace-referens, ägarreferenser till de berörda captures/artefakterna, tider och producer-versioner. Kausalspråk får endast följa verifierad länk, inte tidsmässig närhet ensam. |

**Slutsats:** fråga 1–7 är walking-skeleton-gaten. Fråga 8–10 behövs för kvalificeringen av AGPR-3/4 och reproducerbar Storyteller-diagnostik. Fråga 11 kan inte slutdesignas innan den lokala AutoPull-implementationen är synlig. Fråga 12 är anledningen att korrelation måste finnas från början, men den motiverar inte en collector eller distribuerad tracingplattform i sig.

---

## 2. Korrelation över gränser

### Verifierat

W3C Trace Context definierar HTTP-headern `traceparent` med `version`, 16-byte/32-hex `trace-id`, 8-byte/16-hex `parent-id` och flags. W3C rekommenderar globalt unik, helst slumpgenererad trace-id. OpenTelemetry använder W3C Trace Context som standardpropagator och beskriver trace-/span-ID som mekanismen för att korrelera arbete över process-/servicegränser. OTel varnar samtidigt för att inkommande context är opålitligt och att baggage inte ska innehålla credentials eller PII.

Primärkällor:

- W3C Trace Context Recommendation: https://www.w3.org/TR/trace-context/
- OpenTelemetry Context Propagation: https://opentelemetry.io/docs/concepts/context-propagation/
- OpenTelemetry Logs Data Model: https://opentelemetry.io/docs/specs/otel/logs/data-model/
- OpenTelemetry non-OTLP logging trace context: https://opentelemetry.io/docs/specs/otel/compatibility/logging_trace_context/

### Rekommendation

För första lokala walking skeleton räcker **en slumpmässig operationell korrelationsidentitet skapad vid projektägd operationsgräns**. Detta ger nästan all omedelbar felsökningsnytta utan OTel-SDK/collector. Format och permanent fältnamn ska inte låsas i denna handoff.

Det är ändå hög ROI att göra identiteten **framtidskompatibel** med W3C/OTel: när en HTTP-gräns faktiskt kan bära `traceparent` kan samma operation mappas till en trace, och eventuella underoperationer kan senare få span-relationer. Detta ska ses som migrationsväg, inte som krav att alla nuvarande komponenter producerar spans.

### Vad kan faktiskt propageras nu?

| Gräns | Vad är verifierat | Minsta försvarbara strategi nu |
|---|---|---|
| Projektwrapper → direkt Python SANA/Dia2 | Samma processkod kan explicit bära en operationell identitet i funktionscontext. | Direkt parameter/context i projektägda adaptern; ingen OTel behövs. |
| Projektwrapper → subprocess | Projektlaunchers äger subprocess-start för bl.a. KoboldCpp. | Operationell identitet kan hållas i parentens logg och, om en framtida child-adapter stödjer det, skickas explicit. OTel environment-carrier är 2026 en release-candidate, inte något som ska frysas här. |
| SillyTavern → Custom Chat Completion HTTP | SillyTaverns release-preset innehåller `custom_include_headers`; således finns en upstream-yta för custom headers på custom OpenAI-vägen. | Ett W3C `traceparent` eller projekt-ID-header kan **kandidattestas** på den vägen. Att den aktuella Storyteller Text Completion-baselinen stöder motsvarande headerkonfiguration är **unverified**. |
| HTTP → KoboldCpp intern request | KoboldCpp har verifierade API-/perfytor, men ingen primär källa hittades som visar att ett godtyckligt traceheader-id återges eller exponeras i dess perf/loggdata. | Caller/wrapper äger request-ID och tider. Intern headerpropagation i KoboldCpp är **unverified** och ska inte krävas för baseline. |
| HTTP → Gradio prediction | `gradio.Request` kan ge prediction-funktionen headers, query params och `session_hash` om funktionen accepterar request-objektet. | Projektadaptern kan senare läsa en header utan Dia2-fork; upstream `gradio_app.py` gör inte detta idag. |
| Producer → beständig fil | Filformat har inget gemensamt tracekontrakt. | Loggen äger associationen via artifact-ref/hash; skriv inte intern traceinformation in i mediafilen om inte format/use-case uttryckligen motiverar det. |

**Varför inte bara W3C överallt nu?** W3C löser transport av tracecontext där en carrier finns; det skapar inte spans, persistens eller ägarskap automatiskt. Nuvarande pipeline blandar PowerShell, Node/SillyTavern, KoboldCpp, Python/diffusers, Python/Gradio och filer. Att lägga OTel i alla lager nu skulle vara mer implementation än observabilitynytta.

**Varför inte bara ett godtyckligt correlation-id för alltid?** Det fungerar idag men gör senare broker/multiprocess-migrering onödigt dyr. Därför rekommenderas standardkompatibel semantik och möjlighet att mappa till W3C, utan att låsa ett permanent schema i denna research.

---

## 3. Verkliga capturepunkter och komponentmatris

Tabellen anger **Native** när en upstream/repo-yta är direkt verifierad, **Wrapper** när projektets befintliga eller framtida projektägda gräns kan observera utan upstreamfork, och **unverified** när primär evidens saknas.

| Producent / ansvar | Primär ägare | Verifierad möjlig capturepunkt | Känslighet | Boundedness som bör krävas | Källstatus |
|---|---|---|---|---|---|
| SillyTavern server | SillyTavern | Native `logging.minLogLevel` och `logging.enableAccessLog`; default config anger att accessloggen skriver anslutningar med timestamp/IP/user-agent. | IP/user-agent; eventuellt annan consoletext beroende loggnivå. | Fil/console-logg måste få projektägd retention; fånga inte hela terminalflödet obegränsat. | **Native verified**: SillyTavern config docs + release default config. |
| SillyTavern modellrequest | SillyTavern-/UI-lager för caller-side fakta | Custom OpenAI-preset har `custom_url` + `custom_include_headers`. Det räcker för kandidat-propagation på custom Chat-vägen. | Prompt/body/headers kan vara mycket känsliga. | Logga endpointtyp/tider/status och hashes/metadata; body/header raw off by default. | Header-yta **verified**; samma möjlighet för aktuell Text Completion-baseline **unverified**. |
| SillyTavern processstart | Projektägd SillyTavern-launcher | `Start-SillyTavern.ps1` verifierar installation/node/cmd och startar `Start.bat`. Den använder idag inte `-PassThru`. | Local path/PID. | En start-/exitpost per processinstans. | **Wrapper verified**, PID efter start kräver launcherändring senare. |
| KoboldCpp process/runtime | KoboldCpp | Storyteller runtime-wrapper känner effektiv profil, exe/model/mmproj, context, GPU, port och kan i background-läge få processobjekt/PID. KoboldCpp console har dessutom input/output om inte `--quiet` används. | Model path; console prompt/output är innehållskänsligt. | Lifecycle-milstolpar, inte obegränsad stdout. `--quiet` är upstream privacy-kontroll när rå I/O inte behövs. | **Wrapper + Native verified**. |
| KoboldCpp request/perf | KoboldCpp | `/api/extra/version`, `/api/extra/true_max_context_length`, `/v1/models`, `/v1/chat/completions`, `/api/extra/perf`; repo-proben mäter redan elapsed + usage/finish/perf. | Prompt/response om det loggas. | En per-operation summary + native perf snapshot; rå text opt-in. | **Native verified** i official wiki och repo-probe. |
| AGPR-2 Storyteller operation | Projektägd Storyteller-operation | Befintlig chat-probe ger model/version/context/request elapsed/usage/perf och response-contract. Launcher ger profile/model/processdata. | Storytext och prompt mycket känsligt. | Coarse milestones per turn/probe; inga token-per-eventloggar som default. | **Repo verified**. Full SillyTavern→Kobold correlation på Text Completion-baseline **unverified**. |
| Dia2 model lifetime | Dia2-runtimeägare | Upstream `gradio_app.py` har singleton `_dia`; aktuell projektlauncher patchar `_get_dia()` till en lokal singleton som lazy-laddar Dia2-1B via `Dia2.from_local(...)` först vid Generate. | Local model/reference paths och modell-ID. | En load-start/end per faktisk load; explicit evidence om varm reuse. | **Native + repo wrapper verified** på `449b713...`. |
| Dia2 generation | Dia2-runtimeägare | `dia.generate(..., verbose=True)` returnerar waveform, sample rate och timestamps; Gradio app fångar stdout och queue har `default_concurrency_limit=1`. Projektlaunchern återanvänder denna UI/generationfunktion och binder lokalt på `127.0.0.1`. | Script, prefix/reference voice, waveform, verbose output. | Per render: timings/settings + artifact metadata; raw script/reference only opt-in. | **Native + repo launcher verified**. Den granskade vägen returnerar waveform till Gradio; en projektägd beständig ljudfil/finalize-hook syns ännu inte och är **unverified/gap**. |
| Gradio request | Gradio/Dia2 UI-lager | Prediction kan acceptera `gr.Request` med headers/client/query/session_hash. | Headers/cookies/user info kan innehålla secrets. | Allowlist endast korrelationsheader; logga aldrig hela headers/cookies. | **Native Gradio verified**; Dia2 app använder inte request-objektet idag. |
| SANA-Sprint model load | SANA/diffusers-runtimeägare | Official model card använder `SanaSprintPipeline.from_pretrained(...)` följt av `.to("cuda")`; model repo innehåller scheduler/text_encoder/tokenizer/transformer/vae. | Model revision/path/cache. | En load-start/end; säkra modellidentifierare/revisioner. | **Native verified**. Lokal installerad diffusers-version **unverified**. |
| SANA generation | SANA/diffusers-runtimeägare | `SanaSprintPipeline.__call__` exponerar prompt/settings/generator/output och `callback_on_step_end`; output är PIL/numpy. | Prompt, bild, latents. | Default endast operationstart/slut + eventuellt sampled step milestones; logga inte latents. | **Native verified** i Diffusers Sana-Sprint docs. |
| SANA beständig bild | Generator-/artifactskrivande adapter | Model card visar explicit `image.save(...)`; projektkriteriet kräver beständig fil. | Bildinnehåll/path. | Metadata/hash + filfinalisering; själva bildbytes ligger endast i artifactytan. | **Native save capability + repo requirement verified**. |
| Host process/RAM | Host-observabilityägare, inte varje modellström | PowerShell `Get-Process` eller WMI/CIM `Win32_Process`. WMI exponerar PID, working set, peak working set samt read/write transfer counts. | PID/path/commandline kan vara lokal data. | Endast relevanta PID:n; sampling låg frekvens och tidsbegränsad. CommandLine bör inte hämtas som default. | **Microsoft primary verified**. |
| NVIDIA GPU | Host-/GPU-observabilityägare | `nvidia-smi --query-gpu` och `--query-compute-apps`; befintlig LM-referens använder exakt detta. | Låg; processnamn/PID. | Bounded interval/samples; versionskänslig parser. | **NVIDIA primary verified**. Windows WDDM kan sakna process-GPU-memory. |
| Framtida profilorkestrering | Framtida orkestrerare | Äger explicit `stop/unload → load → connect/select` enligt plan 8. | Modell-/processidentiteter. | Endast state transitions och kvittenser. | **Responsibility verified**, implementation/hook **unverified**. |
| FF-only AutoPull | AutoPull-watcher | AGENTS beskriver clean + fast-forward gate och remote-ref behavior. Ingen spårad implementation hittades i det rekursiva trädet på den synkade basen. | Repo path/branch/SHA; ev. feltext. | En post per poll endast vid state change/attempt, inte varje idle-poll. | Beteendekontrakt **verified**; exakt hook **unverified**. |
| LM Studio | Befintlig `LM-Studio_logs`-ägare | Redan implementerade server/model lifecycle/model I/O/host captures. | Model I/O explicit sensitive. | Befintliga hard caps. | **Repo verified quality reference**; ska inte flyttas in under ny generell ägare. |
| Bild/ljud/storyartefakter | Respektive artifactproducent/outputyta | Artifact finalize + hash/metadata från producer-wrapper. | Själva innehållet kan vara mycket känsligt. | Logg refererar; artifact lagras en gång på sin rätta yta. | **Arkitektur/repo requirement verified**. |
| Evalresultat | `model_evaluations` | Evalkontrakt/resultat/report och länkar till rå runtimeevidens. | Kan innehålla bedömning + testdata. | Evalägd retention; kopiera inte runtime raw events. | **Repo verified**. |

### SillyTavern-källor

- https://github.com/SillyTavern/SillyTavern-Docs/blob/main/Administration/config-yaml.md
- https://github.com/SillyTavern/SillyTavern/blob/release/default/config.yaml
- https://github.com/SillyTavern/SillyTavern/blob/release/default/content/presets/openai/Default.json

### KoboldCpp-källor

- https://github.com/LostRuins/koboldcpp/wiki
- https://github.com/LostRuins/koboldcpp/releases
- Repo-probe: `SillyTavern_UI/harness/Test-KoboldCpp-StorytellerChatProfile.ps1`

### Dia2/Gradio-källor

- https://github.com/nari-labs/dia2
- https://github.com/nari-labs/dia2/blob/main/gradio_app.py
- https://gradio.app/docs/gradio/request
- https://gradio.app/guides/queuing

Observera att upstream `gradio_app.py` defaultar till `nari-labs/Dia2-2B` om den används oförändrad. Den aktuella projektlaunchern på `449b713...` verifierar dock explicit lokal Dia2-1B-binding genom `DIA2_LOCAL_MODEL` och `Dia2.from_local(...)`; 2B-defaulten är alltså inte den projektväg launchern startar.

### SANA/diffusers-källor

- https://huggingface.co/Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers/tree/main
- https://huggingface.co/Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers/blob/main/model_index.json
- https://huggingface.co/Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers/blob/main/README.md
- https://huggingface.co/docs/diffusers/api/pipelines/sana_sprint

Model-repots `model_index.json` anger `SanaSprintPipeline` och `_diffusers_version: 0.33.0.dev0`; detta är modellartefaktens metadata, **inte bevis för vilken diffusers-version som faktiskt installerats lokalt**.

### Windows/NVIDIA-källor

- https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process
- https://docs.nvidia.com/deploy/nvidia-smi/
- https://docs.nvidia.com/deploy/nvml-api/latest/

---

## 4. Minsta gemensamma event-envelope — semantik, inte fryst schema

Ett gemensamt envelope bör bara bära det som behövs för tidsordning, ägarskap och korrelation. Följande är **kandidatsemantik**; Codex/Team Master beslutar senare exakta namn och struktur.

### Gemensamt för nästan alla events

1. **Dokument-/schemaversion** — så att parsern kan skilja formatgenerationer.
2. **Eventidentitet + ordning** — unik eventreferens och sekvens inom operation/capture.
3. **Observerad tid** — UTC och lokal offset; epoch/monoton tid där latens kräver robust differens.
4. **Källtidsstämpel när sådan finns** — separat från när loggern observerade eventet. OTel gör samma distinktion mellan `Timestamp` och `ObservedTimestamp`.
5. **Producent + producentversion** — app/motor/wrapper som faktiskt äger eventet.
6. **Eventtyp/kind** — stabil semantisk klass inom ägaren, inte en global jättetaxonomi.
7. **Severity + outcome/evidence-status** — ett fel är en outcome i sin ägarström; `partial/unverified` måste kunna uttryckas.
8. **Operationell korrelation** — gemensam ID-referens; optional parent/span endast när verklig underoperation finns.
9. **Varaktighet** — endast på events/steps som har definierad start/slut.
10. **Profil-/modellreferens när relevant** — inte obligatoriskt på exempelvis AutoPull.
11. **Artifactreferens/hash när eventet producerar/finaliserar en fil.**
12. **Sanitization/limits/evidence gaps på capture-nivå** — så att läsaren vet vad som medvetet saknas.

### Ska förbli komponent-/eventspecifikt

- SillyTavern: connection mode, backendtyp, endpointklass, requeststatus.
- KoboldCpp: context, usage, finish reason, native `/api/extra/perf`-data.
- SANA: seed/generator, width/height, steps, guidance/scheduler, prompt-hash, warm/cold marker.
- Dia2: prefix/reference-hash, precision, sampling settings, sample rate, audio duration, word timestamp availability.
- Host: PID, working set, read/write transfer deltas, GPU index/utilization/memory.
- Profilorkestrering: from-profile/to-profile, stop/unload/load kvittenser.
- AutoPull: local/remote SHA, clean/dirty, ancestry/FF-decision.
- Artifact: mime/container, bytes, dimension/duration/hash.

**Anti-pattern:** att göra alla fält obligatoriska i ett universellt megaevent. Det skapar null-heavy data, låser terminologi innan runtimes är valda och gör ägarskapet otydligt.

---

## 5. Ägarskap utan redundans — producent → ägarström → konsument → retention

Ägarnamnen nedan är beskrivande **kandidater**, inte beslutade kataloger.

| Producent | Primär rå ägare | Sekundär konsument | Vad får konsumenten lagra? | Retentionprincip — kandidat, ej låst |
|---|---|---|---|---|
| SillyTavern | SillyTavern-specifik runtimeyta | Storyteller operation / incidentgranskning | Referens + korrelations-ID + nödvändig summary, inte kopierad access/consolelogg. | Rolling count+age; exakt N/dagar beslutas lokalt. |
| KoboldCpp | KoboldCpp-specifik runtimeyta | AGPR-2 operation, eval | Referens till request/perf/lifecycle-event och eventuellt hash. | Rolling per operation/process; rå prompt/output kortare/opt-in. |
| AGPR-2 project wrapper | Storyteller-operationens egen sammanfattning om wrappern faktiskt äger hela operationen | Operatör/eval | Endast egen start/slut/steg/refs; kopierar inte SillyTavern/Kobold raw. | Bounded per operation. |
| SANA/diffusers | SANA-/generatorägd runtimeyta | AGPR-3 qualification/eval | Operation summary + artifactref; eval lagrar bedömning, inte runtime raw. | Bounded per imageoperation; raw prompt endast opt-in. |
| Dia2/Gradio | Dia2-/TTS-ägd runtimeyta | AGPR-4 qualification/eval | Operation summary + artifactref/reference-voice hash. | Bounded per render; känsligt raw kortast möjliga retention. |
| Framtida profilorkestrerare | Orkestrerarens state-transition-yta | Alla AGPR operationer | Switch-ID/ref + outcome; inte modellens egna generationevents. | Liten state-transitionhistorik, count+age. |
| Host/GPU | En host-/resourceägare per observerad scope | Runtimeoperationer/eval | Ref till snapshot/capture; undvik att varje modellström kopierar samma nvidia-smi-output. | Kort rolling window + explicit bounded captures. |
| AutoPull | AutoPull-specifik yta | Operatör | SHA/gate/outcome summary. | State-change/attempt-baserad; idle-polls behöver normalt inte persistens. |
| LM Studio | Befintlig `LM-Studio_logs` | Eval/incident | Referens enligt nuvarande kontrakt. | Behåll befintlig policy; flytta inte. |
| Media/story output | Artifactytan | Runtime/eval | Runtime loggar endast path/ref + hash/metadata. | Artifactens egen produkt-/evalpolicy, inte loggerns retention. |
| Eval | `model_evaluations/<eval-id>` | Team Master/Codex | Evalkontrakt, resultat, report, refs till runtimecaptures. | Evalägd; runtimeevidens kopieras inte. |
| Story Creator-runloggar | Befintlig Story Creator-ägare | Team Master | Endast refs till andra lager vid behov. | Separat befintligt ansvar; denna handoff flyttar inget. |

### Felhantering

- Fel **stannar hos producenten som äger det misslyckade steget**.
- Cross-component incident = samma correlation/trace + tidslinje + referenser.
- En orkestrerare får logga “child operation failed” som sitt eget state-resultat, men ska peka på childens felreferens i stället för att duplicera stacktrace/payload.
- “KoboldCpp slutade svara efter GPU-spike” är korrelation. “GPU-spiken orsakade felet” kräver mer evidens och får inte infereras från tidsmässig närhet.

---

## 6. Känsligt innehåll och path-säkerhet

### Föreslagen dataklassning

| Klass | Exempel | Default |
|---|---|---|
| **A — låg känslighet / teknisk metadata** | versioner, durationer, exit/outcome, numeriska settings, seed, bilddimension, sample rate, filstorlek, hash | Får persistens bounded. |
| **B — lokal operativ metadata** | PID, port, project-relative path, modellbasename/revision, GPU-index | Får persistens när frågekontrakt kräver den. Undvik fulla absoluta paths. |
| **C — användar-/mediainnehåll** | Storyteller-text, prompts, captions, genererade bilder/ljud, transkript, referensröst | Default **inte rått i runtime-logg**. Lagra hash/längd/metadata/artifactref. Rå capture kräver explicit diagnostiskt opt-in och kort retention. |
| **D — secrets/auth** | tokens, Authorization/Cookie, API keys, passwords, hemliga headers | **Aldrig rå persistens.** Allowlist av säkra headers är bättre än “logga allt och regex-redigera”. |

### Specifika regler

- **Storyteller-text/prompts:** default hash + UTF-8-byte/teckenlängd + eventuell säker roll/turn-index. Rå text endast när Team Master uttryckligen behöver innehållsdiagnostik.
- **Bild/ljud:** loggen refererar outputfil + SHA-256 + teknisk metadata. Kopiera inte base64, pixelsamples eller waveform.
- **Referensröst:** referera godkänd fil med hash och teknisk metadata; rå ljudfil ligger i sitt artifact/reference-bibliotek. En röst är potentiellt identifierande data även i ett helt lokalt system.
- **Headers:** logga endast allowlistade tekniska headers. `Authorization`, cookies och okända custom headers ska inte persistens.
- **Paths:** repo-/output-root-relative när möjligt. Extern absolut path bör reduceras till redigerad placeholder/basename och vid behov separat hash. Projektets LM-referens gör redan detta.
- **Processkommandon:** lagra executable identity + allowlistade effektiva argument. Rå command line kan innehålla token, user path eller prompt och ska inte vara default.
- **Model-I/O:** samma opt-in-princip som befintlig LM Studio `model_io_events`; sanering är inte bevis att fri text är secret-free.
- **Redactionbegränsning:** regex-/key-redaction kan missa en hemlighet i fri text. Därför är “inte fånga rådata” den primära kontrollen; redaction är defense-in-depth.

---

## 7. Bounded och kraschrobust filpersistens

### Alternativ

| Form | Styrka | Svaghet | Bedömning |
|---|---|---|---|
| **En pretty-JSON-fil per event** | Mycket liten förlustdomän; lätt att atomiskt finalisera. | Filspam, dyr directory traversal, sämre mänsklig operationsöversikt. | Inte default. Bra endast för sällsynta stora fristående events. |
| **En bounded pretty-JSON-fil per operation/capture, atomiskt checkpointad** | Hög läsbarhet, tydlig korrelation, senast kompletta version överlever abrupt avbrott, naturligt byte/eventtak. | Rewrite-amplification om checkpoint sker för ofta. | **Rekommenderad walking skeleton.** |
| **Append till en växande JSON-array/textfil** | Enkel sekventiell skrivning. | En krasch kan lämna ogiltigt dokument; rotation och concurrent writers blir svåra. | Avråds som primär auktoritativ logg. |
| **JSONL** | Bra append/streaming och maskintransport. | Uppfyller inte projektets multiline/pretty-human-readable krav som primär yta; torn final line kräver recovery. | Möjlig framtida sekundär transport/export, **inte primär loggyta**. |

### Minsta persistensstrategi

1. Skapa ett bounded operationsdokument med status `running`/motsvarande semantik.
2. Skriv UTF-8 utan BOM, pretty/multiline JSON.
3. Tempfil i **samma directory/filesystem**, `flush` + `fsync`/Windows commit, därefter replace av målfilen.
4. Bounded retry vid Windows sharing/permission lock; permanent lock = synligt failure, inte tyst framgång.
5. Checkpointa endast vid **grova milstolpar**: start, faktisk model-load sluttid, generation slut, artifact finalize, error/interrupt/final. Inte per token/audio-frame/diffusion-tensor.
6. Hårda tak per operation: serialiserade bytes, eventantal och maximal capturetid där polling används. LM Studio-referensens 8 MiB / 1000 event / 300 s är ett bevisat projektmönster, men nya komponenters exakta tak ska inte kopieras blint utan lokalt test.
7. Finalisera med status, stop reason, counters och explicit evidence gap.
8. Vid hårt processkill kan senaste checkpoint förbli `running`; det är ett **ofullständigt bevis**, inte ett fel som ska döljas.
9. Rotation/retention ska göras via count+age **per ägare**, aldrig en global obegränsad logg. Exakta dagar/counts förblir olåsta.
10. Känsliga opt-in captures ska ha striktare retention än vanlig teknisk metadata.

Python-dokumentationen verifierar att `flush()` + `os.fsync()` flushar buffers till disk och att `os.replace()` är cross-platform replacement API; projektets LM Studio-implementation ger dessutom direkt Windows-prövad bounded retrymodell. Källa: https://docs.python.org/3/library/os.html

---

## 8. Mätbar overhead — liten deterministisk A/B

Instrumentering ska betraktas som en hypotes tills lokal A/B visar att den är billig nog.

### Testdesign

- Använd samma modell/revision, seed, input, settings och varm/kall state per jämförelse.
- Kör interleaved kontroll/instrumenterad variant (t.ex. ABBA) för att minska drift.
- Minst 5 upprepningar per state för screening; öka endast om variationen gör slutsatsen oklar.
- För kvalificeringsgates ska **själva loggingkostnaden mätas separat**: bytes skrivna, antal checkpoints, logger-CPU/RAM och tid i persistens.
- Host-/GPU-sampling ska vara bounded och får inte läggas tätare än vad frågan kräver. `nvidia-smi` är en extern process och dess egen kostnad ska räknas.

### Mätpunkter per profil

**AGPR-2 / Storyteller**

- client request start,
- backend accept/response boundary,
- första token/byte **endast om den aktuella transporten exponerar det verifierbart**,
- total turn latency,
- KoboldCpp native perf/usage/finish,
- RAM/VRAM före/peak/efter.

**AGPR-3 / SANA**

- eventuell cold load start/end,
- instruction accepted,
- generation call start/end,
- bild save/finalize,
- total instruction→beständig fil,
- warm revision utan andra model-load,
- process read-I/O delta + RAM + peak GPU.

SANA-Sprint returnerar den färdiga bilden från pipeline-call. “Första bild”-latens bör därför i baseline betyda första användbara pipeline-output/finaliserad fil, inte ett påhittat streamingmått.

**AGPR-4 / Dia2**

- eventuell cold `_get_dia()` load,
- render start/end,
- waveform returned,
- fil encode/write/finalize,
- total text→beständig audio,
- RAM/VRAM och reference-prefix metadata/hash.

Upstream Gradio-appen returnerar en hel waveform och timestamps efter `dia.generate`. Dia2-projektet beskriver modellen som streaming-capable, men **första-audio-chunk i den nu repo-synliga projektvägen är fortfarande unverified**: launchern exponerar Gradio UI/lazy load, medan den granskade `generate_audio`-funktionen returnerar färdig waveform efter `dia.generate`. Mät därför inte ett falskt “first audio” innan en faktisk streamingpunkt har verifierats.

### Defensibla initiala screeningbudgets — **inte låsta**

Följande är endast startgränser för lokal A/B och måste godkännas/justeras av Codex/Team Master:

- median total runtime: högst cirka **+2 %**,
- p95 total runtime: högst cirka **+5 %**,
- added pre-inference/TTFT overhead för wrapper-only logging: mål **≤20 ms median / ≤50 ms p95**,
- loggerrelaterad peak RAM: mål **≤64 MiB**,
- loggerrelaterad VRAM: mål **0 MiB**; en observerad ökning över cirka **32 MiB** ska utredas,
- vanlig icke-känslig operationslogg: mål **≤1 MiB** och få checkpointwrites; större data kräver explicit motivering,
- hårt capturetak kan initialt använda LM-referensens 8 MiB som screening ceiling, men ska inte automatiskt bli permanent kontrakt.

Budgets ska jämföras med faktisk latens på RTX 3070 Ti; relativa procentsatser räcker inte ensamma för snabba operationer, därför behövs även absoluta millisekundgränser.

---

## 9. Bygg kontra standard — jämförelsematris

| Alternativ | Omedelbar nytta | Kostnad | Huvudrisk | Framtida migration |
|---|---|---|---|---|
| **A. Python/PowerShell-stdlib + komponentwrappers** | Hög: passar redan befintliga launchers/adaptrar, kan ge owner-specific pretty JSON, atomics, hash, process/GPU och artifactrefs direkt. | Låg–medel; egen liten persistens-/saneringskod måste kvalitetssäkras. | Bespoke ID-/eventsemantik kan divergera mellan komponenter om ingen gemensam miniminorm hålls. | Medel: lätt om IDs/timestamps/owner semantics är W3C/OTel-kompatibla från början. |
| **B. Full OpenTelemetry SDK + Collector nu** | Standardiserad trace/span/logmodell, exporters och framtida backendintegration. | Hög: Python + Node + ev. browser/Gradio + wrappers måste instrumenteras; Collector blir ny process/config/dependency. | Överarkitektur, dubbla loggar, större dependency graph, oklart ägarskap och risk att OTel-export blir “sanning” parallellt med projektets pretty-JSON. | Låg senare men dyr nu. |
| **C. Begränsad hybrid** | Hög: owner-specific bounded pretty JSON förblir auktoritativt; operation-ID/trace-semantik och HTTP `traceparent` används där det redan passar. | Låg–medel. Ingen Collector krävs i första steget. | Kräver disciplin att inte kalla varje ID ett “span” utan riktig span lifecycle. | **Lägst total risk:** senare OTel-export/instrumentering kan läggas på wrapper/orchestratorgränser. |

OpenTelemetry Collector är officiellt en vendor-neutral receiver/processor/exporter för telemetry. OTel Python/JS kräver SDK/instrumentation packages för manuell/auto-instrumentering, och JS auto-instrumentation ökar dependency graph. För ett lokalt single-user-system utan broker eller observability-backend finns därför ingen primärkälla som visar att Collector skulle ge högre första-ROI än projektets redan bevisade bounded-file-mönster.

Primärkällor:

- https://opentelemetry.io/docs/collector/
- https://opentelemetry.io/docs/languages/python/instrumentation/
- https://opentelemetry.io/docs/languages/python/
- https://opentelemetry.io/docs/languages/js/
- https://opentelemetry.io/docs/languages/js/libraries/

**Rekommendation: C — begränsad hybrid.** Börja med stdlib/wrapperbaserad, komponentägd pretty-JSON och standardkompatibel correlation semantics. Lägg inte till Collector, exporter eller full OTel SDK förrän en konkret broker/flerprocessgräns eller query-backend gör spans/export materiellt nyttiga.

---

## Rekommenderad minsta walking skeleton — ansvar och eventflöde

Detta är ett **ansvarsflöde**, inte ett schema- eller katalogbeslut.

1. **Operationsgränsen skapar en korrelationsidentitet** när Team Master initierar en verklig AGPR-operation.
2. **Den komponent som äger operationen öppnar ett bounded pretty-JSON-dokument** med producer/version, säker profil-/modellreferens, limits och explicit evidenslucka.
3. **Input registreras som metadata/hash som default.** Rå Storyteller-text, image prompt, TTS-script eller voice prefix fångas endast explicit.
4. **Lifecycle registreras endast där den faktiskt sker.** Om pipeline/modell redan är resident loggas reuse; om wrappern laddar den loggas load start/end. Detta är kritiskt för SANA warm-revision-gaten.
5. **Inference/render omges av monotona timers.** Native perfdata länkas när den finns (KoboldCpp); annars loggas wrapperns exakta gränser.
6. **En lågfrekevent host/GPU-observation tas före/under/efter endast när frågekontraktet kräver resursevidens.** Samma rå snapshot dupliceras inte in i flera ägarloggar.
7. **Output skrivs av artifactproducenten och finaliseras.** Loggern registrerar ref, bytes, hash och teknisk metadata; media/storybytes dupliceras inte.
8. **Error/interrupt finaliseras i samma ägarström** med stop reason, sista slutförda steg och evidensstatus. Ingen generell fellogg.
9. **Cross-component operationer länkas via correlation/trace-referens.** En parent summary får länka child-owner events, inte kopiera dem.
10. **Retention sker per faktisk ägare och känslighetsklass** med count+age och separat strikt opt-in-policy för raw content.
11. **Walking skeleton implementeras först där projektet redan har högvärdesgates:** AGPR-3 cold+warm imageiteration och AGPR-4 neutral/laugh/scream render. Därefter återanvänds mönstret för AGPR-2 utan att göra Storyteller-harness till generell profilmanager.
12. **OTel införs först när ett verkligt nytt behov uppstår:** broker, flera samtidiga processer/tjänster, central query/backend eller extern exporter. Då kan befintlig operationell ID-semantik mappas till trace/span och owner events exporteras utan att byta auktoritativ råägare.

Denna ordning svarar direkt på fråga 1–10 och undviker att bygga telemetry för hypotetiska dashboards.

---

## Fem kvarvarande lokala datapunkter med högst informationsvinst per kostnad

Endast Codex/Team Master kan verifiera dessa eftersom de berör lokala/ospårade runtimes eller faktiskt runtimebeteende.

| Rank | Lokal datapunkt | Varför hög ROI | Minsta verifiering |
|---:|---|---|---|
| 1 | **AGPR-4:s faktiska beständiga audio-/interruptgräns under lokal körning** | Launchern är nu repo-verifierad och 1B/lazy-load/Gradio-vägen är känd, men den granskade koden visar ingen projektägd persistent audio-finalize eller verifierad cancel/stop-kvittens. Detta är den största kvarvarande Voice-observabilityluckan. | Kör den redan planerade bounded qualificationen och verifiera var Gradio placerar output, om projektet kopierar/finaliserar en beständig fil, samt vilket event/processbevis som finns vid avbrott. |
| 2 | **Faktisk AGPR-3 SANA-runtime efter installation** | Avgör om samma `SanaSprintPipeline`-objekt lever över revisioner och vilken diffusers/torch-version som körs — centralt för “ingen viktomladdning”. | Inspektera installerad wrapper/sessionkod + package versions; senare kvalificeringsrun korrelerar load-events med process disk-read-delta. |
| 3 | **Den lokala FF-only AutoPull-watcherns implementation** | Exakt hook saknas i GitHub-trädet. Utan den kan vi inte veta om poll/attempt/state change är rätt eventgräns eller vilka Git-kommandon/branchgates som redan finns. | Läs watcherfilen read-only och kartlägg fetch/status/ancestry/FF/skip branches samt befintlig output. |
| 4 | **SillyTavern 1.19.0:s faktiskt aktiva Storyteller-connection mode och headerpropagation** | Custom Chat-vägen har verifierad custom-header-yta; Text Completion-baselinen är inte verifierad. Detta avgör om W3C kan gå ST→backend utan proxy/extension. | Inspektera sparad aktiv connection config; kandidatprova en ofarlig custom traceheader mot en lokal testmottagare när Codex bedömer det lämpligt. |
| 5 | **Instrumentation-overhead under de redan planerade AGPR-3/4 qualification gates** | Låser sampling/checkpoint-budget på faktisk RTX 3070 Ti i stället för antaganden. | Interleaved A/B med samma seed/input; mät total latency, first usable output, logger write time/bytes, RAM, GPU och process disk I/O. |

Ingen av dessa datapunkter krävs för att avsluta **researchen**; de krävs för att Codex ska kunna frysa implementationen defensibelt.

---

## Kort riskregister

| Risk | Failure mode | Motåtgärd |
|---|---|---|
| **Dubbelägarskap** | Samma backendfel/hostsample kopieras till AGPR-, runtime- och eval-loggar; senare skiljer versionerna sig. | Exakt en rå ägare. Övriga lager lagrar refs + correlation + egen outcome. |
| **Loggspam** | Token/frame/step/poll-events fyller disk och gör incidenter svårare att läsa. | Grova milestones, event/byte/time caps, sampled resource telemetry, state-change-baserad AutoPull-loggning. |
| **Hemlighets-/innehållsläckage** | Prompt, story, voice sample, authheader eller absoluta user paths hamnar i logg. | Default metadata/hash, allowlist headers/argv, project-relative paths, explicit raw opt-in, kort raw retention. |
| **Falsk kausalitet** | Samtidig VRAM-spike antas orsaka backendfel eller polling antas bevisa varför modell unloadades. | Separera `observed`, `inferred`, `acknowledged`; dokumentera evidence gaps och kräv ägarkvittens för orsak. |
| **Versionsdrift** | Upstream CLI/API/logformat ändras och parsern fortsätter “lyckas” felaktigt. | Producer/version i capture, strict parse + unknown-field preservation där rimligt, fail-visible, lokala smoke gates vid uppgradering. |
| **Mätpåverkan** | `nvidia-smi`, fsync eller för tät checkpoint försämrar den latens som mäts. | A/B, låg sampling, coarse checkpoints, mät loggerns egen tid/bytes; hårda budgets låses först lokalt. |

---

## Källförteckning och verifierade fakta

### Projektkällor — synkad GitHub-bas `449b71341bb8b7e1dddd319fc8dd420dca58e021`

- `AGENTS.md`
- `LM-Studio_logs/README.md`
- `LM-Studio_connections/LM-Studio_observability/README.md`
- `LM-Studio_connections/LM-Studio_observability/observability_common.py`
- `LM-Studio_connections/LM-Studio_observability/capture_host_resource_snapshots.py`
- `[ CURRENT ARCHITECTURAL PROJECT STATE ].md`
- `docs/docs_plan/[PLAN] - [8] - [LOCAL AI ROLE PROFILES] - [FRYSTA BESLUT].md`
- `LOCAL_AGENTS/AGPR-2-STORYTELLER/ROLE-CRITERION.md` — verifierat tom.
- `LOCAL_AGENTS/AGPR-3-IMAGE-MASTER/ROLE-CRITERION.md`
- `LOCAL_AGENTS/AGPR-4-VOICE-MASTER/ROLE-CRITERION.md`
- `SillyTavern_UI/harness/README.md`
- `SillyTavern_UI/harness/Start-KoboldCpp-StorytellerRuntime.ps1`
- `SillyTavern_UI/harness/Start-SillyTavern.ps1`
- `SillyTavern_UI/harness/Test-KoboldCpp-StorytellerChatProfile.ps1`
- `scripts/Start-AGPR-4-Voice-Master-UI.ps1` — lokal-only Gradio, explicit Dia2-1B/Mimi, lazy `Dia2.from_local`, CUDA BF16, queue concurrency 1.
- rekursivt Git tree för den synkade basen — ingen repo-spårad path med `AutoPull` hittades.

### Externa primärkällor

**W3C/OpenTelemetry**
- https://www.w3.org/TR/trace-context/
- https://opentelemetry.io/docs/concepts/context-propagation/
- https://opentelemetry.io/docs/specs/otel/logs/data-model/
- https://opentelemetry.io/docs/specs/otel/compatibility/logging_trace_context/
- https://opentelemetry.io/docs/collector/
- https://opentelemetry.io/docs/languages/python/instrumentation/
- https://opentelemetry.io/docs/languages/js/libraries/

**SillyTavern**
- https://github.com/SillyTavern/SillyTavern-Docs/blob/main/Administration/config-yaml.md
- https://github.com/SillyTavern/SillyTavern/blob/release/default/config.yaml
- https://github.com/SillyTavern/SillyTavern/blob/release/default/content/presets/openai/Default.json

**KoboldCpp**
- https://github.com/LostRuins/koboldcpp/wiki
- https://github.com/LostRuins/koboldcpp/releases

**Dia2 / Gradio**
- https://github.com/nari-labs/dia2
- https://github.com/nari-labs/dia2/blob/main/gradio_app.py
- https://gradio.app/docs/gradio/request
- https://gradio.app/guides/queuing

**SANA / Diffusers**
- https://huggingface.co/Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers/tree/main
- https://huggingface.co/Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers/blob/main/model_index.json
- https://huggingface.co/Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers/blob/main/README.md
- https://huggingface.co/docs/diffusers/api/pipelines/sana_sprint

**Windows / NVIDIA / persistence**
- https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process
- https://docs.nvidia.com/deploy/nvidia-smi/
- https://docs.nvidia.com/deploy/nvml-api/latest/
- https://docs.python.org/3/library/os.html

### Explicit `unverified` / öppna evidensluckor

- Exakt lokal form och capturepunkt för de ospårade/tillfälliga `logs/`-katalogerna — avsiktligt ej antagen.
- Voice Master-launcherns tidigare okända form är **inte längre en lucka** efter synk till `449b713...`; kvarvarande lucka är dess faktiska runtime-output/interruptbeteende och projektägd persistent audio-finalisering.
- Exakt AutoPull watcher-fil/hook — beteendekontrakt finns i `AGENTS.md`, implementation syns inte i det spårade trädet på den synkade basen.
- SillyTavern Text Completion-baselinens möjlighet att bära custom W3C/header — Custom OpenAI-preset stöder custom headers, men baselinevägen är inte källverifierad.
- KoboldCpps eventuella stöd för att exponera/eko-logga ett inkommande `traceparent` — ingen primär källa hittad; caller-wrapper måste därför äga korrelationen tills motsatsen verifieras.
- Lokal installerad Dia2-/Gradio-version är ännu inte versionsinventerad i denna research. Projektvägen är däremot verifierat Gradio-baserad med in-process lazy `Dia2.from_local(...)` genom `scripts/Start-AGPR-4-Voice-Master-UI.ps1`.
- Lokal diffusers/torch-version för installerade SANA-Sprint; model metadata anger bara vad model-repot skapades för.
- “First audio chunk” i den lokala AGPR-4-runtimevägen; upstream-modellen är streaming-capable, men upstream Gradio-funktionen som granskats returnerar den färdiga waveformen efter `dia.generate`.
- Exakta permanenta retentiontal, loggpaths, event-/fältnamn och schema — avsiktligt **inte låsta**.

Ingen extern Claude-/underagenttext användes som evidens i denna research. Slutsatserna ovan kommer från direkt repo-evidens och primära upstreamkällor.

---

## Verifiering och klarsignal

Researchens nio frågor har konkreta svar eller uttryckligen avgränsade `unverified`-luckor. Den obligatoriska syntesen innehåller:

1. prioriterat operatörsfrågekontrakt med minsta evidens,
2. komponentmatris med producent/ägare/capture/känslighet/boundedness/källstatus,
3. jämförelsematris stdlib/wrappers vs OpenTelemetry vs hybrid,
4. walking skeleton utan frysta permanenta namn/schema,
5. fem lokala hög-ROI-datapunkter,
6. riskregister för dubbelägarskap, spam, secrets, falsk kausalitet, versionsdrift och overhead.

Före GitHub-publicering verifierades endast denna handoff-delta som UTF-8 utan BOM och med whitespace/diff-check. GitHub-scopekontrollen ska visa exakt en logisk handoffändring ovanpå den synkade basen `449b713...`: denna handoff som innehållsuppdatering och `[INCOMPLETE] → [COMPLETED]`-rename. Inga modeller, servrar, GPU-jobb eller lokala projektprocesser startades.

### PIPSA

**Ingen processomstart krävs.** Detta är research-only. Ingen launcher, runtime, loggimplementation, dependency, schema, profil eller lokal process ändras.

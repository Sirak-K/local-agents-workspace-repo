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

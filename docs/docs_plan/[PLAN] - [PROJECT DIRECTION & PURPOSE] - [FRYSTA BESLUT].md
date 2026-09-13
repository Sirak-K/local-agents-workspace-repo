# PROJECT DIRECTION & PURPOSE — FRYSTA BESLUT

Status: Fastställda projektledande beslut  
Datum: 2026-09-13

## 1. Slutmål

- Projektets yttersta mål är att utveckla, pröva och förstå lokala modeller som kan bli Team Masters framtida lokala agenter.
- LM Studio-baserat Frontier-as-Evaluator-arbete och den tekniska plattform som krävs för det är projektets absoluta prioritet och styrande arbetsriktning just nu.
- Frontier-agenter utvärderar kandidaterna; kandidaten är systemet under test och får aldrig tillgodoräknas Frontier-agentens analys eller arbete.
- Codex är evaluator med prioritet 1 och äger primär lokal orchestration, evidensgranskning och felklassificering.

## 2. Enda aktiva harness

- Vanliga LM Studio Desktop och dess Local Model API är projektets primära och enda aktiva harness för kommunikation mellan Frontier-agenter och lokala agentkandidater.
- Native LM Studio REST API v1 är primär transport. Bionic, CDP och Bionics interna sessions-/Projects-API är inte del av den aktiva evalarkitekturen.
- Godkänt transportundantag 2026-09-13: officiell LM Studio JavaScript-SDK för avbrytbar evalgenerering; native REST för modellinventering och generell observability. SDK-stopp använder den pågående predictionens `cancel()` och inväntar dess slutliga serverstatistik. Modellen ska förbli laddad; unload/reload och kill av delade serverprocesser är inte normalt avbrott.
- Team Master godkänner en minimal tidsbegränsad auth-anpassning för publicerad JavaScript-SDK 1.5.0, som saknar dagens `apiToken`: använd exakt tokenmappning från LM Studios officiella källkod, verifiera giltig token och nekad ogiltig token, aldrig anonym fallback. Ta bort anpassningen vid byte till publicerad SDK med direkt tokenstöd. Publicerad Python-SDK 1.5.0 används inte; dess auth-kontrakt motsvarade inte aktuell dokumentation.
- Bionic är legacy/deprecated och har ingen aktiv prioritets-, harness- eller plattformsstatus. Kvarvarande Bionic-bundet transport-, logg-, sessions- eller runtimeägarskap i aktiva dokument är opålitlig grund enligt NIOTUF och ska ersättas innan beroende implementation används.
- Befintliga filer eller profilmappar med `bionic` i namnet får inte behandlas som aktuell runtime-sanning enbart på grund av sitt namn. Bred namn-/strukturmigrering är en separat operation och ska inte blandas in i loggimplementationen utan ett konkret ägarbehov.

## 3. Första agentroll och modell-audition

- `0-WORKER` är den första och högst prioriterade agentrollen.
- `0-WORKER` är den enda aktiva agentrollen tills Team Master uttryckligen låser upp en annan roll. `AGENT-1-GENERAL/` och `AGENT-2-STORYTELLER/` är utanför scope och ska inte läsas, ändras eller användas som planeringsgrund.
- `LOCAL_AGENTS/AGENT-0-WORKER/` är modellneutral men agentrollspecifik. Gemensam rollkontext, rollskills, rolltools, uppgifter, fixtures och bedömningslogik ska återanvändas mellan modeller så att kandidater jämförs mot samma rollkrav.
- Varje modell får en egen undermapp under `AGENT-0-WORKER/`. Granite-undermappen äger Granite-specifika fakta, konfiguration, template och motiverade modellavvikelser, men får inte bli en parallell ägare av 0-WORKER-rollens gemensamma evalkontrakt.
- Rollen ska kunna ta emot instruktioner och utföra konkret, verifierbart read/write-arbete med en uttryckligen exponerad tool-yta.
- Granite 4.1 3B är första modellkandidaten. Syftet är att empiriskt fastställa hur långt en liten, tool-enabled 3B-modell kan nå innan projektets standard för modellstorlek höjs.
- En liten modellstorlek är inte i sig ett underkännande. Kandidaten bedöms på verifierad rollförmåga, instruktionsefterlevnad, korrekt tool-use, tillförlitlighet och praktisk tid till användbart resultat.
- Harness-, transport-, template-, konfigurations-, tool-, permission- eller loggfel får aldrig klassificeras som modellfel.
- Håll fynd och felorsaker åtskilda efter ägare även i dokumentationen: modellens råutdata och modellspecifika villkor i modellmappen, LM Studio-/SDK-/harnessens dispatch/stopp i plattformsytan och uppgiftens faktiska PASS/FAIL samt WORKER-relevans i evalytan. Samma run-id får länka perspektiven; en oavgjord gränsorsak ska inte påstås vara löst av någon av dem.

## 4. Loggägarskap och separata strömmar

- `LM-Studio_logs/` är den enda projektägda roten för evaluation-oberoende LM Studio-loggar och runtime-evidens. Varje fullständig evalkörning ägs separat av `model_evaluations/<eval-id>/`.
- Evaluation-oberoende observability ska etableras före evalkörningen och delas efter konkret ansvar: `server_events`, `model_lifecycle_events`, `model_io_events` och `host_resource_snapshots`. `model_lifecycle_events` ska primärt observera autentiserad `GET /api/v1/models`-state och dess förändringar; den lokalt observerade men inte officiellt dokumenterade CLI-källan `runtime` får inte vara ensam permanent grund.
- Varje bounded capture ska bli exakt en självständig pretty-JSON-fil i sin ströms filserie; capturemetadata, gränser, fel och evidensluckor ligger i samma fil. Ett separat manifest skulle dubblera ägarskap och ska inte skapas. Händelser eller fel får inte kopieras till en generell tvärgående `error_logs`-fil; fel stannar hos den ström som äger händelsen.
- `model_evaluations/<eval-id>/` är den enda artefaktroten för en fullständig evalkörning och får endast innehålla dess run-mappar, evalspecifika kontrakt, resultat, bedömningar, REPORT SUMMARY och referenser till relevant rå evidens. Generella server-, process-, modell-load/unload- eller hosthändelser får inte lagras där.
- LM Studios egna app-/serverloggar är externa källor. Projektet får fånga dem read-only men ska inte skapa en konkurrerande andra sanningskälla eller ändra originalen.
- Alla projektägda JSON-loggar ska vara pretty/multiline, UTF-8 utan BOM och ha lokalt läsbara tidsstämplar. Absoluta projektsökvägar och hemligheter får inte loggas när relativa eller redigerade värden räcker.
- Varje capture och eval-run ska ha unik identitet, avgränsad tid/disk, källangivelse och explicit uppgift om evidensluckor. `model_io_events` ska dessutom vara explicit opt-in eftersom strömmen kan innehålla andra klienters fulla formatterade prompter och svar.
- Etablerad generisk observability är bounded on-demand-capture, inte en alltid aktiv bevakare. Polling bevisar inte load/unload-orsak och fångar inte automatiskt misslyckade loadförsök eller full crashhistorik. Sanerad model-I/O är inte byte-exakt rå input, och fri text får inte antas vara helt hemlighetsfri enbart på grund av redactionfilter.

## 5. Sessions- och eval-evidens

- Fristående prober använder `store: false` för att undvika dold historik.
- Verkliga flerstegsprober får använda `store: true` och `previous_response_id`, men LM Studios lagrade chatstate är inte projektets revisionsbevis.
- Stateful körningar ska projektlogga hela turordningen samt varje `response_id`/`previous_response_id` utan att duplicera evaluation-oberoende råloggar.
- En kontrollerad eval-run ska kunna knyta ihop exakt instruktion, runtimeförutsättningar, modell-/instansidentitet, effektiv känd konfiguration, rått API-svar, extraherat svar, LM Studio-statistik, tool-evidens, verifieringsutfall, felklass och relevanta källfingerprints.
- Varje fullständig evalkörning ska avslutas med exakt en `[EVAL] - [<eval-id>] - [REPORT SUMMARY].md` i `model_evaluations/<eval-id>/`. Rapporten syntetiserar och länkar evidence utan att ersätta eller skriva om råa run-filer och avslutas med de fyra obligatoriska ERQER-frågorna för extern förbättringsgranskning.

## 6. Frontier-evaluatorn In-The-Loop

- Codex får inte låsas i ett enda blockerande anrop tills WORKER är färdig. Varje aktiv ERST ska ge bounded, löpande evidens och lämna evaluatorn tillgänglig för granskning, avbrott och nästa beslut under körningen. Automatisk watchdog kompletterar, men ersätter inte, evaluatorns möjlighet att ingripa.
- Evaluatorn ska kunna begära stopp vid säkerhetsrisk, scopeöverträdelse, no-progress/tool-loop, konkret brist i evaldesign eller harness samt när fortsatt körning saknar motiverat beslutsvärde. Stopp får inte kräva att modellen först svarar färdigt. Det förbjuder inte kandidatens egen legitima återhämtning när fortsatt arbete är säkert och informativt.
- Avbrott är en obligatorisk runtimegate före berörd eval: verifiera att modellgenerering upphör inom en före körning specificerad stoppbudget, att inga nya tools dispatchas och att redan pågående tools/processer stoppas eller hanteras enligt en verifierad bounded policy. Stängd SSE/HTTP-klient eller timeout är inte i sig server-/toolstopp. Avbrott återställer inte redan utförda skrivningar; granska eftereffekter och fixtures före nytt försök.
- Om en ERST missförstås ska Codex skilja konkret otydlig/motsägelsefull instruktion, felaktig fixture/bedömare eller saknad runtimeförutsättning från kandidatens beteende under ett korrekt kontrakt. Korrigera det faktiska eval-/harnessfelet, inte modellens svar till ett förväntat facit. Vid oklar orsak förblir klassificeringen öppen.
- Bevara originalförsökets partiella evidens, avbrottstid/skäl, stopphandling och verifieringsutfall. En korrigerad instruktion, fixture, grader eller annan evalförutsättning ska versioneras och följas av ett nytt länkat försök med färsk kontrollerad kontext. Originalet får inte döljas eller räknas som kandidatfel om design-/harnessbrist gjorde det ogiltigt; användbart observerat beteende får fortfarande redovisas med begränsning.
- Direkt korrigerande meddelanden i samma task/session är tillåtna som separat märkt assisterad diagnostik när den verifierade runtimeytan tillåter dem. De får inte tyst ändra en kontrollerad baseline eller räknas som oassisterad rollförmåga. Planerad interaktion som ingår i uppgiftens ursprungliga kontrakt är däremot en legitim mätning av den avsedda interaktiva förmågan.
- Hög ROI betyder att förbättra uppgiftens tydlighet, relevans och evidensvärde med minsta motiverade omtag; det är inte en garanti för att varje ERST ger framgång. Ingen blind retry eller lättade kriterier för att få PASS. Bevara versionsbundna jämförelser och tidigare verifierade styrkor.

## 7. Konfiguration och evaldesign före modellbrister

- Vid svagt eller oväntat utfall är den första arbetshypotesen felaktiga eller suboptimala förutsättningar, inte kandidatens egna brister. Utred först modellspecifik effektiv konfiguration och identitet/template, därefter modellneutral konfiguration och runtime/tools/permissions, sedan uppgiftens tydlighet, instruktioner, fixtures och bedömare. Kandidatbegränsningar övervägs först när de relevanta förutsättningarna är oberoende verifierade.
- Hypotesordningen bestämmer utredningen, inte dess slutsats. Flera orsaker kan samverka; evidensluckor innebär öppen klassificering, inte automatiskt modellfel eller automatiskt konfigurationsfel.
- Frontier-evaluatorn är själv en probabilistisk LLM. Missförstånd och komplexa samspel mellan två LLM:er, konfiguration och tools gör dess orsaksbedömning osäker. Därför krävs särskild försiktighet och oberoende kontroll av faktisk input, API-/tool-/diskevidens och bedömningsvillkor. Motivet är en projektstyrande försiktighetsprincip, inte ett verifierat generellt påstående att LLM-utvärdering alltid är svårare än andra uppgifter.
- Spara kontrollerade lager, evidens/luckor, hypotes, korrigeringens ägare och ändring samt länkat versionerat återtest. Bevara originalutfallet och tidigare verifierade styrkor. Regeln får inte användas för att lätta säkerhetskrav, ge kandidaten facit, ändra låsta villkor mitt i en run eller söka blint efter PASS; samma-session-coaching är assisterad diagnostik.

## 8. Implementationsordning och säkerhet

- Den aktuella avbrottsslicen ägs av `LM-Studio_for_codex/lm_studio_sdk_prediction.mjs` och `interruptible_prediction.py` (SDK-transport och bounded IPC), `agent-0-tools/worker_tool_process_control.py` (ägda Windows-processgrupper) och `agent-0-eval/controlled_run.py` (start/insyn/stopp och evalspecifik evidens). Runnern får bara starta uttryckligen vald redan laddad SDK-instans; ingen JIT-laddning eller automatisk retry. Tools kräver uttryckligt ägarskap och stoppverifiering; externa/delade MCP-processer är inte täckta.
- Första slicen är diagnostisk, inte en implementation av alla Evaluation Rounds. Separat stoppsignal ska fungera även före första token. Löpande evidens persisteras bounded och atomiskt; stoppskäl, partiellt svar och slutligt stoppkvitto bevaras. Saknat kvitto betyder overifierat stopp, aldrig framgång på timeout. Live genereringsstopp och legitim slutförandeprobe krävs före kandidatbedömning.
- Första verktygsfria screeningens exakta engelska uppgifter och förhandsmärkta kvalitativa kalibrering ägs av `agent-0-eval/instruction_following_catalog.json`; strukturell bedömning och progressionskontroll av `instruction_following_grading.py`. SDK-undantaget gäller även IMSLE: färsk Chat med enbart aktuell user-instruktion och ingen projektägd System Prompt, rollfil, tool/skill, projektfil eller dold historik. Templatens effektiva standardkonditionering kontrolleras och redovisas separat; detta mäter minimal explicit projektkonditionering, inte okonditionerad basförmåga. JSON-grammatik/structured-output-styrning får inte maskera den instruktionsefterlevnad som mäts. Kända goda/dåliga svar kontrolleras före livebedömning; kvalitativ grundning kräver dokumenterad evaluatorgranskning, inte nyckelords-PASS.
- Konditionering gör inte en jämförelse ogiltig om relevant kontext och övriga villkor är låsta och redovisade. Ingen generell regel förbjuder rollkontext i senare agent-eval: den avsedda produktionskonfigurationen är också ett legitimt system under test. Ett separat med/utan-kontext-experiment kan mäta observerat utfallsdelta, men är inte obligatoriskt inför första IMSLE och startas inte automatiskt efter den. Mängden kontext är inte ensam ett mått på kapacitet eller integrationskostnad; innehåll, runtime/tools, korrekthet, tid och kontrollerade konfigurationsskillnader måste hållas isär.
- Förkontrollen får läsa laddad modellidentitet, kontextlängd och promptformat utan generering. Codex har mandat att själv ladda/avlasta den utvalda kandidaten för en uttryckligen begärd bounded eval; runnern får inte implicit JIT-ladda. Saknade nödvändiga effektiva värden eller live-stoppbevis redovisas som evidensluckor, inte kandidatfel. Första screening omfattar högst ett försök per tre uppgifter, stoppar vid relevant fel och får inte auto-fortsätta till bekräftelser eller fil-/toolarbete. Efter sammanfattningen lämnas kandidaten utan ytterligare generering tills Team Master svarar.
- Team Masters svar efter första screeningen prioriterar två separata frågor i varje ERST: klarade kandidaten den faktiskt avsedda uppgiften, och säger utfallet något relevant om framtida verkligt 0-WORKER-arbete? Endast uppgiftens i förväg kända krav på resultat, scope, säkerhet och nödvändigt format får styra godkännande. Kosmetiska avvikelser får dokumenteras men inte förvandlas till nya eller retroaktiva underkännandekriterier. Ingen generell kvot av syntetiska repetitionsprober ska fördröja ett säkert, representativt nästa arbetsprov; bred tillförlitlighet påstås ändå inte från enstaka träffar. Fil-/tooltest kräver fortfarande separat bevisad verktygstransport, isolering, avbrott och oberoende diskfacit.
- Ett fullbordat modellsvar är inte samma sak som en fullbordad WORKER-uppgift. Om modellen begär ett verktyg som text men ingen faktisk tool-exekvering sker är uppgiften inte klarad i det prövade gränssnittet, även om orsaken ännu inte kan tillskrivas modellen. En senare strikt och dokumenterad transport-/tolkningskorrigering får prövas i ett nytt försök; dess framgång ersätter aldrig det ursprungliga misslyckandet. Ingen rollfil eller annan projektkontext ska påstås ha varit injicerad när endast uppgift och nödvändigt tool-schema gavs.

1. Ersätt aktiv Bionic-bunden plan-, regel- och EVAL-grund som annars skulle styra implementationen.
2. Etablera separerad evaluation-oberoende capture för LM Studio-server, runtime, model-I/O och relevanta host-resurser.
3. Verifiera varje ström isolerat utan automatisk modelladdning eller långvarig bakgrundskörning.
4. Etablera därefter `model_evaluations/<eval-id>/` som evalspecifik artefaktrot som refererar till, men inte duplicerar, råa strömmar.
5. Verifiera löpande observation, evaluatorns tillgänglighet och verkligt request-/genereringsavbrott; verifiera dessutom tool-/processavbrott före toolarbete.
6. Börja först därefter den kontrollerade Granite 4.1 3B-auditionen för `0-WORKER`.

- Den första verktygsfria Granite-screeningen kördes 2026-09-13 efter egen modelladdning, verkligt verifierat stopp och kontroll av faktisk SDK-readback. Tre uppgifter mötte låsta kriterier och ger endast preliminär framgång; längre-än-begärt svar i tredje uppgiften redovisas separat. Ett tidigare försök med rätt modellsvar var ogiltigt på grund av jämförelsefel mellan rå och loggsäkrad konfiguration; det bevaras som harnessfynd, inte kandidatfel. Ingen logg- eller evalrunner får automatiskt starta en tung modell, skapa obegränsad processlast eller fortsätta utan en explicit bounded körning.
- Dokumenterad design, grön transportprobe eller lyckad formatsvarskontroll är inte bevis på agentförmåga.

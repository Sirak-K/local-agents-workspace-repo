# Codex — lokal arbetsordning och verifieringsfynd

## Tidigare kollisionsfri arbetsordning och nytt ägarskap

Tidigare prioriterades Codex egna steg efter lägsta risk för konflikt med ChatGPTs handoff; därför utfördes källåtkomst i steg 10 först. Team Master har nu avslutat ChatGPTs PFMIE-arbete och överfört hela återstående roadmapen till Codex. Den enda aktuella statuskällan är den sammanslagna `[PLAN] - [4] - [PREPARE FOR MASSIVELY IMPROVED EVALS] - [ROADMAP].md`.

Tidigare skrevs endast den separata Codex-roadmapen, detta verifieringsunderlag och `model_evaluations/comfy_ui_eval-playground/source_snapshots/`. Den separata roadmapen är nu borttagen. Framtida ändringar görs i ansvarsrätt projektfiler enligt den sammanslagna ordningen; historiskt ChatGPT-underlag är evidens, inte en aktiv parallell skrivyta.

Steg 1–3 är levererade/verifierade offline och steg 2 därutöver i faktisk lokal FF. Steg 4 kräver separat livekontroll; steg 7 och 9 följer sina respektive nya kodslices. Steg 16:s statiska alternativ är valt; senare frontendkrav behöver separat öppningsbevis. Steg 17–18 tillämpas vid varje relevant integrations-/ERST-gräns, inte som krav att invänta alla sena förberedelser.

## RMS 2/18 — delkontroll 2026-09-14 01:27:09 +02:00

- `git ls-remote origin refs/heads/main` och lokal `origin/main` var båda `194f3426e6135d833819a6cef1210606df7606cf` vid kontrollen; ingen fetch/merge/indexmutation behövdes.
- Lokal installer och `git show origin/main:scripts/github_autopull_chatgpts_repo_work/install_main_autopull.ps1` hänvisade fortfarande till den saknade gamla `tools/main_autopull_watcher.ps1`.
- Riktad process- och Startup-inspektion hittade ingen watcher/startuplauncher för `local_agents_workspace`. Två andra projekt hade watchers; dessa lämnades orörda. Själva inspektionsprocessen räknades inte som watcher.
- Steg 1-reparation, installation, verklig FF-mottagning samt mottagande ChatGPT-sessions faktiska write/testförmåga återstår att verifiera. Screenshotens auktorisering räcker inte som genomförd mottagning.
- Oreparerad installer exekverades inte och ChatGPTs implementation togs inte över. Status är delkontrollerad, inte färdig.
- Standardkontroll: [Git merge](https://git-scm.com/docs/git-merge) definierar att `--ff-only` vägrar icke-FF. FF ändrar dock branch/arbetsfiler; det användes inte som en ofarlig dry-run. [Git fetch](https://git-scm.com/docs/git-fetch) skiljs från worktree-integration.

## RMS 10/18 — utfört lokalt källunderlag

- Källa: den disponibla WF-1-A-kopian samt två små specs/promptdocs från comfy-projektet. Inga modellvikter, media eller inaktiva agentrollmappar lästes.
- Sex filer skapades under `model_evaluations/comfy_ui_eval-playground/source_snapshots/`, totalt 44094 bytes: workflow, specification, prompting, visad nodpalett, källmanifest och README.
- Source manifest äger faktisk insamlingstid, relativa källpaths, original-/snapshothashar, radslutsnormalisering och evidensbegränsningar. JSON-data är oförändrad jämfört med originalkopian; svenska/specialtecken är UTF-8 utan BOM.
- WF-1-A innehåller 15 noder, 16 länkar och 14 nodtyper utan subgrafdefinitions. Kontrollerade id-/endpoint-/slot-/backreferenser samt kvarvarande input/outputreferenser gav inga fynd. Detta är inte full schemavalidering eller runtimekontroll.
- Relevanta playgroundföräldrar och vald workflowfil hade inga observerade reparse-/junction-/symlinkattribut; snapshots är verkliga filer. Alla registrerade snapshothashar och de tre ursprungskällornas hashar verifierades efter skapande.
- Vald workflowtext innehöll inga upptäckta absoluta hostpaths; små specs granskades innan kopiering. Inga innehållsredaktioner behövdes. Credentialkontrollen var en begränsad källgranskning, inte bevis på att hela projektet är secrets-fritt.
- Nodpaletten är uttryckligen endast visad. Widgetsemantik, installerade noder, backend-/frontendversion, frontendöppning och Run-ready är obevisade. Modellsökvägsnamn i JSON är inert övningstext, inte medföljande vikter.
- Kopierade docs har produktionens Run-gates och äldre pipelinebeskrivningar; README förhindrar att dessa förväxlas med aktiva evalinstruktioner. Ingen launcher kopierades eftersom första rename-ERST inte behöver den.
- Underlaget finns lokalt för framtida handoff; ingen Git-publicering gjordes. Faktisk åtkomst i mottagande repovy kontrolleras vid den senare handoffen. Steg 11:s fixture/context/graders implementerades inte av Codex.

## RMS 16/18 — statiskt alternativ 2026-09-14 01:43:03 +02:00

- `Get-NetTCPConnection -State Listen -LocalPort 8000,8188` gav inga lyssnare. Dessa två portar kontrollerades; detta bevisar inte att ingen frontend kan finnas på annan port eller host.
- Read-only fönsterinventering visade inget ComfyUI-namngivet fönster. Ingen browserflik öppnades eller undersöktes; dold flik utesluts inte. Frontendöppning och kompatibel frontendversion är fortfarande obevisade.
- Roadmapens alternativa klarsignal används uttryckligen: ComfyUI-ERST får tills vidare endast göra anspråk på sina deklarerade statiska JSON-, graf-, preservation- och diffkrav. Endast kontroller som faktiskt körts får beskrivas som verifierade.
- Statisk PASS betyder inte frontendkompatibilitet, installerad nodpalett, fungerande backend, körbar generering eller Run-ready. En uppgift som senare kräver frontendöppning måste få separat bevis före körning; den får inte underkänna modellen för saknad plattformsevidens.
- Referensworkflowets prompt-/checkpointvärden är inert övningsmaterial. Ingen launcher, checkpointåtkomst, `/prompt`-queue eller bild-/videogenerering användes. Detta steg tillför inga nya PASS/FAIL-sidokriterier.
- `git ls-remote origin refs/heads/main` var fortfarande `194f3426e6135d833819a6cef1210606df7606cf`. Ingen levererad ChatGPT-ändring observerades på denna branch; deras skrivytor lämnades orörda.

## RMS 17/18 — tidigare partiell offline-regressionskontroll

- Befintlig täckning granskades innan testkörning. Inga nya tester eller ersättningsimports skapades i ChatGPTs scope. Python 3.11 och Node 24.11.1 användes; inga modell-/serveranrop gjordes.
- `python -B -m unittest discover -s tests -p test_worker_instruction_following.py` avslutades med kod 1: `ModuleNotFoundError: No module named 'instruction_following_grading'` vid testmodulens rad 15. Testets sys.path pekar på den gamla `PROJECT_LOCAL-AGENTS/LOCAL_AGENTS/...`-roten. Inga screeningbeteendetester exekverades.
- `node --test tests/worker_file_tool_control.test.mjs` avslutades med kod 1: `ERR_MODULE_NOT_FOUND` för parserimporten under samma gamla rot. Inga parser-/reader-/avbrottsbeteendetester exekverades; detta är inte bevis för trasig dispatch eller modellbrist.
- Dessa testentrypoints ska efter steg 3 skydda tidigare verifierad screening/gradering, Granite-envelope-tolkning, den smala läsgränsen och in-flight readerabort. Därefter krävs relevanta stop/assess/readiness/baseline- och pathidentitykontroller från den faktiskt levererade slicen. Inga gamla reads eller fungerande stoppbeteenden får tas bort enbart för relokering.
- Steg 17 är delkontrollerat, inte utfört: ny kod har inte levererats för lokal diff-/integrationsverifiering. Importfelet är ett befintligt projektflyttproblem inom den redan pågående steg 3-slicen, inte en ny blocker eller nytt arbetssteg.
- Codex-ägda roadmap/INFO lästes tillbaka med UTF-8 och bytekontroll utan BOM efter ändring. Ingen index-/historyoperation utfördes.

## RMS 2/18, 4/18 och 17/18 — leveransgranskning 2026-09-14 02:11:29 +02:00

- Lokal `main` och GitHub `main` var `23f23a5326bf1e838e0d95b499da4760864794e6` före testpasset. Lokal AutoPull-launcher `SSIRA-LocalAgents-MainAutoPull.cmd` pekade på rätt repo och watcher; den separata ComfyUI-launchern fanns kvar. Local Agents-watchern körde och dess logg visade `STATE=SYNCED`. Inget installations- eller avinstallationsskript kördes av Codex.
- Båda evalrunner-CLI:er importerade. `--help` för `start/run/inspect/stop/assess` respektive `start/run/inspect/stop` avslutades med kod 0 och visade `--eval-id` i varje kommando. Aktiv evalkod hade ingen kvarvarande `PROJECT_LOCAL-AGENTS`-, `frontier_evaluations`- eller `parents[4]`-träff; omnämnanden i README/ägartest är negativa kontrakt. Ingen LM Studio-server lyssnade på port 1234 vid kontrollen. CLI/import är inte live-inventory, authkvittens, normal completion eller serverstoppkvitto; RMS 4 förblir delkontrollerad.
- `python -B -m unittest discover -s tests -p test_worker_evaluation_paths.py`: 6 PASS. `test_eval_runner_ownership.py`: 4 PASS. `test_worker_instruction_following.py`: 11 PASS. `node --test tests/worker_file_tool_control.test.mjs`: 2 PASS.
- `test_lm_studio_interrupt_control.py`: 13 PASS, 3 avsiktliga live-SKIP; Windows-jobb/ägda processer verifierades i disponibla temporära ytor, men inga riktiga LM Studio-genereringar kördes. `test_main_autopull_watcher.py`: 9 PASS i isolerade temporära Git-repon. `test_lm_studio_observability.py`: 23 PASS.
- `test_lm_studio_user_api_token.py` kunde först inte importera modulen: testet pekade på projektroten i stället för `tools/lm_studio_user_api_token.py`. Endast denna testpath ändrades, utan auth-/produktionskodändring; omkörning gav 2 PASS. Totalt i detta riktade pass: 70 PASS, 3 live-SKIP, 0 FAIL efter korrigeringen.
- De tre livefallen kräver uttryckliga envflaggor och verifierad LM Studio-server/modell; dessa var inte aktiverade. Inga nya modellspecifika slutsatser följer av testpasset. En framtida Round 2-ERST behöver sitt eget låsta kontrakt/kontext/grader från steg 5 innan RMS 18 kan slutföras.
- ChatGPTs handoff och roadmap-tabell ändrades inte av Codex. När de lokala testerna var klara är den återstående handoff-statusuppdateringen dess ägares ansvar; detta pass motsvarar endast Codex lokala RMS 2/4/17-verifiering.

## RMS 4/18 — live transport- och stoppkontroll 2026-09-14 02:23:04 +02:00

- Före provet: LM Studio-server OFF, ingen modell laddad. `lms server start --port 1234 --bind 127.0.0.1` startade endast loopback-API. Native `GET /api/v1/models` med giltig användartoken visade Granite installerad/oladdad. SDK-inventory med giltig, ogiltig och åter giltig token PASS (1 live-enhetstest); tokenvärdet loggades inte.
- Före load: cirka 6,9 GiB ledigt GPU-minne och 16,8 GiB ledigt RAM. `lms load granite-4.1-3b --context-length 4096 --gpu max --estimate-only` uppskattade 2,32 GiB. Endast Granite laddades med exakt identifierare `granite-4.1-3b`, 4096 kontexttoken, full GPU-offload och 600 sekunder idle-TTL; CLI rapporterade 1,96 GiB faktisk modellload. Detta är en kontrollkonfiguration, inte bevis på identiska villkor som historisk IMSLE.
- De två opt-in livefallen i `test_lm_studio_interrupt_control.py` kördes separat, båda PASS. Normal completion: `model_evaluations/EVAL_sdk-control_2026-09-14-0217/8b8e984416944815bb4694e3e27f2523/evidence.json`, `state=completed`, `stopReason=eosFound`, `cancel_command_sent=false`. Begäransspecifikt stopp: `.../5b46816cfbb4480fb4c62ee9f2ba8da1/evidence.json`, `state=verified_cancel`, `stopReason=userStopped`, `cancel_command_sent=true`, tre ägda toolprocesser totalt och noll aktiva vid kvitto; `late-tool-write.txt` saknades även vid separat efterkontroll. Modell och server fanns kvar efter stoppet.
- Dessa två runs är transportdiagnostik, inte WORKER-ERST eller modellspecifik prestationsbedömning. De tre tidigare offline-SKIP:en har nu separata livekontroller: ett authfall och två genereringsfall. Originalevidens ändrades inte.
- Efter provet avlastades endast Granite explicit och den av Codex startade API-servern stoppades. `lms ps` visade ingen modell och `lms server status` OFF. Ingen ComfyUI-backend, checkpoint eller `/prompt` kördes.
- Claudes externa ComfyUI-review lästes som rådgivande data. Den bekräftar redan fryst liten kontext/fixture, separat UI-format, statisk verifiering och läckagekontroll. Den ger ingen ny obligatorisk RMS. Rename-ERST ska bedömas som struktur-/precisionsgate, inte i sig som bevis på ComfyUI-domänkompetens; dess negativa skadefall hör hemma i steg 11.

## RMS 5/18 — låst nästa verktygsfria kontextuppgift 2026-09-14

- En enda eval-fixture `structured_edit_context.md` definierar generella regler för en liten nästlad JSON-ändring. Den är inte en generell produktionsprompt och ger inte facit. `structured_edit_catalog.json` låser exakt instruktion, systemroll, kontextfilens SHA-256, temperatur 0, 30 s körbudget, 5 s stoppbudget, 512 outputtokens, inga tools och ett oberoende JSON-sluttillstånd. Uppgiften mäter en simulerad, teknologioberoende strukturerad ändring; den påstår inte faktisk filförmåga eller ComfyUI-expertis.
- `evaluation_contracts.py` kräver bounded UTF-8 utan BOM, exakt kontexthash och deklarerad systemroll; oväntad eller ändrad källa nekas. Den befintliga `controlled_run.py` använder samma avbrytbara SDK-Chat (`system` följt av `user`), kräver modellbindning före generering, sparar katalog-/kontexthash och ogiltigförklarar stopp, trunkering eller källa som ändrats under körningen. Ingen ny harness eller dold retry tillkom.
- `test_evaluation_contracts.py`: 3 PASS, inklusive positivt resultat, preservation-/typ-/formatmissar, hash-/rollbrott, exakt SDK-input och låsta budgetar. Tidigare `test_worker_instruction_following.py`: 11 PASS. Dessa är offlinekontrakt, inte modellresultat eller ny live-kvittens; RMS 18 äger den aktuella uppgiftens operativa preflight.

## RMS 11/18 — första ComfyUI-fixture, end-to-end-integration återstår 2026-09-14

- En liten modellneutral kontext i `agent-0-context/comfyui_workflow_editing.md` skiljer UI-workflow från API prompt och förbjuder backendstart, modellload och `/prompt` i den statiska övningen. Formatdistinktionen kontrollerades mot officiella ComfyUI-dokument för workflow JSON 0.4 och API-format. Ingen produktionskontext eller komplett nodinventering påstås vara installerad.
- `workflow_rename_fixture.json` binder WF-1-A-snapshoten (20 632 byte, SHA-256), kontextens SHA-256, två identifierade nodtitlar, enkel filalias, 60 s, högst sex tool calls och 512 outputtokens. `comfyui_workflow_grading.py` kopierar endast den låsta källan till en unik eval-run-workspace och jämför det faktiskt skrivna JSON-sluttillståndet med exakt de två avsedda title-ändringarna. Övriga värden, noder och länkar måste vara semantiskt oförändrade; formattering/nyckelordning är inte ett sidokriterium.
- Vid denna tidigare delkontroll gav `test_comfyui_workflow_grading.py` 3 PASS för unik kopia, korrekt rename, fel titel, extra ändring, ogiltig JSON och käll-/kontextbrott. Den efterföljande RMS 6-integrationen med faktisk file-task-runner, read/write/readback och stoppevidens är nu genomförd och redovisas nedan. Detta förblir en struktur-/precisionsgate, inte bevis på ComfyUI-domänexpertis, frontendöppning, installerade noder eller Run-ready.
- AFPPBET-kontroll upptäckte att RMS 8 felaktigt pekade på den verktygsfria `controlled_run.py` som tool-loopägare. Roadmap och frysta beslut korrigerades före RMS 8-kod: watchdog hör till `worker_file_task_evaluation.py` orchestration; fast validator hör till toolytan.

## Process- och Gitstatus

Tidigare skapades små källsnapshots och Codex-ägda arbetsdokument. Det nuvarande passet slog ihop planstatus, skapade två avgränsade transportdiagnostiska runs och ändrade inte historisk evalevidens. Den befintliga Local Agents-watchern lämnades igång. LM Studio-servern och Granite återställdes till OFF/oladdad; ingen omstart behövs. Inget stageades, committades eller pushades av Codex. Spårade lokala ändringar medför att AutoPull avsiktligt avstår från framtida FF tills arbetsytan åter är ren; GitHub-publicering påverkas inte.

## RMS 6–9 och 12–18 — färdigställande 2026-09-14

- Bounded filarbete använder en gemensam path-/budgetpolicy, strikt UTF-8, verkliga vanliga filer, hashvillkorad atomisk textreplacement och oberoende readback. Kandidaten får ingen shell-, nätverks-, backend-, vikt- eller godtycklig hoståtkomst. Windows Job Object styr endast evaluatorägda fasta validatorprocesser och påstås inte vara ett fullständigt OS-sandbox.
- Det första liveförsöket att nå en mutation via Granite-textbryggan producerade `old_ text` i stället för kontraktets `old_text`; den strikta parsern dispatchade därför inget tool. Detta är ett orsaksneutralt diagnostikutfall, inte ett modell-FAIL. Ett länkat korrigerat transportprov använde en evaluatorägd giltig mutationsrequest samtidigt som verklig SDK-generering pågick: `userStopped`, cancel skickat, noll aktiva writes, en avbruten write, oförändrad/stabil filhash och inga sena/temp-skrivningar. Provet är stopp-/toolevidens och ger ingen kandidatprestationspoäng.
- En effektbaserad watchdog stoppar efter tre konsekutiva faktamässigt likvärdiga toolutfall utan relevant effekt. Fast statisk workflowvalidator körs med evaluatorvald argv, tresekundersbudget och verklig OS-exitstatus; kandidatändrad kod eller fritt kommando exekveras aldrig.
- Den officiella Workflow JSON 0.4-schemakopian är hashbunden och används med graf-, slot-, endpoint-, backreference-, typ- och visad-palettkontroller. Okänd subgrafsemantik ger reviewkrav. Statisk PASS påstår inte frontendöppning, installerad runtime, Run-ready eller generering.
- Tre modellneutrala kandidat-skills finns med hashbundet explicit/discovery-läge. De är kandidatens runtime-data, inte Codex skills. Katalogexponering, separat bounded skill-read och faktisk toolhändelse kan spåras; ett task-PASS bevisar inte att en skill orsakade resultatet.
- `worker_task_catalog.json` innehåller exakt åtta rounds × tre uppgiftsrecept. Endast poster med verkligt lokalt kontrakt och runner är låsta; adaptiva poster kan inte köras och får exakt instruktion, fixture och grader först när tidigare evidens motiverar uppgiften. Detta bevarar trajectoryn utan att fabricera tjugofyra körklara tester.
- Mekanisk evidensreview kontrollerar identitet, rekonstruerad instruktion/hash, källor, fixture, retrylänk, assessmentbindning, scope och stoppevidens men gör aldrig modellfelsattribuering. REPORT SUMMARY-kontrollen kräver exakt en fil och lämnar alltid de fyra ERQER-domänerna och orsaksseparation till explicit semantisk review.
- Nästa konkreta ERST är `nested_record_edit`. Kontrakt, context-hash, färsk system/user-ordning, temperatur, token-/tidsbudget, tools-förbud och grader är låsta. Runnern nekar generation före verifierad exakt modellbindning, icke-tom faktisk renderad input och tokenbudget som ryms i verklig kontext. Server, auth och laddad modell kontrolleras färskt vid evalstart; ingen gammal readinesscapture eller automatisk retry godtas.
- Claudes externa svar bekräftade huvudsakligen redan frysta gränser. Den användbara preciseringen är att title-ändringen mäter struktur/preservation och inte ensam ComfyUI-expertis. Inget nytt obligatoriskt RMS tillkom.
- Slutlig riktad regression utan liveinferens: 89 Python-fall PASS, 3 uttryckligen opt-in livefall SKIP och 10 Node-fall PASS. Matrisen omfattade pathägarskap, tidigare screening, authupplösning, observability, interrupt/process, kontextkontrakt, workflow-fixture/schema/graf, watchdog, fast validator, skills, 8×3-recept, filrunner, evidensreview och AutoPull. `git diff --check` gav inga whitespacefel; endast förväntade Git-radslutsvarningar visades.

# Codex — lokal arbetsordning och verifieringsfynd

## Kollisionsfri ordning

Team Masters beslut: prioritera de egna stegen efter lägsta risk för konflikt med pågående ChatGPT-arbete. Oberoende lokal källåtkomst i steg 10 genomförs först. Stegnumren och de andra aktörernas scope/status ändras inte.

Codex skriver endast sin separata roadmap, detta verifieringsunderlag och `model_evaluations/comfy_ui_eval-playground/source_snapshots/`. ChatGPTs kod, tester, roadmap och pågående handoff lämnas orörda. Framtida ChatGPT-slices får läsa snapshots som input; de får inte mutera dem som delat tillstånd.

Steg 2 återupptas när steg 1 är tillgängligt. Steg 4, 7 och 9 kräver sina respektive ChatGPT-slices. Steg 16:s förhandsbestämda statiska alternativ är nu valt; en senare ERST med frontendkrav behöver separat öppningsbevis. Steg 17–18 tillämpas vid aktuell integrations-/ERST-gräns, inte som ett krav att invänta alla sena förberedelser.

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

## RMS 17/18 — partiell offline-regressionskontroll

- Befintlig täckning granskades innan testkörning. Inga nya tester eller ersättningsimports skapades i ChatGPTs scope. Python 3.11 och Node 24.11.1 användes; inga modell-/serveranrop gjordes.
- `python -B -m unittest discover -s tests -p test_worker_instruction_following.py` avslutades med kod 1: `ModuleNotFoundError: No module named 'instruction_following_grading'` vid testmodulens rad 15. Testets sys.path pekar på den gamla `PROJECT_LOCAL-AGENTS/LOCAL_AGENTS/...`-roten. Inga screeningbeteendetester exekverades.
- `node --test tests/worker_file_tool_control.test.mjs` avslutades med kod 1: `ERR_MODULE_NOT_FOUND` för parserimporten under samma gamla rot. Inga parser-/reader-/avbrottsbeteendetester exekverades; detta är inte bevis för trasig dispatch eller modellbrist.
- Dessa testentrypoints ska efter steg 3 skydda tidigare verifierad screening/gradering, Granite-envelope-tolkning, den smala läsgränsen och in-flight readerabort. Därefter krävs relevanta stop/assess/readiness/baseline- och pathidentitykontroller från den faktiskt levererade slicen. Inga gamla reads eller fungerande stoppbeteenden får tas bort enbart för relokering.
- Steg 17 är delkontrollerat, inte utfört: ny kod har inte levererats för lokal diff-/integrationsverifiering. Importfelet är ett befintligt projektflyttproblem inom den redan pågående steg 3-slicen, inte en ny blocker eller nytt arbetssteg.
- Codex-ägda roadmap/INFO lästes tillbaka med UTF-8 och bytekontroll utan BOM efter ändring. Ingen index-/historyoperation utfördes.

## Process- och Gitstatus

Endast små källsnapshots och Codex-ägda arbetsdokument skrevs. Inga server-/modell-/watcherprocesser startades, stoppades eller ändrades; ingen omstart behövs. Inget stageades, committades, pushades eller mergades.

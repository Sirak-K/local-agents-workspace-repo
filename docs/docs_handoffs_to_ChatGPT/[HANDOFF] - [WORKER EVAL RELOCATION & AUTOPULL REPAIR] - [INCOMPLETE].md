# Handoff till ChatGPT — WORKER eval-relokering och AutoPull-reparation

## 1. Direkt uppdrag till mottagande ChatGPT

Team Master lämnar denna handoff tillsammans med två planfiler. **Implementera det nedan avgränsade uppdraget, inte bara en analys eller ytterligare plan.** Team Master ska inte behöva skriva kompletterande instruktioner när handoff och underlag är åtkomliga.

Detta är det första direkt implementerbara paketet i PREPARE FOR MASSIVELY IMPROVED EVALS: roadmapsteg **1 och 3**. Alla andra steg är utanför denna handoffs implementationsscope. De aktiveras genom senare avgränsade handoffs/lokalt arbete; denna fil är inte en beställning att göra hela roadmapen i ett svep.

Nytta: återställ en fungerande repo-mottagningsväg och rätt projekt-/evidenspaths innan kontext, mutation och ComfyUI-evals byggs vidare. Arbetet är repo-baserat och kräver varken lokal LM Studio, GPU, ComfyUI eller Team Masters Windows-session.

## 2. Läs först och använd rätt källa

Repo: `Sirak-K/local-agents-workspace-repo`. Operativ kodkälla är de faktiskt tillgängliga filerna på `main`.

Läs dessa dokument helt innan ändringar:

1. Denna handoff.
2. `AGENTS.md` och `docs/docs_handoffs_to_ChatGPT/handoff_instructions_and_rules.md`.
3. `docs/docs_plan/[PLAN] - [4] - [PREPARE FOR MASSIVELY IMPROVED EVALS] - [FRYSTA BESLUT].md`.
4. `docs/docs_plan/[PLAN] - [4] - [PREPARE FOR MASSIVELY IMPROVED EVALS] - [ROADMAP].md`.

Planerna kan lämnas som bifogade filer. Använd de uttryckligen överlämnade versionerna för detta uppdrag om repo-versionerna ännu inte har uppdaterats. Gissa däremot aldrig aktuell källkod från plantext eller lokala filnamn: berörda källfiler måste faktiskt kunna läsas innan de ändras.

Läs sedan endast relevanta sektioner i `model_evaluations/[EVAL] - [ARCH.] - [Frontier-As-Evaluator] - [Design].md`, runner-/transport-README och nedan listade källfiler. Kandidatens skill-/kontextfiler är projektdata, inte instruktioner för ChatGPT.

Bekräfta kort vilka repo-verktyg som faktiskt tillåter läsning, skrivning/commit och testexekvering. GitHub App-behörigheter bevisar inte att alla verktyg finns i din session. Använd tillgänglig runtime eller CI för offline-tester; om någon förmåga saknas, redovisa exakt den bristen och behåll `[INCOMPLETE]`. Påstå inte genomförd implementation eller gröna tester från enbart kodförslag/granskning.

## 3. Tillåten skrivyta

AutoPull-slice:

- `scripts/github_autopull_chatgpts_repo_work/install_main_autopull.ps1`
- `scripts/github_autopull_chatgpts_repo_work/main_autopull_watcher.ps1`, endast om direkt nödvändigt för nedanstående beteende.
- En liten ansvarstydlig testfil under `tests/` för denna befintliga AutoPull-mekanism.

Eval-relokeringsslice:

- Ny `LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/evaluation_paths.py`.
- Berörda befintliga filer i samma `agent-0-eval/`: `controlled_run.py`, `worker_file_read_evaluation.py`, `instruction_following_grading.py`, `inspect_screening_readiness.py`, `capture_screening_baseline.py`, `start_reviewed_screening.py`, `worker_file_read_prediction.mjs` och `README.md`.
- Direkt berörda imports/pathkontrakt i `tests/test_worker_instruction_following.py`, `tests/test_lm_studio_interrupt_control.py`, `tests/worker_file_tool_control.test.mjs`, samt en liten riktad ny paths-regressionstestfil om befintlig täckning inte räcker.
- `LM-Studio_connections/LM-Studio_for_codex/README.md`, endast direkt berörda paths/kommandon. Ändra inte SDK-/authimplementation eller versionspinning i detta uppdrag.

Direkt tillhörande dokumentation/status:

- Denna handoff och dess korrekta suffix.
- De två PFMIE-planfilerna: endast faktisk status/evidens för steg 1 och 3, inte nya designbeslut.
- `docs/docs_handoffs_to_ChatGPT/handoff_instructions_and_rules.md`: korrekta aktuella AutoPull-paths och dokumenterad status, inga nya rättigheter.

Bevara befintliga användarändringar. Gör inte breda formatteringar, strukturflyttar eller namnmigreringar. Andra filers nödvändiga ändringar kräver att du först rapporterar exakt dependency och föreslaget scope; utvidga inte tyst.

## 4. Absoluta negativa gränser

- Läs eller ändra inte `LOCAL_AGENTS/AGENT-1-GENERAL/` eller `AGENT-2-STORYTELLER/`.
- Ändra inte `[TODO].MD`, personliga docs, produktionsworkflows eller material i det andra comfy-projektet.
- Ändra/radera inte historiska eval-runneresultat, assessment-filer, råa loggar eller deras hash-/pathinnehåll. En historisk path är evidens, inte ett sök-/ersättningsmål.
- Ladda inte modeller, läs inte vikter, kör inte inferens eller GPU-arbete, anropa inte localhost och exekvera inte ComfyUI-launchers.
- Installera/starta inte AutoPull på Team Masters riktiga dator från detta uppdrag. Tester använder enbart disponibla repos/processer i faktisk tillgänglig testmiljö.
- Ingen auto-merge av PR, automatisk branchbyte, force-push, reset, rebase, clean, stash eller överskrivning av dirty arbetsfiler.
- Implementera inte senare mutation, kontextinjektion, skills, ComfyUI-graders eller nytt harness. Bygg inte en allmän pathplattform på Bionic-legacyhelpern.

## 5. RMS 1/18 — reparera befintlig AutoPull-mottagning

Verifierat vid överlämningen: skripten ligger i `scripts/github_autopull_chatgpts_repo_work/`, men installern bygger watcherpath som `tools/main_autopull_watcher.ps1`. Använd live-snippet före patch; radnumren i planerna kan ha flyttats.

Gör följande:

1. Rätta installerpath till den faktiskt samlokaliserade watchern. Använd verifierad script-/reporot, inga personbundna absoluta paths.
2. Kontrollera att flytten inte lämnat direkt berörda installer-/startupreferenser felaktiga. Behåll befintligt ansvar och ändra bara nödvändiga referenser; inget andra watcher-/synksystem.
3. Behåll säker `origin/main`-fetch och endast FF till lokal `main`. En PR:s arbete blir tillgängligt i lokal `main` efter merge till fjärr-`main`, inte genom PR-auto-merge.
4. Skydda dirty tracked/staged state, divergens, fel branch, pågående Git-operation och ospårade filkollisioner. Fetch/review kan ske utan osäker worktree-mutation.
5. Testa i temporära repos: säker FF, dirty skip, divergens, fel branch, stoppsignal/singleton och kolliderande ospårad fil. Ingen installation i riktig Startup eller användarprofil får ske i tester.
6. Om PowerShell-testmiljö saknas: implementera portabelt granskningsbar korrigering/testkod men rapportera exekveringen som ej körd. Begär inte att Team Master löser triviala kodändringar; lokal verifiering förblir Codex-ägd.

Klarsignal: referenser följer verklig placering, inga destruktiva fallbackvägar införda och faktiskt körda tillgängliga tester redovisade. Verklig lokal installation/mottagning är separat roadmapsteg 2 och ska inte markeras utförd av dig.

## 6. RMS 3/18 — kanonisk projekt- och evalrot

Verifierat nuläge:

- Fyra Pythonfiler använder fortfarande `Path(__file__).resolve().parents[4]`, vilket är för högt efter projektflytten.
- `controlled_run.py`, `worker_file_read_evaluation.py` och readiness-pathen använder gammal `LM-Studio_logs/frontier_evaluations`-rot.
- `worker_file_read_prediction.mjs` använder gamla relativa SDK-importnivåer.
- De listade testsuiterna har imports med `PROJECT_LOCAL-AGENTS/LOCAL_AGENTS`, trots att rollroten nu är `LOCAL_AGENTS`.

Gör följande i en sammanhängande relokeringsslice:

1. Inför `evaluation_paths.py` som gemensam ägare av aktuell projektrot och säker eval/run-pathkonstruktion. Verifiera roten mot faktisk layout; ersätt inte bara fyra felaktiga uttryck med fyra nya duplicerade rotägare.
2. Bind varje ny körning till explicit eval-id och unikt run-id under `model_evaluations/<eval-id>/<run-id>/`. Runnern ska inte välja en historisk eval automatiskt. Nuvarande etablerade eval-id-format ska stödjas utan omdöpning.
3. Validera identiteter före I/O; neka absolut path, traversal, separatorinjektion, rootescape och otillåten kollision/överskrivning. Skydda verklig containment när befintliga länkar påverkar resolved paths. Nya runs bevaras separat.
4. Uppdatera hela kedjan start/inspect/stop/assess/readiness/baseline/reviewed-screening så att varje operation använder uttrycklig eval/run-identitet och hittar samma ägarhem. Utför inte själva live-operationerna.
5. Bevara SDK-stoppkvitto, partiell evidens, loggsanering, katalog-/assessment-hashar, immutable assessment och länkade versionerade återförsök. Inför ingen gammal-rotsfallback eller historikomskrivning.
6. Korrigera JavaScript-importerna och direkt berörda testsuiteimports mot faktisk layout. Bevara den existerande lilla read-only-toolens budget/beteende; workflowstora reads är senare steg 6.
7. Uppdatera exakta README-kommandon för ny eval-id/run-id-användning. Alla nya evalspecifika writes ska hamna i evalhemmet; evaluation-oberoende driftloggar stannar under `LM-Studio_logs/`.
8. Kontrollera offline import/path resolution, att korrekt evidence/stop/readiness/baseline/assessment-path används, negativa identity-/containment-/collisionfall och bevarad assessmentintegritet.

Klarsignal: den berörda runtimekedjan har ett gemensamt pathansvar och stämmer med dokumentationen; tillgängliga offline regressionskontroller är körda. Lokalt auth-/provider-/Windows-stoppbevis är separat roadmapsteg 4/17, inte ett mocktestresultat.

## 7. Verifiering och arbetskadens

- Varje arbetspass börjar i chatten med `RMS 1/18` respektive `RMS 3/18` och en kort operativ beskrivning. Bevara planen som en kompakt tabell.
- Utför en slice i taget med direkt tillhörande tester/dokumentation. Kolla befintlig testtäckning före nya testfiler; inga redundanta/cosmetiska tester.
- Använd små, riktade offline-testselektorer. Befintliga Node-tester kan köras med `node --test tests/worker_file_tool_control.test.mjs` efter korrigerade imports. Python instruction-/paths-tester körs riktat med `python -m unittest discover -s tests -p test_worker_instruction_following.py` och motsvarande selektor för eventuell ny paths-testfil.
- Kör inte hela interrupt-suiten utan att först kontrollera dess exekveringsgränser. Windows-/livefall är Codex-ägda. Ett plattforms-skip är inte ett passerat Windows-/LM Studio-test; bevara dessa testers riktiga verifieringsvärde.
- Kontroller som saknar din faktiska runtime redovisas separat med exakt kommando och dependency. Vid behov kan avgränsad testkod skapas utan att dess resultat påstås; status förblir ofullständig tills handoffens egna verifieringskrav uppfyllts.
- Alla nya/ändrade textfiler ska vara UTF-8 utan BOM. Verifiera verkliga bytes, svenska tecken och inga mojibake-signaler. JSON-evidens är pretty/multiline med läsbara timestamps och relativa paths där möjligt.
- Genomför avgränsade repoändringar via tillgängligt GitHub-skrivverktyg enligt Team Masters handoffpolicy. Ingen orelaterad commit-/index-/historymutation. Kontrollera verklig publicerad fil/diff om du committar; påstå inte push eller PR från enbart förslag.

## 8. Slutrapport och statusansvar

Rapportera i denna fil och ditt slutmeddelande:

1. Exakta ändrade/skapade/raderade filer.
2. Utförda steg 1 och 3 med faktisk klarsignal.
3. Exakta körda testkommandon, resultat samt separat ej körda/skippade kontroller.
4. Beteenden som bevarats och kvarstående konkreta risker.
5. Vad Codex ska verifiera lokalt i steg 2, 4 och relevant del av 17.
6. PIPSA: ingen faktisk modell/server/watchermiljö har ändrats av din repoimplementation; när ändringar integreras måste Codex hantera berörd lokal watcher enligt processreglerna.

Markera endast dina ChatGPT-ägda roadmaprader utförda när deras egna implementation-/offlinekrav är uppfyllda. Lämna Codexrader och senare ChatGPT-steg orörda. Om endast implementation är klar men obligatorisk offlineexekvering saknas, skriv det uttryckligen och behåll ofullständig status.

Du äger suffixet: byt denna fils basnamn till ` - [COMPLETED].md` först när hela det avgränsade uppdraget här faktiskt är implementerat och verifierat. Separat lokal integration kan fortfarande vara pending även när denna avgränsade repo-handoff är färdig. Skapa inte en ny handoff eller initiera senare steg utan ett nytt uppdrag.

**Initial status:** Ej startad. Inga implementationer eller tester har körts genom denna handoff.

## 9. ChatGPT arbetsstatus 2026-09-14

Status förblir **INCOMPLETE**. Repo-skrivning/commit via GitHub Connector fungerar. Connectorn erbjuder däremot ingen repo-monterad exekveringsyta, och den separata container-runtime som finns i sessionen kan inte nå GitHub-nätverket; därför har jag inte kört Python-/Node-/PowerShell-regressionskommandona och påstår inte gröna offline-tester.

### RMS 1/18

Implementerat på `main`: installerpath till samlokaliserad watcher, FF-only/dirty/branch/Git-operation-skydd, explicit kollisionsskydd för ospårad fil, temporär-repo-testkod, separat Local Agents Startup-launcher (`SSIRA-LocalAgents-MainAutoPull.cmd`) samt Windows PowerShell 5.1-parserfix. Team Master körde därefter installern lokalt och visade `STATE=SYNCED`; detta är separat lokal integrations-evidens från Team Master och inte ett ChatGPT-kört test. Handoffens egna temporära PowerShell-regressionstester återstår att exekvera av Codex.

### RMS 3/18

Implementerat/grovimplementerat på `main`: gemensam `evaluation_paths.py`; canonical `model_evaluations/<eval-id>/<run-id>/`; explicit eval-id i `controlled_run.py` och `worker_file_read_evaluation.py`; eval-id inuti ny evidence; readiness/baseline/review-kedjan bunden till eval/run; JS-SDK-importnivå reparerad; Node-tooltestens gamla `PROJECT_LOCAL-AGENTS`-imports reparerade; ny statisk `tests/test_eval_runner_ownership.py`; reviewed-screening-launchern rättad till faktisk `controlled_run.py run --eval-id --run-id --baseline-file`-kontrakt.

Kvar innan denna handoff får markeras completed: `tests/test_worker_instruction_following.py` och `tests/test_lm_studio_interrupt_control.py` använder fortfarande pre-relocation imports/API-antaganden och måste migreras; `agent-0-eval/README.md` måste få exakta nya eval-id/run-id-kommandon; relevanta AutoPull-/Python-/Node-offlinetester måste faktiskt köras; eventuella fel som de avslöjar måste rättas. Kontrollera särskilt assessment-integritet, baseline/retry cross-eval-nekande och start/inspect/stop/assess-paths.

PIPSA: ChatGPT:s repoimplementation har inte laddat modell, anropat LM Studio/localhost eller ändrat modell/servermiljö. Team Master startade separat den lokala AutoPull-watchern efter repoändringen. Codex bör verifiera commits/diff från `origin/main` i ren/isolerad yta om lokal tracked arbetsyta fortfarande är dirty.

# PREPARE FOR MASSIVELY IMPROVED EVALS — Frysta beslut

## 1. Uppdrag och granskningsstatus

- Arbetsmomentet förkortas PFMIE endast i arbetsdokumentation. Fullständigt namn används i planfilernas namn; implementation namnges efter permanent ansvar.
- Förberedsgranskning utförd 2026-09-14 av Codex med en oberoende read-only underagent. Endast plan-/regelunderlag ändras i detta pass; inga runners, tools, fixtures, beroenden eller processer implementeras eller startas.
- Primär designkälla är `model_evaluations/[EVAL] - [ ARCH. ] - [Frontier-As-Evaluator] - [Design].md` och Team Masters beslut. Den associerade roadmapen härleds från dessa frysta beslut och är inte en parallell designkälla.
- 0-WORKER:s primära slutmål är professionellt, precist, välstrukturerat och verifierbart ComfyUI-workflowarbete. Tidiga teknologioberoende uppgifter är kvalificeringsgrund, inte konkurrerande slutmål.
- Behåll fem phases, åtta rounds och tre ERST per round. Ingen ny screening, stor upprepningskvot eller extra fas införs som förberedelsekrav.
- Roadmapen omfattar återstående implementation och relevant lokal verifiering, inte själva nästa kandidat-evalen. Vid senare operativa arbetspass börjar uppdateringar med `RMS <steg>/18`; genomför inte roadmapen utan Team Masters startbesked.
- Team Master har avslutat ChatGPT:s PFMIE-arbete och gett Codex ansvar för hela återstående implementationen och verifieringen. Endast `[PLAN] - [4] - [PREPARE FOR MASSIVELY IMPROVED EVALS] - [ROADMAP].md` äger de 18 globala stegens status; den tidigare separata Codex-roadmapen är borttagen. Historiska handoff-commits och verifieringsnoteringar är evidens, inte parallellt statusägarskap.

## 2. Verifierade fynd och deras konsekvenser

| Evidens | Faktiskt fynd | Nödvändig åtgärd |
| --- | --- | --- |
| `agent-0-eval/controlled_run.py:20,32`, `worker_file_read_evaluation.py:14,22` | För hög rotberäkning och gammal `LM-Studio_logs/frontier_evaluations`-rot. | Samlad relokering med explicit eval-id och run-id. |
| `instruction_following_grading.py:14`, `inspect_screening_readiness.py:15,103` | Samma rot-/evidensproblem även utanför de två runners. | Korrigera samtliga direkt berörda konsumenter i samma slice. |
| `worker_file_read_prediction.mjs:2–4` och imports i befintliga Python-/Node-tester | Gamla parentnivåer och `PROJECT_LOCAL-AGENTS`-prefix. | Verifiera imports och paths offline; bevara tidigare testsignal. |
| `agent-0-tools/worker_workspace_text_tool.mjs:7–40` | Read-only, en tillåten fil, högst två läsningar, 4096 bytes. | Bevara tidigare lilla läsprobe; inför uppgiftsstyrd fil-/anrops-/bytebudget och mutation innan större workflowarbete. |
| `model_evaluations/comfy_ui_eval-playground/workflows/` | Fem disponibla UI-workflowkopior, cirka 10–89 KB. | Använd utvalda unika kopior; ingen automatisk spegling eller kopiering av hela runtime. |
| `scripts/github_autopull_chatgpts_repo_work/install_main_autopull.ps1:14` | Installern hänvisar fortfarande till `tools/main_autopull_watcher.ps1`. | Rätta till den befintliga flyttade watchern och tillhörande instruktioner. |
| `comfy_ui_workspace/scripts/comfyui/start_comfy_ui_backend.sh` | Riktigt startskript refererar extern ComfyUI-installation och processkontroll. | Eventuell kopia är endast läs-/redigeringsmaterial och får aldrig exekveras av kandidaten. |
| Gemensam evaldesign, implementationsstatus | Begränsad läsdispatch och genererings-/toolstopp har historisk live-evidens; full write/skills/no-progress saknar verifiering. | Återanvänd bevisad mekanism; verifiera endast nya eller ändrade gränser och relevant regression. |

Radnummer gäller granskningstillfället. Historiska loggar/assessment-hashar ändras inte för att passa ny struktur. Tidigare live-framgång är inte bevis på att den flyttade koden fungerar nu.

## 3. Historisk ChatGPT-handoff och nuvarande Codex-ansvar

- ChatGPT genomförde den avgränsade första handoffen för AutoPull och kanoniska evalsökvägar. Från Team Masters nya beslut gör ChatGPT inget ytterligare PFMIE-arbete; Codex äger nu återstående portabel implementation, lokala kontroller och status i den enda roadmapen.
- Portabla testdubblar kan visa kodkontrakt men inte äkta LM Studio-auth/cancel, Windows Job Objects, lokal fil-/processisolering eller frontendkompatibilitet. Codex verifierar sådana gränser separat när berörd slice kräver dem.
- Screenshotens GitHub App-behörigheter bevisar repoauktorisering, inte att ChatGPT-sessionen har exponerade skrivverktyg eller testexekvering. Före varje handoff ska mottagaren bekräfta exakt skriv-/läsåtkomst och verklig testväg: tillgänglig runtime eller CI. Saknas exekvering redovisas tester som ej körda; inga påhittade gröna testresultat eller `[COMPLETED]`.
- Den tidigare handoffens ofullständiga suffix speglade att ChatGPT inte själv kunde köra lokala tester; Codex har senare körda testresultat dokumenterade i verifieringsunderlaget. Handoff-filen är historisk och inte en ny PFMIE-arbetskö.

## 4. Connector och befintlig FF-only AutoPull

- Använd det etablerade flödet: ChatGPT:s tillgängliga GitHub-verktyg skriver/committar i repo → `main` → lokal FF-only AutoPull. En PR kommer till lokal `main` först efter merge; ingen auto-merge, force-push eller automatisk branchbyte ingår.
- Befintlig ägare är `scripts/github_autopull_chatgpts_repo_work/`. Återanvänd och reparera dess två skript; skapa ingen parallell watcher eller synkplattform.
- Behåll endast `main`, tidsbegränsad polling, singleton/stoppsignal, fetch och säker FF. Dirty tracked/staged state, pågående Git-operation, divergens, fel branch eller kolliderande ospårade filer får aldrig lösas genom reset/rebase/clean/stash eller överskrivning.
- Normalt upptäcks ändringar vid nästa poll, inte bokstavligen omedelbart. Vid osäker FF ska remote-resultat fortfarande kunna granskas utan att arbetsfiler ändras.
- Den första ChatGPT-leveransen är mottagen. Lokal installation, rätt repo, separat launcher, säker FF och processstatus är verifierade av Codex; ingen bred Git-städning krävs av PFMIE.
- Den granskade [officiella GitHub-guiden](https://learn.chatgpt.com/docs/third-party/github) gäller Codex-repointegration/review och etablerar inte i sig ChatGPT-sessionens skriv-/exekveringsförmåga; den senare hålls uttryckligen verifieringsberoende.

## 5. Permanent ägarskap och minsta implementerbara slices

- `agent-0-eval/evaluation_paths.py` äger projektrot och säker konstruktion av `model_evaluations/<eval-id>/<run-id>/`. Alla berörda runners/preflight/assess/baseline använder samma ägare; inga kompatibilitetswrites till gamla roten. Identiteter är explicit indata, inte fabrikerad historik.
- `agent-0-eval/evaluation_contracts.py` äger deterministisk laddning/validering av uppgiftskontrakt, kontextreferenser och hashfingerprints. Katalogdata/prompttext ägs av JSON-/textfiler, inte kodkonstanter med hela instruktioner.
- Befintlig `controlled_run.py`, SDK-transport och processkontroll återanvänds. Ny filuppgiftsorchestration namnges `worker_file_task_evaluation.py` med transport `worker_file_task_prediction.mjs`. Den ersätter lässpecialiseringen först när det gamla läsprovet och dess stoppbevis har regressionstestats; ingen parallell allmän harness införs.
- `agent-0-tools/worker_workspace_access.mjs` äger gemensam canonical-path-, filallowlist- och budgetkontroll först när read/write-slicen behöver delningen. Befintlig lästool konsumerar den; `worker_workspace_mutation_tool.mjs` äger faktisk bounded mutation och readback. Gemensamma gränser ska inte dupliceras i varje adapter.
- `agent-0-eval/comfyui_workflow_validation.py` äger rena offline-format-/grafkontroller; `comfyui_workflow_grading.py` äger uppgiftens mål- och preservationbedömning. Valid workflow och klarad uppgift är skilda kontroller.
- `agent-0-eval/fixture_workspace.py` äger verifierad kopiering, före-/efterfingerprints och unik disponibel workspace. Manifest och context sources är data, inte nya generiska managers.
- Dessa nya ägare skapas endast i den slice som behöver deras beteende. Nödvändiga imports, beroenden, felhantering, integration och tester ingår atomiskt med den konsumerande slicen.
- Det äldre Bionic-bundna `tools/agent_role_paths.py` ska inte användas som ny grund. Utred endast dess direkta konsumenter innan eventuell exakt borttagning av helper och dess gamla test; inga inaktiva rollmappar läses eller migreras.

## 6. Säker workspace och verkställbara budgetar

- Kandidatens tools får endast nå namngivna små text-/JSON-filer i aktuell disponibel workspace. Befintliga workflowfilnamn kan ha mellanslag/brackets; använd säkra enkla fixturealias och bevara originalnamnet i manifest, inte en osäker global pathregex-lättnad.
- Kandidaten får inte läsa modellvikter, `models/`, `.safetensors`, `.gguf`, checkpoint-/LoRA-binärer, secrets, originals, graderfacit eller godtyckliga hostvägar. Modellfilnamn som vanlig text i ett workflow är tillåtna.
- Ingen generisk shell-, nätverks-, ComfyUI-launcher-, modellload-/download- eller `/prompt`-tool exponeras. ComfyUI-checkpoints får aldrig laddas och GPU-generering får aldrig startas. LM Studio-kandidaten är däremot själva evalsystemet och får hanteras av evaluatorn enligt befintligt bounded mandat.
- Mutation kräver expected-before-hash, UTF-8 utan BOM, tillåtna filer, total skriv-/fil-/anropsbudget, bounded atomisk commit och oberoende efterkontroll. Ogiltigt input eller stopp före commit lämnar originalfixture intakt.
- Avbrott är inte rollback: en redan slutförd mutation bevaras som partiell evidens. Efter stoppkvitto får inga nya writes/dispatch ske; kontrollera inga aktiva ägda tools och inga sena sidoeffekter.
- Bygg no-progress-watchdog i filuppgiftsrunnerns orchestration ovanpå faktiska toolhändelser, med tidigare beslutade tre konsekutiva likvärdiga resultat utan relevant framsteg som startpolicy. Meningsfull effekt/hash/exitstatus räknas; brus/mtime ensam gör det inte. Legitima återhämtningssteg ska tillåtas. Den verktygsfria `controlled_run.py` ska inte bli ägare av denna tool-loop.
- Round 4–5:s test-/validatoroperationer exponeras endast som fasta evaluatorägda, icke-tunga verifieringskommandon, utan shell och utan möjlighet att exekvera kandidatändrad kod. Kandidatvald kodexekvering kräver separat verklig OS-isolering före användning, inte en allmän förberedande installation av VM/container.

## 7. Kontext: vad, varifrån och vart

- Före nästa Round 2 krävs endast de kontextkällor den utvalda teknologioberoende uppgiften använder. Befintlig `agent-0-context/agent-0-system_prompt.txt` är möjlig input, inte bevis för injektion. Inget stort ComfyUI-paket blockerar den rundan.
- Före varje ComfyUI-ERST krävs endast ett task-specifikt, hashbundet kontexturval med deklarerad roll/ordning och de format-, nod- och verifieringsfakta just uppgiften behöver. För den låsta title-ändringen ägs detta av `agent-0-context/comfyui_workflow_editing.md`, fixturemanifestet och den visade nodpaletten. Skapa inte ett parallellt generellt kontextpaket eller tomma framtidsfiler innan en konkret senare uppgift behöver dem.
- Projektkontext härleds från relevanta små specs/promptregler i `comfy_ui_workspace/docs/docs_comfyui-workflows/` och Team Masters workflowregler. Journals, gamla lösningar och graderfacit injiceras inte.
- Formatfakta hämtas från [Workflow JSON 0.4](https://docs.comfy.org/specs/workflow_json_0.4), [Node Definition JSON](https://docs.comfy.org/specs/nodedef_json) och vid behov officiell frontend/custom-node-källkod för exakt låst fixture. Endast små relevanta utdrag/schema hämtas; ingen bred docsdownload eller nedladdning av modeller behövs.
- Officiellt schema lagras separat som verifierardata i `agent-0-eval/schemas/workflow_ui_0_4.json`, med källa, hämtningstid, hash och dokumenterad schemadialekt. Nödvändigt JSON Schema-bibliotek versionsbinds i `requirements-eval.txt` först i validatorslicen; schema ger inte ensamt graf- eller frontendbevis.
- Nodpaletten är uppgiftsreducerad. Installerade nodfakta kräver verklig read-only inventory från redan aktiv miljö eller versionsbunden källkod; workflowmetadata ensam bevisar inte installation. Om endast visade noder finns underlag för, märks paletten uttryckligen som visad och uppgiften begränsas därefter.
- Varje injicerad källa har exakta bytes/hash, deklarerad meddelanderoll/ordning, storleksbudget och källursprung. Inga dolda presets, gammal Chat eller tysta fallbackfiler. Effektiv template-/standardkonditionering redovisas separat; okända interna detaljer fabriceras inte.
- Samma semantiska kontext provas först för alla modeller. Granite-specifik adapter får endast korrigera en evidensbunden presentations-/dispatchskillnad och redovisas separat; ingen heuristic tool-repair eller lösningsfakta smygs in.

## 8. Playground och första demonstrerbara ComfyUI-slice

- Kopierade workflows är enbart källmaterial. Välj initialt WF-1-A-kopian, eftersom den ger ett verkligt workflow utan den senare subgrafkomplexiteten; kontrollera verklig struktur före fixtureval och sanera endast sådant som behövs för delning.
- Varje muterande ERST får en ny verklig filkopia och `fixture_manifest.json` med relativ aliaspath, original- och saneringshash, format/version, tillåtna ändringar, bevarandekrav, relevant palett och verifieringsbegränsningar. Kandidaten ser bara uppgiftsinput, aldrig graderfacit.
- Första end-to-end ComfyUI-provet är att döpa om exakt identifierade noders synliga `title` enligt låst instruktion. Ändra inte `type`, node-id, `Node name for S&R`, widgetdata eller länkar under förevändning att detta är samma slags namn.
- Kontrollera utvalda titlar, full parsed-JSON-likhet utanför tillåtna paths, giltig fil och skyddade kontrollfiler. Serialiseringsskillnader är tillåtna om uppgiften inte kräver bytebevarande. Kalibrera mot korrekt, fel nod, fel titel och oavsiktlig extra ändring.
- Grundfixturen ska först valideras. Befintliga strukturfel, okänd schemadialekt eller saknade nodfakta rättas/avgränsas hos fixture-/harnessägaren, inte räknas som modellfel.
- Utöka grafvalidering först när nod-/länk-/subgrafändringar behöver den: id-unikhet, länkar, slot-index, endpoints, input/outputreferenser, tillgängliga typkontrakt och definitionsreferenser. Bevara okända fält; anta inte att wildcard/dynamiska typer eller widgets följer generella statiska regler.
- Eventuella kopior av `scripts/comfyui/start_comfy_ui_backend.sh` eller små integrationsexempel kommer från comfy-projektets faktiska källfiler och märks som övningsmaterial. Kopiera endast inför en konkret uppgift; inkludera inte exekverbar hostintegration eller stora assets.

## 9. Senare ERST, skills och slutsatsgränser

- Bygg två eller tre modellneutrala WORKER-skills i `LOCAL_AGENTS/AGENT-0-WORKER/agent-0-skills/` med olika komplexitet: precis rename/preservation, grafändring/verifiering och avancerad felsökning/subgrafsprocedur. De är kandidatens runtime-data, inte Codex skills; faktisk exponering/användning måste registreras.
- Skapa uppgiftsrecept för kvarvarande rounds men lås exakt instruktion/fixture/rubric först inför respektive ERST. SFRLTT-fynd får anpassa senare detaljer; skapa inte alla framtida stora fixtures i förväg.
- Senare prov täcker nod-/länkändring, felreparation, relevant ComfyUI-kontextbruk, koherent roadmap och återupptagning. Sista ComfyUI-provet skapar ett helt nytt workflow från låst känd palett; ingen bildkvalitet eller kreativ pipeline-elegans krävs.
- Negativa resultat bedöms enbart mot förhandskrav som påverkar uppgift, scope, säkerhet eller leverans. Kosmetik och icke-kritiska metadata-/layoutvarningar ger inte ensamma FAIL. Leniency är förhandsbestämd, aldrig retroaktiv ändring av facit.
- `statiskt verifierad struktur` är inte `frontendöppnad`, `runtimevaliderad`, `Run-ready` eller lyckad generering. Om sista uppgiften kräver frontendöppning verifieras den separat utan queue/modelload; annars begränsas påståendet till statiskt styrkta egenskaper.
- Hela agentinstallationsbeslutet hålls separat från modellbedömning. En negativ modellspecifik slutsats kräver bevis för ensam modellorsak; harness-/fixture-/tool-/kontextfel dokumenteras hos rätt ägare.
- Varje fullständig eval får exakt en REPORT SUMMARY med befintliga fyra ERQER-frågeområden, källreferenser och tydlig separation av orsaker. Automatisera evidenskompletthet/hashes, inte LLM-orsaksbevis eller påhittade kvalitativa verdicts.

## 10. Klarsignaler utan onödig blockering

### Eftergranskning: transportdiagnostik före ytterligare tool-eval

Aktuell livekontroll 2026-09-14: `EVAL_4_2026-09-14-152322` genomförde tre frysta native reads, samtliga utan toolrequest/handler/receipt och med oförändrad fixture. Samma source-set/avlästa villkor/instans, men olika fångad vanlig output mellan första och senare försöken; försök 2 och 3 hade samma fragmenthash. Ingen byte-identisk PASS/FAIL-jämförelse finns. Startspärren nekade den verkliga reviewen; fortsatt tool-eval hålls stängd utan ensamorsaksbedömning. Separat bounded lifecyclecapture avslutades normalt och registrerade avlastning; därefter stoppades servern. Nästa åtgärd är read-only-interface-/templategranskning, inte blind retry. Detaljer och ERQER finns i evalens REPORT SUMMARY.

- EVAL 2:s lyckade native läsning och EVAL 3:s missade dispatch är inte ett kontrollerat A/B-par: flera projektkällor ändrades, EVAL 2 saknar rå-envelope och vissa effektiva inställningar är ofångade. De äldre källhasharna kan inte rekonstrueras från tillgängliga Git-blobs. Ingen retroaktiv kodsnapshot eller byte-identitet får påstås.
- Alla aktiva runners sparar nu en bounded snapshot av exakta UTF-8-projektkällor med relativ path, innehåll, filhash och source-set-hash. Lokalt identifierbar importkedja och explicita JS-entrypoints ingår. Snapshoten ersätter inte versions-/artefaktidentitet för installerade dependencies, modellfil eller LM Studios interna backend; installerad SDK-entrypoint, Zod-entrypoint och Node-version redovisas separat med denna begränsning.
- De publika SDK 1.5.0-callbacks för start, namn, argumentfragment, parsed request, finalized request, failure och dequeue fångas tillsammans med redan befintliga round-/fragment-/result-/receipt-händelser. Native och Granite-adapter hålls åtskilda. Rå tooltext är bounded; dess hash får inte felaktigt beskrivas som fångat komplett innehåll om råtexten saknas, är för stor eller redigerats.
- Ingen publik textinjektionshook till native parser/dispatch är verifierad. `.act()` tar genererade toolrequest-händelser från server-/generatorlagret. Uteblivet klientevent lokaliserar en evidenslucka före callbacken, men isolerar inte automatiskt en viss Desktop-parser eller modellvikterna. Se [officiell act-dokumentation](https://lmstudio.ai/docs/typescript/agent/act) och [officiell generatorbeskrivning](https://github.com/lmstudio-ai/docs/blob/main/2_typescript/3_plugins/3_generator/tool-calling-generators.md).
- `tool_transport_reproducibility.py` kör exakt tre sekventiella read-only-diagnostikförsök med samma fixture, instruktion, schema, sampling, source-set och laddade instans; varje försök får färsk Chat och befintlig 30 s kör-/5 s stoppbudget. Ändrade villkor, instansbyte eller overifierat avslut stoppar serien. Aktuellt run-id sparas före start och avbryts via befintlig read-runner. Serien laddar inte modeller och ger aldrig kandidatbedömning.
- Serien jämför fångad output och eventtyper utan att anta identiskt interninnehåll. `public_tool_raw_byte_identity_established` gäller bara den fångade första predictionens publika toolråtext och fragment. Tre lyckade reads är begränsat transportbevis, inte garanterad reliabilitet eller bevis för andra toolklasser.
- Ordinarie read/text/file-toolrunners kräver `--transport-review-file`: tre distinkta verifierade reads, oförändrad evidencehash/source-set/installerad runtime samt samma instans. Review gäller högst 30 minuter som operativ färskhetsbudget, inte statistisk modelltröskel. Saknad/ogiltig review stoppas före tokenhämtning och runskapande; instansmismatch stoppas före genereringstillstånd. Explicit bounded stoppdiagnostik är undantagen och förblir diagnostik.
- Efter en misslyckad serie startas ingen full eval eller blind likadan serie. Utred första skillnaden mellan toolrequest, guard, handler och receipt; korrigera rätt ägare och dokumentera nytt versionerat försök först när en motiverad förändring eller kontrollerad diagnostisk fråga finns. Bevara tidigare lyckad screening, strikt adapter, mutationsscope, stopp och statiska graders.
- Implementationen är offlineverifierad. Ingen ny live-diagnostik har körts under denna ändring; dispatchfelet är inte därmed löst och nya tool-evals är inte startklara förrän verklig transportreview lyckats. Historiska råfiler och bedömningar lämnas oförändrade.

- Nästa teknologioberoende eval kräver relokerad fungerande runner, aktuellt transport-/stoppbevis och den specifika uppgiftens kontrakt/kontext/grader. ComfyUI-paket, skills och hela sena kvalificeringen får inte blockera denna start.
- Roadmapens globala stegnummer visar rekommenderad bygg-/verifieringsordning, inte ett krav att slutföra alla 18 steg före nästa eval. Steg 17–18 tillämpas även vid varje tidigare relevant sliceboundary; tidig Round 2 kan bli startklar efter steg 3–5 och sin riktade integration/preflight. AutoPull är handoffinfrastruktur, inte ett mått på modellförmåga.
- Första mutation kräver därutöver verifierad write-scope, readback, budgetar och verkligt stopp utan sena writes. Första ComfyUI-ERST kräver dessutom den första självvaliderande workflowfixturen och domänkontexten.
- Lokal verifiering är kort, riktad och opt-in vid implementation; inga breda sweeps, modellviktsläsningar, tunga testkommandon eller GPU-generationer används för förberedelser.
- Bevara tidigare lyckad JSON-transformation/routing/grundning, read-only-läsning, strikt tooldispatch och cancel/normal completion med minsta relevanta regressionsmatris. Mocktester visar kodkontrakt; live-evidens visar provider-/OS-effekt.
- Vid slutkontroll uppdateras berörda README/design/statusfiler i samma slice. Inga befintliga gates får märkas implementerade innan faktiska bevis finns.

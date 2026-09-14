# EVAL 3 — REPORT SUMMARY

## Identitet och beslut

| Fält | Värde |
| --- | --- |
| EVAL-ID | `EVAL_3_2026-09-14-140930` |
| Kandidat | Granite 4.1 3B |
| Modellfil | `granite-4.1-3b-Q4_K_M.gguf` |
| Kvantisering | Q4_K_M |
| LM Studio | 0.4.24.0 |
| JavaScript-SDK | 1.5.0 |
| Kontextlängd | 8192 |
| Parallella sessioner | 1 |
| Sampling | temperature 0 |
| Evaluator | Codex |
| Relation till föregående eval | Versionslänkad fortsättning från EVAL 2:s blockerade Round 3; godkända Round 1–2 kördes inte om |
| Högsta genomförda Round | Round 3 |
| Round 3 | FAIL, 0/3 självständiga native uppgifter |
| Progression | Round 4–8 kördes inte eftersom den förhandsbestämda tool-gaten inte öppnades |
| Rollbeslut | Lås inte kandidaten som daglig 0-WORKER ännu |

## Vad som faktiskt kördes

Körningen startade LM Studio-servern och laddade uttryckligen endast `granite-4.1-3b` med 8192 tokens, en parallell session, full GPU-offload, två timmars TTL och utan speculative draft/MTP. Preflight verifierade giltig respektive ogiltig token, normal serverbekräftad completion, begäransspecifik cancel med `userStopped`, modellidentitet, effektiv template, sampling och miljöversioner. Därefter kördes Round 3:s tre separata filuppgifter i ordning. Ett strikt Granite-adapterförsök gjordes efter native read-glappet och redovisas enbart som assisterad diagnostik.

## Preflight

| Kontroll | Run-ID | Utfall |
| --- | --- | --- |
| SDK-auth | Live unittest, ingen separat runmapp | PASS: giltig token accepterades, ogiltig nekades och giltig fungerade igen |
| Verifierat cancel | `d99f9b17402249e18c64929ffac1ad0e` | PASS: `verified_cancel`, serverns stop reason `userStopped` |
| Normal completion | `da3ecd73ebbf4da28163a199230fa5bc` | PASS: exakt `OK`, naturligt `eosFound` |
| Readiness capture | `676343071a4b480382e8c0093b0b9083` | Avsiktligt `blocked`: capture observerar förutsättningar men auktoriserar aldrig själv en eval |
| Baseline source review | `724012d456784c24bbbd1fe5014d7af5` | PASS: modellfil, Q4_K_M, template-hash, load/sampling och miljöversioner länkades till primärevidens |

## Samlat uppgiftsresultat i körordning

| Round | Uppgift | Run-ID | Villkor | Faktiskt utfall | Bedömning |
| --- | --- | --- | --- | --- | --- |
| 3.1 | Läs en nested JSON-fil och återge två exakta värden | `5cd4009469354fc08b2b5fc7d281f9e5` | Native SDK tool path | Kandidaten producerade ett korrekt `read_workspace_text`-envelope för rätt fil. SDK:n signalerade ingen parse/finalize/guard/handler/receipt, filen lästes inte och värdena återgavs inte. | FAIL: uppgiften slutfördes inte |
| 3.1-D | Samma filläsning via strikt modelladapter | `40f7e270cd8848ee9902c117926af5b6` | Assisterad diagnostik | Modellutdata matchade inte adapterns dokumenterade, exakta envelope-kontrakt. Parsern avvisade utan reparation; inget tool kördes. | FAIL som assisterad diagnostik |
| 3.2 | Skapa exakt två-radersfil och använd creation-toolens oberoende readback | `67fe808dea5a4d459f802f1bf717aa1d` | Native SDK tool path | Inget tool-anrop observerades, ingen fil skapades och svaret var `STATUS=SUCCESS`. Kontrollfilen var oförändrad. | FAIL; självrapport inkonsekvent med disk/tool-evidens |
| 3.3 | Läs och gör en SHA-256-skyddad literal textändring | `5f929214d5b8455eb1acca72e4b5d8d5` | Native SDK tool path | Inget read- eller replace-anrop observerades, målfilen ändrades inte och svaret var `STATUS=FAILED`. Kontrollfilen var oförändrad. | FAIL; självrapport korrekt förenlig med misslyckandet |

## Roundutfall och progression

| Round | Status i denna eval | Gatekonsekvens |
| --- | --- | --- |
| 1 — IMSLE | Inte omkörd; EVAL 2-evidens kvarstår | Ingen ny slutsats |
| 2 — limit-testing | Inte omkörd; EVAL 2-evidens kvarstår | Ingen ny slutsats |
| 3 — basic tool usage | 0/3 självständiga native uppgifter PASS | Round 4 öppnas inte |
| 4 — intermediate tool usage | Inte körd | Blockerad av Round 3 |
| 5 — advanced tool usage | Inte körd | Blockerad av Round 3 |
| 6 — skill usage | Inte körd | Blockerad av Round 3 |
| 7 — ComfyUI-specialisering | Inte körd | Blockerad av tidigare gate |
| 8 — deployment audition | Inte körd | Blockerad av tidigare gate |

Detta är en genomförd gated eval, inte en genomförd åttarounds-sweep. Att forcera Round 4–8 efter 0/3 i den grundläggande tool-rundan skulle minska både säkerhet och tolkningsvärde.

## Modellspecifik prestationsredovisning

Följande punkter beskriver endast direkt observerade kandidatoutputs, inte obestyrkta orsaker:

1. I native read-uppgiften producerade kandidaten rätt verktygsnamn och rätt tillåten filsökväg i ett Granite-format `<tool_call>`-envelope.
2. I adapterdiagnostiken producerade kandidaten inte ett envelope som den strikta, förhandsdefinierade parsern kunde acceptera utan reparation.
3. I creation-uppgiften producerade kandidaten `STATUS=SUCCESS` trots att ingen creation-begäran eller fil fanns i evidensen.
4. I replacement-uppgiften producerade kandidaten `STATUS=FAILED`, vilket stämde med att ingen operation hade genomförts.
5. Ingen av de tre självständiga Round-3-uppgifterna blev faktiskt slutförd.

Inga bredare påståenden om modellens inneboende tool-förmåga, skuld eller generella 0-WORKER-kapacitet görs från dessa fyra observationer.

## Harness- och plattformsfynd

1. Den nya dispatchkedjan gav användbar negativ evidens: när tool-aktivitet saknades fanns inte heller events för raw parse, finalized request, guard, handler eller receipt.
2. I native read-runnen fanns ett syntaktiskt korrekt Granite tool-envelope i modellresultatet, men LM Studio SDK 1.5.0 exponerade det som text och startade ingen tool-dispatch. Det lokaliserar glappet till template/parser–dispatchgränsen i denna integration.
3. Samma modell, template-hash och read-instruktion gav en slutförd native tool-read i EVAL 2. Runnerkoden hade därefter fått ny evidensinstrumentering, så resultaten visar bristande reproducerbarhet men bevisar inte ensam vilken komponent som orsakar skillnaden.
4. Det strikta adapterspåret reparerade inte malformed output och fabricerade inte tool-argument. Det bevarade säkerhetsgränsen men gav ingen fallback-framgång i denna run.
5. Hashar, tool receipts, diskutfall och completion claims hölls åtskilda; textpåståenden kunde därför inte räknas som utförda filoperationer.

## Evaldesign- och evaluatorfynd

1. Instruktionshashen finns nu i varje Round-3-evidensfil och kan bindas direkt till bedömningen.
2. `operation_status` och `self_report` visade två olika, beslutrelevanta felbilder: falsk framgång i creation och sanningsenligt misslyckande i replacement.
3. En direkt evaluatorstyrd tool-canary användes inte som kandidatbevis, eftersom den skulle kringgå den faktiska modelloutput→template/parser→tool-kedjan.
4. Ingen uppgift upprepades tills PASS. Adapterförsöket bevarades separat och gav ingen native kredit.
5. Round 4 stoppades av den etablerade gaten; stoppet beror på uppgiftsutfall och tool-evidens, inte kosmetiska kriterier.

## Praktisk slutsats

Granite 4.1 3B är inte redo att låsas som Team Masters dagliga 0-WORKER på nuvarande LM Studio SDK-toolväg. Den viktigaste orsaken till att inte fortsätta är praktisk: de tre grundläggande filuppgifterna blev inte utförda. Samtidigt är det inte professionellt försvarbart att kalla hela utfallet ett rent modellfel, eftersom native read-outputen innehöll rätt tool-envelope men dispatchkedjan stannade före parser/handler, och ett motsvarande read hade fungerat i EVAL 2.

Nästa högsta ROI-arbete är därför ett avgränsat plattforms-/harnessarbete som reproducerar och lokaliserar varför samma Granite-envelope ibland blir ett SDK tool request och ibland bara text. Först när den vägen är deterministiskt verifierad bör Round 3 återtestas som en ny versionerad eval. ComfyUI- och bredare skilluppgifter ska inte användas för att felsöka denna grundläggande dispatchgräns.

## Eftergranskning och avslutad runtime

- Den mekaniska evidence reviewn passerade för samtliga fyra uppgifts-/diagnostikrun: identitet, instruktionshash, oförändrade källfingerprints, retryvillkor, assessment-hash, fixturekontrakt, efterhash och workspace-scope.
- Ingen källa ändrades mellan respektive run och dess assessment.
- Granite-instansen avlastades efter rapporteringen; `lms ps --json` gav `[]`.
- LM Studio-servern som startades för EVAL 3 stoppades; port 1234 hade noll lyssnare.
- Inga Git-filer stageades eller committades.

## Evidensindex

- `d99f9b17402249e18c64929ffac1ad0e/evidence.json` — verifierat cancel.
- `da3ecd73ebbf4da28163a199230fa5bc/evidence.json` — normal completion.
- `676343071a4b480382e8c0093b0b9083/readiness.json` — readiness capture.
- `724012d456784c24bbbd1fe5014d7af5/` — baseline-, identitets- och miljöreview.
- `5cd4009469354fc08b2b5fc7d281f9e5/evidence.json` och `assessment.json` — native read.
- `40f7e270cd8848ee9902c117926af5b6/evidence.json` och `assessment.json` — strikt adapterdiagnostik.
- `67fe808dea5a4d459f802f1bf717aa1d/evidence.json` och `assessment.json` — creation/readback.
- `5f929214d5b8455eb1acca72e4b5d8d5/evidence.json` och `assessment.json` — hash-skyddad replacement.

## EXTERNAL-REVIEW-QUESTIONS-EVAL-RESULT [ERQER]

Reviewern ska utgå från rå evidens, hålla modell-, harness- och evaldesignorsaker separata och prioritera praktiskt hög ROI framför kosmetik.

1. Vad kunde Frontier-evaluatorn Codex ha gjort mycket bättre eller annorlunda i denna gated fortsättnings-eval?
2. Hur kan framtida utvärderade agenter ge mer användbara och försvarsbara resultat eller insikter på modellspecifik respektive modellneutral nivå?
3. Hur kan framtida evals förbättras icke-kosmetiskt och icke-trivialt?
4. Vilka andra mycket höga eller höga ROI-insikter bör Codex adressera eller implementera?
5. Vilket minsta reproduktionskontrakt kan säkert skilja mellan Granite-envelopeproduktion, LM Studio-templateparsning, SDK request-finalisering och tool-dispatch utan att ersätta kandidatens ansvar med evaluatorstyrd exekvering?
6. Vilken evidens krävs för att avgöra om EVAL 2:s native read-PASS och EVAL 3:s native read-FAIL är modellvariation, runnerinstrumenteringspåverkan eller LM Studio/SDK-parservariation?

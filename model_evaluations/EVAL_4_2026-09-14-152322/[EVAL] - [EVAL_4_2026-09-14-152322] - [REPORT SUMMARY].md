# EVAL_4_2026-09-14-152322 — REPORT SUMMARY

## 1. Beslutsvärde och omfattning

Codex körde 2026-09-14 en avgränsad **transportdiagnostik**, inte en ny fullständig kandidat-eval. Frågan var: kan tre likadana read-only-försök under samma laddade Granite-instans ge verifierad native tool-exekvering, och vilka publika output-/eventskillnader syns?

**Resultat: 0/3 exekverade läsningar.** Ingen full tool-eval eller automatisk omkörning startades. Den verkliga startspärren avvisade denna review. Diagnostiken ger ingen kandidatpoäng och ingen negativ modellspecifik prestationsbedömning.

Det nya beslutsvärdet är att projektkällor och fångade effektiva villkor nu var lika mellan försöken, medan den observerade vanliga textoutputen inte var lika i alla tre. Därmed finns inte det byte-identiska PASS/FAIL-par som skulle kunna isolera runtimevariation från genererad outputvariation.

## 2. Kontrollerade villkor och luckor

- Evaluator: Codex. Kandidatinstallation: Granite 4.1 3B Q4_K_M, SDK-identifierare `granite-4.1-3b`.
- SDK-readback: modellpath `lmstudio-community/granite-4.1-3b-GGUF/granite-4.1-3b-Q4_K_M.gguf`, 2 099 501 664 byte, samma `instanceReference=xE9Byn/z4lTLLjyHYoiGDJxS` i alla tre.
- Load-readback: kontext 8192, auto-fit false, GPU-offloadkvot 1, CPU-pool 6, Flash Attention true, en parallell session. Exponerade draft-MTP/sidecar-flaggor var false.
- Prediction-readback: temperatur 0, max 512 outputtokens och exakt ett registrerat `read_workspace_text`-schema med obligatorisk relativ `path` och `additionalProperties=false`. Max två prediction-rounds, två tool-anrop, ingen parallell toolexekvering; 30 s körbudget och 5 s stoppbudget per försök.
- Färsk SDK Chat per försök; endast aktuell user-uppgift från projektet. Ingen WORKER-rollkontext, projektägd systemprompt, formatcoaching eller Granite-adapter. Tool-schema/template-konditionering finns däremot; detta är inte zero-context-basförmåga.
- Effektiv templatehash: `fed2756d2d24e127b951dcf139d0b03ab7db8ef23a456128ebc9c2db4901d476`. Varje prediction rapporterade 255 prompttokens.
- Samma fasta fixture: `project/config/service.json` med `queue_name=render-diagnostic`, `retry_limit=3` och irrelevanta kontrollfält. Original- och sluthash matchade per försök.
- Exakta bytes för 16 projektkällor fångades, återverifierades och var oförändrade efter serien. Source-set: `d89d255c7f42ce78ca654022e83072149472250f95c5186d39a8ba7c4b981b29`. Samma conditions-hash i alla tre: `71e74d72cb0e5d92a27e5108393a5ddde65b336d97e1a9d6f23df051e6d4f2a9`.
- Runtime: publicerad SDK 1.5.0, Node v24.11.1. Installerade SDK-/Zod-entrypoint-hashar finns i originalreview. Native inventory lyckades med giltig token; avsiktligt ogiltig token nekades med HTTP 401. Token sparades inte.
- Luckor: exakt backendidentitet, samtliga interna inställningar och text före intern serverklassificering exponeras inte av denna capture. GGUF-filen hashades inte på nytt; identifierbar modellpath/storlek/kvantisering avlästes. Temperatur 0 antas inte garantera determinism. Slutreadback är inte en oberoende fångst av varje internt inferenstillstånd.

## 3. Uppgiften och utfallen i körordning

Exakt instruktion i varje försök:

> Read project/config/service.json using the available file tool. Tell me the queue_name and retry_limit from that file. Do not guess values or modify files.

| Ordning | Run-id | Observerad leverans | Faktisk tool-effekt | Avslut / genereringstid |
| --- | --- | --- | --- | --- |
| 1 | `45518d72a7b44c5babbc91d80ca4af5b` | Vanlig text med toolnamn och rätt relativ path; inget avslutande envelope-tag i fångat svar. Inga efterfrågade filvärden. | 0 completed, 0 active; fil oförändrad. | `eosFound`, 0,586653 s |
| 2 | `12849c0345dd451bbf1daa79d58afea7` | Vanlig text med enbart path-objekt efter öppningstag; inget toolnamn/arguments-objekt eller avslutande tag i fångat svar. Inga filvärden. | 0 completed, 0 active; fil oförändrad. | `eosFound`, 0,105338 s |
| 3 | `51262282c95f452bb1387af0eb90c1a7` | Samma fångade vanliga textbytes som försök 2. Inga filvärden. | 0 completed, 0 active; fil oförändrad. | `eosFound`, 0,108903 s |

Genereringstider är SDK:s `stats.totalTimeSec`, inte tid till användbart verifierat resultat: inget försök levererade sådant resultat.

Fångat svar, försök 1:

```text
<tool_call>{
  "name": "read_workspace_text",
  "arguments": {
    "path": "project/config/service.json"
  }
}
```

Fångat svar, försök 2 och 3:

```text
<tool_call>{
  "path": "project/config/service.json"
}
```

Dessa är outputobservationer, inte bevis på ensam modellorsak eller på exakt text före serverns interna hantering.

## 4. Harness-/SDK-fynd, skilda från modellbedömning

- Alla tre gav normal round-/fragment-/message-/resultkedja och naturligt slut. Ingen av de instrumenterade publika toolrequest-callbacks nåddes: start, namn, argumentfragment, parsed, finalized, failure eller dequeue. Inte heller guard, handler eller receipt nåddes.
- De fångade vanliga textfragmentens SHA-256 var `b8b1e8f5864cc85754a37fae696436dab1189838c3a458098ff88c58ca735b2c` i försök 1 och `54e5e920be190e9eb0c09f64c4b08bac7f461cf931bd12063bac57e7dc264093` i försök 2 och 3.
- Review redovisar `observed_outputs_identical=false`, `event_sequences_identical=true` och `public_tool_raw_byte_identity_established=false`. Lika tomma tool-eventsekvenser betyder inte fungerande dispatch. Parsed tool-råtext saknas helt, så dess byte-identitet kan inte bedömas.
- Detta motiverar fortsatt stängd tool-evalgate. Det isolerar inte Desktop-parsern, SDK:n, templatehanteringen eller modellvikterna som ensam felägare. Den synliga outputvariationen förhindrar det föreslagna kausala argumentet från byte-identisk output med varierande dispatch.
- EVAL 2:s lyckade native read kan inte användas som kontrollerat PASS-par här: andra projektkällor och ofullständig historisk råcapture. Ingen historisk evidens kompletterades retroaktivt.

## 5. Evaluatorprocess, säkerhet och nästa åtgärd

Resursuppskattning före laddning var 2,62 GiB; cirka 7 GiB GPU-minne var ledigt. Endast Granite laddades. Ingen ComfyUI-backend, checkpointoperation, bildgenerering, kandidatkod eller skrivtool användes.

Den extra no-generation-readiness-capturen verifierade laddad modell men behöll avsiktligt screeningstatus `blocked` för sina ännu ej utförda bredare live-baselinekrav. Den användes inte som godkänd screening eller kandidatbehörighet. Den separata transportdiagnostiken var det auktoriserade experimentet.

Alla tre försöken avslutades naturligt innan något konkret behov av manuellt avbrott uppstod; ett avbrott fabricerades därför inte. Efteråt avlästes `idle`, `queued=0` och noll aktiva tools. Granite avlastades efter denna kontroll. Ingen Git-index-/history-operation utfördes.

Den 90 s bounded generiska lifecyclecapturen avslutades normalt med initialt modellstate och registrerad avlastning. Därefter stoppades LM Studio-servern. Slutkontroll: `lms ps --json=[]` och noll lyssnare på port 1234.

Nästa hög-ROI-åtgärd är read-only-granskning av det faktiskt renderade toolinterfacet och dess överensstämmelse med den effektiva Granite-templaten samt publikt kontrakt. Välj därefter högst ett motiverat versionsbundet experiment hos rätt ägare; inte fler oförändrade full-evals, blind retry eller påhittad parserinjektionshook. Att ge tydligare gränssnittskontext är ett möjligt separat conditioned experiment, inte en retroaktiv reparation av denna serie.

## 6. Evidensförteckning

Alla paths är relativa till denna evalrot; originalfilerna är revisionsbevis.

| Evidens | Fil / datapekare |
| --- | --- |
| Serie och admissionbeslut | `ac0556c76ec04d9d81ea2a35c9e51449/transport_review.json`: `runs`, `status`, identiteter och jämförelseflaggor |
| Försök 1–3 | Varje run-id ovan: `evidence.json`, särskilt `events`, `result`, `fixture`, `source_snapshot` och `runtime_identity` |
| No-generation-readiness | `478a7c9d9bd64b2f8b9c74964784790e/readiness.json` |
| Generisk driftobservation, separat ägare | `../../LM-Studio_logs/model_lifecycle_events/20260914_152356121_56803623-72d8-493c-844e-5bd922519a86.json`, korrelation med denna eval-id; bounded native capture, inte kandidatbedömning |

Reviewens hashreferenser till de tre original-evidencefilerna har bevarats. Rapporten återger observationer, inte nya automatiska modellverdicts.

## EXTERNAL-REVIEW-QUESTIONS-EVAL-RESULT [ERQER]

### Tillägg efter Team Masters ROI-omprioritering — separat read-only-inspektion

Originalserien och dess evidens/bedömning är oförändrade. Befintliga fragment rekonstruerar sluttexten exakt; avvikelsen börjar vid teckenposition 16 (nollbaserat), där `name` respektive `path` följer samma prefix. Fragment är inte verifierade enskilda tokens och avvikelsepositionen isolerar inte cache eller GPU.

Separat efterföljande inspektion: `06686f3aa3d1411896919b1250b45ff5/tool_interface_inspection.json`, `generation_requested=false`, endast `model_bound` och `model_inspection`. Public `applyPromptTemplate(chat, {toolDefinitions})` med exakt sparad instruktion/schema gav toolnamnet, korrekt schema och full `name`/`arguments`/avslutande tag-vägledning; inputantal 255. Det är en rekonstruktion med den då laddade instansens template, inte fångad historisk `.act()`-request. Samma tokenantal ensamt bevisar inte lika inputbytes.

Praktiskt beslut: ingen uppenbar saknad interfaceinstruktion motiverar en blind templatefix. Inga fler predictions, full-evals, cache-/kernelstudier eller omladdningsserier har körts. Grundläggande native toolkompatibilitet är fortfarande inte godkänd; nästa eventuella generering måste ha en liten explicit intervention och ett förhandsbestämt installationsbeslut. Modellen avlastades och servern stoppades efter inspektionen.

1. Vad kunde jag, Codex som Frontier-evaluator, gjort mycket bättre eller annorlunda? Prioritera om den valda tre-försöksdiagnostiken och captureluckorna gav rätt beslutsvärde.
2. Hur kan framtida agentkandidater ge mer lönsamma, användbara och försvarsbara insikter på modellspecifik respektive modellneutral nivå? Vilket minsta verifierat interface-/conditioningexperiment skiljer praktisk installationsförmåga från transportglapp?
3. Hur kan framtida EVALS förbättras icke-kosmetiskt och icke-trivialt? Föreslå ett faktiskt publikt genomförbart nästa experiment; varken oförändrad full-eval eller en icke-existerande text-till-native-parser-hook.
4. Vilka övriga mycket höga eller höga ROI-insikter bör Codex adressera eller implementera? Ange evidens, rätt ägare, beslutsnytta, tradeoff och minsta verifiering; lämna obevisad orsak öppen.

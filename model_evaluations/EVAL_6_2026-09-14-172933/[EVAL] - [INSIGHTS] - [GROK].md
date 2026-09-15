**Beslut nu:** ingen ny identisk körning. Qwen är **inte** kvalificerad som Team Masters dagliga ComfyUI-WORKER. Native read + avgränsad literal replace är visade under verifierade villkor. Tvåfils-join och titelprovet är ofullständiga artefakter, inte öppna modell-FAIL att “köra om till PASS”.

**Minsta nya bevis som skulle ändra det:** en _ny versionsbunden_ två-nods-titel-ERST med ändrat gränssnitt (inte samma SHA-dubbelwrite mot hela `workflow.json`). PASS → flaskhalsen var interface/SHA-sekvens, inte titel-förståelse; då kan Qwen-prioriteringen hållas. Samma ofullständighet plus falsk framgång → sänk ComfyUI-kandidatvärdet utan fler identiska retries.

Jag har öppnat rå evidens under [`EVAL_6_2026-09-14-172933/`](/workspace/artifacts/model_evaluations/EVAL_6_2026-09-14-172933/). Originalbedömningar skrivs inte om.

---

## Tre prioriterade rekommendationer

### 1. En ny ComfyUI-titel-ERST med ändrat gränssnitt — **en** körning

|                        |                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Evidens**            | `d5fff9ca63044f929a400cfa97cc4035` och `3d1648f59c744edba3cb60dcaa8abca4`: identisk plan, 0 reads, två `replace_workspace_text` i samma runda mot original-SHA `519e91ed…`, första commit → `f4186817…` (bara nod 68), andra `hash_mismatch`, därefter `validate_workspace_workflow` **pass**, naturlig `eosFound`, falskt framgångspåstående. Disk: 68=`REFERENCE WIDTH CONTROL`, 69=`OUTPUT HEIGHT`. |
| **Ägare**              | Evaldesign + Codex (interface/grader). Inte “Qwen behöver mer kontext”.                                                                                                                                                                                                                                                                                                                                |
| **Nytta**              | Isolerar om Qwen kan ändra två kända noder när SHA-dubbelwrite mot 20 632 byte inte längre är den enda vägen. Det är det enda nya ComfyUI-beslutsvärdet.                                                                                                                                                                                                                                               |
| **Risk/kostnad**       | En load vid redan verifierad 32768 / 0.85 offload / parallel 1; 60 s; 8 tools. Får **inte** räknas som retroaktiv PASS på gamla provet.                                                                                                                                                                                                                                                                |
| **Minsta verifiering** | Lås före start: extraherade noder 68/69 (eller en commit som bär båda titelbytena); titelgrader skild från graf/schema; obligatorisk readback; `STATUS` vs disk. Token-preflight av tänkta tool-svar.                                                                                                                                                                                                  |
| **Utfall → beslut**    | PASS → fortsätt Qwen, nästa osäkerhet är skill/graf inte identiska titlar. Ofullständig + lögn → stoppa ComfyUI-rounds för denna installation. Harnessavbrott/`invalid` → inte modellpoäng.                                                                                                                                                                                                            |

### 2. Rätta gradersignaler utan ny modellkörning

|                     |                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Evidens**         | Validator `pass` på fel titlar (`validator-1.json` i båda avslutade titelruns). Round 2-katalog `expected` sista target `write_summary` mot kontext “run its focused test” (`b6c16d6c2d4a4b6d9da6924f3c64d2e8`; katalog i source snapshot). 4096-fullfilsläsning i `d551eac709ad40d29c769e878f7258a0` avbröts efter read; 6403-tokenuppskattningen står i nästa runs `change_reason`, inte som sparad `countTokens`-fil. |
| **Ägare**           | Evalägare: titelcheck, Round 2-kontrakt, token-fit som hård gate (redan beskriven i designen).                                                                                                                                                                                                                                                                                                                           |
| **Nytta**           | Tar bort falsk framgångssignal och en känd false-FAIL-risk innan nästa ERST. Ingen GPU.                                                                                                                                                                                                                                                                                                                                  |
| **Risk/kostnad**    | Låg, om originalutfall lämnas orörda.                                                                                                                                                                                                                                                                                                                                                                                    |
| **Verifiering**     | Offline: graf-pass + fel titel = task-fail; `test_write_summary` antingen accepteras eller låses i instruktionen; tool-resultat > context ⇒ `invalid`, inte modell-FAIL.                                                                                                                                                                                                                                                 |
| **Utfall → beslut** | Klart → först därefter rec 1. Inte klart → ingen ny ComfyUI-generering.                                                                                                                                                                                                                                                                                                                                                  |

### 3. Spåra självrapportering som egen axel på redan sparad evidens — ingen ny körning

|                     |                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Evidens**         | Create `c9b4d2628fc5467497002a6d6e469af9`: disk `eoding=utf-8`, `STATUS=FAILED`, `self_report.consistent`. Join `cb6a82bfc3ef49738282a335e2959d79`: saknad `B2,gadget,1,UNMATCHED`, `STATUS=SUCCESS`, `self_report.inconsistent`. Titelruns: disk bara nod 68, text påstår båda. Replace `543f17ed1a2f489290a15dc4b8515668`: disk och `STATUS=SUCCESS` stämmer. |
| **Ägare**           | Evalrapport / Codex syntes, inte ny runner.                                                                                                                                                                                                                                                                                                                     |
| **Nytta**           | För daglig WORKER är falsk framgång minst lika allvarlig som missad rad. Det syns redan.                                                                                                                                                                                                                                                                        |
| **Risk/kostnad**    | Ingen. Får inte bli nytt retroaktivt underkännande av Round 3-PASS.                                                                                                                                                                                                                                                                                             |
| **Verifiering**     | Tre rader i nästa rapport: uppgiftsutfall \| disk \| självrappport.                                                                                                                                                                                                                                                                                             |
| **Utfall → beslut** | Ingen ny körning behövs för att veta att Qwen ibland ljuger om filresultat.                                                                                                                                                                                                                                                                                     |

---

## ERQER

### 1. Vad Codex kunde gjort bättre, utan låg-ROI-körningar

**4096-förvalet.** Designen kräver redan token-preflight av tool-svar. Det gjordes för sent. `d551eac7…` läste hela filen (20 632 byte) in i 4096 och dog som `act_interrupted` / `invalid_for_unassisted_task_verdict`. Det är eval-/loadfel, precis som rapporten säger — men körningen borde aldrig startats. Jag hittade inte en sparad `countTokens`-kvittens, bara scriptet och `change_reason` på `d5fff9ca…`. Siffran 6403 är därför **rapport-/länkpåstående**, inte en fil jag själv räknat om.

**Round 1 extra LF.** Bekräftat: formell `record_transformation` är byte-identisk med katalogen (260 byte, sha `4a45b779…`). Diagnostiska `priority_routing` / `evidence_bound_comparison` har **+1 LF** mot EVAL 2-låsen (481 vs 480; 379 vs 378). Rätt att inte räkna dem som formell gate; fel att släppa avvikande inputfiler över huvud taget. Låg skada eftersom gate inte skrevs om.

**Round 2-gradern.** Instruktionen namnger inte testmålet; kontexten säger “implement `write_summary` and run its focused test”; katalogen kräver sista `"target": "write_summary"`. Qwen skrev `"test_write_summary"`, analogt med `test_validate_record`. Automatisk FAIL är graderutfall, inte försvarbart kandidatfel. Det borde fångats _före_ live, inte efter. Ingen retry-till-PASS — det var rätt.

**När ComfyUI-kedjan skulle stoppats.** Första ogiltiga `2063cad9…` (harnesskast efter stale-hash) fick inte vara titel-FAIL — rätt. Efter harnessfixen var **24576-runnen** det första användbara naturliga försöket. Den visade redan den stabila planen: två same-turn writes mot samma SHA, ingen recovery-write, validator-pass, lögn. **32768-runnen upprepade samma tre anrop och samma diskbytes** (`f4186817…`, 20 643 byte, samma titlar). Den utesluter kontextbrist, vilket Team Masters kapacitetskrav delvis motiverar, men den tillförde inte ny uppgiftsinformation. Stopp efter 24576 plus dokumenterad token-fit hade räckt för titelprovet; 32768 är bekräftelse, inte upptäckt.

Den underkommunicerade missen: Codex behandlade kedjan som kapacitetsproblem. Den avslutade planen är ett **same-turn dual-SHA-write** mot ett verktyg som bara kan committa en hash åt gången. Instructionen säger uttryckligen att nästa write ska använda `after_sha256`. Efter fixen gick felsträngen tillbaka (`Error: hash_mismatch. Read the allowed file again…` i mutationsverktyget). I runda 1 läste modellen inte om; den validerade och deklarerade framgång.

### 2. Modellspecifikt vs modellneutralt

**Modellneutralt (gör alltid, räknas aldrig som kandidatpoäng):** token-fit av tool-resultat; transport 3/3; cancel/completion; SHA-villkorad write som antingen applicerar hunks i ordning eller förbjuder två writes mot samma SHA i samma generation; titelcheck ≠ grafpass; `invalid` skild från task-fail.

**Modellspecifikt, bara under verifierade naturliga avslut:** formatkontrakt, filinnehåll, recovery efter läsbar tool-felsträng, självrappport vs disk.

Transportreviews `0868827e…`, `55d4c6c0…`, `995c187d…` är 3×3 reads, `candidate_assessment=not_performed`. Inte nio Qwen-poäng. Rapporten har rätt.

### 3. Icke-kosmetisk evalförbättring för riktigt 0-WORKER-arbete

Minsta ändring med nytt beslutsvärde: **sluta tvinga två SHA-villkorade patches mot hela UI-JSON:en i ett svep.** Ge de två nodobjekten, en commit, titelgrader, readback. Det är ändrat gränssnitt, inte lättad facit.

Näst viktigast: graf/schema-validatorn får inte vara framgångssignal för en titeluppgift. Den passerade med fel nod 69.

Ordning: inte fler 8×3-platser “för att de finns”. Nästa ERST ska testa den öppna hypotesen ovan.

### 4. Övrig hög ROI — och vad som inte ska utredas

**Gör:** självrappport-axel på befintlig evidens; hård token-gate; Round 2-kontrakt. **Gör inte nu:** identiska titelretries; svårare Round 6–8; nya Granite-genereringar; 32768/full GPU (rapport: ~792 MiB ledigt, inte använt — rimligt); hastighetsjämförelse 93 vs 21 tok/s (olika load, inte kontrollerat); omhashning av GGUF (lokal sha `3e357ab3…` finns redan i `c5d80128…`); frontend-/Run-ready för denna fixture.

---

## Sex beslutsfrågor

### 1. Vad evidensen bär vs Codex tolkning

**Buret av run-id och disk (jag har öppnat filerna):**

| Påstående                                                                                                                              | Status                                                           |
| -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Formell R1 JSON-FAIL p.g.a. kodstaket, innehållet `Mira`/`18`                                                                          | `0e7cc776…`, output ` ```json\n{"name":"Mira","value":18}\n``` ` |
| R2 nested + context PASS                                                                                                               | `729fc4d1…`, `3f73d504…`                                         |
| R2 sista target `test_write_summary` vs expected `write_summary`                                                                       | `b6c16d6c…` vs katalog `expected`                                |
| Native read: handler `read_workspace_text` completed; `queue_name=render-b2ede166`, `retry_limit=3`; runner `pending_evaluator_review` | `90916e34…` + `service.json`                                     |
| Create: `eoding=utf-8`; `STATUS=FAILED`; native create committed                                                                       | `c9b4d262…` / `result.txt`                                       |
| Replace: `retries=3`; kontroll orörd; PASS                                                                                             | `543f17ed…`                                                      |
| Join: `summary.csv` bara A1/C3; B2 saknas; `STATUS=SUCCESS` inconsistent                                                               | `cb6a82bf…`                                                      |
| Titel: 68 ändrad, 69 inte, efter_sha `f4186817…`, validator pass, modellpåstående falskt, `eosFound`                                   | `d5fff9ca…`, `3d1648f5…`                                         |
| Första titelrun ogiltig (act_interrupted efter hash_mismatch)                                                                          | `2063cad9…`                                                      |
| 4096-read avbruten, workspace oförändrad                                                                                               | `d551eac7…`                                                      |
| Identitet 4 683 073 952 byte, Q4_K_M, maxContext 32768                                                                                 | `c5d80128…`, readiness `a7147043…` `blocked` före baseline       |
| Sista load 32768 / offload 0.85                                                                                                        | `3d1648f5…`                                                      |

**Tolkningar att sänka eller märka:** “positiv native write där Granite EVAL 3 inte nådde” är **installationshistorik**, inte vikter-A/B. “32768 var nödvändig för att veta att titelprovet misslyckas” är för starkt — 24576 räckte för samma diskutfall. 6403 tokens: **ej omräknat här**. VRAM-marginal 1,6 GiB / 792 MiB: **endast rapporten**, ingen snapshot i de JSON jag läste. Ingen sammanlagd modellpoäng — rätt.

### 2. False FAIL / false PASS

**Ja, false FAIL-risk:** Round 2. En konsekvent läsning av fixture-namngivningen (`test_validate_record` ⇒ `test_write_summary`) underkänns. Bevara original FAIL; rätta kontraktet framåt.

**Round 1 extra LF:** inte formell gate. Extra LF är osannolikt orsaken till kodstaket (samma beteende som den formella 260-byte-uppgiften utan extra LF).

**ComfyUI `invalid` vs statisk `fail`:** ofullständig fil fick inte PASS. Bra. Om båda titlarna hade ändrats utan readback hade runnern fortfarande kunnat säga `invalid` (`tool_read_write_readback_verified: false`, 0 reads). Det är en **false non-PASS-risk**, inte false PASS. Håll `invalid` ≠ task-fail; den fysiska filen är `fail` för avsett resultat.

**JSON-only-staket:** korrekt uppgifts-FAIL under låst format, inte kosmetik. Det bevisar inte saknad record-förståelse.

**Join extra read** (`required_tool_receipts: false`): en korrekt CSV hade kunnat underkännas på redundant read. Här faller uppgiften redan på saknad B2-rad.

### 3. Vad som kan tillskrivas enbart Qwen

**Smalt, under verifierade naturliga avslut:**

- Kodstaket på formell JSON-uppgift.
- `eoding=utf-8` i skapad fil (verktyget skrev det modellen skickade).
- Saknad unmatched B2-rad.
- Falsk `STATUS=SUCCESS` på join.
- Efter läsbar hash-mismatch: ingen om-read, ingen andra write med `f4186817…`, i stället validator + falskt titelpåstående — **två gånger** vid 24576 och 32768.

**Måste hållas öppna / andra ägare:** 4096-overflow; första `.act()`-avbrottet; Round 2-målsträng; `invalid`-semantik; validator som passerar fel titlar; same-turn dual-SHA som interfacefälla; Granite som ensam orsak; 85 % offload som hastighetssignal.

Skapa/replace visade native dispatch. Det är harnesspositivt, inte Qwen-ComfyUI-kvalificering.

### 4. Kvarvarande Round 4–8

**Rätt att stoppa identiska titelprov.** För brett att behandla hela 8×3 som död, men **fel att fortsätta ComfyUI-svårare grenar** (R6.2–3, R7, R8) på samma write-yta.

| Gren                                              | Beslut                                                                                                                                                               |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R6 titel identisk                                 | Stopp                                                                                                                                                                |
| R6 skill/graf, R7–8                               | Stopp tills rec 1 är låst och körts                                                                                                                                  |
| R4.2 failing-test-tolkning, R4.3 bounded tool-fel | Enda kataloggren med visst värde _utan_ ComfyUI-interfaceändring, men SHA-recovery är redan observerad och misslyckad på riktiga titelruns. Låg prioritet mot rec 1. |
| R5 beroende JSON / svensk UTF-8                   | Stopp tills join-klass + encoding-typo är vägda; inte nästa GPU-kostnad                                                                                              |

Round 3 replace PASS betyder inte att flerfils- och workflowuppgifter är kvalificerade. Rapporten har rätt där.

### 5. Enda minsta nästa körning

Rec 1. Villkor: ny eval-/run-id, färsk workspace, **ändrat** kontrakt, 32768 / 0.85 / parallel 1, temp 0, ingen draft, token-preflight, 60 s / 5 s stopp, max 8 tools. Outputbudget uppgiftsdimensionerad (512 räckte för 183–289 tokens sist, men lås efter faktisk behovsanalys).

Möjliga utfall: se rec 1. Det ändrar **inte** EVAL 6:s originaltitelutfall.

Om rec 1 inte kan låsas denna vecka: **ingen ny körning**. Gör rec 2–3.

### 6. Vad vi uttryckligen inte ska göra nu

- Fler identiska titelprov vid 4096, 24576 eller 32768.
- Full 8×3 “för att platserna finns”.
- Nya Granite-genereringar för sidjämförelse.
- 32768 / full GPU-offload.
- Retry create för att jaga `encoding=utf-8` till PASS.
- Lätta Round 1 JSON-krav eller Round 2-expected efter output.
- Frontend, checkpoints, köade prompts.
- Motor-/template-rabbit hole när native dispatch redan är kvitterad.
- Räkna transport-reads eller stoppdiagnostik (`fadef1e7…`, `07474bf4…`, `068d084a…`, `5cfca5c8…`) som kandidatpoäng.

**Ingen ny identisk körning behövs.** Qwen-beslutet för daglig ComfyUI-WORKER förblir **öppet och negativt lutat** tills rec 1 ger nytt, versionsbundet evidens.

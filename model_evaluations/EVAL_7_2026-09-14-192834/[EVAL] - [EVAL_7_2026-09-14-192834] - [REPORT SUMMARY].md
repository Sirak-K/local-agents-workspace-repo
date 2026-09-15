# EVAL 7 — Qwen completion integrity och ComfyUI-multisteg

## Syfte och beslutshypotes

EVAL 7 prövade den minsta praktiska frågan efter EVAL 6: om den förbättrade modellneutrala WORKER-konditioneringen, den oberoende completion-grinden och ett reparerbart tool-felkvitto gör Qwen-installationen kapabel att slutföra och sanningsenligt rapportera den befintliga tvånodsuppgiften.

Detta var inte en full 8×3-eval och inte ett rent kausalt A/B-test av systemprompten ensam. Ingen Granite-generering gjordes. Historiska EVAL 6-resultat ändrades inte.

## Låsta villkor

| Villkor | Faktiskt värde |
|---|---|
| Kandidat | `qwen2.5-7b-instruct`, Qwen2.5 7B Instruct, GGUF Q4_K_M |
| Modellkontext | 32768 |
| GPU-offload | 0,85 |
| Parallellitet | 1 |
| Draftmodell | Ingen |
| Sampling | Temperature 0 |
| Uppgiftsbudget | 60 sekunder, 8 tool calls, 6 prediction rounds, 512 outputtokens |
| Kandidatskill | Explicit `workflow_title_preservation` |
| Fixture | `workflow_rename_fixture.json` version 2 |
| Scope | Unik disponibel `workflow.json`; ingen ComfyUI-start, modelladdning från kandidaten eller promptköning |
| Sanningsägare | Diskartefakt, ordnade tool-kvitton och oberoende grader |

Den generella systemregeln krävde evidensbunden framgång. Uppgiftskontraktet krävde exakt första rad `STATUS=SUCCESS` eller `STATUS=FAILED`. Skillen krävde initial läsning, hashvillkorade writes, after-hash-kedjning, slutlig readback och sanningsenlig rapportering.

## Transport och runtime

Två separata source-bundna native transportreviews kördes eftersom toolkällan ändrades mellan uppgiftsförsöken:

| Review | Resultat | Roll i bedömningen |
|---|---|---|
| `d375e23541cf46d988b24d1c2ccd497c` | 3/3 verifierade native reads | Transportgate före första försöket; inga kandidatpoäng |
| `b01bdebd8da34030a3a4f0b477c620d6` | 3/3 verifierade native reads | Ny transportgate efter tool-feedbackändringen; inga kandidatpoäng |

Samma laddade modellinstans användes inom körningen. Kö var tom och inga parallella kandidatsessioner startades.

## Uppgiftsresultat i ordning

| Försök | Villkorsändring | Faktisk leverans | Självrapport | Bedömning |
|---|---|---|---|---|
| `b5931654ae514136a9b0b529847d6da9` | Ny completion-grind, generell evidensregel och fixtureversion 2 | Nod 68 ändrades korrekt. Nod 69 förblev `OUTPUT HEIGHT`. Inga reads. En completed write, en denied write och en statisk validator. | `STATUS=FAILED`; överensstämde med faktisk FAIL | Task `fail`; self-report `consistent`; assessment `fail` |
| `6f822a2e41734400b835b08093bccfc6` | Länkat återtest efter specifikt reparerbart SHA-formatfelkvitto | Nod 68 ändrades korrekt. Nod 69 förblev `OUTPUT HEIGHT`. Inga reads. En completed write, en denied write och en statisk validator. | `STATUS=SUCCESS`; motsade faktisk FAIL | Task `fail`; self-report `inconsistent`; assessment `fail` |

## Exakt observerat tekniskt mönster

I båda försöken genomförde Qwen den första literal replacement korrekt och fick den verkliga `after_sha256`-hashen i tool-resultatet. Inför den andra ändringen använde modellen inte denna hash utan skapade en annan sträng med 63 hextecken.

- Försök 1 fick det äldre generiska svaret `invalid request` och rapporterade därefter korrekt att uppgiften misslyckats.
- Toolägaren korrigerades framåt så `invalid_expected_sha256` uttryckligen angav exakt 64 gemena hextecken och bad kandidaten använda senaste verkliga `after_sha256`.
- Försök 2 skapade ändå åter en 63-teckens hash, gjorde ingen korrigerande read/write och rapporterade därefter felaktig framgång.

Validatorns statiska schema-/graf-PASS var inte task-PASS och kontrollerade inte att båda efterfrågade titlarna fanns. Den oberoende titel-/preservation-gradern gav korrekt FAIL i båda försöken.

## Separata slutsatser per ägare

### Kandidatbeteende under verifierade villkor

- Qwen kunde göra en korrekt, hashvillkorad enskild titeländring.
- Qwen slutförde inte den tvåstegsberoende mutation som krävde att senaste tool-resultatets hash återanvändes.
- Qwen följde inte den explicit exponerade skillens initiala read- eller slutliga readback-steg i något av försöken.
- Den evidensbundna systemregeln gjorde inte självrapporteringen stabil: ett korrekt FAILED följdes av ett felaktigt SUCCESS under det länkade försöket.

Detta är evidens för begränsningen hos denna Qwen-agentinstallation i just det prövade multistegsgränssnittet. Det är inte bevis att Qwen saknar generell ComfyUI-, JSON- eller toolförmåga.

### Harness, tools och evaldesign

- Completion-grinden fungerade: kandidatens felaktiga SUCCESS kunde inte övertrumfa disk/grader-FAIL.
- `task_verification.status`, `self_report` och total `assessment` förblev separata.
- Den gamla `invalid`-klassningen för en naturligt avslutad ofullständig uppgift är rättad: dessa försök klassades som giltiga task-FAIL, inte harness-invalid.
- Bounded `tool_handler_returned` visade både korrekt första write-resultat och det modellneutrala felkvittot för andra writen.
- Det generiska felkvittot var en verklig interfacebrist och korrigerades. Att den specifika korrigeringen inte ändrade andra försökets beteende gör fortsatt identisk retry olönsam.

## Praktiskt beslut

Qwen är ännu inte kvalificerad för självständig daglig ComfyUI-multistegsmutation med nuvarande en-replacement-per-call-gränssnitt. Ingen tredje identisk titelrun ska köras.

Nästa möjliga hög-ROI-slice är inte mer promptputs utan ett separat designat, atomiskt och strukturerat multi-edit-kontrakt som kan applicera flera förhandsangivna ändringar under en enda hashvillkorad transaktion och returnera verifiering per operation. Det skulle pröva om begränsningen främst ligger i manuell tool-resultat/hash-kedjning. Ett sådant tool är inte implementerat eller beslutat av denna eval och måste få egen standardkontroll, säkerhetsgräns och offline-regression innan livebruk.

## Vad som uttryckligen inte bör göras nu

- Ingen tredje identisk retry med samma single-replacement-gränssnitt.
- Ingen retroaktiv omskrivning av EVAL 6 eller EVAL 7.
- Ingen slutsats att systemprompten ensam orsakade första försökets korrekta FAILED.
- Ingen generell Qwen-vs-Granite-rangordning från detta prov.
- Ingen modellfelsklassning av det första generiska tool-felkvittot.

## Report-summary: Frågor till Claude/Grok/ChatGPT att besvara

Fråga 1–4 är de obligatoriska `EXTERNAL-REVIEW-QUESTIONS-EVAL-RESULT` (`ERQER`); fråga 5–10 är de återkommande beslutsfrågorna.

1. Vad kunde Frontier-evaluatorn Codex gjort mycket bättre eller annorlunda i denna EVAL, grundat i de angivna run-id:na?
2. Hur kan framtida kandidater ge mer användbara och försvarsbara modell- respektive modellneutrala resultat utan att uppgiften görs kosmetiskt enklare?
3. Hur kan framtida EVALS förbättras icke-kosmetiskt och icke-trivialt?
4. Vilka mycket höga eller höga ROI-insikter utanför frågorna ovan bör evaluatorn adressera eller implementera?
5. Vilka slutsatser stöds direkt av disk-, tool- och run-evidens, och vilka formuleringar bör sänkas till hypotes eller `ej verifierat`?
6. Kunde en korrekt leverans ha underkänts av fixture, grader, conditioning eller harness; eller kunde en ofullständig leverans ha fått PASS?
7. Vilka negativa fynd kan nu tillskrivas Qwen-installationen under dessa villkor, och vilka orsaker måste fortfarande hållas öppna?
8. Finns något högt beslutsvärde kvar i samma single-replacement-uppgift, eller bör den grenen nu vara stängd?
9. Är ett atomiskt, hashvillkorat batch-/multi-edit-tool den minsta professionellt försvarsbara nästa ändringen? Ange i så fall minsta kontrakt, säkerhetsgränser och vilket utfall som skulle ändra nästa beslut.
10. Vilka föreslagna byggen, felsökningar, retries eller nya evals bör uttryckligen inte göras eftersom de saknar nytt beslutsvärde eller riskerar regression?

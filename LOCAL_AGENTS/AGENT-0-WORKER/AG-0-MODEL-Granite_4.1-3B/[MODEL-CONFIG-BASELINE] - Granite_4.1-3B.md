# Granite 4.1 3B Q4_K_M — första WORKER-baseline

Status: **tabellen nedan är en tidigare föreslagen målkonfiguration, inte de faktiskt använda villkoren**. Den första kontrollerade verktygsfria screeningen kördes 2026-09-13. Faktiska villkor framgår av SDK-readback i `model_evaluations/EVAL_1_2026-09-13-204437/b67327cef4a84c56ae5a9931f4d155ee/baseline_source_review.json` och varje uppgifts `evidence.json`. Inget tabellvärde ska i efterhand påstås ha gällt om det inte finns i readback. Ändra inte villkor mitt i ett försök; varje ändring får ett nytt versionerat kontrakt.

## Lokal instans och observerat utgångsläge

- Lokal modellfil: `.lmstudio/models/lmstudio-community/granite-4.1-3b-GGUF/granite-4.1-3b-Q4_K_M.gguf` (2 099 501 664 byte). Den 2026-09-13 verifierades SHA-256 `87320650cc9c4b082ba36cd0a15cecf73c75389f34aadd854913b1bb576454fd`; både hash och storlek matchade filens LFS-post i [utgivarens metadata](https://huggingface.co/api/models/lmstudio-community/granite-4.1-3b-GGUF/tree/main). Efter laddning matchade SDK:s modellpath/storlek/kvantisering den hashade lokala filen; faktiskt laddade bytes exponeras inte oberoende. Källcapture: `model_evaluations/EVAL_1_2026-09-13-204437/84f671fbc21a4731b54db9bd05702845/readiness.json` och baseline-review ovan.
- Bildinventeringens utgångsläge skiljer sig från målkolumnen nedan endast på följande punkter: hardware AUTO **på**, Context Length och GPU Offload **AUTO**, Max Concurrent Predictions **4**, Limit Response Length **av** och Context Overflow **Truncate Middle**. Övriga synliga värden och override-rutor följer målkolumnen. Spara faktisk appkonfiguration före ändring; bilder är inte runtime-readback.
- Modellfamiljens källfakta, inklusive språk, träning, templateformat och storleksjämförelse, finns enbart i [[MODEL-NOTES] - Granite_4.1-3B.md](<./[MODEL-NOTES] - Granite_4.1-3B.md>). [chat-template-snapshot.jinja](./chat-template-snapshot.jinja) är lokal granskningskopia, inte bevis på effektiv session-template.

## Faktisk första screening och tidigare föreslagna målvärden

Första screeningens faktiskt avlästa kärnvärden: LM Studio 0.4.24.0, SDK 1.5.0, Granite Q4_K_M, kontext 8192, auto-fit `false`, GPU-offloadkvot 1, en parallell session, Flash Attention `true`, CPU-pool 6, temperatur 0, outputgräns 1024 och tools `none`. Effektiv template är Jinja med SHA-256 `fed2756d2d24e127b951dcf139d0b03ab7db8ef23a456128ebc9c2db4901d476`; den lokala snapshoten skiljer sig endast genom en avslutande radbrytning. Första renderade input hade endast user-instruktion, 67 inputtokens och ingen system-/tool-injektion. SDK-readback exponerar inte här alla UI-fält (t.ex. faktisk batchstorlek, seed och ärvda top-k/top-p-värden); de förblir okända och tabellen får inte fylla luckorna med antaganden. Tider och bedömningar finns i run-evidensen.

Modellens observerade beteende i första filförsöket `a2a1e80f70584ffc949b7e21b19afccb`: utan WORKER-rollkontext genererade Granite ett `<tool_call>`-omslaget, JSON-giltigt anrop till `read_workspace_text` med rätt relativ filväg, men inga filvärden i sitt dåvarande svar. I det separat villkorade försöket `9cad35130ffa4f1b8e4583473b8d0243` gav modellen rätt `queue_name` och `retry_limit` efter att filinnehållet faktiskt hade återförts. Detta beskriver modellens utdata under två redovisade villkor; **tool-dispatchens plattformsutfall** ägs av [`LM-Studio_for_codex/README.md`](../../../../LM-Studio_connections/LM-Studio_for_codex/README.md) och **uppgiftsbedömningen** av [`agent-0-eval/README.md`](../agent-0-eval/README.md). Ingen generell modellbrist eller bred tooltillförlitlighet härleds från detta.

`Ingen override` betyder att rutan lämnas avmarkerad, **inte** att ett visst effektivt backendvärde är bevisat. `På`/`Av` avser LM Studios per-model load-default där inställningen finns. Alla ändringar jämfört med bildinventeringen är avsiktliga mål, inte redan utförda åtgärder.

| Nr | LM Studio-inställning | Första baseline | Praktisk avgränsning |
| --- | --- | --- | --- |
| 1 | System Prompt | Tomt modell-defaultfält | Verifiera separat faktisk request-/profilkontext; tomt fält betyder inte tom systeminput. |
| 2 | Automatic Optimize Based on Hardware | **Av** | Låser upp explicit kontext och GPU-offload; AUTO och fast `8192` får inte samexistera som påstådd baseline. |
| 3 | Context Length | **8192 token** | Liten faktisk laddningsbudget för Round 1; modellens 131k max är inte laddat värde. |
| 4 | GPU Offload | **40 lager** | Avser samtliga lager enligt IBM-kortet; verifiera att LM Studio verkligen laddar dem utan minnesfel. |
| 5 | CPU Thread Pool Size | 6 | Behåll synligt värde; ändra först vid konkret CPU-/prefillproblem. |
| 6 | Evaluation Batch Size | 2048 | Prefill-batch, inte antal EVAL-uppgifter; sänk bara efter verifierat load-/minnesfel. |
| 7 | Physical Batch Size | 512 | Behåll synligt värde; kontrollera eventuell minnestopp vid load. |
| 8 | Max Concurrent Predictions | **1** | En kandidatprobe åt gången; detta begränsar inte tools/subprocesser. |
| 9 | Flash Attention | På | Behåll om aktuell backend visar stöd utan fallback/fel. |
| 10 | Temperature | 0 | Behåll synligt lågvariansvärde; exakt samplingsemantik måste verifieras för LM Studio-builden. |
| 11 | Limit Response Length | **På, 1024 output-token** | R1 har korta svar; märk tokenlimit/trunkering som runtimevillkor, inte modellfel. |
| 12 | Context Overflow | **Stop at Limit** | Undvik tyst `Truncate Middle`; verifiera exakt tillgängligt UI-val och faktisk effekt. |
| 13 | Stop Strings | Tomt | Inga egna stopsträngar utöver modellens/templateens stoppkontrakt. |
| 14 | Reasoning Budget | Av, Unrestricted | Inget separat Thinking-läge är verifierat för denna modell/template. |
| 15 | Reasoning Budget Message | Oförändrad standardtext | Inaktiv när budget-override är av; ingen baseline-tuning. |
| 16 | Offload KV Cache to GPU Memory | På | Behåll med 8192 kontext och en prediction, följ faktisk VRAM-användning. |
| 17 | Unified KV Cache | På | Behåll observerat experimentellt värde bara om load lyckas; dokumentera backend/fallback. |
| 18 | Context Checkpoints | 32 | Behåll observerat värde; inga påståenden om agentminne. |
| 19 | K Cache Quantization Type | Ingen override | Inför inte extra KV-kvantisering för kort första runda; effektiv typ okänd tills readback. |
| 20 | V Cache Quantization Type | Ingen override | Samma princip som K, men verifiera effektiv typ separat. |
| 21 | Keep Model in Memory | På | Undvik onödig reload mellan prober; färsk konversation krävs ändå. |
| 22 | Try mmap() | På | Behåll; eventuell mapping-fallback är ett load-/miljöfynd. |
| 23 | Speculative Decoding | Off | Ingen draft-modell eller extra avkodningsväg i baseline. |
| 24 | Top K Sampling | 40 | Behåll observerat värde inför första jämförelsen. |
| 25 | Top P Sampling | Override på, 0.95 | Behåll observerat värde inför första jämförelsen. |
| 26 | Min P Sampling | Ingen override | Effektivt ärvt/defaultvärde okänt, inte automatiskt noll. |
| 27 | Repeat Penalty | Ingen override | Effektivt värde okänt; verifiera före slutsats om kod-/JSON-upprepning. |
| 28 | Presence Penalty | Ingen override | Effektivt värde okänt; undvik obestyrkt nyhetsbias. |
| 29 | Chat Template | Ingen ändring/override | Jämför effektiv template med GGUF/upstream och lokal snapshot; verifiera texttur före R1, tool-rundtur först när tools ska mätas. |
| 30 | RoPE Frequency Base | Auto, ingen override | Följ modellmetadata; ingen kontextförlängning. |
| 31 | RoPE Frequency Scale | Auto, ingen override | Samma som ovan. |
| 32 | Seed | Override på, 42 | Registrerad diagnostisk sampling-seed; senare tillförlitlighet kräver oberoende indata och flera verifierade seeds. |
| 33 | llama.cpp Arguments Override | Av | Inga dolda specialargument som kringgår synliga inställningar. |

## Genomförd förkontroll och senare justeringar

1. Codex laddade själv vald Granite-instans med `--gpu max --context-length 8192 --parallel 1` efter en 2,62 GiB resursuppskattning. SDK-readback, inte denna tabell, visar faktisk `contextLength=8192`, offloadkvot 1 och en parallell session. Den avsedda siffran 40 GPU-lager verifierades inte som ett separat lagertal. Inga tabellvärden ändrades mitt i försöken.
2. Lokal GGUF-hash matchade utgivaren; SDK path/storlek/kvantisering matchade den valda filen. Public SDK exponerade effektiv template, renderad första prompt, kontext, Flash Attention, CPU-pool, temperatur, outputgräns och tools `none`. Batch, seed, ärvd top-k/top-p, overflow-policy och andra saknade backendvärden är evidensluckor, inte verifierade målträffar eller kandidatfel. Ingen projektägd WORKER-profil eller System Prompt injicerades; en färsk SDK Chat med en user-instruktion per försök användes.
3. Två korta livekontroller gav naturligt `OK`/`eosFound` respektive separat verifierad `userStopped` och ägt processgruppstopp. Därefter gav tre engelska IMSLE-uppgifter preliminärt 3/3 enligt den förhandsbestämda rubriken. Första ogiltiga harnessförsöket och korrigerad ny version bevaras. Tredje svaret var för långt för ordet ”briefly” och gav ett dåligt exempel (`credits/hour`), trots att de tre rubricvillkoren uppfylldes. Detta är metoddata inför senare prompt-/rubricjustering, inte en efterhandsändrad PASS-gräns.
4. Team Master har därefter godkänt fortsatt eval. EVAL 2 och EVAL 3 bevaras som separata versionerade körningar; en ändring av ett föreslaget tabellvärde måste appliceras av rätt ägare, laddas om om det är ett load-default enligt [LM Studios dokumentation](https://lmstudio.ai/docs/app/advanced/per-model), läsas tillbaka och jämföras utan att tidigare utfall skrivs om. Tid till resultat och uppgiftsspecifik kvalitet väger tyngre än enbart tokens/sekund.
5. I EVAL 3 producerade modellen rätt `read_workspace_text`-namn och rätt relativ filsökväg i native read-svaret, `STATUS=SUCCESS` utan utförd operation i creation-uppgiften och `STATUS=FAILED` utan utförd operation i replacement-uppgiften. Detta är endast direkt observerade modelloutputs. Uppgiftsutfall, tool-dispatch och orsaksskiljning finns i [EVAL 3:s rapport](../../../model_evaluations/EVAL_3_2026-09-14-140930/%5BEVAL%5D%20-%20%5BEVAL_3_2026-09-14-140930%5D%20-%20%5BREPORT%20SUMMARY%5D.md); ingen generell modellskuld eller bred toolförmåga härleds här.

De maskinläsbara baseline-filerna i evalens run-mappar är evidens för faktiskt avlästa villkor, inte en duplicerad handunderhållen konfigurationskopia av den här måltabellen.

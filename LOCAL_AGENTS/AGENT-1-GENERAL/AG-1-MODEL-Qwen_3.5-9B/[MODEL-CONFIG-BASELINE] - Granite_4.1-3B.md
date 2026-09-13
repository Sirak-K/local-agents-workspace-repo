# Granite 4.1 3B Q4_K_M — första WORKER-baseline

Status: **vald målkonfiguration, ännu inte applicerad eller runtime-verifierad**. Gäller den första kontrollerade, verktygsfria EVAL-rundan i LM Studio. Detta dokument beskriver vad som ska ställas in; det är inte en export av appens faktiska tillstånd. Ändra inte villkor mitt i en runda. Spara nuvarande appvärden före applicering och skapa en ny dokumenterad baseline-version om ett värde senare ändras.

## Lokal instans och observerat utgångsläge

- Lokal modellfil: `.lmstudio/models/lmstudio-community/granite-4.1-3b-GGUF/granite-4.1-3b-Q4_K_M.gguf` (2 099 501 664 byte observerade). [Utgivaren](https://huggingface.co/lmstudio-community/granite-4.1-3b-GGUF) är LM Studio-teamet; filhash och laddad identitet återstår att verifiera.
- Bildinventeringens utgångsläge skiljer sig från målkolumnen nedan endast på följande punkter: hardware AUTO **på**, Context Length och GPU Offload **AUTO**, Max Concurrent Predictions **4**, Limit Response Length **av** och Context Overflow **Truncate Middle**. Övriga synliga värden och override-rutor följer målkolumnen. Spara faktisk appkonfiguration före ändring; bilder är inte runtime-readback.
- Modellfamiljens källfakta, inklusive språk, träning, templateformat och storleksjämförelse, finns enbart i [[MODEL-NOTES] - [GRANITE].md](<./[MODEL-NOTES] - [GRANITE].md>). [chat-template-snapshot.jinja](./chat-template-snapshot.jinja) är lokal granskningskopia, inte bevis på effektiv session-template.

## Värden som ska användas

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

## Gate före första kontrollerade Round 1

1. Spara nuvarande inställningar före ändring. Applicera ovanstående modell-defaults när LM Studio inte genererar; [LM Studios dokumentation](https://lmstudio.ai/docs/app/advanced/per-model) säger att ändrade load-defaults gäller vid **nästa modelladdning** och kan överstyras vid load. Ladda därefter om modellen; anta inte att dokumentet eller ett UI-fält bevisar effektiv inference.
2. Verifiera installerad GGUF-identitet/hash, LM Studio-/backend-build, aktiv WORKER-profil och färsk stateful kedja eller uttryckligen stateless request. Läs tillbaka effektiv `n_ctx=8192`, GPU-offload, batch, samtidighet, Flash Attention, KV-cachetyp, sampling, outputgräns, overflow-policy, prompt och template där LM Studio faktiskt exponerar dem; följ load-log och VRAM/OOM/CPU-fallback. Jämför eventuell GGUF-metadata och LM Studios templatefält med snapshoten. Ett vanligt native chattsvar bevisar inte den byte-exakt renderade systemprompten; om den inte exponeras ska begränsningen redovisas. Okända värden ska märkas okända; körningen får då vara diagnostisk men inte en fullt kontrollerad baseline. Om 8192/40 inte laddar säkert, behandla exempelvis 4096 som en ny dokumenterad baseline-kandidat, inte som en tyst ändring under pågående runda.
3. Verifiera en komplett native texttur utan tools och att Round 1-bedömaren accepterar kända goda svar och avvisar kända fel. Kör därefter tre små engelska IMSLE-prober. Identisk output vid `temperature=0` får inte antas; ett reproducerbarhetspåstående kräver minst tre färska körningar med samma korta input, verifierad seed och oförändrade villkor. Svensk användbarhet och faktisk tool-rundtur prövas separat senare.
4. Logga effektiv konfiguration och evidensursprung separat från session/fixture. Notera total tid till **verifierat korrekt resultat**, eventuell tid till första token och LM Studio-/transportlatens när den kan skiljas från generering. Precision, korrekt scope och pålitlighet går före hastighet; en snabbare inställning får bara behållas efter envariabel-jämförelse utan regression.

Ingen `.json`-kopia skapas nu: ingen existerande runner läser ett sådant kontrakt, och två manuellt underhållna källor skulle riskera drift. Lägg till maskinläsbar konfiguration först när en faktisk konsument och deterministisk validering finns.

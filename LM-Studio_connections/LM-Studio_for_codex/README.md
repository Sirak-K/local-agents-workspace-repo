# Codex → LM Studio evaluator connection

Den här mappen äger Codex minimala, projektlokala anslutning till LM Studio för Frontier-styrd modellutvärdering. Den ändrar inte vilken modell som driver Codex; Codex anropar i stället en lokal kandidatmodell som system under utvärdering.

## Runtime-kontrakt

- Basadress: `http://127.0.0.1:1234`
- Autentisering i projektets aktiva LM Studio-konfiguration: `Authorization: Bearer $LM_API_TOKEN`
- Modellkatalog: `GET /api/v1/models`
- Chat: `POST /api/v1/chat`
- Modellidentifierare: exakt värde från `models[].key`
- Chatinput: `input`
- Textsvar: posten i `output` vars `type` är `message`
- Smoke-proben använder `temperature: 0` och `store: false`

## Säker standard

Smoke-testet kräver att den uttryckligen valda modellen redan är laddad. Det startar inte en oväntad JIT-laddning och skriver aldrig ut API-token.

## Körning

```powershell
.\LM-Studio_connections\LM-Studio_for_codex\codex_lm_studio_connection_smoke.ps1
```

Annan redan laddad modell kan väljas explicit:

```powershell
.\LM-Studio_connections\LM-Studio_for_codex\codex_lm_studio_connection_smoke.ps1 -Model "models-key"
```

Klarsignal är exitkod `0`, svaret `OK` och slutraden `CODEX LM STUDIO CONNECTION ESTABLISHED`.

## Avbrytbar SDK-transport

Team Master har godkänt officiell JavaScript-SDK för avbrytbar evalgenerering i samma LM Studio-harness. Native REST ovan behåller modellinventering och generell observability. `lm_studio_sdk_prediction.mjs` äger en enda pågående prediction; `interruptible_prediction.py` äger bounded JSON-line-IPC, separat cancel och cleanup av enbart den egna SDK-klienten. IPC är transport, inte JSON-line-loggfiler. Evalevidens ägs av WORKER-runnern.

- SDK är versionslåst till `@lmstudio/sdk` 1.5.0 i `package.json`/`package-lock.json`.
- Publicerad 1.5.0 saknar dagens dokumenterade `apiToken`-parameter. Explicit godkänt, tidsbegränsat undantag mappar token till SDK:ns offentliga klientcredentials enligt [officiell tokenkod](https://github.com/lmstudio-ai/lmstudio-js/blob/main/packages/lms-shared-types/src/lmstudioAPIToken.ts) och [aktuell officiell klientkod](https://github.com/lmstudio-ai/lmstudio-js/blob/main/packages/lms-client/src/LMStudioClient.ts). Ta bort anpassningen när en publicerad SDK med direkt `apiToken` införs. Giltig token och nekad ogiltig token är live-verifierade; ingen anonym fallback eller ändrad serverautentisering.
- `listLoaded()` väljer ett specifikt redan laddat handle med exakt instansidentifierare. `.model()`/`.load()` används aldrig eftersom de kan ladda modellen. API-token finns bara i processmiljön, aldrig argv, IPC eller evidens.
- `cancel()` skickas till egen prediction; strömmen konsumeras till slutligt svar och statistik. `userStopped` är serverkvittot, inte klientens timeout. Se [LM Studio cancellation](https://lmstudio.ai/docs/typescript/llm-prediction/cancelling-predictions).
- Chat byggs med offentliga `Chat.empty()`/`append()` enligt [LM Studio Working with Chats](https://lmstudio.ai/docs/typescript/llm-prediction/working-with-chats) och installerad 1.5.0. Felaktig äldre direktkonstruktor/metod är borttagen; ett verkligt SDK-kontraktsprov verifierar färsk user-only-input och separat explicit systeminput utan inferens. Kontrollerad screening väntar på evaluatorns `continue` efter modellbindning; cancel kan också stoppa väntan före prediction.
- Klientcleanup, parent-EOF eller en stoppdeadline garanterar inte revisionsbevis för serverstopp. Uteblivet kvitto blockerar eval. Inga externa MCP-tools styrs av denna transport.

## Observerad tool-dispatch i denna integration

I den avgränsade kombinationen LM Studio 0.4.24.0, JavaScript-SDK 1.5.0, laddad Granite 4.1 3B och ett registrerat read-only-verktyg visade SDK:s effektiva prediction-konfiguration verktygsschemat, men `.act()` gav `eosFound` och vanlig text utan strukturerad tool-begäran eller tool-callback. Inget verktyg exekverades i originalkörningen `model_evaluations/EVAL_1_2026-09-13-204437/a2a1e80f70584ffc949b7e21b19afccb/`. Detta är ett observerat dispatch-/tolkningsglapp i **den testade kombinationen**, inte bevis för att LM Studio generellt saknar tool-use eller för att modellen ensam orsakat felet. Rått modellformat och uppgiftsbedömning ägs separat av modell- respektive WORKER-evalytan.

Den senare opt-in-vägen i WORKER-runnern tolkar endast ett strikt giltigt Granite-envelope och kör samma begränsade verktyg i ett nytt försök. Den är inte native SDK-tool-dispatch; dess lyckade utfall får aldrig tillskrivas den ordinarie `.act()`-vägen. [LM Studios officiella tool-dokumentation](https://lmstudio.ai/docs/developer/openai-compat/tools) skiljer uttryckligen mellan modellens textbegäran och plattformens strukturerade tolkning/exekvering.

Beroenden är installerade lokalt. Reproducerbar installation vid ny miljö (inga modeller hämtas eller startas):

En oanvänd, agentgenererad experimentell `.venv/` med Python-SDK ligger kvar Git-ignorerad eftersom dess borttagning blockerades av körmiljöns policy. Den används inte och får inte bli alternativ transport eller dependency-owner. Minsta cleanup är manuell borttagning av just denna connection-mapps `.venv/`; SDK-lösningen behöver endast Node-beroendena nedan.

```powershell
npm ci --prefix LM-Studio_connections/LM-Studio_for_codex --ignore-scripts --no-audit --no-fund
```

Start-/insyns-/stoppkommandon och verifieringsgränser: [WORKER-evalens README](../../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/README.md).

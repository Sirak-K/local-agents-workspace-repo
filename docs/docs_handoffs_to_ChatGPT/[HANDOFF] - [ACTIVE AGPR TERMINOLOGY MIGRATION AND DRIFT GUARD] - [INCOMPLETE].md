# HANDOFF — ACTIVE AGPR TERMINOLOGY MIGRATION AND DRIFT GUARD

## Mål och nytta

Genomför en sammanhängande repo-only-slice som gör `AGPR` (`Agent Profile`) till konsekvent aktiv terminologi och förhindrar att de ersatta uppercase-termerna `TAR`, `TAR-*` och `AGENT-*` återkommer i aktuella projekt-/runtimeytor.

Arbetet är större än ren dokumentationsputs: skapa en körbar, plattformsoberoende Python-validator med deterministiska offline-unittester, rätta de nu verifierade aktiva avvikelserna och dokumentera den nya AGPR-2 Storyteller-launchern. ChatGPT kan äga hela slicen eftersom den endast kräver GitHub-repot, Python och statisk/offline-verifiering. Ingen lokal SillyTavern-, KoboldCpp-, modell-, GPU- eller Windows-processåtkomst krävs.

Utgå från aktuell GitHub `main` på minst commit `23d2da43aa60c12f949e05de404526d373719137` och kontrollera att följande launcherfiler syns innan arbete börjar:

- `SillyTavern_UI/harness/Start-KoboldCpp-StorytellerRuntime.ps1`
- `SillyTavern_UI/harness/Start-KoboldCpp-StorytellerChat.ps1`
- `scripts/Start-AGPR-2-Storyteller-Chat.cmd`

## Låsta semantiska beslut

- `AGPR` betyder `Agent Profile` och är den enda aktiva profilförkortningen framåt.
- `AGPR-0-WORKER`, `AGPR-1-GENERAL`, `AGPR-2-STORYTELLER`, `AGPR-3-IMAGE-MASTER` och `AGPR-4-VOICE-MASTER` är befintliga toppnivåprofiler under `LOCAL_AGENTS/`.
- `TAR`, `TAR-*` och uppercase `AGENT-*` är förbjudna i de aktiva ytor som validatorn äger.
- Lowercase ansvarsbundna interna namn som `agent-0-eval`, `agent-2_system_prompt.txt` och `agent-2-runtime_config` är befintliga komponent-/filnamn och ska inte ändras av denna handoff.
- Vanliga ord som engelska `agent` och svenska `tar` får inte flaggas.
- Historiska artefakter får innehålla äldre terminologi och ska varken skrivas om eller göra standardkörningen röd.

## Tillåten skrivyta

Skapa:

- `tools/validate_active_agent_profile_terms.py`
- `tests/test_validate_active_agent_profile_terms.py`

Ändra endast när det behövs för denna slice:

- `[ CURRENT ARCHITECTURAL PROJECT STATE ].md`
- `LM-Studio_connections/LM-Studio_for_codex/README.md`
- `docs/docs_plan/[PLAN] - [Realize The Storyteller-Chat-Agent] (RTSCA) - [Summary].md`
- `SillyTavern_UI/harness/README.md`
- `scripts/README.md`
- denna handoff-fil

Vid full PASS: byt denna fils suffix från `[INCOMPLETE]` till `[COMPLETED]` och behåll samma basnamn.

Alla andra filer är read-only. Skapa ingen `.github/`-workflow, generell profilmanager, ny katalogtaxonomi eller compatibility-alias.

## Operativ implementation

### 1. Aktiv terminologivalidator

Implementera `tools/validate_active_agent_profile_terms.py` med endast Python-standardbiblioteket.

Standardkörningen från reporoten ska:

- skanna relevanta textfiler under de aktuella ytorna `LOCAL_AGENTS/`, `SillyTavern_UI/`, `scripts/`, `LM-Studio_connections/` och aktiva `docs/docs_plan/` samt `[ CURRENT ARCHITECTURAL PROJECT STATE ].md`,
- vara case-sensitive och flagga exakta uppercase legacyformer `TAR`, `TAR-<nummer>` och `AGENT-<nummer>` inklusive längre uppercase profilnamn,
- inte flagga lowercase interna komponentnamn eller vanliga språkord,
- ignorera binära/irrelevanta filformat,
- explicit exkludera `docs/docs_plan/- old/**`, `docs/docs_handoffs_to_ChatGPT/**`, `SillyTavern_UI/_local_runtime/**`, `.git/**`, `.venv/**`, `node_modules/**`, read-only `docs/docs_personal/**`, read-only `docs/docs_frameworks/**` och den historiska filen `docs/docs_plan/[PLAN] - [Realize The Storyteller-Chat-Agent] (RTSCA) - [Claude's ideas].md`,
- behandla UTF-8-dekodningsfel i skannade textfiler som ett tydligt valideringsfel,
- skriva deterministiskt sorterade fynd i kompakt format med relativ sökväg, radnummer och matchad token,
- returnera exit code `1` vid fynd/dekodningsfel och `0` med en enda kompakt PASS-sammanfattning när allt är rent.

Ge validatorn en testbar funktionsgräns och en CLI-root-override, exempelvis `--root`, så tester kan använda temporära fixtures utan att mutera repot. Uppfinn inga beständiga nya profilnamn eller breda allowlist-mekanismer.

### 2. Deterministiska offline-unittester

Implementera `tests/test_validate_active_agent_profile_terms.py` med `unittest` och temporära kataloger. Testa minst:

1. `TAR`, `TAR-1`, `AGENT-2` och `AGENT-2-STORYTELLER` detekteras,
2. lowercase `agent-0-eval`, `agent-2_system_prompt.txt`, svenska `tar` och engelska `agent` passerar,
3. varje låst exkluderad yta ovan ignoreras,
4. flera fynd sorteras deterministiskt och rapporterar korrekta radnummer/tokens,
5. en ren aktiv fixture ger exit code `0` och kompakt PASS,
6. en skannad ogiltig UTF-8-fil ger ett begripligt deterministiskt fel och exit code `1`.

Tester får inte använda nätverk, subprocess-start av modeller/appar, externa paket eller skriva utanför temporär testyta.

### 3. Korrigera verifierade aktiva avvikelser

Rätta endast verkliga uppercase legacyreferenser i de fem tillåtna dokument-/operatorfilerna. Minst följande nu verifierade avvikelser ska bort:

- toppnivåsökvägar `LOCAL_AGENTS/AGENT-0-WORKER/...` ska peka på befintliga `LOCAL_AGENTS/AGPR-0-WORKER/...`,
- Storyteller-text som säger `AGENT-2`/`AGENT-2-STORYTELLER` ska säga `AGPR-2`/`AGPR-2-STORYTELLER` där den beskriver den aktuella profilen,
- `SillyTavern_UI/harness/README.md` ska beskriva AGPR-2-scope och den faktiska nya launcheruppdelningen: gemensam `Start-KoboldCpp-StorytellerRuntime.ps1`, bevarad Text Completion-baseline och separat Chat Completion/non-thinking-wrapper,
- `scripts/README.md` ska lista `Start-AGPR-2-Storyteller-Chat.cmd` som kandidatentrypoint och tydligt säga att struktur/offlinegate är PASS men live modell-A/B fortfarande väntar på lokal körning/godkännande.

Gör ingen bred case-insensitive ersättning. Ändra inte historiska citat, Bionic-/LM Studio-arkitektur, modellval, samplerinställningar, context/KV-flaggor eller runtimebeteende.

## Förbjudet arbete

- Ändra inte någon `.ps1`, `.psm1`, `.cmd` eller runtimeimplementation som inte uttryckligen listas ovan.
- Ändra inte `AGENTS.md`, plan 7/8, andra handoffs, caption-, Worker-, AutoPull-, ComfyUI-, Image Master- eller Voice Master-ytor.
- Radera/renama inte historiska filer eller gamla planmappar.
- Starta inte modeller, lokala servrar eller tunga processer.
- Använd inte externa Python-paket eller nätverksanrop.
- Markera inte handoffen `[COMPLETED]` om validatorn eller dess unittest inte kan köras och passera i ChatGPT-miljön.

## Obligatorisk verifiering

Kör minst:

```text
python -m unittest tests/test_validate_active_agent_profile_terms.py
python tools/validate_active_agent_profile_terms.py
python -m py_compile tools/validate_active_agent_profile_terms.py tests/test_validate_active_agent_profile_terms.py
git diff --check
```

Verifiera dessutom att:

- Git-diffen från startcommit endast innehåller de tillåtna filerna,
- alla ändrade/nya textfiler avkodas som UTF-8 utan BOM,
- testerna inte innehåller nätverks-, modell- eller processstart,
- standardvalidatorn ger PASS på det uppdaterade repot,
- lowercase interna `agent-*`-komponentnamn inte har massändrats.

## Klarsignal och rapport

`COMPLETED` kräver att validatorn, unittest, py_compile, diff-check, encodingkontroll och scopekontroll faktiskt har passerat.

Rapportera i handoff-filen:

- exakt skapade/ändrade/renamade filer,
- antal deterministiska unittest-fall,
- exakta körda kommandon och PASS/FAIL,
- vilka legacyfynd som korrigerades,
- bekräftelse på att historiska/read-only ytor och lowercase interna komponentnamn lämnades orörda,
- eventuella återstående risker,
- processläge enligt PIPSA; denna offline-slice ska normalt inte kräva omstart.

## ChatGPT implementation report — 2026-09-15

**Status remains `INCOMPLETE`.** Implementationen och de deterministiska unittesterna är färdiga, men ChatGPT-miljön kan inte materialisera hela GitHub-repot som ett lokalt filsystem. Därför har den obligatoriska standardkörningen av validatorn mot **hela uppdaterade repot** inte kunnat exekveras på ett sätt som uppfyller handoffens full-repo-gate. Suffixet lämnas därför avsiktligt `[INCOMPLETE]`.

Under arbetet avancerade `main` från startcommit `61701a323e43e4756745e7698cf1f610b44dd751` först till `7b0b9e8641bfecda0f28b6e603272f14a296a27c` och därefter till `8fb3dc4067bc7a1432b68f86333fbcf01cbc3759`. De samtidiga ändringarna låg utanför denna handoffs skrivyta. Den senare committen etablerade dessutom `AGPR-0-CODER`; därför pekar de två korrigerade aktiva operatörslänkarna på den aktuella `AGPR-0-CODER`-pathen i stället för att återinföra den äldre WORKER-pathen. Handoffens ursprungliga kontraktstext har inte skrivits om.

### Skapade / ändrade / renamade filer

Skapade:

- `tools/validate_active_agent_profile_terms.py`
- `tests/test_validate_active_agent_profile_terms.py`

Ändrade i implementationens staging-commit:

- `[ CURRENT ARCHITECTURAL PROJECT STATE ].md`
- `LM-Studio_connections/LM-Studio_for_codex/README.md`
- `docs/docs_plan/[PLAN] - [Realize The Storyteller-Chat-Agent] (RTSCA) - [Summary].md`
- `SillyTavern_UI/harness/README.md`
- `scripts/README.md`

Ändrad i denna rapportcommit:

- `docs/docs_handoffs_to_ChatGPT/[HANDOFF] - [ACTIVE AGPR TERMINOLOGY MIGRATION AND DRIFT GUARD] - [INCOMPLETE].md`

Renamade: inga. `[COMPLETED]` används inte innan återstående full-repo-gates faktiskt passerat.

### Levererat beteende

- Python-standardbiblioteksvalidator med testbar `scan_repository(...)`-gräns och CLI-override `--root`.
- Case-sensitive detektion av uppercase `TAR`, `TAR-<nummer>` och `AGENT-<nummer>` inklusive längre uppercase profilnamn.
- Deterministiskt sorterade fynd med relativ path, radnummer och matchad token.
- UTF-8-dekodningsfel blir deterministiska valideringsfel med exit code `1`.
- Ren körning ger exit code `0` och exakt en kompakt PASS-rad.
- Samtliga låsta exclusions är explicita; binära/irrelevanta format ignoreras.
- Lowercase interna namn som `agent-0-eval` och `agent-2_system_prompt.txt`, svenska `tar` och engelska `agent` lämnas tillåtna.
- Harness-README dokumenterar AGPR-2-scope samt gemensam Storyteller-runtime, bevarad Text Completion-baseline och separat Chat Completion/non-thinking-wrapper.
- `scripts/README.md` listar `Start-AGPR-2-Storyteller-Chat.cmd` som kandidatentrypoint och skiljer offline/struktur-PASS från den ännu lokala live modell-A/B-gaten.

### Korrigerade verifierade legacyfynd

- `[ CURRENT ARCHITECTURAL PROJECT STATE ].md`: de två uppercase `AGENT-0-WORKER`-pathreferenserna är borta; de aktiva paths som nu dokumenteras följer aktuell `AGPR-0-CODER`-struktur på `main`.
- `LM-Studio_connections/LM-Studio_for_codex/README.md`: den uppercase legacy-path som började med `LOCAL_AGENTS/AGENT-0-WORKER/...` är borta och länken följer aktuell `AGPR-0-CODER`-path.
- Storyteller-summaryn: de två aktiva `AGENT-2`-referenserna är ersatta med `AGPR-2`.
- `SillyTavern_UI/harness/README.md`: `AGENT-2`/`AGENT-2-STORYTELLER` i aktiv scope-/directorytext är ersatta med AGPR-2-termer.

Ingen bred case-insensitive ersättning har gjorts.

### Deterministiska unittest-fall

`tests/test_validate_active_agent_profile_terms.py` innehåller **8** deterministiska `unittest`-fall. De täcker alla obligatoriska fall samt separat kontroll av irrelevant/binärt format och att rotfilen `[ CURRENT ARCHITECTURAL PROJECT STATE ].md` faktiskt skannas.

### Körda kontroller och exakta resultat

- `python -m unittest tests/test_validate_active_agent_profile_terms.py`
  - **PASS** — `Ran 8 tests in 0.006s` / `OK`.
- `python -m py_compile tools/validate_active_agent_profile_terms.py tests/test_validate_active_agent_profile_terms.py`
  - **PASS**.
- UTF-8/BOM-kontroll på de lokalt verifierade nya Pythonfilerna samt de byte-exakt rekonstruerade och kirurgiskt ändrade arkitektur-/LM Studio-dokumenten
  - **PASS** — UTF-8 och ingen BOM.
- Statisk kontroll av validator/test för nätverks-, modell- och processstartmarkörer
  - **PASS** — inga förbjudna imports/anrop hittades.
- GitHub candidate-diff `8fb3dc4067bc7a1432b68f86333fbcf01cbc3759...eb4bcdc2d1d29ec38519ebd1bf634f61bd6a5902`
  - **PASS för scope** — exakt de sju implementationspaths som listas ovan; inga runtime-, Caption-, Worker-/Coder-, AutoPull-, ComfyUI-, Image Master- eller Voice Master-filer ändras av handoff-committen.
- Byte-identitetskontroll före kirurgisk dokumentändring
  - **PASS** — lokal rekonstruktion av `[ CURRENT ARCHITECTURAL PROJECT STATE ].md` gav exakt Git blob `77e54c3799657c685ec43645e2fdb27e96789dde`; lokal rekonstruktion av `LM-Studio_connections/LM-Studio_for_codex/README.md` gav exakt Git blob `e81d84a43e5d0db7ea2becea0425df20744774f8`.

### Oexekverade obligatoriska gates / exakt blockerare

Följande full-repo-gate är fortfarande **inte** verifierad enligt handoffens ordalydelse:

```text
python tools/validate_active_agent_profile_terms.py
```

ChatGPT-containern har Python men saknar en lokal checkout av användarens GitHub-repo. GitHub Connector ger fil-/Git-dataåtkomst men monterar inte repot i containerns filsystem, och containerns outbound DNS kan inte klona/hämta repot direkt. Validatorn och dess CLI har körts i isolerad testyta, men det är inte samma sak som standardkörning från den fullständiga uppdaterade reporoten och räknas därför inte som completion-bevis.

`git diff --check` behöver också köras en sista gång på den fullt materialiserade slutdiffen tillsammans med standardvalidatorn innan suffixet får ändras till `[COMPLETED]`.

### Historiska/read-only ytor och lowercase interna namn

Historiska exclusions, `docs/docs_personal/**`, `docs/docs_frameworks/**`, andra handoffs, plan 7/8, Caption-, AutoPull-, ComfyUI-, Image Master- och Voice Master-implementationer har inte ändrats av denna handoff. De samtidiga AGPR-3/AGPR-4-installations-/kvalificeringsändringarna på `main` har uttryckligen bevarats. Lowercase interna `agent-*`-namn har inte massändrats.

### Återstående risk / nästa gate

Återstående risk är endast att en legacytoken eller UTF-8-avvikelse kan finnas i en annan aktiv, oförändrad scan-owner-fil som ChatGPT-containern inte kunnat materialisera för full standardkörning. Kör standardvalidatorn och `git diff --check` i en full checkout. Om båda passerar tillsammans med de redan passerade unittest-/compile-/encoding-/scopegates ovan kan handoffen därefter byta suffix till `[COMPLETED]` utan implementationsändring.

### PIPSA

Ingen processomstart krävs för denna repo-only/offline-slice. Inga modeller, lokala servrar, SillyTavern/KoboldCpp-processer eller AGPR-3/AGPR-4-installationer har startats, stoppats eller ändrats av ChatGPT.

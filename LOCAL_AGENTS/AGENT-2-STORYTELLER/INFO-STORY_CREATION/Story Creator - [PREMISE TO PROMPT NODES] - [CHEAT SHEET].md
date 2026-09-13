# Story Creator — Färdig premiss till redigerade promptnoder

Exemplet använder `STORY-E2E-001`. Använd alltid samma Story ID i filnamnet, premissens första rad och terminalkommandot.

## Fas 1 — Bekräfta produktionspremissen

1. Öppna `PROJECT_BIONIC/STORY_CANVAS-PREMISES/Story - [STORY-E2E-001].md`.
2. Bekräfta att första raden är exakt `Story-ID: STORY-E2E-001`.
3. Bekräfta att en tom rad följer och att resterande text är den kompletta engelska premiss som ska produceras.

## Fas 2 — Starta hela Story Creation-körningen

1. Öppna Git Bash i projektets workspace-rot.
2. Kör:

`./scripts/story_creator/run_story_creation_to_prompt_nodes.sh STORY-E2E-001`

3. Följ de numrerade, timestampade posterna som visas i terminalen. Samma händelser skrivs fortlöpande till körningens `story_creation_pipeline_logs.txt`.
4. Låt skriptet automatiskt starta LM Studio-servern, ladda modellen från `agent_config_story_creator.json`, skapa Story-artefakterna, genomföra SAQC-iterationerna, avlasta modellen, köra dry-run och redigera promptnoderna.

## Fas 3 — Bekräfta produktionsresultatet

1. Fortsätt när terminalen visar:
   - `Overall: APPROVED`
   - `Applied segment: SEGMENT-001`
   - `STORY CREATION TO PROMPT NODES: SUCCESS`
2. Öppna körningens `story_creation_pipeline_logs.txt` och bekräfta att sista `[PIPELINE]`-händelsen har status `[SUCCESS]`.
3. Vid `NOT_APPROVED` eller `FAIL`, använd den första konkreta `Blocker:`-raden och motsvarande logghändelse som nästa åtgärd.

## Fas 4 — Granska Story-paketet

1. Öppna `Story - [STORY-E2E-001] - [QUALITY CONTROL].md`.
2. Bekräfta `Overall: APPROVED`, `SAQC: APPROVED`, `SAQC Final Outcome: NO_CORRECTIONS_NEEDED` och `Remaining blocker: None`.
3. Läs `[FULL].md` som Story-version och `[PROMPT-REALIZED].md` som den mänskligt läsbara workflowprompt-versionen.
4. Använd `[PROMPT-REALIZED].json` som maskinkälla och SAQC-rapporterna som iterationsbevis.

## Fas 5 — Använd de redigerade workflowfilerna

1. Ladda om WF-1-A, WF-2-A och WF-3 från disk i ComfyUI.
2. Öppna WF-1-A och bekräfta att dess Story-specifika positiva prompt motsvarar `SEGMENT-001` i `[PROMPT-REALIZED].md`.
3. Kör WF-1-A när referensbilden ska genereras.

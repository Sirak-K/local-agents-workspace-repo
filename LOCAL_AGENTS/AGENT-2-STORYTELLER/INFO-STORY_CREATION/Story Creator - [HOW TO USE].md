# Story Creator — How to Use

## Result

One English premise becomes one complete, quality-controlled Story package:

`Premise → SSC → Full → Prompt-Realized JSON/Markdown → SAQC iterations → Quality Control report → APPROVED → automatic SEGMENT-001 prompt-node application`

The configured Story model performs Creator and SAQC work through separate LM Studio REST requests. The shared Python pipeline owns the fixed order, validation, file writes, model release, dry-run and ComfyUI workflow updates.

## One-time prerequisites

1. Enable LM Studio Local Model API authentication and keep the existing API token stored as the Windows user variable `LM_API_TOKEN`.
2. Install the model identified by `model` in `PROJECT_BIONIC/BIONIC_AGENTS/bionic_agent-2-Lumimaid/agent-2-runtime_config/agent_config_story_creator.json`.
3. Keep the `story-creator` MCP connection configured with its isolated Python runtime and `tools/story_creator_mcp_server.py`.
4. Install `PROJECT_BIONIC/BIONIC_AGENTS/bionic_agent-2-Lumimaid/agent-2-ctx/SKILL.md` in Bionic.
5. Create the dedicated Bionic project `Story Creator` with `PROJECT_BIONIC/BIONIC_AGENTS/bionic_agent-2-Lumimaid/agent-2-ctx/` selected directly as Working directory. This gives every Story session direct access to the live `ctx_*.md` source files without a copied context package.
6. Close Bionic and run `python tools/bionic_model_profile_configurator.py --runtime-config PROJECT_BIONIC/BIONIC_AGENTS/bionic_agent-2-Lumimaid/agent-2-runtime_config/agent_config_bionic_runtime.json --apply` once after installing or changing the configured chatbot model. Start Bionic again afterward. For Lumimaid, the command atomically applies the project-owned system prompt, removes incompatible project-level template overrides and preserves the model metadata template plus LM Studio's default tool-use handling; it does not change context length, response length or sampling values.

The production pipeline starts the LM Studio localhost server, loads the configured Story model, resolves the persistent token, performs Story Creation and SAQC, releases the model and applies approved prompts automatically.

## Terminal production

### 1. Create the premise

Create `PROJECT_BIONIC/STORY_CANVAS-PREMISES/Story - [STORY-ID].md` with this exact structure:

`Story-ID: STORY-ID`

Leave one blank line, then write the English premise. Keep the same Story ID in the filename, first line and command.

### 2. Run production

Standard two-segment Story:

`./scripts/story_creator/run_story_creation_to_prompt_nodes.sh STORY-ID`

Explicit 2–10 segment Story:

`./scripts/story_creator/run_story_creation_to_prompt_nodes.sh STORY-ID --segments 4`

The terminal displays the numbered Story Creation log in real time. Successful completion ends with `Overall: APPROVED`, `Applied segment: SEGMENT-001` and `STORY CREATION TO PROMPT NODES: SUCCESS`.

## Bionic Story work

1. Discuss or develop the premise in English with the Story Creator Bionic agent.
2. Approve the proposed next `STORY-###` ID.
3. Ask the agent to save the premise.
4. Before production, verify the complete displayed premise and its Story ID.
5. Approve the explicit question: `Should I create the complete Story artifacts and apply the approved Prompt-Realized values to the ComfyUI prompt nodes now?`
6. The agent sends the displayed premise SHA-256 to `create_story_and_apply_prompt_nodes`. Any premise change requires a new preview and approval.

## Generated package and logs

One approved run writes five Story VSSA files under `PROJECT_BIONIC/GENERATED-STORY-ARTIFACTS/<STORY-ID>_ARTIFACTS/`:

1. `<STORY-ID>_VSSA_PREMISE.md`
2. `<STORY-ID>_VSSA_SSC.md`
3. `<STORY-ID>_VSSA_FULL.md`
4. `<STORY-ID>_VSSA_PRMPRZ.json`
5. `<STORY-ID>_VSSA_PRMPRZ.md`

Read `<STORY-ID>_SAQC.md` first. Each SAQC iteration also writes one SAQC JSON report and exactly five referenced VSSAQC JSON reports. `Overall: APPROVED` is valid only when the final complete SSC → Full → Prompt-Realized SAQC iteration required no corrections and every deterministic validation passed.

Every production run writes one live human-readable TXT log and one pretty machine-readable JSON log under `story_creation_pipeline_logs/<run-id>/`. Quality evidence lives under the Story's `saqc-reports/` directory in `PROJECT_BIONIC/GENERATED-STORY-ARTIFACTS/`.

After successful completion, reload the updated WF-1-A, WF-2-A and WF-3 files from disk in ComfyUI before generation.

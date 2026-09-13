# Story Creator — Design

## Purpose

Story Creator turns one supplied premise into one coherent English Story package through one operation:

`Editable premise → approved Premise VSSA → Story Segment Core VSSA → Full VSSA → Prompt-Realized JSON/Markdown VSSA → configured Story model SAQC → SAQC/VSSAQC reports → APPROVED or NOT_APPROVED → automatic SEGMENT-001 workflow application`

The user never requests Full, Prompt-Realized or their reviews separately. Deterministic local tooling owns orchestration, validation, file I/O, workflow inspection and hashes.

## Current responsibility allocation

- `tools/story_creation_to_prompt_nodes_pipeline.py` owns authentication, LM Studio runtime preparation, Story Creation, SAQC, model release, dry-run and prompt-node application.
- `tools/lm_studio_story_model_runtime.py` owns LM Studio server readiness and load/unload of the model ID read from `agent_config_story_creator.json`.
- `tools/story_creator_orchestrator.py` owns SSC, Full, Prompt-Realized, SAQC iterations, validation and artifact writes.
- `tools/story_creator_premise_and_preferences_store.py` owns premise metadata and hashes, Story reads, latest production status and the only agent-writable preference file.
- The terminal script and Bionic MCP production tool both call the same complete Python pipeline.

Model selection follows demonstrated Story responsibility, never the host application's harness. Operation selection is deterministic and requires no controller model. SAQC requires a separate review pass, not a separate model: the configured Story model receives Creator instructions first and Quality Control instructions afterward. A model may be added later only when measured evidence shows a concrete unmet responsibility and an alternative provides an A/B-proven net-positive contribution.

The SAQC/VSSAQC manifest is project-owned runtime data in `PROJECT_BIONIC/INFO_STORY_QUALITY_CONTROL/story_artifact_quality_control_INFO/story-artifact-quality-control.json`. It points to canonical VSSADB and VSSA-QC-I Markdown for SSC, Full and Prompt-Realized; `tools/story_artifact_quality_control.py` loads and validates the contract.

Bionic uses exactly one installed Skill whose project-owned source is `PROJECT_BIONIC/BIONIC_AGENTS/bionic_agent-2-Lumimaid/agent-2-ctx/SKILL.md`. The dedicated `Story Creator` Bionic project uses that source folder directly as its Working directory. Its live `ctx_*.md` files remain the chatbot's intended runtime project-knowledge source; no copied context package exists. The Skill owns role, context routing, MCP selection and conversation flow without duplicating their knowledge.

`PROJECT_BIONIC/BIONIC_AGENTS/bionic_agent-2-Lumimaid/agent-2-runtime_config/` owns the configured Story chatbot model's reproducible Bionic adapter profile and Story Creator runtime config, separate from model-neutral project knowledge. Lumimaid remains the configured standby Story model. Its Bionic profile preserves the model metadata template and LM Studio's documented default tool-use path; it removes only incompatible project-level template overrides. The installed Story and Chat Agent skill provides reusable workflow instructions, but does not replace the model's requirement to emit parseable tool calls. `tools/bionic_model_profile_configurator.py` synchronizes the project-owned system prompt, removes incompatible project-level template overrides and performs obsolete exact stop-string cleanup while preserving unrelated model settings.

## REST+MCP integration contract

The local `story-creator` stdio MCP server is configured in LM Studio's `mcp.json` and exposes exactly:

- `story_creator_capability()`
- `read_story(story_id?, artifact?)`
- `save_story_premise(story_id, premise_text, replace_existing, expected_sha256?)`
- `update_story_preferences(operation, section, old_text?, new_text?)`
- `create_story_and_apply_prompt_nodes(story_id, premise_sha256, segments?)`

The MCP server owns only schemas, annotations and delegation. The complete production tool verifies the approved premise hash and calls the same Python pipeline as the terminal entrypoint. `LM_API_TOKEN` is resolved from the current process or the persistent Windows user environment and injected into the REST client without being written to project files or logs. Read-only Story operations and local premise/preference persistence do not require inherited REST authentication.

## Story Creation pipeline logging

`tools/story_creation_pipeline_logging/` owns one ordered event source for every complete production run. The shell entrypoint creates its run ID before Python starts so the terminal follower can display every event live. A direct Bionic production call creates the same event store inside the shared Python pipeline.

Each material operation emits one event object with a monotonic sequence number, local timestamp, concrete category, event name, status and content-safe details. The event store atomically updates the parallel pretty `story_creation_pipeline_logs.json` and appends only previously unwritten events to `story_creation_pipeline_logs.txt`; it never replaces the TXT file during an active run. TXT is Team Master's continuously open live and retrospective reading surface; JSON is the canonical machine-readable source for the terminal follower and future minimal GUI. Component-specific SAQC iteration reports remain separate audit artifacts, while the replaced LM Studio and ComfyUI run-log implementations are not parallel Story Creation timeline owners.

Interactive Story work through Bionic is part of the Story Creator production contract. The configured chatbot model uses the installed Skill, reads Story preferences from the isolated context Working directory when they first become relevant in a session, reuses them until they change, selectively reads the smallest relevant `ctx_` files and maps concrete project-data or mutation requests to the five MCP tools. Greetings and role questions remain ordinary tool-free chat; brainstorming and creative discussion use the current preference context without speculative file searches. The Skill never hardcodes a tool-call serialization format; Bionic supplies the active tool schema, the runtime template serializes it through LM Studio's default protocol, and Bionic alone executes calls and returns tool results. Chat history is not a persistent Story source of truth; premises, artifacts, preferences and production logs are.

Before production, Bionic shows the Story ID and complete premise, asks for explicit creation approval and binds that approval to the premise SHA-256. An unambiguous affirmative reply in the immediately following user turn transitions directly to `create_story_and_apply_prompt_nodes` with the confirmed Story ID and hash; it must not repeat `read_story` or the approval question. A changed premise requires a new preview and approval. Conversational intent never bypasses the shared Python pipeline, SAQC or workflow-application validation.

## Public execution contracts

Normal Story production through approved first-segment prompt-node application:

`./scripts/story_creator/run_story_creation_to_prompt_nodes.sh STORY-ID [--segments N]`

The entrypoint creates the live terminal log view and calls `tools/story_creation_to_prompt_nodes_pipeline.py`. Bionic calls that same Python owner through `create_story_and_apply_prompt_nodes`.

The underlying orchestrator remains directly inspectable through:

`python tools\story_creator_orchestrator.py STORY-ID [--segments N]`

- `STORY-ID` identifies `PROJECT_BIONIC/STORY_CANVAS-PREMISES/Story - [STORY-ID].md`.
- Omitted `--segments` means exactly 2 segments.
- The permitted range is 2–10 segments.
- The user entrypoint starts LM Studio Local Model API and loads the configured Story model when required.
- Successful completion transactionally writes approved `SEGMENT-001` prompts to WF-1-A, WF-2-A and WF-3.

## Narrative authority and persistent artifacts

At production start the orchestrator writes the approved canvas premise byte-exactly as `<STORY-ID>_VSSA_PREMISE.md`. It then creates `<STORY-ID>_VSSA_SSC.md`, abbreviated `SSC`. SSC is the sole derived authority for Story facts, character identity, scene grouping, segment order, START/MID/END states, both inter-keyframe intervals and continuity requirements.

Full and Prompt-Realized are distinct artifacts derived in sequence from the same validated SSC. Full is created first; Prompt-Realized then receives the premise, accepted SSC and accepted Full as explicit source context:

1. `<STORY-ID>_VSSA_FULL.md`
2. `<STORY-ID>_VSSA_PRMPRZ.md`
3. `<STORY-ID>_VSSA_PRMPRZ.json`
4. `<STORY-ID>_SAQC.md` plus per-iteration SAQC/VSSAQC JSON evidence

Prompt-Realized JSON is the machine-readable source for workflow application. Its Markdown counterpart is rendered deterministically for human review. Neither artifact may invent or override SSC facts.

## Segment and scene contract

- One segment contains START, MID and END plus the START→MID and MID→END inter-keyframe intervals.
- All Full segment prose contains 500–1000 words in total. Its approximate target is `500 + 5 × premise word count`, capped at 1000 words when the premise contains 100 words or more.
- The premise is Full's non-exhaustive creative foundation: every explicit premise fact must remain true, while the configured Story model may freely add compatible characters, locations, events and other coherent Story elements, especially for a sparse premise. As premise detail increases, it should prefer direct development of supplied material. Full must remain recognizably grounded in the premise and coherent with accepted SSC.
- Each scene contains at least two semantically grouped segments.
- Inside one scene, the next segment's START semantically matches the preceding segment's END.
- A deliberate cut, location change or time jump is allowed between scenes.
- The system describes textual and narrative material only; the user loads the correct images in ComfyUI.

## Workflow responsibility

The initial Story Creator supports only the reference-guided production path:

- WF-1-A receives exactly one Story-specific reference-production prompt per Story.
- WF-1-B is excluded because its edit instruction is workflow-specific rather than Story-specific.
- Every segment receives complete runtime text for all five active WF-2-A prompt owners: SHARED, START, MID, END and END reference-role policy.
- Every segment receives complete runtime text for the two Story-owned WF-3 positive prompt owners: START→MID and MID→END. WF-3's negative conditioning remains workflow-owned and unchanged.
- WF-2-B is disabled until an active pure workflow is deliberately reintroduced.
- WF-4 and WF-5 are excluded because they have no Story-specific prompt responsibility.

Every runtime prompt must be English, model-family-correct, semantically derived from the accepted Story sources and free from placeholders, authoring notes, QC commentary, project meta-language and operator instructions. Prompt-Realized preserves Story meaning without preserving narrative sentences verbatim when direct visual or motion wording is stronger for the target node.

## Orchestration and quality gate

One execution performs these bounded stages:

1. Generate and deterministically validate SSC.
2. Preserve the validated SSC as the Creator phase's narrative authority.
3. Generate Full from the premise and accepted SSC as complete English narrative prose near its premise-scaled target, with creative autonomy proportional to premise sparsity, then deterministically validate structure, sentence completion and the 500–1000-word range.
4. Use one focused Story-model call for WF-1-A and one WF-2-A plus one WF-3 call per segment. Each call receives only semantically named output fields, workflow-specific owner instructions, its exact prompting guide and the relevant accepted Story sources. Map those fields deterministically to the live Story-owned prompt nodes; exclude every negative prompt node.
5. Deterministically validate schema, exact prompt-owner coverage, absence of placeholders and project meta-language, and the positive-only WF-1-A FLUX.2 contract; render Prompt-Realized Markdown deterministically from JSON.
6. Run the remaining deterministic and artifact-specific checks for language, fidelity, structure, prompt-owner coverage and continuity.
7. After all five Story VSSA files are assembled, run SAQC in the same Story-version order as the Creator phase: SSC first, Full second and Prompt-Realized last. Premise VSSAQC records the approved snapshot state without an extra model call. The configured Story model receives the premise and current accepted artifacts in every Quality Control request; it does not rely on hidden memory from an earlier REST request.
8. Let each review first return a compact `APPROVED`, `REVISED` or `NOT_APPROVED` assessment. Request a second structured correction payload only after `REVISED`; `APPROVED` never generates or applies correction content. SSC and Full use English narrative-review rules; Prompt-Realized uses separate JSON and Markdown rules for machine-readable syntax/content, English prompt text and semantic equivalence.
9. Apply each accepted correction to the current version, deterministically revalidate it, and only then continue the iteration. Prompt-Realized corrections are applied to JSON and its Markdown representation is rendered again from the accepted JSON.
10. Define one SAQC iteration as the complete ordered sequence SSC → Full → Prompt-Realized. If any review makes a correction, start a new complete iteration from the corrected SSC; only an iteration with no corrections produces `SAQC Final Outcome: NO_CORRECTIONS_NEEDED`.
11. Permit at most three complete SAQC iterations. Continued correction need or any unresolved defect after the third iteration produces `NOT_APPROVED`; otherwise write the consolidated Quality Control report with the iteration count and final outcome. Full tail repair never triggers a second Full-generation inference.

`Overall: APPROVED` is legal only after one complete SAQC iteration returns no corrections and every deterministic gate is approved. Otherwise the run ends as `Overall: NOT_APPROVED` with concrete remaining defects. SAQC is bounded to three complete iterations; a failing integration test may receive at most three evidence-driven attempts, and unchanged test retries are forbidden.

Every started iteration writes one permanent pretty UTF-8 SAQC JSON report under `PROJECT_BIONIC/GENERATED-STORY-ARTIFACTS/<STORY-ID>_ARTIFACTS/saqc-reports/` and exactly five referenced VSSAQC JSON reports under its `vssaqc-reports/` child. Report IDs increase monotonically per Story, and earlier reports are never deleted or overwritten. `tools/story_creator_orchestrator.py` persists model results, outcomes, corrections, before/after hashes, timestamps and configured model ID directly; no additional report-writing LLM request exists.

The mandatory execution order is complete Story artifact assembly → sequential model-based SAQC review/correction → deterministic revalidation → consolidated Quality Control report → Story-model release → automatic `SEGMENT-001` workflow dry-run → automatic transactional prompt-node application. SAQC ends before ComfyUI generation and evaluates only textual Story artifacts; its approval never judges the adherence or quality of subsequently generated media.

## Automatic first-segment workflow application

The user entrypoint invokes the reusable workflow applier after the consolidated SAQC result is `APPROVED`:

- Dry-run: `python tools\story_prompt_workflow_applier.py STORY-ID --segment SEGMENT-ID --dry-run`
- Apply: `python tools\story_prompt_workflow_applier.py STORY-ID --segment SEGMENT-ID --apply`

`SEGMENT-001` targets WF-1-A, WF-2-A and WF-3. Workflow application consumes Prompt-Realized schema 2.0 and a completed Story package whose consolidated report contains `SAQC Final Outcome: NO_CORRECTIONS_NEEDED`, `SAQC Iterations: 1..3` and `Overall: APPROVED`. It also requires current Premise-/SSC-source hashes, a complete canonical SAQC/VSSAQC chain, matching workflow hashes, exact node mapping and zero placeholders before a transactional all-or-nothing write. The component remains separately callable for diagnostics and future automatic per-segment ComfyUI execution.

## Deferred JoyCaption option

JoyCaption is not part of the current runtime. If future evidence shows insufficient inter-segment transition precision, it may describe the actual preceding END image to help correct the following START prompt. SSC remains narrative authority; JoyCaption would only observe generated media.

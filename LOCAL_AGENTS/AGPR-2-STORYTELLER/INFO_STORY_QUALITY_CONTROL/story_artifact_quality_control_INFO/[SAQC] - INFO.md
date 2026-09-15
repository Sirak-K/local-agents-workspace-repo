# Story Text Quality Control — Specification

## Responsibility

Quality control is an automatic closing stage of the same Story Creator execution. It reviews:

1. `<STORY-ID>_VSSA_PREMISE.md`
2. `<STORY-ID>_VSSA_SSC.md`
3. `<STORY-ID>_VSSA_FULL.md`
4. `<STORY-ID>_VSSA_PRMPRZ.json`
5. `<STORY-ID>_VSSA_PRMPRZ.md`

The user never invokes artifact-specific QC skills. SAQC is strictly a pre-generation textual process: it reviews Story artifacts and their cross-artifact consistency, never generated images or videos. QC never modifies workflow JSON, runs ComfyUI or generates media, and its approval is not a media-adherence verdict.

## Source authority

- The premise owns explicit user facts and constraints.
- Validated SSC owns the derived narrative truth, identities, scene/segment structure, chronology, keyframe states, transition intent and continuity.
- Top-level active workflow JSON owns executable conditioning structure.
- Current workflow prompting documentation owns workflow- and model-family-specific prompt guidance.
- Prompt-Realized JSON owns machine-readable workflow application data; its Markdown form is a deterministic projection.

## Required gates

SSC must satisfy the requested 2–10 segment count, complete START/MID/END and both intervals, valid scene grouping of at least two segments, premise fidelity, internal consistency and explicit continuity within each scene.

Full must:

- contain 500–1000 English narrative prose words in total, with an approximate target of `500 + 5 × premise word count` capped at 1000;
- use the same scene/segment IDs and order as SSC;
- preserve every explicit premise fact plus every SSC fact and dependency while remaining a recognizable development of the premise's core idea;
- permit new characters, locations, events and other coherent Story elements only when they contradict no premise fact, with broad autonomy for a sparse premise and stronger preference for supplied material as premise detail increases;
- use polished, grammatical and natural English with coherent causality, tense, viewpoint and continuity;
- avoid contradiction, accidental repetition, vague referents, premise-incompatible additions and filler.

Prompt-Realized must:

- contain exactly one WF-1-A Story prompt;
- contain all five active WF-2-A prompt-owner values for every segment;
- contain all three active WF-3 prompt-owner values for every segment;
- contain no WF-1-B, WF-2-B, WF-4 or WF-5 Story prompt entries;
- match the live workflow's connected node roles, model family, conditioning route and current hashes;
- preserve SSC identity, environment, chronology, endpoint states and inter-segment continuity;
- distinguish each keyframe as one visible moment and each interval as physical transition;
- contain no placeholders, author instructions, QC commentary, generic token accumulation or negative-prompt owners.

The Markdown and JSON Prompt-Realized artifacts must be semantically identical.

## SAQC model pass

Story Artifact Quality Control (`SAQC`) is the mandatory final Story-creation stage after all five VSSA files have been assembled and before workflow application can begin. It uses the same configured Story model as Story generation, but with Quality Control instructions. A separate SAQC model may be evaluated later only for a concrete unmet responsibility with measurable evidence.

SAQC must give Lumimaid the premise and the relevant current artifacts again; separate LM Studio REST requests do not share reliable hidden memory. One `SAQC Iteration` reviews and, when necessary, corrects the completed Story versions in Creator order: SSC first, Full second and Prompt-Realized JSON plus Markdown last. Each accepted correction is deterministically revalidated before the corrected version becomes input to the next review.

Each artifact review returns a compact structured assessment first. A separate structured correction payload is requested only after `REVISED`, so `APPROVED` cannot spend output tokens on inactive correction content.

The model reviews SSC, Full and Prompt-Realized because each Story contains different plots, language and narrative dependencies that deterministic scripts cannot evaluate completely. Premise VSSAQC is a short deterministic record of the approved byte-exact snapshot. `PROJECT_BIONIC/INFO_STORY_QUALITY_CONTROL/story_artifact_quality_control_INFO/story-artifact-quality-control.json` owns the iteration/report manifest and points to each canonical VSSADB and VSSA-QC-I file. `tools/story_artifact_quality_control.py` loads those files, constructs each structured Lumimaid request and applies only schema-bounded corrections.

The SAQC request must independently check:

- grammatical, natural and internally coherent narrative English;
- preservation of every explicit premise fact plus identity, environment, chronology, START/MID/END state and motion consistency across the accepted SSC, Full and Prompt-Realized package;
- contradictions, omissions, unsupported additions and ambiguous references across artifacts;
- valid and semantically appropriate machine-readable Prompt-Realized JSON content;
- semantic agreement between Prompt-Realized JSON and its Markdown projection.

For SSC, Lumimaid reviews the English title, invariants, scene summaries, segment states, motion and narrative continuity. For Full, it reviews grammatical English, spelling, punctuation, tense, viewpoint, causality, fidelity, proportional creative expansion and the 500–1000-word contract. For Prompt-Realized, it inspects JSON and Markdown with separate format requirements: JSON structure and string values, workflow/prompt-owner placement, English model-facing text, stray characters and punctuation, and exact semantic agreement with the Markdown representation.

Deterministic scripts still parse JSON, validate its schema, verify workflow identifiers and compare the JSON with its Markdown projection. These checks prove exact machine contracts only; they cannot replace Lumimaid's grammatical, narrative or semantic review. Prompt-Realized corrections are persisted in JSON and Markdown is rendered again from the accepted JSON so the two representations cannot drift. The Quality Control Markdown file is the report produced from these checks and is not recursively reviewed as an input artifact.

## Correction, iteration and verdict policy

- A correction changes only the smallest content necessary and may not invent missing creative decisions or runtime contracts.
- The verdict controls mutation: `APPROVED` authorizes no edit, so the Python script discards any accidentally populated correction fields; only `REVISED` corrections can change an artifact.
- Full corrections replace only the title or complete prose of defective segments and must preserve accepted premise and SSC content while bringing the complete prose within its required length contract.
- Deterministic validation runs after every accepted correction.
- If any Story version is corrected, SAQC starts a new complete iteration at SSC so downstream consistency is reviewed again against the corrected package.
- The maximum is three complete SAQC iterations. Continued correction need, missing evidence or any unresolved defect after iteration three produces `Overall: NOT_APPROVED` with the exact remaining defect.
- `SAQC Final Outcome: NO_CORRECTIONS_NEEDED` is legal only when an entire SSC → Full → Prompt-Realized iteration completes without any correction.
- `Overall: APPROVED` is legal only when that final no-correction iteration and every deterministic gate is approved.

The consolidated `<STORY-ID>_SAQC.md` records Overall status, `SAQC Final Outcome`, `SAQC Iterations`, artifact verdicts, concrete findings, checked active workflows/hashes, corrections attempted and any remaining blocker. It must not reproduce the Story or prompts in full.

## Iteration evidence reports

Every started SAQC iteration writes one permanent pretty UTF-8 JSON report to `PROJECT_BIONIC/GENERATED-STORY-ARTIFACTS/<STORY-ID>_ARTIFACTS/saqc-reports/<STORY-ID>_SAQC_REPORT_<REPORT-ID>.json` and exactly five referenced VSSAQC reports under `vssaqc-reports/`. The numeric report ID increases monotonically per Story; existing reports are never deleted or overwritten. The SAQC report records:

- the exact structured Lumimaid result for SSC, Full and Prompt-Realized;
- the iteration outcome and all focused corrections;
- before/after hashes for all five VSSA files;
- human-readable start/end timestamps, elapsed time and configured model ID.

Each VSSAQC report is bound to one VSSA, its owning SAQC report and the same Story/iteration/report IDs. The final correction-free iteration requires five `APPROVED` VSSAQC reports; Premise VSSAQC remains intentionally short.

`tools/story_artifact_quality_control.py` writes this evidence directly from the already returned structured model results. It must not make a separate LLM request merely to narrate or reformat the report.

## Execution gate

- All model instructions and generated artifacts use English.
- Model tasks receive only small prepared inputs and exact output schemas.
- Normal total Story execution targets 1–3 minutes.
- Any individual inference must time out before five minutes and produce `NOT_APPROVED`.
- Completion requires a written consolidated Quality Control report.

## Workflow-application sequence

`story_prompt_workflow_applier.py --apply` is downstream of the integrated SAQC stage. It accepts only Prompt-Realized schema 2.0 with current Premise-VSSA and SSC hashes, a consolidated report containing `SAQC Final Outcome: NO_CORRECTIONS_NEEDED`, valid `SAQC Iterations: 1..3`, `Overall: APPROVED`, the current Prompt-Realized JSON hash and a complete canonical SAQC/VSSAQC chain. No Story content is written into ComfyUI prompt nodes before the clean final SAQC iteration and its deterministic revalidation are complete.

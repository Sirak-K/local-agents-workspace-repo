# Prompt-Realized Guidelines

## Responsibility

Prompt-Realized is the same Story represented as complete English runtime text per active Story-relevant prompt owner. It is generated automatically after Full by focused Lumimaid calls from the premise, accepted Story Segment Core (`SSC`), accepted Full, live prompt-owner contract, workflow-specific owner instructions and exact prompting guides; it is never a separate user operation or a prose summary.

## Active reference-guided contract

- WF-1-A: exactly one Story-level reference-production prompt.
- WF-2-A: exactly five complete prompt values per segment — SHARED, START, MID, END and END reference-role policy.
- WF-3: exactly two complete Story-owned prompt values per segment — START→MID and MID→END.
- WF-1-B, WF-2-B, WF-4 and WF-5 are excluded from current Story generation.

The live conditioning extractor and workflow prompting documents determine exact filenames, node identities, composition order, encoder behavior and model-family requirements. The deterministic composer receives this prepared contract; the controller must not inspect workflow JSON, discover project context or guess node IDs.

## Conversion rules

- SSC is the sole derived narrative authority. Preserve its facts, causality, chronology, scene/segment IDs and continuity semantically; replace narrative wording with stronger target-model visual or motion wording when appropriate.
- Keep only content expressible through subject identity, appearance, pose, action, expression, gaze, interaction, objects, environment, lighting, camera or temporal motion.
- Convert internal emotion into observable behavior only when SSC supports it.
- WF-1-A establishes the Story-level visual reference and must not become a per-segment prompt.
- WF-2-A SHARED owns stable segment-level visual conditions; START, MID and END each describe exactly one visible present moment.
- WF-3 interval prompts describe only the physical transition between their fixed endpoint images, including body mechanics, contacts, momentum and arrival.
- Negative prompt nodes are workflow-owned static conditioning and are excluded from Story Creator, Prompt-Realized and SAQC.
- Within a scene, each following START must be semantically compatible with the preceding END; Story Creator never manages generated image files.
- Emit complete model-facing text with no placeholders, authoring notes, QC commentary, Story Creator/project terminology or operator instructions.
- Judge the complete intended visible scene first. When a human is present, prioritize exact source-supported identity, appearance, clothing, pose, action, expression, gaze, body mechanics, contacts and spatial relationship.
- WF-1-A uses a direct positive FLUX.2 image description with the subject and key action first; plot summaries, future actions, abstract continuity labels and negation lists are not runtime image content.

## Persistent outputs

`[PROMPT-REALIZED].json` is the machine-readable source and includes Story ID, scene/segment order, SSC hash, workflow hash, workflow filename, node ID, node title, field name and complete prompt text.

`[PROMPT-REALIZED].md` is rendered deterministically from that JSON for readable review. It must not diverge from the JSON or create a second prompt source of truth.

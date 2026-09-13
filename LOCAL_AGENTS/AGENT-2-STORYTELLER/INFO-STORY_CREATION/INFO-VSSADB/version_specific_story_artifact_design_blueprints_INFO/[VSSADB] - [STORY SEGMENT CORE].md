# Story Segment Core Blueprint

## Responsibility

- Create the sole narrative authority for every downstream Story version.
- Use polished, concise English and preserve every explicit premise fact without unsupported invention.
- Define the title, persistent Story invariants, semantic scene grouping and exact chronological segment order.

## Scene and segment structure

- Create exactly the requested 2–10 segments using sequential `SCENE-NNN` and `SEGMENT-NNN` identifiers.
- Every scene contains at least two consecutive segments and one concise summary.
- Every segment defines one narrative purpose, concrete START, MID and END states, START→MID motion and MID→END motion.
- Each state describes one visible present moment; motion fields describe only the feasible physical transition between their fixed endpoint states.
- Within a scene, copy the preceding segment's END state verbatim into the following segment's START state.
- Preserve identity, appearance, objects, environment, camera-relevant continuity and chronology unless the premise explicitly changes them.

## Output boundary

- Keep every field specific enough to support Full prose and workflow-specific Prompt-Realized text.
- Do not include prose expansion, workflow node instructions, QC commentary, placeholders or multiple alternative Story choices.

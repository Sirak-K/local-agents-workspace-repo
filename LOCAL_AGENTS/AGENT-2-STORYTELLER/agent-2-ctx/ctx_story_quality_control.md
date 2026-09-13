# Story Artifact Quality Control

- SAQC is mandatory after all Story content artifacts exist and before any workflow node may be edited.
- The configured Story model performs a separate textual review with explicit premise and current artifact inputs; it never relies on hidden memory from Creator requests.
- Every iteration reviews in Creator order: SSC, Full, then Prompt-Realized JSON and Markdown.
- A correction is applied, deterministically revalidated, and followed by a new complete iteration from SSC.
- An iteration with no corrections yields `NO_CORRECTIONS_NEEDED` and may produce `APPROVED` when all deterministic checks also pass.
- At most three complete iterations run. Remaining correction need or any unresolved defect yields `NOT_APPROVED`.
- SSC review covers English text, facts, structure, character identity, states, causality, and continuity.
- Full review covers English grammar, spelling, punctuation, sentence completion, premise fidelity, SSC coherence, and the 500-1000-word contract.
- Prompt-Realized review separately covers JSON structure, workflow-owner placement, English runtime text, stray characters, and semantic equivalence with its Markdown rendering.
- One immutable pretty JSON report is written for every started iteration. The consolidated Markdown report records the final gate.
- SAQC never evaluates generated images or videos and never changes workflow-owned negative prompts.

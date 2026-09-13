# Story Artifacts

One production operation creates exactly five sibling artifacts for one Story ID:

1. `[STORY SEGMENT CORE].md`: compact structured authority for title, characters, invariants, scenes, segments, START/MID/END states, motion, and continuity.
2. `[FULL].md`: complete English narrative prose derived from the premise and accepted SSC. Total segment prose is 500-1000 words, targeting `500 + 5 x premise word count`, capped at 1000.
3. `[PROMPT-REALIZED].json`: canonical machine-readable mapping from accepted Story meaning to exact Story-owned workflow prompt nodes.
4. `[PROMPT-REALIZED].md`: deterministic human-readable rendering of the canonical JSON.
5. `[QUALITY CONTROL].md`: consolidated deterministic and SAQC outcome required before workflow application.

- SSC is created first, Full second, and Prompt-Realized last.
- Full and Prompt-Realized are never independent user operations.
- Explicit premise facts must remain true; compatible additions are allowed, especially when the premise is sparse.
- Prompt-Realized may rephrase narrative prose into stronger visual or motion language but may not change accepted Story meaning.
- Generated artifacts are not directly edited by the chatbot in this version. Revise the premise and explicitly approve a complete new production run.

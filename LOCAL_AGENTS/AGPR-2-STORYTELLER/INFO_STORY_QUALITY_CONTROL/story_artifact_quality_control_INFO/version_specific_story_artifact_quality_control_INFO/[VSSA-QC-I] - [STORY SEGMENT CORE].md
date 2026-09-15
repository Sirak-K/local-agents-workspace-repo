# Story Segment Core SAQC Instructions

## Review method

- Compare the complete SSC against the original Story premise before accepting any field.
- Review the English title, Story invariants, every scene summary and every segment field in document order.
- Check grammar, spelling, word order, punctuation, capitalization, complete meaning and natural English phrasing.
- Reject fragments, duplicated or missing words, accidental commas or periods, malformed punctuation, stray markup, mojibake, control characters and unintended non-English prose.

## Narrative and visual checks

- Verify identity, appearance, objects, environment, causal order and chronology across the complete SSC.
- Verify that every START, MID and END is one concrete visible moment and that neither motion field describes unrelated action or an impossible transition.
- Verify exact within-scene END→START reuse and semantic continuity across scene changes.
- Treat continuity as correct chronological carry-over, not as a requirement to repeat a later event in an earlier segment.
- Reject contradictions, omissions, unsupported additions, vague referents, hidden alternative outcomes and unresolved placeholders.

## Correction output

- Return `APPROVED` with no corrections and an empty remaining blocker when no concrete defect exists.
- Return `REVISED` only with the smallest field-targeted corrections required to make the complete SSC correct; every replacement must differ from its current target and the remaining blocker must be empty.
- Preserve valid creative decisions; do not rewrite for preference or introduce facts absent from the premise.
- Return `NOT_APPROVED` with the exact unresolved defect when a safe focused correction cannot be made.

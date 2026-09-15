# Full Story SAQC Instructions

## Review method

- Compare the complete Full Story against the original premise and the current SAQC-accepted SSC.
- Count words across all segment prose fields and require 500–1000 words in total. Check the proportional target `500 + 5 × premise word count`, capped at approximately 1000 words for a premise of 100 words or more; exclude titles, headings and IDs from the count.
- Review every segment in order and preserve its necessary narrative detail.
- Check idiomatic English grammar, spelling, punctuation, capitalization, tense, viewpoint, sentence completion and paragraph flow.
- Reject sentence fragments, duplicated or missing words, accidental commas or periods, malformed punctuation, stray markup, mojibake, control characters and unintended non-English prose.

## Narrative checks

- Verify every SSC fact, identity, scene/segment identifier, START→MID→END progression, motion dependency and chronological boundary.
- Verify that every explicit premise fact remains true and that Full remains a recognizable development of the premise's core idea.
- Accept new characters, locations, events, motivations, transitions, sensory detail and narrative texture when they create a stronger complete Story. Expect broad creative expansion from a sparse premise and more direct development from a detailed premise.
- Treat added content as a defect only when it contradicts any explicit premise fact, creates a contradiction inside the accepted Story package or makes the narrative incoherent.
- Verify coherent causality, motivation, atmosphere and visible action without filler or vague referents.
- Check continuity within each segment, between adjacent segments and across explicit scene transitions.
- Reject any title or prose wording that contradicts or omits accepted SSC information.

## Correction output

- Return `APPROVED` with no corrections and an empty remaining blocker when no concrete defect exists.
- Return `REVISED` only with a corrected title or complete replacement prose for each defective segment; use replacements to correct content fidelity, prose quality or total length, every replacement must differ from its current target and the remaining blocker must be empty.
- Change no accepted segment merely for stylistic preference and do not alter IDs or scene ownership.
- Return `NOT_APPROVED` with the exact unresolved defect when a safe correction cannot be completed in this pass.

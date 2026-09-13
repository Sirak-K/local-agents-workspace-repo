# Prompt-Realized SAQC Instructions

## Shared review method

- Compare Prompt-Realized against the original premise, current SAQC-accepted SSC and current SAQC-accepted Full Story.
- Review only the supplied textual Story artifacts and their contracts. Do not evaluate, predict or require evidence from images or videos generated later by ComfyUI.
- Review the JSON and Markdown completely as two representations of the same Prompt-Realized Story version.
- Verify clear English grammar, spelling, punctuation, capitalization and unambiguous model-facing wording in every prompt value.
- Reject duplicated or missing words, accidental commas or periods, malformed punctuation, mojibake, control characters, stray markup, unintended non-English prose, placeholders, author instructions and QC commentary.

## Workflow- and model-adherence checks

- Treat every prompt value as direct runtime conditioning for its exact node. Reject Story Creator, SSC, Prompt-Realized, SAQC, workflow, artifact-production, plot-summary and operator language.
- Evaluate the complete intended visible scene first. When a human is present, verify exact source-supported identity, appearance, clothing, pose, action, expression, gaze, body mechanics, contacts and spatial relationship before secondary scene details.
- WF-1-A Node 74 must be a direct positive FLUX.2 image description in this order: framing; subject count and visual description; visible pose/action/expression/gaze; required visible details and contacts; clothing/objects; camera/composition; environment/background; lighting; materials/texture/finish. Put the subject and key action first, describe one present moment and replace exclusions with the intended positive visual state.
- WF-2-A Node 1 must contain only concrete stable visual facts and reference authority. Nodes 131, 169 and 5 must each contain one observable present-moment human/scene state. Node 158 must only distinguish the visual constants retained from references from the current END pose/action.
- WF-3 Nodes 105 and 122 must describe the physical path between their connected endpoint images through observable movement, body mechanics, contacts, momentum and arrival. Negative prompt nodes are outside the Story artifact and SAQC review contract.
- Convert intentions, decisions and emotions into source-supported visible behavior. Reject abstract preservation categories with no actual visual values and reject future actions inside a current image prompt.
- Compare every prompt against the premise, accepted SSC and accepted Full Story for semantic coverage; exact source wording is unnecessary and must not be preserved when it weakens model-facing visual or motion language.

## JSON-specific checks

- Require exactly one valid JSON root object with no Markdown fence, commentary or stray characters before or after it.
- Verify correct quotes, escaping, commas, colons, braces and brackets; distinguish required JSON syntax from accidental punctuation inside string values.
- Verify exact schema fields, Story/scene/segment identifiers, source hashes, workflow hashes, workflow filenames, roles, node IDs, node titles and target fields.
- Verify that every prompt string belongs to the correct prompt owner and contains semantically correct Story content for that owner.

## Markdown-specific checks

- Verify headings, scene and segment order, workflow roles, node identifiers, field labels and prompt text against the JSON representation.
- Verify that no JSON prompt value is missing, changed, duplicated or displayed under another prompt-owner heading.
- Check that rendered prompt paragraphs remain readable and contain no JSON syntax residue or unintended formatting text.

## Correction output

- Return `APPROVED` with no corrections and an empty remaining blocker only when both JSON and Markdown are approved by their respective checks.
- Return `REVISED` only with the smallest exact prompt-owner text corrections required; every replacement must differ from its current target, the remaining blocker must be empty, and IDs, hashes, filenames, roles, node mappings and schema structure remain unchanged.
- Corrections target the machine-readable prompt model; the Python renderer recreates Markdown from the corrected JSON-owned values.
- Return `NOT_APPROVED` with the exact unresolved defect when structural metadata is stale or a safe focused text correction cannot be made.

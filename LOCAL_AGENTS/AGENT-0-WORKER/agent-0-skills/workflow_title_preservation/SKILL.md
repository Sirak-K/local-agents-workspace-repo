---
name: workflow_title_preservation
description: Make an exact display-title change in a supplied ComfyUI UI-workflow while preserving all unrelated data.
---

1. Read the provided UI-workflow file and locate each target by its ID. Check its current title against the requested starting value.
2. Change only the requested title values. A display title is not the node class/type or its `Node name for S&R` property. Keep IDs, widget values, inputs, outputs, links and metadata unchanged.
3. Use the expected-before hash for a conditional write; use the actual write receipt's after-hash for any subsequent write. Do not invent hashes or claim a write without a receipt.
4. Read the final file back and verify the requested titles. Report actual tool/validation failures instead of hiding them. Static success does not establish frontend opening or generation.

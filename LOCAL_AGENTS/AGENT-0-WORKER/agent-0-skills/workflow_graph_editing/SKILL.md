---
name: workflow_graph_editing
description: Plan and verify a bounded ComfyUI node/link edit using supplied slot and node contracts.
---

1. Read the workflow and relevant supplied node contracts. Distinguish UI nodes/links from API-format class_type/inputs. If a necessary node, widget or slot contract is missing, ask for it or report a blocked edit; do not guess.
2. Identify the smallest graph change meeting the requested goal. Keep node and link IDs unique; synchronize link endpoints, slot indices and input/output backreferences. Preserve unrelated fields and unknown metadata.
3. Make conditional writes only within the named disposable files. Stop if the starting hash changed unexpectedly.
4. Read back and run the provided static validator. Check the intended graph effect and preservation separately. Report errors and evidence gaps honestly; passing schema alone does not establish node semantics or runtime behavior.

# ComfyUI workflow editing context

The supplied file is a ComfyUI UI-workflow JSON: `nodes` is a list of node objects and `links` records graph connections. A node's numeric `id` identifies it within the workflow; its `title` is a display label. Changing only a title does not require changing the node's type, inputs, outputs or graph links.

This is not an API-format prompt. API-format prompts use node IDs as object keys with `class_type` and `inputs`; do not convert the supplied UI workflow to that format for a title edit.

Work only on the provided disposable file. Preserve unrelated node fields, links and workflow metadata. Static JSON/diff checks can verify a precise edit, but do not prove the workflow opens in a particular frontend or runs successfully. Do not load checkpoints, start ComfyUI, queue a prompt or generate media.

# ComfyUI Workflow Responsibilities

- Only active JSON files directly under `workflows/` define production workflow roles.
- WF-1-A creates exactly one Story-specific reference image and receives one complete positive image description.
- WF-1-B performs its fixed reference edit independently of Story Creator and receives no Story-specific prompt changes.
- WF-2-A creates START, MID, and END keyframes from an external reference and receives shared plus phase-specific Story prompts.
- WF-3 creates one segment video from START/MID/END and receives two chronological motion prompts: START->MID and MID->END.
- WF-4 assembles approved segments and WF-5 restores or upscales video; neither receives Story-specific prompt text.
- Story Creator never edits negative prompt nodes.
- Runtime prompts contain only concrete model-understandable image or motion descriptions: no workflow IDs, node IDs, Story Creator terms, artifact names, placeholders, authoring notes, or quality-control commentary.
- Prompt-Realized JSON is applied only after final SAQC approval, matching Story source hashes, matching workflow hashes, and a successful dry-run.
- ComfyUI generation output is outside SAQC; SAQC evaluates text before any image or video is generated.

# ComfyUI source snapshots

Codex-owned local source evidence for future WORKER evaluator handoffs. ChatGPT may consume these files read-only to implement later fixture/context/validation slices; do not change the snapshots as shared test state.

- `workflow_reference.json`: normalized real copy of the supplied WF-1-A playground workflow, not a production workflow or an ERST result.
- `workflow_specification.md` and `workflow_prompting.md`: small local project source docs. Their production Run gates and legacy pipeline descriptions are not authority to launch those pipelines or to inject inactive-role behavior.
- `shown_node_palette.json`: input/output/type observations for the 14 types shown in the snapshot. This is not an installed-node inventory or an authoritative widget/runtime contract.
- `source_manifest.json`: source projects, relative paths, original and snapshot hashes, normalization, capture time and evidence limits.

Use an independent per-ERST copy with its own task contract and fixture manifest. Do not mutate this reference for every attempt. The first intended domain task is scoped node `title` renaming; do not confuse visible title with node `type`, id or `Node name for S&R`.

No model weights, media assets or executable host launcher are included. Model filenames and generation-node structures are inert exercise data. Never queue `/prompt`, load ComfyUI checkpoints or execute a launcher to use these sources. Static evidence must not be labeled Run-ready or frontend-opened.

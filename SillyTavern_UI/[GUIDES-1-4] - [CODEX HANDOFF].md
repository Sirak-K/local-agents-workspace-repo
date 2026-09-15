# GUIDES 1–4 — CODEX HANDOFF

**Handoff status:** current fast-track guide phase CLOSED on 2026-09-15.

## Gate status

| Guide | Status | Proven capability |
|---|---|---|
| 1 — Harness & Chat UI | PASS | SillyTavern -> KoboldCpp -> DefiantFable GGUF works locally; streaming, continuity and backend verifier pass. |
| 2 — Correct Agent Configuration | CLOSED on proven stable baseline | Pre-Advanced-Formatting Text Completion path works without visible `<think>` leakage; failed template/Jinja experiment isolated as configuration/harness work, not model defect. |
| 3 — Text File Reading | PASS | Direct `.md` + `.txt` attachment reading across two files; seven facts correct; deliberately absent fact not invented. |
| 4 — Image Multimodality | PASS | Verified Qwen3.5 mmproj loads; `MultimodalVision` active; local image -> KoboldCpp -> grounded caption works end-to-end. |

## Stable runtime baseline — preserve first

### Storyteller TEXT

```text
Model:       Qwen3.5-9B-The-Defiant-Fable-Uncnr-Heretic-NEO-MAX-Q4_K_S.gguf
KoboldCpp:   1.120
API:         Text Completion -> KoboldCpp
Endpoint:    http://127.0.0.1:5001
Context:     8192 requested
ST port:     8001
Streaming:   ON
```

Advanced Formatting rollback baseline:

```text
Context Template:  Default
Instruct Mode:     OFF
Instruct Template: Alpaca (inactive)
System Prompt:     Neutral - Chat
Reasoning:         OFF
Custom Stops:      empty
Start Reply With:  empty
```

Recurring entrypoint:

```powershell
.\scripts\Start-KoboldCpp-Text.cmd
```

Do not reintroduce the removed experimental non-thinking/Jinja launch/test path as a normal baseline without a fresh controlled test.

### VISION fast-track profile

```text
Model:      same DefiantFable GGUF
Projector:  mmproj-F16.gguf
SHA256:     f70dc3509053962b0d0d3ee8a7eacebf5d60aa560cad78254ae8698516ae029f
Context:    4096 requested; 4352 effective in observed run
Offload:    23/33 layers in observed run
Module:     TextGeneration MultimodalVision
```

Entry points:

```powershell
.\scripts\Download-DefiantFable-mmproj-F16.cmd
.\scripts\Start-DefiantFable-Vision.cmd
```

## Highest-ROI Codex backlog

### P0 — custom production caption delivery

Desired repo surface:

```text
SillyTavern_UI/my_custom_chat_extensions/custom_image_captioning/
```

Observed current behavior:

- backend captioning is functional,
- one timed test returned 195 completion tokens and completed in roughly tens of seconds,
- SillyTavern UI delivery/rendering appeared much later than backend completion,
- caption text is rendered before/above the associated image,
- weak progress visibility caused repeated clicks and multiple duplicate caption requests in one run.

Build/profile a caption path that:

1. shows an unmistakable in-flight state immediately,
2. prevents accidental duplicate requests for the same image,
3. exposes the caption as soon as backend response completes,
4. uses image-first / caption-below presentation or another explicit Team-Master-approved layout,
5. optionally writes/exports the completed caption to a local file for downstream agent consumption,
6. supports a dedicated secondary endpoint/model without disturbing the Storyteller runtime.

SillyTavern Image Captioning already exposes `Use secondary URL`; evaluate this rather than coupling captioning permanently to the Storyteller endpoint.

### P1 — dedicated low-latency vision/caption model

DefiantFable 9B is accepted functionally but is not selected as the final production caption model. Benchmark a smaller local vision model against the actual Team Master workload with emphasis on:

- latency,
- grounded scene description,
- OCR honesty,
- VRAM residency on RTX 3070 Ti 8 GB,
- ability to coexist operationally with Storyteller and later ComfyUI workflows.

Keep model, projector/runtime and UI/integration failures separate.

### P1 — Storyteller hardening

Resolve without breaking the stable Text Completion baseline:

- exact Qwen3.5 thinking/non-thinking template behavior,
- visible `<think>` prevention at the correct layer,
- final system-prompt placement,
- final sampler profiles,
- stable 1000–2000 word responses,
- context/runtime optimization beyond the current 8192 baseline.

Prior experiment facts:

- derived ChatML/Instruct formatting introduced visible empty `<think>...</think>` blocks,
- a later Jinja/non-thinking experiment was invalid because KoboldCpp reported it could not parse the supplied `jinja_kwargs`,
- its verifier produced a false-positive marker PASS while visible `Thinking Process:` text still appeared.

Do not call these model defects without independent isolation.

### P2 — document hardening

Guide 3 direct attachments are already PASS. Later work:

- text-layer PDFs,
- Data Bank/RAG,
- local embeddings,
- chunk/retrieval tuning,
- larger real project documents.

### P2 — broader multimodality

Later integration:

- SillyTavern Image Generation -> ComfyUI,
- image-generation workflow mapping,
- longer multimodal sessions,
- video/multiframe if useful.

Do not run heavy ComfyUI inference during controlled KoboldCpp GPU profiling unless concurrency is the explicit test subject; prior evidence shows GPU competition materially changes AutoFit/offload.

## Repo / local-worktree caution

Team Master currently has intentional local modifications to:

```text
.gitignore
MY ACC$.MD
```

They were preserved across a manual recovery sync and must not be overwritten casually. A temporary stash backup was also intentionally retained after `stash apply`.

Normal repo sync remains AutoPull/AutoSync; manual Git intervention should only be used when there is concrete evidence sync is blocked.

## Evaluation principle

Prioritize traceable evidence, correctness, safety, maintainability and practical usefulness. Keep failure causes separated across model, runtime, template, UI, retrieval, projector, VRAM and integration layers; never assign an unproven defect to the model.

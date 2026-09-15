# GUIDE 4 — IMAGE MULTIMODALITY

**Current-sprint objective:** prepare and minimally verify DefiantFable image understanding without changing the stable text profile. Deep VRAM/context optimization is deferred to later Codex hardening.

**Active model only:** `Qwen3.5-9B-The-Defiant-Fable-Uncnr-Heretic-NEO-MAX-Q4_K_S.gguf`

## Verified projector source

The exact published DefiantFable GGUF repository states that vision is enabled and requires one separate `mmproj`. The same repository publishes `mmproj-BF16.gguf`, `mmproj-F16.gguf`, and `mmproj-F32.gguf`.

For the RTX 3070 Ti 8 GB fast-track profile, use **`mmproj-F16.gguf`**:

```text
Size:    ~918 MB
SHA256:  f70dc3509053962b0d0d3ee8a7eacebf5d60aa560cad78254ae8698516ae029f
Source:  DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF
```

Do not use an unrelated LLaVA/Qwen projector.

## Preserve the proven text path

- `TEXT` = stable Guide-2 path, no mmproj.
- `VISION` = separate runtime using the same Defiant GGUF + verified `mmproj-F16.gguf`.

TEXT is not reinterpreted if VISION encounters a projector/VRAM problem.

## Automated local setup

With the TEXT KoboldCpp process stopped, run from repo root:

```powershell
.\scripts\Download-DefiantFable-mmproj-F16.cmd
```

Select the same active DefiantFable GGUF. The script downloads the projector beside the model and verifies the exact SHA256.

Then start the isolated vision profile:

```powershell
.\scripts\Start-DefiantFable-Vision.cmd
```

Select the same GGUF again. The fast-track VISION context starts at `4096` to leave more VRAM headroom; AutoFit remains active.

## SillyTavern

Keep SillyTavern on the normal local KoboldCpp connection. In Extensions -> Image Captioning:

```text
Source:    Multimodal
Provider:  KoboldCpp
```

Leave automatic captioning OFF for the first controlled test.

## Fast vision validation

Test three ordinary local images:

1. one clear colored object,
2. a scene with at least three objects and obvious relative positions,
3. an image containing a short clearly readable text string.

Ask:

```text
1. Describe the main subject and its dominant colour.
2. List the visible objects and describe their relative positions.
3. Transcribe only the clearly readable text; say what is unclear.
```

## PASS for current fast-track sprint

- KoboldCpp loads DefiantFable + `mmproj-F16.gguf` without architecture/projector error,
- SillyTavern can send an image through the local multimodal path,
- all three answers are visibly grounded in the supplied images,
- obvious unreadable text is not confidently fabricated,
- the separate TEXT profile remains available and unchanged.

## Resource rule

Vision adds roughly another 0.9 GB projector before working buffers. On the current 8 GB GPU, do not run ComfyUI inference concurrently during validation. If VISION OOMs, reduce vision context and/or GPU offload one variable at a time; do not call this a model failure.

## Deferred hardening

Later Codex work may handle optimal context/GPU-layer split, alternate projector precision comparison, complex OCR/scene benchmarks, image-generation/ComfyUI integration inside SillyTavern, longer multimodal conversations and video/multiframe capability.

Guide 4 concerns image **understanding**. SillyTavern image generation through ComfyUI remains a separate later multimodality integration task.

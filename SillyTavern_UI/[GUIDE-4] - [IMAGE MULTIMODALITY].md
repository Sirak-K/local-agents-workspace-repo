# GUIDE 4 — IMAGE MULTIMODALITY

**Current-sprint status: PASS / CLOSED (2026-09-15).**

**Objective:** minimally verify DefiantFable image understanding without changing the stable text profile. Production latency/UI hardening is deferred to Codex.

**Active model:** `Qwen3.5-9B-The-Defiant-Fable-Uncnr-Heretic-NEO-MAX-Q4_K_S.gguf`

## Verified projector

```text
File:    mmproj-F16.gguf
Size:    ~918 MB
SHA256:  f70dc3509053962b0d0d3ee8a7eacebf5d60aa560cad78254ae8698516ae029f
Source:  DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF
```

Downloader entrypoint:

```powershell
.\scripts\Download-DefiantFable-mmproj-F16.cmd
```

The download completed and exact SHA256 verification passed.

## Separate VISION runtime

```powershell
.\scripts\Start-DefiantFable-Vision.cmd
```

Verified runtime evidence:

- KoboldCpp `1.120`.
- context request `4096`; effective aligned context `4352`.
- `mmproj-F16.gguf` applied successfully.
- vision encoder identified as `Qwen3.5-9B`.
- projector `qwen3vl_merger`.
- projector model size ~`875.61 MiB`.
- projector uses CUDA0.
- AutoFit succeeded; model offload `23/33` layers in the observed VISION run.
- `Active Modules: TextGeneration MultimodalVision`.
- no OOM or projector/architecture mismatch.

TEXT and VISION remain separate runtime profiles; a VISION issue must not be reinterpreted as a TEXT-model failure.

## SillyTavern Image Captioning baseline

```text
Source: Multimodal
API:    KoboldCpp
Model:  [Currently loaded]
Use secondary URL: OFF during validation
Automatically caption images: OFF
```

Captioning is invoked with:

```text
Magic Wand -> Generate Caption
```

## Functional validation result

A real image was sent through the local SillyTavern -> KoboldCpp multimodal path. The backend returned a grounded caption identifying the visible lighthouse/woman/boats/harbor/sunset structure and correctly reported no clearly readable text where appropriate.

A later timed image test returned:

```text
prompt_tokens:     59
completion_tokens: 195
total_tokens:      254
```

The returned caption correctly identified a woman in a yellow top, a man in a light-blue shirt, their relative positions, visible windows/background and absence of readable text. `reasoning_content` for that test was effectively empty.

Therefore image understanding/caption generation is functionally proven for the current sprint.

## Important production observations — DEFERRED, not Guide-4 blockers

### 1. Caption delivery UX / latency

Backend caption generation can complete in roughly tens of seconds in observed testing, but SillyTavern UI delivery/rendering appeared substantially later than the backend response. This needs profiling before production use. Do not attribute the UI delay to the model without isolating the frontend/server event path.

### 2. Caption placement

SillyTavern's captioned user message renders caption text before/above its image media in the ordinary vertical chat flow. This is functional but judged counterintuitive for Team Master use.

### 3. Duplicate work risk

During an earlier slow run, several caption requests were triggered for the same image because progress visibility was weak. The UI's spinner/hourglass state is not sufficiently obvious for the desired workflow. A custom integration should prevent duplicate in-flight requests and expose clear progress/completion state.

### 4. Dedicated caption model is a high-ROI option

DefiantFable 9B is the Storyteller model, not necessarily the optimal production captioner. SillyTavern exposes `Use secondary URL`, so later Codex hardening should evaluate a smaller dedicated local vision/caption model on a separate endpoint instead of forcing Storyteller and captioning to share one runtime.

### 5. Desired custom extension surface

Preferred future repo area:

```text
SillyTavern_UI/my_custom_chat_extensions/custom_image_captioning/
```

High-ROI goals for that work:

- immediate, explicit `captioning...` progress state,
- one in-flight caption request per selected image unless intentionally retried,
- deliver caption immediately when backend response arrives,
- conventional image-first / caption-below presentation or another clearly controlled layout,
- optionally persist/export the completed caption to a file for direct downstream agent use,
- support a dedicated secondary caption endpoint/model,
- preserve the stable Storyteller TEXT runtime independently.

## Resource rule

Do not run ComfyUI inference concurrently during controlled VISION profiling on the current RTX 3070 Ti 8 GB unless concurrency itself is the test subject. The projector consumes ~0.9 GB before working buffers, and GPU competition changes AutoFit/offload behavior.

## Deferred broader multimodality

Codex/later work may handle:

- dedicated low-latency caption-model selection,
- secondary-endpoint architecture,
- caption UI/export extension above,
- optimal context/GPU-layer split,
- complex OCR/scene benchmarks,
- image-generation/ComfyUI integration inside SillyTavern,
- longer multimodal conversations,
- video/multiframe capability.

# GUIDE-4 PASS

Guide 4 is closed for the current sprint because local image understanding and caption generation are proven end-to-end. Production caption UX/latency is explicitly deferred rather than hidden inside the PASS decision.

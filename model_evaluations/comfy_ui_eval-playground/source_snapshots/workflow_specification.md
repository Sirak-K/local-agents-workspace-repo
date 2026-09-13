# WF-1-A — Specification

## Technical role

T2I reference production. One Run generates exactly one standalone reference image without image input.

## Canonical active workflows

- Primary: `workflows/WF-1-A ) T2I - REF. PROD. - FLUX.2 DEV - [PRIMARY].json`
- Secondary: `workflows/WF-1-A ) T2I - REF. PROD. - FLUX.2 Klein 9B Base - [SECONDARY].json`

## Runtime contract

| Surface | Primary FLUX.2 Dev | Secondary Klein 9B Base |
|---|---|---|
| Generator | `flux2_dev_fp8mixed.safetensors` | `flux-2-klein-base-9b.safetensors` |
| Textencoder | `mistral_3_small_flux2_fp8.safetensors`, type `flux2` | `qwen_3_8b_fp8mixed.safetensors`, type `flux2` |
| VAE | `flux2-vae.safetensors` | `flux2-vae.safetensors` |
| Sampling | Euler, `Flux2Scheduler`, 20 steps | Euler, `Flux2Scheduler`, 20 steps |
| Guidance | `FluxGuidance(4)` → `BasicGuider` | `CFGGuider`, CFG 5 |
| Canvas | Linked width/height controls: 768 × 1344, batch 1 | 768 × 1344, batch 1 |
| Topology | 15 active nodes, 16 links | 15 active nodes, 17 links |

Both graphs are fully connected and contain exactly one `SaveImage`. The locked output root for new WF-1-A results is `image/WF-1-A/...`.

## Run gate

- No external media input is required.
- Story Creator must apply a complete SAQC-approved Prompt-Realized value to Node 74 before Run.
- The completed prompt must directly describe one present-moment reference image with the intended human and complete visible scene.
- Accept only one complete, correctly framed output with the intended identity, anatomy, pose, lighting and background.
- Promote changes only after a controlled comparison against the nearest approved WF-1-A baseline.

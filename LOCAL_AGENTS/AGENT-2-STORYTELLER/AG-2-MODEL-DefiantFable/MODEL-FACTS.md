# DefiantFable — verified runtime facts

Active Guide-2 candidate only.

## Exact local GGUF observed

`Qwen3.5-9B-The-Defiant-Fable-Uncnr-Heretic-NEO-MAX-Q4_K_S.gguf`

## Verified from actual KoboldCpp 1.120 runtime

- Runtime architecture: `qwen35`
- Parameter count: approximately `8.95 B`
- Quant indicated by exact filename: `Q4_K_S`
- Training context reported by model metadata: `262144`
- Current controlled harness context: `8192`
- mRoPE present
- Hybrid/recurrent characteristics present
- KoboldCpp effective runtime: Context Shift automatically disabled for this model/runtime because mRoPE is used
- SWA is not used by this model in the observed runtime
- F16 KV baseline
- Flash Attention effective runtime reported enabled
- CUDA MMQ effective runtime reported false
- Successful AutoFit after competing GPU workload was removed
- Stable load and generation through KoboldCpp -> SillyTavern
- SillyTavern streaming verified

## Guide-1 verification snapshot

- KoboldCpp: `1.120`
- API: `http://127.0.0.1:5001`
- `/api/extra/true_max_context_length`: `8192`
- `/v1/models`: model status `loaded`
- RTX 3070 Ti 8 GB observed around 6.4 GB VRAM during final backend verification

## Not yet verified — do not infer from filename

- Exact upstream Hugging Face repository
- Exact merge/finetune lineage beyond the verified Qwen3.5 runtime architecture
- Exact embedded Jinja/chat template
- Thinking/non-thinking contract
- Model-card recommended samplers
- Model-card output/context recommendations
- mmproj relationship for later multimodal work

These remain open until source/model metadata evidence is captured. A filename containing terms such as `Uncnr`, `Heretic`, or `NEO-MAX` is not itself evidence of behavior, capability, quality, or lineage.

## Next gate

Use SillyTavern Text Completion -> KoboldCpp with Instruct Mode and metadata-derived Context/Instruct templates enabled. Reconnect, then record the template SillyTavern actually derives before changing system prompt or samplers.
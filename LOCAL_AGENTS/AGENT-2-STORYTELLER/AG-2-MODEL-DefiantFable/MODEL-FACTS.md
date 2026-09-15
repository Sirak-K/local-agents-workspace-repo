# DefiantFable — verified runtime facts

Active Guide-2 candidate only.

## Exact local GGUF observed

`Qwen3.5-9B-The-Defiant-Fable-Uncnr-Heretic-NEO-MAX-Q4_K_S.gguf`

## Verified source repository

Exact GGUF filename is published in:

`DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF`

The exact non-MTP `Q4_K_S` file is approximately 6.55 GB in that repository.

## Verified from actual KoboldCpp 1.120 runtime

- Runtime architecture: `qwen35`
- Parameter count: approximately `8.95 B`
- Quant: `Q4_K_S`
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

## Guide-2 template evidence

With SillyTavern `1.19.0` connected through `Text Completion -> KoboldCpp`, metadata-derived Context and Instruct templates enabled, and Instruct Mode enabled:

- SillyTavern notification: `Instruct Template: "ChatML" auto-selected`
- SillyTavern notification: `Context Template: "ChatML" auto-selected`
- Context Template shown: `ChatML`
- Instruct Template shown: `ChatML`
- Derived role sequences shown:
  - system prefix `<|im_start|>system`, suffix `<|im_end|>`
  - user prefix `<|im_start|>user`, suffix `<|im_end|>`
  - assistant prefix `<|im_start|>assistant`, suffix `<|im_end|>`
- Derived template Stop Sequence shown: `<|im_end|>`
- Custom Stopping Strings field observed empty
- Tokenizer observed: `Best match (recommended)`
- Token Padding observed: `64`
- Reasoning controls observed OFF
- `Bind Model to Templates` observed OFF during validation
- `Start Reply With` observed empty

This is accepted as the current text-only Guide-2 template baseline because it was derived from the connected model/backend metadata rather than manually guessed. Template correctness still remains subject to behavioral smoke-test evidence; do not silently replace it with another preset.

## Model-card/runtime notes to validate later

Public model/conversion material identifies the family as Qwen3.5-based and describes thinking/reasoning and creative-writing use. Related conversion notes recommend temperature `<= 1.0` and repetition penalty `1.0` (off), but sampler values must be tested against this exact local GGUF before becoming project defaults.

## Still open / deliberately deferred

- Full merge/finetune lineage proof beyond the verified Qwen3.5 runtime architecture and exact published GGUF source
- Exact thinking/non-thinking operating contract for this SillyTavern text-completion path
- Final Validation and Story sampler profiles
- Long-output requirement around 1000–2000 words per response
- Higher-context optimization beyond 8192
- mmproj/multimodal relationship; deferred to the later multimodality work

Filename terms such as `Uncnr`, `Heretic`, or `NEO-MAX` are not themselves evidence of behavior, capability, quality, or safety characteristics.

## Next gate

Keep derived `ChatML` Context + Instruct templates. Add the Guide-2 baseline system prompt, then run a fresh-chat template/system-prompt validation before sampler optimization.
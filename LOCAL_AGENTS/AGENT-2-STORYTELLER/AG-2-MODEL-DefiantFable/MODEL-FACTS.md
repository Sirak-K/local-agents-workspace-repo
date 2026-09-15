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
- Current controlled baseline context: `8192`
- mRoPE present
- Hybrid/recurrent characteristics present
- KoboldCpp effective runtime: Context Shift automatically disabled for this model/runtime because mRoPE is used
- FastForward remains the prefix-reuse mechanism
- The hybrid/recurrent path can use KoboldCpp SmartCache checkpoints; this is not equivalent to Context Shift and does not extend the context window
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

## Guide-2 template evidence: first attempt and failure attribution

With SillyTavern `1.19.0` connected through `Text Completion -> KoboldCpp`, metadata-derived Context and Instruct templates enabled, and Instruct Mode enabled:

- SillyTavern auto-selected `ChatML` for Context and Instruct.
- Role sequences shown were structurally ChatML:
  - system prefix `<|im_start|>system`, suffix `<|im_end|>`
  - user prefix `<|im_start|>user`, suffix `<|im_end|>`
  - assistant prefix `<|im_start|>assistant`, suffix `<|im_end|>`
- Stop Sequence shown: `<|im_end|>`
- Custom Stopping Strings empty
- Tokenizer: `Best match (recommended)`
- Token Padding: `64`
- Reasoning controls OFF
- `Bind Model to Templates` OFF
- `Start Reply With` empty

Behavioral smoke then showed a visible empty `<think>...</think>` block before every assistant answer. Memory/continuity and prose behavior otherwise worked.

**Attribution:** this is a template-path/configuration failure, not evidence of a model defect. Generic ChatML role framing is insufficient for Qwen3.5 non-thinking generation.

## Verified Qwen3.5 thinking/non-thinking contract

Official Qwen3.5 material states that thinking is enabled by default and that Qwen3.5 does **not** use Qwen3's `/think` / `/nothink` soft switch. Non-thinking is selected through chat-template parameters, specifically `chat_template_kwargs: {"enable_thinking": false}`.

The official Qwen3.5 Jinja generation prompt renders:

- `<|im_start|>assistant` followed by `<think>` when thinking is enabled/default;
- `<|im_start|>assistant` followed by an empty `<think>\n\n</think>\n\n` prefill when `enable_thinking=false`.

That empty block belongs in the **compiled prompt**, not as newly generated visible assistant output.

Sources:
- `https://huggingface.co/Qwen/Qwen3.5-9B`
- `https://huggingface.co/Qwen/Qwen3.5-9B/blob/main/chat_template.jinja`

## Corrected Storyteller runtime path

KoboldCpp supports Jinja Chat Completions and chat-template kwargs. The controlled Defiant path is therefore:

1. KoboldCpp `1.120` started with `--jinjathink false`; this version auto-enables Jinja and selects `enable_thinking=false` without shell-embedded JSON.
2. Do not use Qwen3 `/think` or `/nothink` switches; Qwen3.5 does not support them.
3. SillyTavern uses `Chat Completion -> Custom (OpenAI-compatible)`.
4. Endpoint base URL: `http://127.0.0.1:5001/v1`.
5. SillyTavern Text Completion Instruct Mode is not the active template layer on this path.
6. Chat Completion Prompt Manager is the system-prompt layer to validate; do not assume the Advanced Formatting Text Completion system prompt is sent unchanged.

KoboldCpp sources/reference:
- v1.120 release notes state that `--jinjathink` automatically enables Jinja.
- Per-request `chat_template_kwargs: {"enable_thinking":false}` remains supported, but the fixed server flag is the lower-risk Windows launcher contract until the active SillyTavern UI is proven to transmit that field.

## Validation sampler baseline after corrected template PASS

Official Qwen3.5 non-thinking API example uses:

- Temperature `0.7`
- Top-P `0.8`
- Top-K `20`
- Presence penalty `1.5`

Keep repetition penalty neutral (`1.0`) unless exact DefiantFable evidence justifies a change. Samplers are not considered locked until the corrected non-thinking template path passes behavioral validation.

## Still open / deliberately deferred

- Full merge/finetune lineage proof beyond the verified Qwen3.5 runtime architecture and exact published GGUF source
- Final Validation and Story sampler profiles
- Long-output requirement around 1000–2000 words per response
- Higher-context optimization beyond 8192
- mmproj/multimodal relationship; deferred to the later multimodality work

Filename terms such as `Uncnr`, `Heretic`, or `NEO-MAX` are not themselves evidence of behavior, capability, quality, or safety characteristics.

## Next gate

Preserve the proven Text Completion baseline. Build and statically verify a separate Chat Completion/non-thinking profile and acceptance probe, then run one bounded local A/B only after explicit approval for model load/generation. The probe must inspect both `message.content` and `message.reasoning_content`; marker-only checks are insufficient.

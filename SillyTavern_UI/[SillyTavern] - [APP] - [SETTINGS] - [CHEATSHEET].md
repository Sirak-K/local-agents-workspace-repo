# SILLYTAVERN — APP SETTINGS CHEATSHEET

**Purpose:** compact UI inventory for future agents. Use this to locate the right SillyTavern surface without needing screenshots.

**Verified UI baseline:** SillyTavern `1.19.0`, pinned commit `06bde939fb1e9c4c8d8641d810f0a916b5bce127`, observed 2026-09-15.

> Treat section purpose/names as the stable contract. Exact icon placement and low-ROI controls may move between SillyTavern versions.

---

## Top-bar settings map

| UI surface | Main purpose | High-ROI configuration / sections |
|---|---|---|
| **AI Response Configuration** | Generation behavior and provider-specific presets. | Text/Chat Completion preset identity; response length/output budget; context size; **Streaming**; temperature; Top-P/Top-K/Min-P and penalty/repetition controls; Chat Completion **Prompt Manager** when applicable. Change one variable at a time during debugging. |
| **API Connections** | Select provider/backend and connect the UI to inference. | Connection Profile; API (`Text Completion`, `Chat Completion`, etc.); source/API type; endpoint/base URL; API key when applicable; context derivation; Connect; Auto-connect. |
| **Advanced Formatting** | Text Completion prompt construction and instruct formatting; also shared formatting/stop/tokenizer controls. | **Context Template**, **Instruct Template**, **System Prompt**, template derivation/binding, Story String, Context Formatting, instruct sequences, Custom Stopping Strings, Tokenizer, Reasoning, Start Reply With. Do not assume its System Prompt/Instruct Template is the active layer for Chat Completion APIs. |
| **World Info** | Lore/world-state injection into prompts. | World/lore entries; keys/triggers; activation; placement/order; scan/recursion/budget controls. Keep disabled/out of validation runs unless the test explicitly evaluates lore/RAG behavior. |
| **User Settings** | UI behavior and general per-user interaction preferences. | UI Theme; Theme Colors; Character Handling; Chat/Message Handling; **Streaming FPS**; Smooth Streaming; Auto-scroll Chat; message timestamps; markdown/display behavior; Auto-Swipe; Auto-Continue; autocomplete. |
| **Backgrounds** | Visual chat background management. | Select/upload/manage backgrounds and chat-specific background state. Cosmetic unless a visual workflow explicitly depends on it. |
| **Extensions** | Built-in/system and installed extension controls. | Extension-specific configuration. High-ROI examples in this workspace: attachments, connection manager, memory, regex, token counter, vectors, image captioning/image generation/ComfyUI, translate, TTS. Image generation/ComfyUI is intentionally deferred to later multimodality work. |
| **Persona Management** | Configure the human/user identity inserted into chat context. | Persona name/avatar; **Persona Description**; Position; Connections (`Default`, `Character`, `Chat`); persona switching/locking behavior. |
| **Character Management** | Create/import/select/edit assistant character cards. | Character selection; favorites/tags/filter/sort; create/import; character card fields/instructions; per-character connections/settings. Default `Assistant` is sufficient for neutral harness tests. |

---

## API mode split — high-ROI mental model

### Text Completion

SillyTavern serializes the prompt itself. Highest-impact layers are **Advanced Formatting -> Context Template / Instruct Template / System Prompt**.

Typical local path:

```text
Text Completion -> KoboldCpp -> http://127.0.0.1:5001
```

Use this only when SillyTavern can faithfully represent the model's required template.

### Chat Completion

SillyTavern sends role-structured messages to an OpenAI-compatible chat endpoint. Model Jinja/template processing may occur in the backend. The system-prompt layer is **Chat Completion Prompt Manager / Main Prompt**, not the Advanced Formatting Text Completion System Prompt.

Verified custom source exists in the pinned UI:

```text
Chat Completion
-> Custom (OpenAI-compatible)
-> Custom Endpoint / Base URL
```

The Custom source is keyless-capable. Example local base: `http://127.0.0.1:5001/v1`.

**Rule:** never assume Text Completion and Chat Completion settings are interchangeable. Record which path generated the evidence.

---

## Advanced Formatting — detailed high-ROI map

### Context Template

Controls how chat history, character/persona/scenario and examples are assembled for **Text Completion**.

High-ROI controls:
- Context Template preset.
- Story String.
- Position.
- Example Separator / Chat Start.
- Context Formatting: Always add character name, Generate only one line per request, Collapse Consecutive Newlines, Trim spaces, Trim Incomplete Sentences, Separators as Stop Strings, Names as Stop Strings.
- **Derived template state** when supported by model metadata.

### Instruct Template

Controls user/assistant/system role framing for Text Completion models.

High-ROI controls:
- Instruct Mode ON/OFF.
- Instruct Template preset.
- **Derive from model metadata** when available.
- Activation Regex.
- Wrap Sequences with Newline.
- Replace Macro in Sequences.
- Sequences as Stop Strings.
- Skip Example Dialogues Formatting.
- Include Names.
- Story String Prefix/Suffix.
- User Message Prefix/Suffix.
- Assistant Message Prefix/Suffix.
- System Message Prefix/Suffix; `System same as User`.
- Misc Sequences: First/Last Assistant Prefix, First/Last User Prefix, System Instruction Prefix, **Stop Sequence**, User Filler Message.

**Rule:** if the model-specific template cannot be faithfully represented, do not guess a merely similar template; prefer a backend-Jinja Chat Completion path when supported.

### System Prompt

For Text Completion, controls the system-level instruction inserted into the serialized prompt.

High-ROI controls:
- System Prompt preset.
- Prompt Content.
- Post-History Instructions.

For Chat Completion, use that API mode's Prompt Manager/Main Prompt instead unless current-version evidence shows otherwise.

### Stops / tokenizer / reasoning / misc

- **Custom Stopping Strings:** explicit JSON-array stop sequences; wrong values can truncate responses. `Replace Macro in Stop Strings` controls macro expansion.
- **Template Stop Sequence:** separate from Custom Stopping Strings and may be derived by the selected Instruct template.
- **Tokenizer:** normally `Best match (recommended)` unless a model-specific reason requires otherwise.
- **Token Padding:** prompt-budget safety margin; observed baseline `64`.
- **Reasoning:** Auto-Parse, Auto-Expand, Show Hidden, Add to Prompts, Max and Reasoning Formatting. Treat as model-specific. Do not use Auto-Parse merely to hide a template/runtime failure.
- **Miscellaneous:** Bind Model to Templates; Non-markdown strings; Start Reply With; Show reply prefix in chat.

### Observed Defiant Text Completion attempt

Metadata derivation produced:

```text
Context Template:   ChatML
Instruct Template:  ChatML
System prefix:       <|im_start|>system
System suffix:       <|im_end|>
User prefix:         <|im_start|>user
User suffix:         <|im_end|>
Assistant prefix:    <|im_start|>assistant
Assistant suffix:    <|im_end|>
Stop Sequence:       <|im_end|>
Custom Stops:        empty
Tokenizer:           Best match (recommended)
Token Padding:       64
Reasoning controls:  OFF
Bind Model:          OFF during validation
Start Reply With:    empty
```

Behavioral validation then showed visible empty `<think>...</think>` blocks on every assistant response. Therefore this is recorded as a **failed/incomplete Qwen3.5 non-thinking template path**, not as the final Defiant configuration.

---

## Chat Completion Prompt Manager — high ROI

Used by Chat Completion APIs to construct the role-structured prompt/message stack.

Important concepts:
- **Main Prompt** — primary system instruction; project baseline belongs here on the corrected Defiant Chat Completion path.
- Prompt order/enable state — determines which prompt fragments are actually sent.
- Additional/jailbreak/NSFW/auxiliary prompts — can materially alter behavior; disable/empty during clean validation where possible.
- Character/persona/world-info blocks can also enter the prompt stack; keep controlled when attributing model behavior.

When moving from Text Completion to Chat Completion, explicitly re-home and re-verify the system prompt instead of assuming it migrated.

---

## API Connections — current project paths

Guide-1 transport baseline:

```text
API:       Text Completion
API Type:  KoboldCpp
API URL:   http://127.0.0.1:5001
```

Guide-2 corrected Defiant/Qwen3.5 non-thinking path:

```text
API:                    Chat Completion
Chat Completion Source: Custom (OpenAI-compatible)
Custom Endpoint/Base:   http://127.0.0.1:5001/v1
```

`Derive context size from backend` is independent of template correctness.

---

## AI Response Configuration — what matters first

For reproducible evaluation, prioritize:

1. API mode/provider preset identity,
2. response length/output budget,
3. context size,
4. Streaming,
5. temperature,
6. Top-P / Top-K / Min-P,
7. penalties/repetition controls,
8. only then advanced/dynamic samplers.

Never change several sampler dimensions at once while diagnosing a failure.

---

## User Settings — useful operational controls

Observed major groups:

- **UI Theme / Theme Colors** — visual only.
- **Character Handling** — character search/import/display behavior.
- **Chat/Message Handling** — messages loaded, **Streaming FPS**, swipes/gestures, Auto-scroll Chat, edit/delete behavior, markdown/display options.
- **Miscellaneous** — Smooth Streaming, sound, relaxed API URLs, lorebook import dialog, input restoration, Moving UI.
- **Auto-Swipe / Auto-Continue / AutoComplete Settings** — automation/convenience; keep conservative during controlled evaluation.

`Streaming` itself is a generation setting; `Streaming FPS` / `Smooth Streaming` affect presentation behavior.

---

## Persona Management — prompt impact

Key fields:
- Persona name/avatar.
- **Persona Description** — can enter the prompt and therefore alter model behavior.
- Position — controls where persona text is injected.
- Connections — Default / Character / Chat.
- Global persona-switch/locking behavior.

For controlled model tests, keep persona content minimal unless persona behavior is under evaluation.

---

## Chat action menu (bottom-left wand/menu)

Not a settings tab, but commonly used during testing:

- Author's Note
- CFG Scale
- Token Probabilities
- Start new chat
- Close chat
- Manage chat files
- Delete messages
- Regenerate
- Impersonate
- Continue

For clean evals, **Start new chat** is preferable to reusing history after a template/API/system-prompt change.

---

## Extensions: interpretation rule

Extensions may add settings, prompt transforms or external services. Examples visible/available in the pinned runtime include image generation, image captioning, memory, regex, token counter, translate, TTS and vectors.

**Evaluation rule:** record whether behavior comes from core SillyTavern, KoboldCpp/model, or an extension. Never attribute an extension failure to the model without evidence.

---

## Project-specific navigation shorthand

- **Open API Connections** -> plug icon.
- **Open Advanced Formatting** -> `A` icon.
- **Open AI Response Configuration** -> sliders icon.
- **Open User Settings** -> user/gear icon.
- **Open Persona Management** -> smiley/persona icon.
- **Open Character Management** -> ID-card/list icon.

Current Guide-2 gate: corrected Defiant backend Jinja/non-thinking Chat Completion path, then Prompt Manager/Main Prompt validation.

# Handoff: SillyTavern Caption Delivery Extension

**Status:** `DEFERRED — DO NOT EXECUTE`

**Team Master priority override — 2026-09-15:** Image Captioning fungerar redan tillräckligt bra och ska inte få mer projekttid nu. Extensions, caption-hardening och ComfyUI är lägst prioriterade i det aktuella SillyTavern/KoboldCpp-arbetet. Storyteller-agentens modell-/runtimekonfiguration, långsiktiga stabilitet, realistisk prestandaoptimering och sparade profiler är P0.

Denna fil bevaras endast som spårbar tidigare specifikation. ChatGPT ska inte välja, implementera, committa eller byta suffix på den utan en ny uttrycklig aktivering från Team Master. `INCOMPLETE`-suffixet betyder här endast att den tidigare beställningen aldrig utfördes; det är inte en aktiv arbetskö.

## Goal and practical value

Create an additive SillyTavern UI extension that fixes the verified caption-delivery UX problems without modifying SillyTavern core or disturbing the stable Storyteller TEXT runtime.

The extension must:

1. show an unmistakable in-flight state immediately after image selection,
2. prevent accidental duplicate caption requests and concurrent caption load,
3. expose a completed caption as soon as the caption promise resolves,
4. present an extension-owned image-first / caption-below result,
5. provide copy and browser-download export for the completed caption,
6. reuse SillyTavern's existing multimodal caption settings, including its secondary endpoint,
7. keep request state, timing and errors deterministic and independently testable.

This is suitable for ChatGPT because the core controller, UI assets and offline tests are a self-contained multi-file repo slice. It does not require access to Team Master's local KoboldCpp process, GPU, model, browser session or private files.

## Verified current foundation

- Guide 1–4 is closed for the current sprint. Read `SillyTavern_UI/[GUIDES-1-4] - [CODEX HANDOFF].md` and `SillyTavern_UI/[GUIDE-4] - [IMAGE MULTIMODALITY].md` before editing.
- Pinned SillyTavern version: `1.19.0`, commit `06bde939fb1e9c4c8d8641d810f0a916b5bce127`.
- The built-in Image Captioning extension already performs functional end-to-end captioning.
- The observed production UX defects are delayed/unclear delivery, weak progress visibility, repeated clicks causing duplicate requests, and caption-before-image presentation.
- The built-in shared helper `getMultimodalCaption(base64Img, prompt)` is exported and already owns provider routing plus secondary endpoint behavior.
- Built-in caption internals such as `getCaptionForFile` and `sendCaptionedMessage` are not public exports and must not be copied or called as hidden globals.
- The built-in helper currently provides no verified abort signal or backend cancellation contract.

Pinned upstream reference surfaces:

- `https://github.com/SillyTavern/SillyTavern/blob/06bde939fb1e9c4c8d8641d810f0a916b5bce127/public/scripts/extensions/caption/index.js`
- `https://github.com/SillyTavern/SillyTavern/blob/06bde939fb1e9c4c8d8641d810f0a916b5bce127/public/scripts/extensions/shared.js`
- `https://docs.sillytavern.app/for-contributors/writing-extensions/`

## Locked implementation boundary

Implement a normal third-party UI extension. Do not patch, fork or replace the built-in caption extension.

The runtime integration adapter must use supported exported SillyTavern modules and delegate the actual multimodal request to `getMultimodalCaption`. It must read the existing Image Captioning settings instead of introducing a second provider, model, endpoint or secret configuration.

The extension owns only:

- its own image-selection action and result panel,
- request admission and duplicate/concurrency prevention,
- visible state and elapsed-time presentation,
- extension-local result rendering,
- copy and browser-download export,
- a small dependency-injected controller that can be tested without SillyTavern.

The first slice must allow at most one active caption operation globally. A repeated activation for the same image must reuse/focus the existing operation or report that it is already running; it must never dispatch a second request. Selecting another image while busy must produce a clear busy state without dispatching another request. Retry is allowed only after the earlier operation has completed or failed.

Use responsibility-based internal names. Do not introduce new global mode names, provider catalogs, stable schemas or duplicated semantic configuration.

## Required behavior

### Extension-owned interaction

- Add a clearly named caption action without deleting or silently overriding the built-in action.
- Let the user choose one supported image file.
- Render the selected image preview immediately.
- Show a visible `Captioning...` state before awaiting the request.
- Show elapsed time while running or, if continuous timer rendering would add unnecessary complexity, show exact start and completion duration.
- On success, render the caption exactly once below the image.
- Provide `Copy caption` and browser-based `.txt` download actions.
- On failure, keep the image visible, show a useful error state and permit a deliberate retry.
- Reset the file input so the same file can be deliberately selected again after completion/failure.

### Request controller

Keep admission/state/timing logic independent of DOM and SillyTavern imports. Inject the async caption operation into the controller.

The controller must deterministically cover:

- idle -> running -> succeeded,
- idle -> running -> failed,
- duplicate activation while running,
- different-image activation while globally busy,
- retry after failure,
- cleanup after settlement,
- exactly one terminal result per accepted operation,
- monotonic elapsed-duration calculation through an injected clock.

The exact local class/function names are implementation details, but they must describe responsibility and remain internal to this extension.

### Integration adapter

- Convert the selected supported image to the data URL shape required by `getMultimodalCaption` using supported exported SillyTavern utilities.
- Use the existing caption prompt from `extension_settings.caption.prompt`, with SillyTavern macro substitution where supported by the public surface.
- Call `getMultimodalCaption` exactly once for each accepted operation.
- Do not reproduce the provider switch or construct KoboldCpp/OpenAI/Ollama endpoint payloads inside this extension.
- Do not persist API keys, endpoint secrets or copied provider configuration.
- Do not write directly to an arbitrary local filesystem path. The first slice may use Clipboard API and a user-initiated browser download only.

## Explicitly deferred or forbidden

- No changes to `SillyTavern_UI/_local_runtime/**`.
- No changes to SillyTavern built-in caption/shared/core files.
- No changes to `SillyTavern_UI/harness/**`, `scripts/**`, Guide files, `AGENTS.md`, `.gitignore` or `MY ACC$.MD`.
- Do not modify or resolve the unrelated existing WORKER/AutoPull handoff.
- No Server Plugin.
- No model download, model execution, localhost/API probing, GPU work or browser/UI automation.
- No Storyteller TEXT, Jinja, thinking-mode, RAG or ComfyUI work.
- Do not hide, disable or monkey-patch the built-in caption action.
- Do not claim actual backend cancellation. `AbortController` or a `Cancel` label is forbidden unless a real abort signal is carried through the actual caption request and independently verified. That is not part of this slice.
- Do not add third-party runtime or test dependencies. Prefer browser-native APIs and Node's built-in `node:test`.
- Do not introduce speculative framework structure, generic helpers or placeholder architecture beyond what this vertical slice directly consumes.

## Allowed write surface

Create files only inside:

```text
SillyTavern_UI/my_custom_chat_extensions/custom_image_captioning/
```

Expected responsibility-based files:

```text
manifest.json
index.js
caption_request_controller.js
settings.html
style.css
package.json
README.md
tests/caption_request_controller.test.mjs
```

The exact list may be reduced when a file is unnecessary. Additional files require a concrete responsibility and must remain inside the allowed folder. Do not create generated bundles, dependency directories, screenshots or test-output artifacts.

ChatGPT may update and rename this handoff file according to its status rules. No other path is authorized.

## Offline verification and completion gate

At minimum, use Node's built-in test runner. From repository root, the intended command shape is:

```text
node --test "SillyTavern_UI/my_custom_chat_extensions/custom_image_captioning/tests/caption_request_controller.test.mjs"
```

Tests must prove:

1. two same-image activations during one active operation execute the injected caption function once,
2. a different-image activation while busy executes no second caption function,
3. success is published once and leaves the controller retryable,
4. failure is published once and leaves the controller retryable,
5. retry after settlement creates exactly one new operation,
6. elapsed duration uses the injected clock and cannot depend on wall-clock sleeps,
7. stale completion from an obsolete operation cannot overwrite a newer accepted result if the implementation can create such a condition,
8. the manifest points to existing extension assets and declares compatibility with the pinned SillyTavern version when supported by its manifest contract.

Also perform a targeted static review that verifies:

- no forbidden path changed,
- no provider-routing logic was duplicated,
- the rendered extension-owned structure places image before caption,
- visible status and failure text exist,
- no secret or absolute local path was added,
- files are UTF-8 without BOM.

If the GitHub environment cannot execute Node tests, implement the work but keep the filename suffix `[INCOMPLETE]`; record the exact unexecuted command and what remains for Codex. Do not report inferred success as executed verification.

## Required final report in this file

Before finishing, add a concise report containing:

- every created/changed/deleted file,
- implementation behavior delivered,
- every executed check and its exact result,
- any unexecuted check or blocker,
- known limitations and deferred local validation,
- PIPSA: whether any process restart would be needed after Codex installs the extension locally.

Rename this file to the same base name ending in `[COMPLETED].md` only if every ChatGPT-owned implementation and offline verification requirement actually passed. Local SillyTavern/KoboldCpp integration remains Codex-owned and is not implied by ChatGPT's `COMPLETED` status.

# Claude Research Input — Local Runtime Observability

> Per the handoff's own protocol: this is **research input**, not verified evidence. I have no access to the repo (GitHub fetch is robots-blocked for this URL), the pinned commit, or any local files. Every claim that would require reading `AGENTS.md`, `LM-Studio_logs/README.md`, the AGPR role docs, or live SillyTavern/KoboldCpp/Gradio/diffusers/Windows-NVIDIA source is marked **`unverified`** below. Treat the rest as general engineering practice to be checked against primary sources by ChatGPT/Codex.

---

## 1. Operator question contract

| #   | Question                                                  | Minimum evidence                                                                                                                             |
| --- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Which model/profile served this request?                  | `producer` (service name + version) + `model_ref` on the generate/synthesize event                                                           |
| 2   | What was the actual request path (ST → broker → backend)? | Shared `correlation_id` joined across every producer's log for that operation                                                                |
| 3   | Latency breakdown (queue/unload/load/generate/deliver)?   | `phase` + `duration_ms` on each sub-event, summable to `total_ms`                                                                            |
| 4   | Where's the output artifact?                              | `artifact_ref` (path) on the completion event                                                                                                |
| 5   | Process/GPU lifecycle — load/unload, VRAM peak?           | `vram_peak_mb` on load/generate events, `event_type: unload/load` pair                                                                       |
| 6   | Did a reload happen mid-session, and why?                 | `role_switch` event with `from_role`, `to_role`, `reason`                                                                                    |
| 7   | Was the operation interrupted/cancelled?                  | `outcome` field: `success \| cancelled \| error`                                                                                             |
| 8   | Why is a result missing?                                  | Either an `error` event with `stage` + `cause`, or an explicit **evidence gap** (no completion event found — logged as absence, not silence) |
| 9   | Which params/voice preset were used?                      | `params` snapshot on the producer event (subject to the redaction policy in §6)                                                              |
| 10  | Was this a retry, and of what?                            | `retry_of: <correlation_id>`                                                                                                                 |
| 11  | Cold or warm start?                                       | `previous_role` + `idle_ms` on the load event                                                                                                |
| 12  | Did logging itself distort the timing?                    | Separate self-instrumentation overhead number (see §8), not mixed into operation `duration_ms`                                               |

A field that doesn't answer one of these, and isn't a security/audit obligation (§6), shouldn't exist — this list is the backward-derivation the handoff asks for.

## 2. Correlation across boundaries

**Simple `correlation_id`** (UUID minted once per top-level operation — a role switch or an invoke) beats W3C Trace Context/OpenTelemetry trace/span IDs _for this system_, because:

- Hop count is small and fixed: SillyTavern → broker → backend → subprocess. OTel's value (auto-instrumentation across many services/languages, sampling, vendor-neutral backends) is built for fan-out topologies this isn't.
- A flat `correlation_id` + a `phase` field per sub-step (unload/load/generate) gives you the same "reconstruct the timeline" capability as spans, at a fraction of the implementation cost — you don't need parent/child span relationships when there's no branching concurrency (per the single-active-role constraint already locked for this system).

**Unverified:** whether SillyTavern's extension/server-plugin layer and KoboldCpp's HTTP API let a custom correlation header pass through cleanly end-to-end without patching. This needs a source check against current SillyTavern server-plugin docs and the KoboldCpp API, or a five-minute local spike test — I can't confirm it from here.

**Migration path:** if a `correlation_id` is _shaped_ like a trace ID (16-byte hex) and event fields are named close to OTel semantic conventions from the start (§4), swapping to real OTel later is a rename, not a rewrite.

## 3. Real capture points

All rows below are **unverified** — I have no access to current SillyTavern, KoboldCpp, Gradio/Dia2, diffusers/SANA, or Windows/NVIDIA source/docs to confirm hook surfaces. Structure to fill in once checked:

| Component                      | Native capture? | Needs wrapper/middleware? | Needs upstream change? | Source status                                                                                                                                         |
| ------------------------------ | --------------- | ------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| SillyTavern                    | ?               | ?                         | ?                      | unverified                                                                                                                                            |
| KoboldCpp                      | ?               | ?                         | ?                      | unverified                                                                                                                                            |
| Gradio/Dia2                    | ?               | ?                         | ?                      | unverified                                                                                                                                            |
| diffusers/SANA-Sprint          | ?               | ?                         | ?                      | unverified                                                                                                                                            |
| Windows/NVIDIA (VRAM, process) | ?               | ?                         | ?                      | unverified — `nvidia-smi`/NVML polling is a plausible fallback for VRAM peak but needs confirming against what's already in `LM-Studio_observability` |

Don't let this table get filled from inference — each cell needs a primary-source citation before it's trusted.

## 4. Minimal common event envelope

Shared fields (kept deliberately small):

```
schema_version, ts (UTC ISO 8601), correlation_id, producer (service+version),
event_type, phase, outcome, duration_ms, model_ref, artifact_ref, severity
```

Everything component-specific (generation params, voice preset ID, quantization, step count) goes in a nested `detail` object, not flattened into the shared schema — this is what keeps the envelope "few fields" per the handoff's own constraint (§4 of the handoff) instead of drifting into a universal megaschema.

## 5. Ownership without redundancy

| Producer                               | Stream                                                                                      | Consumer                           | Retention           |
| -------------------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------- |
| Broker                                 | its own component log                                                                       | operator, via query tool (§ below) | bounded (count/age) |
| AGPR-2 (Storyteller/KoboldCpp)         | its own component log                                                                       | operator                           | bounded             |
| AGPR-3 (Image Master)                  | its own component log                                                                       | operator                           | bounded             |
| AGPR-4 (Voice Master/Dia2)             | its own component log                                                                       | operator                           | bounded             |
| Eval artifacts, Story Creator run logs | **untouched** — existing streams, explicitly out of scope per the handoff's negative bounds | —                                  | —                   |

Each raw event has exactly one owner (the component that generated it). Cross-component incidents are **linked by `correlation_id`**, never copied between streams — a query tool joins them on read, nothing is duplicated at write time. Runtime evidence stays structurally separate from eval results and generated media artifacts by living in a different directory/stream entirely, not by field-level filtering.

## 6. Sensitive content & path safety

- **Story/prompt text, generated media, reference voices, raw model I/O:** default to metadata only at INFO (length, hash, param snapshot). Raw content only at DEBUG, opt-in, and ideally as a reference to the artifact file rather than inlined in a log line.
- **Tokens/headers/credentials:** never logged, at any level.
- **Absolute paths:** prefer paths relative to a known root; if absolute paths are unavoidable, treat them as low-but-nonzero sensitivity (they can carry a Windows username).
- **Why this matters even fully local:** logs get pasted into other tools (this conversation is a live example), shared with other AI agents in the same multi-agent workflow (ChatGPT, Codex), or committed to the repo. "Local-only" doesn't mean "never leaves the machine" in this workflow — the redaction discipline should assume logs may travel.

## 7. Bounded, crash-robust persistence

**Direct conflict to flag:** the handoff states JSONL doesn't satisfy the "human-readable multiline" requirement, which contradicts the JSONL recommendation I gave earlier in this conversation for a _different_ (SillyTavern-only) design. For _this_ system, given that explicit requirement:

- **Recommend: one pretty-printed JSON file per operation**, named by `correlation_id`, written once at completion via temp-file-then-atomic-rename (`os.replace()` is atomic on Windows too). This satisfies human-readability _and_ atomicity — the file is either fully written or doesn't exist, no partial-write corruption risk.
- Compared to the alternatives: per-event files (too many small files, filesystem overhead at scale) and a single appended JSONL stream (best for tailing/grep performance, but fails the stated readability requirement outright).
- **Windows file locking:** open → write → close → rename per operation; don't hold a handle open across the operation's lifetime, which avoids lock contention with antivirus/Explorer indexing.
- **Retention:** cap by count or age, pruned by a periodic sweep — never on the hot path.

## 8. Measurable overhead

A deterministic micro-benchmark: run N identical operations per role (e.g., 20× AGPR-2 generate, 20× AGPR-3 generate, 20× AGPR-4 invoke) with logging fully on vs. a no-op logger, compare p50/p95 for first-token/first-image/first-audio latency, total runtime, and peak VRAM/RAM. A reasonable target ceiling to test against — **not to assume**: logging overhead under roughly 1% of total operation time at INFO level with non-blocking (async/buffered) writes. This number must be locked by a local A/B, not taken on faith.

## 9. Build vs. standard vs. OpenTelemetry

| Approach                     | Fit for this system                                                                                                                                                                                                                                                                                                                                                             |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Std-lib + component wrappers | Lowest cost, matches single-user/few-hop reality, fastest to a working walking skeleton                                                                                                                                                                                                                                                                                         |
| OpenTelemetry SDK            | Overkill for the hop count and single-user scope right now                                                                                                                                                                                                                                                                                                                      |
| **Hybrid (recommended)**     | Plain structured logging per §7, but field names chosen to line up with OTel semantic conventions (`duration_ms`-style naming, `service.name`, a trace-ID-shaped `correlation_id`) — so if the system grows into a real multi-process broker (which it's already becoming, per the current architecture work), migrating the transport to OTLP later is a rename, not a rewrite |

---

## Synthesis

**1–4.** See tables above (operator questions, capture-point matrix — largely unverified pending source checks, build-vs-standard comparison, and the recommended skeleton: broker + three component loggers, each writing bounded pretty-JSON per-operation files sharing the envelope in §4, correlated by a flat `correlation_id`, queried on-demand by a small offline join tool rather than a live central logging service).

**5. Top five local-only unknowns**, ordered by expected information gain per cost:

1. Whether SillyTavern's extension/plugin layer supports custom header propagation to backend calls — determines whether `correlation_id` propagation needs a header, a query param, or a request-body field.
2. What KoboldCpp's API currently exposes for load/unload timing and VRAM reporting natively vs. requiring an external NVML poll.
3. Whether Gradio/Dia2's process model supports clean programmatic load/unload, or requires a subprocess restart (materially changes the `unload_ms`/`load_ms` numbers and what's even measurable).
4. Current state of the uncommitted Voice Master launcher work — this document must not guess its shape, and neither can I.
5. Whether `LM-Studio_observability`'s existing Python implementation already solves any of §2–§4 in a way worth reusing verbatim rather than re-deriving.

**6. Risk register**

| Risk                                                    | Mitigation                                                                                           |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Double ownership (two components logging the same fact) | One producer per raw event, enforced by the matrix in §5                                             |
| Log spam                                                | INFO stays complete-but-minimal; DEBUG is opt-in and off by default                                  |
| Secret/content leakage                                  | Redaction-by-default per §6, raw content is opt-in and artifact-referenced, not inlined              |
| False causality (correlation without real order)        | Every event carries `ts` in UTC + `correlation_id` + `phase`, never inferred from file order         |
| Version drift (schema changes silently)                 | `schema_version` field from day one; treat any schema change as a version bump, not an in-place edit |
| Measurement itself distorting timing                    | Overhead is benchmarked separately (§8) and never folded into operation `duration_ms`                |

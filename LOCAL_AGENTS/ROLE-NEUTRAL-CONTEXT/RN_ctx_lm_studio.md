# LM Studio Runtime

- LM Studio Desktop and Local Model API are the project's primary and only active harness for Frontier-agent communication with local agent candidates. LM Studio-based Frontier-as-Evaluator work is the current governing priority.
- Native REST API v1 is the primary transport. Every consumer must verify the concrete request, response, authentication, chat-template, thinking, stop, context, load, unload, stateful and integration behavior it relies on; OpenAI-compatible endpoints are secondary compatibility surfaces.
- A model is selected by its role-specific runtime configuration. Shared context must never assume or hardcode a model name, model path, agent prompt, or active role.
- `LM_API_TOKEN` is read from the current process or persistent Windows user environment and is never stored in project files or logs.
- Readiness is established from successful process and API checks, not from a visible application window.
- Runtime configuration should preserve model metadata unless a verified incompatibility requires a project-owned override.
- Local operation can remain offline after the required application, model, runtime, and packages are installed.
- Bionic is legacy/deprecated and must not be treated as an active harness, transport, session owner or log owner.

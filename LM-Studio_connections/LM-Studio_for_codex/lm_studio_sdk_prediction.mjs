/** Single owned prediction. JSON lines are bounded IPC, never persistent logs. */
import { LMStudioClient, Chat } from "@lmstudio/sdk";
import { createInterface } from "node:readline";
import { once } from "node:events";
import { pathToFileURL } from "node:url";

// Approved SDK 1.5.0 adapter. Remove when adopting a release with apiToken.
// https://github.com/lmstudio-ai/lmstudio-js/blob/main/packages/lms-shared-types/src/lmstudioAPIToken.ts
export function authenticatedOptions(token, baseUrl) {
  const match = /^sk-lm-(?<clientIdentifier>[a-zA-Z0-9]{8}):(?<clientPasskey>[a-zA-Z0-9]{20})$/.exec(token);
  if (!match) throw new Error("invalid_token_shape");
  const url = new URL(baseUrl);
  if (url.protocol !== "ws:" || !["127.0.0.1", "localhost", "[::1]"].includes(url.hostname)
      || url.username || url.password || url.search || url.hash || url.pathname !== "/") {
    throw new Error("non_loopback_origin");
  }
  return { baseUrl: baseUrl.replace(/\/$/, ""), ...match.groups,
    verboseErrorMessages: false,
    logger: { info() {}, warn() {}, error() {}, debug() {} } };
}

export function predictionChat(systemPrompt, instruction) {
  const chat = Chat.empty();
  if (systemPrompt) chat.append("system", systemPrompt);
  chat.append("user", instruction);
  return chat;
}

async function emit(event) {
  const line = JSON.stringify(event) + "\n";
  if (Buffer.byteLength(line) > 262144) throw new Error("ipc_byte_limit");
  if (!process.stdout.write(line)) await once(process.stdout, "drain");
}

export async function main() {
  let prediction;
  let started = false;
  let cancelled = false;
  let cancelDispatched = false;
  let finalReceived = false;
  let client;
  let allowStart;
  const startApproval = new Promise(resolve => { allowStart = resolve; });
  const commands = createInterface({ input: process.stdin, crlfDelay: Infinity });
  const cancel = async () => {
    cancelled = true;
    allowStart(false);
    if (prediction && !finalReceived && !cancelDispatched) {
      cancelDispatched = true;
      await prediction.cancel();
      await emit({ type: "cancel_sent" });
    }
  };
  // Observe cancellation even while start awaits inventory/model metadata.
  // This prevents a queued pre-start stop from unnecessarily starting inference.
  commands.on("line", line => {
    if (Buffer.byteLength(line) <= 65536) {
      try {
        const instruction = JSON.parse(line);
        if (instruction.command === "cancel") void cancel().catch(() => process.exit(3));
        if (instruction.command === "continue") allowStart(true);
      } catch { /* The command loop reports malformed input without secrets. */ }
    }
  });
  commands.on("close", () => { if (!finalReceived) void cancel(); });
  const emergencyDeadline = setTimeout(() => process.exit(3), 135000);
  try {
    for await (const line of commands) {
      if (Buffer.byteLength(line) > 65536) throw new Error("command_byte_limit");
      const command = JSON.parse(line);
      if (command.command === "cancel") { await cancel(); continue; }
      if (command.command === "continue") continue;
      if (command.command !== "start" || started) throw new Error("invalid_command");
      started = true;
      client = new LMStudioClient(authenticatedOptions(process.env.LM_API_TOKEN || "", command.base_url));
      // listLoaded yields specific handles; .model() is forbidden (may JIT-load).
      const loaded = await client.llm.listLoaded();
      if (command.inventory) {
        await emit({ type: "inventory", models: loaded.map(m => ({ identifier: m.identifier, model_key: m.modelKey })) });
        finalReceived = true;
        break;
      }
      const model = loaded.find(m => m.identifier === command.model);
      if (!model) throw new Error("model_not_loaded");
      const info = await model.getModelInfo();
      await emit({ type: "model_bound", model_info: info });
      if (cancelled) {
        finalReceived = true;
        await emit({ type: "not_started" });
        break;
      }
      const chat = predictionChat(command.system_prompt || "", command.instruction);
      if (command.inspect_model) {
        // Public read-only SDK calls; no prediction, model load or private API.
        const contextLength = await model.getContextLength();
        const rendered = await model.applyPromptTemplate(chat);
        const inputTokens = await model.countTokens(rendered);
        await emit({ type: "model_inspection", model_info: info,
          context_length: contextLength, rendered_input: rendered, input_tokens: inputTokens });
        finalReceived = true;
        break;
      }
      if (command.require_start_approval && !(await startApproval)) {
        finalReceived = true;
        await emit({ type: "not_started" });
        break;
      }
      let progressBucket = -1;
      prediction = model.respond(chat, { temperature: 0, maxTokens: command.max_tokens,
        onPromptProcessingProgress(progress) {
          const bucket = Math.floor(progress * 10);
          if (bucket > progressBucket) {
            progressBucket = bucket;
            void emit({ type: "prompt_progress", percent: bucket * 10 });
          }
        } });
      await emit({ type: "prediction_started" });
      if (cancelled) await cancel();
      // Consume in a concurrent task so the command loop remains interruptible.
      void (async () => {
        try {
          for await (const fragment of prediction) {
            await emit({ type: "fragment", content: fragment.content, reasoning_type: fragment.reasoningType });
          }
          const result = await prediction.result();
          finalReceived = true;
          await emit({ type: "result", content: result.content, stats: result.stats,
            model_info: result.modelInfo, load_config: result.loadConfig,
            prediction_config: result.predictionConfig });
        } catch {
          await emit({ type: "error", code: "prediction_transport_error" });
        } finally {
          commands.close();
        }
      })();
    }
  } catch (error) {
    const allowed = new Set(["model_not_loaded", "invalid_token_shape", "non_loopback_origin", "invalid_command", "command_byte_limit"]);
    await emit({ type: "error", code: allowed.has(error.message) ? error.message : "sdk_auth_or_transport_error" });
  } finally {
    clearTimeout(emergencyDeadline);
    if (prediction && !finalReceived) await cancel();
    if (client) await client[Symbol.asyncDispose]();
    commands.close();
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(() => process.exit(3));
}

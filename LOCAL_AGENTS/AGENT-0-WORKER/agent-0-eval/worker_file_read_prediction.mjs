/** One bounded WORKER read-only agent action through the existing LM Studio SDK. */
import { LMStudioClient, tool } from "../../../../LM-Studio_connections/LM-Studio_for_codex/node_modules/@lmstudio/sdk/dist/index.mjs";
import { z } from "../../../../LM-Studio_connections/LM-Studio_for_codex/node_modules/zod/index.js";
import { authenticatedOptions, predictionChat } from "../../../../LM-Studio_connections/LM-Studio_for_codex/lm_studio_sdk_prediction.mjs";
import { workerWorkspaceTextTool } from "../agent-0-tools/worker_workspace_text_tool.mjs";
import { parseGraniteToolCallEnvelope } from "../AG-0-MODEL-Granite_4.1-3B/granite_tool_call_envelope.mjs";
import { createInterface } from "node:readline";
import { pathToFileURL } from "node:url";

function emit(event) {
  const line = JSON.stringify(event) + "\n";
  if (Buffer.byteLength(line) > 262144) throw new Error("ipc_byte_limit");
  process.stdout.write(line);
}

export async function main() {
  const commands = createInterface({ input: process.stdin, crlfDelay: Infinity });
  const abort = new AbortController();
  let allowStart;
  const approval = new Promise(resolve => { allowStart = resolve; });
  let cancelled = false;
  let completed = false;
  let started = false;
  let client;
  let toolState = { active: 0, completed: 0, aborted: 0, denied: 0 };
  let lastResult = null;
  let lastMessage = "";
  let bridgeUsed = false;
  let bridgeSourceContent = null;
  let sentCancel = false;
  const cancel = () => {
    cancelled = true;
    allowStart(false);
    if (!sentCancel) {
      sentCancel = true;
      abort.abort();
      emit({ type: "cancel_sent" });
    }
  };
  commands.on("line", line => {
    if (Buffer.byteLength(line) <= 65536) {
      try {
        const command = JSON.parse(line);
        if (command.command === "cancel") cancel();
        if (command.command === "continue") allowStart(true);
      } catch { /* The main loop reports invalid initial commands. */ }
    }
  });
  commands.on("close", () => { if (!completed) cancel(); });
  const deadline = setTimeout(() => process.exit(3), 45000);
  try {
    for await (const line of commands) {
      if (Buffer.byteLength(line) > 65536) throw new Error("command_byte_limit");
      const command = JSON.parse(line);
      if (command.command === "cancel") continue;
      if (command.command === "continue") continue;
      if (command.command !== "start" || started) throw new Error("invalid_command");
      started = true;
      if (command.max_tokens !== 512 || command.max_rounds !== 2 || !command.require_start_approval
          || typeof command.instruction !== "string" || command.instruction.length > 1024) {
        throw new Error("invalid_contract");
      }
      if (command.granite_text_tool_bridge && command.model !== "granite-4.1-3b") {
        throw new Error("invalid_contract");
      }
      client = new LMStudioClient(authenticatedOptions(process.env.LM_API_TOKEN || "", command.base_url));
      const loaded = await client.llm.listLoaded();
      const model = loaded.find(item => item.identifier === command.model);
      if (!model) throw new Error("model_not_loaded");
      const info = await model.getModelInfo();
      emit({ type: "model_bound", model_info: info });
      if (cancelled || !(await approval)) {
        completed = true;
        emit({ type: "not_started" });
        break;
      }
      const reader = await workerWorkspaceTextTool({ tool, z,
        workspaceRoot: command.workspace_root,
        allowedRelativePath: command.allowed_relative_path,
        controllerSignal: abort.signal,
        diagnosticDelayMs: command.diagnostic_delay_ms || 0,
        record: emit });
      toolState = reader.state;
      const chat = predictionChat("", command.instruction);
      const options = {
        temperature: 0, maxTokens: 512, maxPredictionRounds: 2,
        allowParallelToolExecution: false, signal: abort.signal,
        onRoundStart(index) { emit({ type: "round_started", index }); },
        onRoundEnd(index) { emit({ type: "round_ended", index }); },
        onPredictionFragment(fragment) {
          emit({ type: "fragment", index: fragment.roundIndex, content: fragment.content });
        },
        onPredictionCompleted(result) {
          lastResult = result;
          emit({ type: "round_result", index: result.roundIndex,
            stats: result.stats, content: result.content });
        },
        onMessage(message) {
          if (message.getRole() === "assistant") lastMessage = message.getText();
          emit({ type: "message", role: message.getRole(), content: message.getText() });
        },
        onToolCallRequestFinalized(index, callId, info) {
          emit({ type: "tool_requested", index, call_id: callId,
            name: info.toolCallRequest.name });
        },
        guardToolCall(index, callId, { toolCallRequest, allow, deny }) {
          if (abort.signal.aborted || toolCallRequest.name !== "read_workspace_text"
              || toolState.active + toolState.completed >= 2) {
            emit({ type: "tool_guard_denied", index, call_id: callId });
            deny("Tool unavailable or call budget exhausted.");
          } else {
            allow();
          }
        },
        handleInvalidToolRequest(error, request) {
          emit({ type: "invalid_tool_request", name: request?.name || null });
          if (request) return "Error: invalid tool request.";
          throw error;
        },
      };
      try {
        const actionStarted = performance.now();
        const outcome = await model.act(chat, [reader.definition], options);
        if (command.granite_text_tool_bridge && !abort.signal.aborted
            && lastResult?.stats?.stopReason === "eosFound" && toolState.completed === 0) {
          const request = parseGraniteToolCallEnvelope(lastMessage || lastResult.content);
          if (request) {
            bridgeUsed = true;
            bridgeSourceContent = lastMessage || lastResult.content;
            emit({ type: "text_tool_bridge_request", name: request.name,
              arguments: request.arguments });
            const toolContent = await reader.execute(request.arguments, {
              signal: abort.signal, callId: 0, status() {}, warn() {},
            });
            abort.signal.throwIfAborted();
            chat.append({ role: "assistant", content: [{ type: "toolCallRequest",
              toolCallRequest: { type: "function", name: request.name,
                arguments: request.arguments } }] });
            chat.append({ role: "tool", content: [{ type: "toolCallResult",
              content: toolContent }] });
            emit({ type: "text_tool_bridge_followup_started" });
            const followup = model.respond(chat, { temperature: 0, maxTokens: 512,
              signal: abort.signal });
            for await (const fragment of followup) {
              emit({ type: "fragment", index: 1, content: fragment.content });
            }
            const result = await followup;
            lastResult = result;
            lastMessage = result.content;
            emit({ type: "bridge_followup_result", stats: result.stats,
              content: result.content });
          }
        }
        completed = true;
        emit({ type: "result", content: lastMessage || lastResult?.content || "",
          stats: lastResult?.stats || null, model_info: lastResult?.modelInfo || info,
          load_config: lastResult?.loadConfig || null,
          prediction_config: lastResult?.predictionConfig || null,
          rounds: outcome.rounds + (bridgeUsed ? 1 : 0),
          total_execution_seconds: (performance.now() - actionStarted) / 1000,
          text_tool_bridge_used: bridgeUsed, bridge_source_content: bridgeSourceContent,
          tool_state: toolState });
      } catch {
        completed = true;
        emit({ type: "act_interrupted", last_stop_reason: lastResult?.stats?.stopReason || null,
          tool_state: toolState, cancel_requested: cancelled,
          text_tool_bridge_used: bridgeUsed, bridge_source_content: bridgeSourceContent });
      }
      break;
    }
  } catch (error) {
    const allowed = new Set(["invalid_command", "command_byte_limit", "invalid_contract",
      "model_not_loaded", "invalid_token_shape", "non_loopback_origin", "invalid_workspace_tool_scope"]);
    emit({ type: "error", code: allowed.has(error.message) ? error.message : "tool_transport_error" });
  } finally {
    clearTimeout(deadline);
    if (!completed) cancel();
    if (client) await client[Symbol.asyncDispose]();
    commands.close();
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(() => process.exit(3));
}

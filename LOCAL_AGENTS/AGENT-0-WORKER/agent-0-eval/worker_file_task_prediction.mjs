/** One bounded read/replace WORKER task through the authenticated LM Studio SDK. */
import { LMStudioClient, tool } from "../../../LM-Studio_connections/LM-Studio_for_codex/node_modules/@lmstudio/sdk/dist/index.mjs";
import { z } from "../../../LM-Studio_connections/LM-Studio_for_codex/node_modules/zod/index.js";
import { authenticatedOptions, predictionChat } from "../../../LM-Studio_connections/LM-Studio_for_codex/lm_studio_sdk_prediction.mjs";
import { workerWorkspaceAccess } from "../agent-0-tools/worker_workspace_access.mjs";
import { workerWorkspaceTextTool } from "../agent-0-tools/worker_workspace_text_tool.mjs";
import { workerWorkspaceMutationTool } from "../agent-0-tools/worker_workspace_mutation_tool.mjs";
import { workerWorkspaceCreationTool } from "../agent-0-tools/worker_workspace_creation_tool.mjs";
import { workerWorkspaceValidationTool } from "../agent-0-tools/worker_workspace_validation_tool.mjs";
import { workerSkillReadTool } from "../agent-0-tools/worker_skill_read_tool.mjs";
import { parseGraniteToolCallEnvelope } from "../AG-0-MODEL-Granite_4.1-3B/granite_tool_call_envelope.mjs";
import { lmStudioToolEventCallbacks } from "./lm_studio_tool_event_callbacks.mjs";
import { createInterface } from "node:readline";
import { pathToFileURL } from "node:url";
import { setTimeout as delay } from "node:timers/promises";

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
  let client = null;
  let lastResult = null;
  let lastMessage = "";
  let bridgeCalls = 0;
  const pendingBridgeRequests = [];
  const roundText = new Map();
  let toolRequests = 0;
  let reader = null;
  let writer = null;
  let creator = null;
  let validator = null;
  const toolState = () => ({ read: reader?.state || null, write: writer?.state || null,
    create: creator?.state || null,
    validator: validator?.state || null });
  const cancel = () => {
    cancelled = true;
    allowStart(false);
    if (!abort.signal.aborted) {
      abort.abort();
      emit({ type: "cancel_sent" });
    }
  };
  commands.on("line", line => {
    if (Buffer.byteLength(line) > 65536) return;
    try {
      const command = JSON.parse(line);
      if (command.command === "cancel") cancel();
      if (command.command === "continue") allowStart(true);
      if (command.command === "validation_result") validator?.receive(command.request_id, command.result);
    } catch { /* Main loop owns invalid initial command reporting. */ }
  });
  commands.on("close", () => { if (!completed) cancel(); });
  const deadline = setTimeout(() => process.exit(3), 70000);
  try {
    for await (const line of commands) {
      if (Buffer.byteLength(line) > 65536) throw new Error("command_byte_limit");
      const command = JSON.parse(line);
      if (["cancel", "continue", "validation_result"].includes(command.command)) continue;
      if (command.command !== "start" || command.max_tokens !== 512
          || command.max_rounds !== 6 || command.max_tool_calls !== 6
          || !command.require_start_approval || typeof command.instruction !== "string"
          || Buffer.byteLength(command.instruction, "utf8") > 4096
          || typeof command.system_prompt !== "string"
          || Buffer.byteLength(command.system_prompt, "utf8") > 8192
          || (!Array.isArray(command.allowed_relative_paths) && typeof command.allowed_relative_path !== "string")
          || command.granite_text_tool_bridge && command.model !== "granite-4.1-3b"
          || command.force_text_tool_bridge && (!command.granite_text_tool_bridge
              || command.model !== "granite-4.1-3b")) {
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
      const allowedPaths = command.allowed_relative_paths || [command.allowed_relative_path];
      const access = await workerWorkspaceAccess({ workspaceRoot: command.workspace_root,
        allowedRelativePaths: allowedPaths, maxFileBytes: 65536,
        maxReadCalls: 8, maxTotalReadBytes: 524288,
        maxWriteCalls: 2, maxTotalWriteBytes: 131072, controllerSignal: abort.signal });
      reader = await workerWorkspaceTextTool({ tool, z, access,
        allowedRelativePath: command.allowed_relative_paths ? null : command.allowed_relative_path,
        controllerSignal: abort.signal, record: emit });
      writer = workerWorkspaceMutationTool({ tool, z, access,
        controllerSignal: abort.signal, record: emit,
        diagnosticDelayMs: command.diagnostic_mutation_delay_ms || 0 });
      if (command.allow_create === true) {
        creator = workerWorkspaceCreationTool({ tool, z, access,
          controllerSignal: abort.signal, record: emit });
      }
      const chat = predictionChat(command.system_prompt, command.instruction);
      if (command.diagnostic_request) {
        // Deterministic evaluator dispatch, never a repair of a model tool call.
        const prediction = model.respond(chat, { temperature: 0, maxTokens: 512 });
        const cancelPrediction = () => { void prediction.cancel(); };
        abort.signal.addEventListener("abort", cancelPrediction, { once: true });
        if (abort.signal.aborted) cancelPrediction();
        let mutationError = false;
        const mutation = writer.execute(command.diagnostic_request, { signal: abort.signal })
          .catch(() => { mutationError = true; });
        emit({ type: "evaluator_mutation_dispatched", arguments: command.diagnostic_request });
        for await (const fragment of prediction) {
          emit({ type: "fragment", index: 0, content: fragment.content });
        }
        const result = await prediction;
        await mutation;
        abort.signal.removeEventListener("abort", cancelPrediction);
        completed = true;
        emit({ type: "result", content: result.content, stats: result.stats,
          model_info: result.modelInfo, load_config: result.loadConfig,
          prediction_config: result.predictionConfig, tool_state: toolState(),
          evaluator_dispatch: true, mutation_error: mutationError });
        break;
      }
      validator = workerWorkspaceValidationTool({ tool, z, controllerSignal: abort.signal, record: emit });
      const enabled = new Set(command.enabled_tools ||
        ["read_workspace_text", "replace_workspace_text", "validate_workspace_workflow"]);
      const knownTools = new Set(["read_workspace_text", "replace_workspace_text",
        "validate_workspace_workflow", "create_workspace_text"]);
      if (!enabled.size || [...enabled].some(name => !knownTools.has(name))
          || enabled.has("create_workspace_text") !== Boolean(creator)) {
        throw new Error("invalid_contract");
      }
      const definitions = [];
      if (enabled.has("read_workspace_text")) definitions.push(reader.definition);
      if (enabled.has("replace_workspace_text")) definitions.push(writer.definition);
      if (enabled.has("validate_workspace_workflow")) definitions.push(validator.definition);
      if (creator && enabled.has("create_workspace_text")) definitions.push(creator.definition);
      if (command.skill_mode === "discovery") {
        definitions.push(workerSkillReadTool({ tool, z, skills: command.skills,
          controllerSignal: abort.signal, record: emit }));
      }
      const options = {
        temperature: 0, maxTokens: 512, maxPredictionRounds: 6,
        allowParallelToolExecution: false, signal: abort.signal,
        onRoundStart(index) { emit({ type: "round_started", index }); },
        onRoundEnd(index) { emit({ type: "round_ended", index }); },
        onPredictionFragment(fragment) {
          roundText.set(fragment.roundIndex,
            (roundText.get(fragment.roundIndex) || "") + fragment.content);
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
        ...lmStudioToolEventCallbacks(emit),
        guardToolCall(index, callId, { toolCallRequest, allow, deny }) {
          toolRequests++;
          if (command.granite_text_tool_bridge) {
            const preserved = parseGraniteToolCallEnvelope(roundText.get(index) || "");
            if (preserved && preserved.name !== toolCallRequest.name) {
              pendingBridgeRequests.push(preserved);
              emit({ type: "native_tool_name_mismatch", index, call_id: callId,
                native_name: toolCallRequest.name, preserved_name: preserved.name });
              emit({ type: "tool_request_guarded", index, call_id: callId,
                name: toolCallRequest.name, decision: "denied_name_mismatch" });
              deny("Native tool name did not match the preserved Granite envelope.");
              return;
            }
          }
          if (abort.signal.aborted || toolRequests > 6
              || ![...enabled,
                ...(command.skill_mode === "discovery" ? ["read_worker_skill"] : [])].includes(toolCallRequest.name)) {
            emit({ type: "tool_guard_denied", index, call_id: callId });
            emit({ type: "tool_request_guarded", index, call_id: callId,
              name: toolCallRequest.name, decision: "denied_scope_or_budget" });
            deny("Tool unavailable or call budget exhausted.");
          } else {
            emit({ type: "tool_request_guarded", index, call_id: callId,
              name: toolCallRequest.name, decision: "allowed" });
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
        const began = performance.now();
        if (command.force_text_tool_bridge) {
          let rounds = 0;
          const toolsByName = new Map([
            ["read_workspace_text", reader], ["replace_workspace_text", writer],
            ["create_workspace_text", creator],
          ]);
          while (!abort.signal.aborted && rounds < 6) {
            emit({ type: "round_started", index: rounds });
            const prediction = model.respond(chat, { temperature: 0, maxTokens: 512,
              signal: abort.signal });
            for await (const fragment of prediction) {
              emit({ type: "fragment", index: rounds, content: fragment.content });
            }
            lastResult = await prediction;
            lastMessage = lastResult.content;
            emit({ type: "round_result", index: rounds, stats: lastResult.stats,
              content: lastResult.content });
            rounds++;
            const request = parseGraniteToolCallEnvelope(lastMessage);
            if (!request) break;
            emit({ type: "adapter_tool_request_parsed", index: rounds - 1,
              call_id: bridgeCalls + 1, name: request.name, arguments: request.arguments,
              raw_content: lastMessage });
            const selected = toolsByName.get(request.name);
            if (!selected || !enabled.has(request.name) || toolRequests >= 6) {
              emit({ type: "text_tool_bridge_denied", name: request.name });
              break;
            }
            toolRequests++;
            bridgeCalls++;
            emit({ type: "text_tool_bridge_request", name: request.name,
              arguments: request.arguments });
            const content = await selected.execute(request.arguments, { signal: abort.signal,
              callId: bridgeCalls, dispatchOrigin: "model_specific_adapter" });
            chat.append({ role: "assistant", content: [{ type: "toolCallRequest",
              toolCallRequest: { type: "function", name: request.name,
                arguments: request.arguments } }] });
            chat.append({ role: "tool", content: [{ type: "toolCallResult", content }] });
            emit({ type: "text_tool_bridge_followup_started", bridge_calls: bridgeCalls });
          }
          completed = true;
          emit({ type: "result", content: lastMessage, stats: lastResult?.stats || null,
            model_info: lastResult?.modelInfo || info, load_config: lastResult?.loadConfig || null,
            prediction_config: lastResult?.predictionConfig || null, rounds,
            tool_requests: toolRequests, total_execution_seconds: (performance.now() - began) / 1000,
            text_tool_bridge_calls: bridgeCalls, tool_state: toolState() });
          break;
        }
        const outcome = await model.act(chat, definitions, options);
        while (command.granite_text_tool_bridge && bridgeCalls < 4
            && outcome.rounds + bridgeCalls < 6 && !abort.signal.aborted
            && lastResult?.stats?.stopReason === "eosFound") {
          const preservedRequest = pendingBridgeRequests.shift() || null;
          const request = preservedRequest
            || parseGraniteToolCallEnvelope(lastMessage || lastResult.content);
          if (!request || toolRequests >= 6) break;
          if (!preservedRequest) toolRequests++;
          bridgeCalls++;
          emit({ type: "adapter_tool_request_parsed", index: outcome.rounds + bridgeCalls - 1,
            call_id: bridgeCalls, name: request.name, arguments: request.arguments,
            raw_content: lastMessage || lastResult.content });
          emit({ type: "text_tool_bridge_request", name: request.name,
            arguments: request.arguments });
          const selected = request.name === "read_workspace_text" ? reader
            : request.name === "create_workspace_text" ? creator : writer;
          if (!selected || !enabled.has(request.name)) break;
          const content = await selected.execute(request.arguments, { signal: abort.signal,
            callId: bridgeCalls, dispatchOrigin: "model_specific_adapter" });
          abort.signal.throwIfAborted();
          chat.append({ role: "assistant", content: [{ type: "toolCallRequest",
            toolCallRequest: { type: "function", name: request.name,
              arguments: request.arguments } }] });
          chat.append({ role: "tool", content: [{ type: "toolCallResult", content }] });
          emit({ type: "text_tool_bridge_followup_started", bridge_calls: bridgeCalls });
          const followup = model.respond(chat, { temperature: 0, maxTokens: 512,
            signal: abort.signal });
          for await (const fragment of followup) {
            emit({ type: "fragment", index: outcome.rounds + bridgeCalls, content: fragment.content });
          }
          lastResult = await followup;
          lastMessage = lastResult.content;
          emit({ type: "bridge_followup_result", stats: lastResult.stats,
            content: lastResult.content });
        }
        completed = true;
        emit({ type: "result", content: lastMessage || lastResult?.content || "",
          stats: lastResult?.stats || null, model_info: lastResult?.modelInfo || info,
          load_config: lastResult?.loadConfig || null,
          prediction_config: lastResult?.predictionConfig || null,
          rounds: outcome.rounds + bridgeCalls, tool_requests: toolRequests,
          total_execution_seconds: (performance.now() - began) / 1000,
          text_tool_bridge_calls: bridgeCalls, tool_state: toolState() });
      } catch {
        // Do not claim tool stop while any callback is still active.
        const until = performance.now() + 5000;
        while ((reader.state.active || writer.state.active || creator?.state.active || validator.state.active) && performance.now() < until) {
          await delay(10);
        }
        completed = true;
        if (lastResult?.stats?.stopReason === "userStopped") {
          emit({ type: "result", content: lastResult.content, stats: lastResult.stats,
            model_info: lastResult.modelInfo, load_config: lastResult.loadConfig,
            prediction_config: lastResult.predictionConfig, tool_state: toolState(),
            text_tool_bridge_calls: bridgeCalls });
        } else {
          emit({ type: "act_interrupted", last_stop_reason: lastResult?.stats?.stopReason || null,
            tool_state: toolState(), cancel_requested: cancelled,
            text_tool_bridge_calls: bridgeCalls });
        }
      }
      break;
    }
  } catch (error) {
    const allowed = new Set(["invalid_contract", "command_byte_limit", "model_not_loaded",
      "invalid_token_shape", "non_loopback_origin", "invalid_workspace_tool_scope"]);
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

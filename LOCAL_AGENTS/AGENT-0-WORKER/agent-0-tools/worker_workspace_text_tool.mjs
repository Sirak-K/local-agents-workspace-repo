/** One bounded, read-only WORKER file tool scoped to an evaluator-created fixture. */
import { setTimeout as delay } from "node:timers/promises";
import { workerWorkspaceAccess } from "./worker_workspace_access.mjs";

export async function workerWorkspaceTextTool({ tool, z, workspaceRoot, allowedRelativePath,
    controllerSignal, diagnosticDelayMs = 0, record, access = null }) {
  if (!Number.isInteger(diagnosticDelayMs) || diagnosticDelayMs < 0 || diagnosticDelayMs > 3000) {
    throw new Error("invalid_workspace_tool_scope");
  }
  const policy = access || await workerWorkspaceAccess({ workspaceRoot,
    allowedRelativePaths: [allowedRelativePath], controllerSignal });
  const state = { active: 0, completed: 0, aborted: 0, denied: 0 };
  const execute = async ({ path }, context) => {
      const trace = { call_id: Number.isInteger(context?.callId) ? context.callId : null,
        dispatch_origin: context?.dispatchOrigin || "native_sdk", name: "read_workspace_text" };
      record({ type: "tool_handler_entered", ...trace, path: String(path).slice(0, 120) });
      if (controllerSignal.aborted || context?.signal?.aborted) {
        state.denied++;
        record({ type: "tool_handler_receipt", ...trace, status: "denied" });
        throw new Error("tool_dispatch_after_stop_denied");
      }
      if ((allowedRelativePath && path !== allowedRelativePath) || !policy.isAllowed(path)) {
        state.denied++;
        record({ type: "tool_denied", path: String(path).slice(0, 120) });
        record({ type: "tool_handler_receipt", ...trace, status: "denied" });
        return "Error: requested path is unavailable in this workspace.";
      }
      const signal = AbortSignal.any([controllerSignal, context.signal]);
      state.active++;
      record({ type: "tool_started", path });
      try {
        if (diagnosticDelayMs) await delay(diagnosticDelayMs, undefined, { signal });
        signal.throwIfAborted();
        const { text, sha256 } = await policy.readBytes(path, signal);
        state.completed++;
        record({ type: "tool_completed", path, content: text, sha256 });
        record({ type: "tool_handler_receipt", ...trace, status: "completed", sha256 });
        return text;
      } catch (error) {
        if (signal.aborted) {
          state.aborted++;
          record({ type: "tool_aborted", path });
          record({ type: "tool_handler_receipt", ...trace, status: "aborted" });
        } else {
          record({ type: "tool_failed", path, code: "workspace_read_error" });
          record({ type: "tool_handler_receipt", ...trace, status: "failed" });
        }
        throw error;
      } finally {
        state.active--;
      }
    };
  const definition = tool({
    name: "read_workspace_text",
    description: "Read a small UTF-8 text file at a relative path inside the provided workspace. Use it when the requested answer depends on file contents.",
    parameters: { path: z.string() },
    implementation: execute,
  });
  return { definition, state, execute };
}

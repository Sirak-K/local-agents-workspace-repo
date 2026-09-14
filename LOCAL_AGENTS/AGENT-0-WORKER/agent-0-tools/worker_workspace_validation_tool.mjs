/** Fixed validator bridge: no shell, arbitrary commands or candidate code. */
export function workerWorkspaceValidationTool({ tool, z, controllerSignal, record }) {
  const state = { active: 0, completed: 0, aborted: 0 };
  let counter = 0;
  const pending = new Map();
  const execute = async ({ path }, context) => {
    const trace = { call_id: Number.isInteger(context?.callId) ? context.callId : null,
      dispatch_origin: context?.dispatchOrigin || "native_sdk", name: "validate_workspace_workflow" };
    record({ type: "tool_handler_entered", ...trace, path: String(path).slice(0, 120) });
    const signal = AbortSignal.any([controllerSignal, context.signal]);
    if (signal.aborted) {
      record({ type: "tool_handler_receipt", ...trace, status: "denied" });
      signal.throwIfAborted();
    }
    if (path !== "workflow.json" || counter >= 2 || state.active) {
      record({ type: "tool_handler_receipt", ...trace, status: "denied" });
      throw new Error("validator_scope_or_budget_denied");
    }
    const requestId = String(++counter);
    state.active++;
    try {
      return await new Promise((resolve, reject) => {
        const onAbort = () => {
          pending.delete(requestId);
          state.aborted++;
          record({ type: "tool_handler_receipt", ...trace, status: "aborted" });
          reject(new Error("validator_aborted"));
        };
        pending.set(requestId, result => {
          signal.removeEventListener("abort", onAbort);
          pending.delete(requestId);
          state.completed++;
          record({ type: "tool_handler_receipt", ...trace, status: "completed",
            validation_status: result?.status || null });
          resolve(JSON.stringify(result));
        });
        signal.addEventListener("abort", onAbort, { once: true });
        record({ type: "tool_validation_requested", request_id: requestId, path });
      });
    } finally {
      state.active--;
    }
  };
  return { state, execute, receive: (requestId, result) => pending.get(requestId)?.(result),
    definition: tool({ name: "validate_workspace_workflow",
      description: "Run the fixed static JSON/schema/graph checker on workflow.json. This never starts ComfyUI or generates media; report the actual validation result, including failures.",
      parameters: { path: z.string() }, implementation: execute }) };
}

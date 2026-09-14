/** Read only evaluator-approved skill contents; no filesystem path parameter. */
export function workerSkillReadTool({ tool, z, skills, controllerSignal, record }) {
  if (!Array.isArray(skills) || skills.length < 2 || skills.length > 3) throw new Error("invalid_skill_scope");
  const sources = new Map(skills.map(item => [item.id, item]));
  let calls = 0;
  return tool({ name: "read_worker_skill", description: "Retrieve one named WORKER skill from the supplied catalog. No other files are accessible.",
    parameters: { id: z.string() }, implementation: async ({ id }, context) => {
      const trace = { call_id: Number.isInteger(context?.callId) ? context.callId : null,
        dispatch_origin: context?.dispatchOrigin || "native_sdk", name: "read_worker_skill" };
      record({ type: "tool_handler_entered", ...trace, skill_id: String(id).slice(0, 120) });
      if (controllerSignal.aborted || context.signal.aborted) {
        record({ type: "tool_handler_receipt", ...trace, status: "denied" });
        context.signal.throwIfAborted();
        controllerSignal.throwIfAborted();
      }
      const source = sources.get(id);
      if (++calls > 2 || !source) {
        record({ type: "tool_handler_receipt", ...trace, status: "denied" });
        throw new Error("skill_scope_or_budget_denied");
      }
      record({ type: "skill_loaded", id, sha256: source.sha256 });
      record({ type: "tool_handler_receipt", ...trace, status: "completed",
        sha256: source.sha256 });
      return source.content;
    } });
}

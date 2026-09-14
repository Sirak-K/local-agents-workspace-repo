import test from "node:test";
import assert from "node:assert/strict";
import { workerWorkspaceValidationTool } from "../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-tools/worker_workspace_validation_tool.mjs";

test("fixed validation waits for a matching receipt and abort drains the pending callback", async () => {
  const controller = new AbortController();
  const events = [];
  const validator = workerWorkspaceValidationTool({ tool: value => value,
    z: { string: () => ({}) }, controllerSignal: controller.signal, record: value => events.push(value) });
  const context = { signal: controller.signal };
  await assert.rejects(validator.execute({ path: "../original.json" }, context), /scope/);
  const first = validator.execute({ path: "workflow.json" }, context);
  assert.equal(validator.state.active, 1);
  assert.equal(events.find(event => event.type === "tool_validation_requested").request_id, "1");
  validator.receive("unknown", { status: "pass" });
  assert.equal(validator.state.active, 1);
  validator.receive("1", { status: "fail", exit_status: 1 });
  assert.equal(JSON.parse(await first).exit_status, 1);
  const second = validator.execute({ path: "workflow.json" }, context);
  controller.abort();
  await assert.rejects(second, /aborted/);
  assert.equal(validator.state.active, 0);
  assert.equal(validator.state.aborted, 1);
  validator.receive("2", { status: "pass" });
  assert.equal(validator.state.completed, 1);
  assert.deepEqual(events.filter(event => event.type === "tool_handler_receipt")
    .map(event => event.status), ["denied", "completed", "aborted"]);
});

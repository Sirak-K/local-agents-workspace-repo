import test from "node:test";
import assert from "node:assert/strict";
import { workerSkillReadTool } from "../../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-tools/worker_skill_read_tool.mjs";

test("skill retrieval exposes only approved content and records the actual source hash", async () => {
  const controller = new AbortController();
  const events = [];
  const skills = [
    { id: "title", content: "title procedure", sha256: "a".repeat(64) },
    { id: "graph", content: "graph procedure", sha256: "b".repeat(64) },
  ];
  const definition = workerSkillReadTool({
    tool: (value) => value,
    z: { string: () => ({}) },
    skills,
    controllerSignal: controller.signal,
    record: (value) => events.push(value),
  });
  const context = { signal: controller.signal };
  assert.equal(
    await definition.implementation({ id: "title" }, context),
    "title procedure",
  );
  assert.deepEqual(
    events.find((event) => event.type === "skill_loaded"),
    { type: "skill_loaded", id: "title", sha256: "a".repeat(64) },
  );
  assert.equal(
    events.find((event) => event.type === "tool_handler_receipt").status,
    "completed",
  );
  await assert.rejects(
    definition.implementation({ id: "../secret" }, context),
    /scope/,
  );
  await assert.rejects(
    definition.implementation({ id: "graph" }, context),
    /budget/,
  );
  controller.abort();
  await assert.rejects(definition.implementation({ id: "title" }, context));
});

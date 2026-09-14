import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { parseGraniteToolCallEnvelope } from "../LOCAL_AGENTS/AGENT-0-WORKER/AG-0-MODEL-Granite_4.1-3B/granite_tool_call_envelope.mjs";
import { workerWorkspaceTextTool } from "../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-tools/worker_workspace_text_tool.mjs";

const accepted = '<tool_call>{"name":"read_workspace_text","arguments":{"path":"project/config/service.json"}}\n</tool_call>';

test("Granite envelope parser accepts the documented one-call shape, not repairs", () => {
  assert.deepEqual(parseGraniteToolCallEnvelope(accepted), {
    name: "read_workspace_text", arguments: { path: "project/config/service.json" },
  });
  assert.equal(parseGraniteToolCallEnvelope(accepted.replace("</tool_call>", "")), null);
  assert.equal(parseGraniteToolCallEnvelope('{"name":"read_workspace_text","arguments":{"path":"project/config/service.json"}}}'), null);
  assert.equal(parseGraniteToolCallEnvelope(accepted.replace("read_workspace_text", "write_file")), null);
  assert.deepEqual(parseGraniteToolCallEnvelope('<tool_call>{"name":"replace_workspace_text","arguments":{"path":"workflow.json","expected_sha256":"' + 'a'.repeat(64) + '","old_text":"old","new_text":"new"}}</tool_call>'), {
    name: "replace_workspace_text", arguments: { path: "workflow.json",
      expected_sha256: "a".repeat(64), old_text: "old", new_text: "new" },
  });
  assert.equal(parseGraniteToolCallEnvelope('<tool_call>{"name":"replace_workspace_text","arguments":{"path":"workflow.json"}}</tool_call>'), null);
  assert.deepEqual(parseGraniteToolCallEnvelope('<tool_call>{"name":"create_workspace_text","arguments":{"path":"result.txt","content":"OK\\n"}}</tool_call>'), {
    name: "create_workspace_text", arguments: { path: "result.txt", content: "OK\n" },
  });
  assert.equal(parseGraniteToolCallEnvelope('<tool_call>{"name":"create_workspace_text","arguments":{"path":"result.txt"}}</tool_call>'), null);
});

test("workspace reader enforces the one-file boundary and aborts in-flight work", async () => {
  const root = await mkdtemp(join(tmpdir(), "worker-tool-"));
  try {
    await mkdir(join(root, "project", "config"), { recursive: true });
    await writeFile(join(root, "project", "config", "service.json"), '{"queue_name":"q"}', "utf8");
    const abort = new AbortController();
    const events = [];
    const reader = await workerWorkspaceTextTool({
      tool: config => config, z: { string: () => ({}) }, workspaceRoot: root,
      allowedRelativePath: "project/config/service.json",
      controllerSignal: abort.signal, diagnosticDelayMs: 3000,
      record: event => events.push(event),
    });
    const context = { signal: abort.signal };
    assert.match(await reader.execute({ path: "project/config/other.json" }, context), /unavailable/);
    assert.equal(reader.state.denied, 1);
    const pending = reader.execute({ path: "project/config/service.json" }, context);
    await new Promise(resolve => setTimeout(resolve, 25));
    assert.equal(reader.state.active, 1);
    abort.abort();
    await assert.rejects(pending);
    assert.equal(reader.state.active, 0);
    assert.equal(reader.state.aborted, 1);
    assert.equal(reader.state.completed, 0);
    assert.deepEqual(events.filter(event => event.type.startsWith("tool_")).map(event => event.type),
      ["tool_handler_entered", "tool_denied", "tool_handler_receipt",
        "tool_handler_entered", "tool_started", "tool_aborted", "tool_handler_receipt"]);
    assert.deepEqual(events.filter(event => event.type === "tool_handler_receipt")
      .map(event => event.status), ["denied", "aborted"]);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { lmStudioToolEventCallbacks } from "../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/lm_studio_tool_event_callbacks.mjs";

test("public callback chain preserves raw tool evidence, queueing and call correlation", () => {
  const events = [];
  const hooks = lmStudioToolEventCallbacks(event => events.push(event));
  const raw = '<tool_call>{"name":"read_workspace_text","arguments":{"path":"fixture.txt"}}</tool_call>';
  const request = { name: "read_workspace_text", arguments: { path: "fixture.txt" } };
  hooks.onToolCallRequestStart(0, 7, { toolCallId: "native-id" });
  hooks.onToolCallRequestNameReceived(0, 7, request.name);
  hooks.onToolCallRequestArgumentFragmentGenerated(0, 7, '{"path":"fixture.txt"}');
  hooks.onToolCallRequestEnd(0, 7, { toolCallRequest: request, isQueued: true, rawContent: raw });
  hooks.onToolCallRequestDequeued(0, 7);
  hooks.onToolCallRequestFinalized(0, 7, { toolCallRequest: request, rawContent: raw });
  assert.deepEqual(events.map(event => event.type), ["tool_request_started", "tool_request_name_received",
    "tool_request_argument_fragment", "tool_request_parsed", "tool_request_dequeued", "tool_request_finalized"]);
  assert.ok(events.every(event => event.call_id === 7 && event.index === 0));
  assert.equal(events[3].raw_content, raw);
  assert.equal(events[3].raw_content_sha256, createHash("sha256").update(raw).digest("hex"));
  assert.equal(events[3].is_queued, true);
});

test("failure and oversized raw evidence never become a fabricated parsed request", () => {
  const events = [];
  const hooks = lmStudioToolEventCallbacks(event => events.push(event));
  const error = new Error("cannot parse request");
  error.rawContent = "x".repeat(17000);
  hooks.onToolCallRequestFailure(1, 3, error);
  assert.equal(events[0].type, "tool_request_failed");
  assert.equal(events[0].raw_content, null);
  assert.equal(events[0].raw_content_sha256, createHash("sha256").update(error.rawContent).digest("hex"));
  assert.equal(events[0].name, undefined);
});

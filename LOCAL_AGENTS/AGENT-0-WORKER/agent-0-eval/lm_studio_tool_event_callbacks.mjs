/** Normalize every public granular lmstudio-js 1.5.0 .act() tool callback. */
import { createHash } from "node:crypto";

function rawEvidence(rawContent) {
  if (typeof rawContent !== "string") {
    return { raw_content: null, raw_content_sha256: null };
  }
  const bytes = Buffer.byteLength(rawContent, "utf8");
  return {
    raw_content: bytes <= 16384 ? rawContent : null,
    raw_content_sha256: createHash("sha256").update(rawContent, "utf8").digest("hex"),
  };
}

export function lmStudioToolEventCallbacks(record) {
  if (typeof record !== "function") throw new TypeError("record callback required");
  return {
    onToolCallRequestStart(index, callId, info) {
      record({ type: "tool_request_started", index, call_id: callId,
        tool_call_id: info?.toolCallId || null });
    },
    onToolCallRequestNameReceived(index, callId, name) {
      record({ type: "tool_request_name_received", index, call_id: callId, name });
    },
    onToolCallRequestArgumentFragmentGenerated(index, callId, content) {
      record({ type: "tool_request_argument_fragment", index, call_id: callId, content });
    },
    onToolCallRequestEnd(index, callId, info) {
      record({ type: "tool_request_parsed", index, call_id: callId,
        name: info.toolCallRequest.name, arguments: info.toolCallRequest.arguments,
        is_queued: info.isQueued, ...rawEvidence(info.rawContent) });
    },
    onToolCallRequestFinalized(index, callId, info) {
      record({ type: "tool_request_finalized", index, call_id: callId,
        name: info.toolCallRequest.name, arguments: info.toolCallRequest.arguments,
        ...rawEvidence(info.rawContent) });
    },
    onToolCallRequestFailure(index, callId, error) {
      record({ type: "tool_request_failed", index, call_id: callId,
        error_name: error?.name || "Error", error_message: error?.message || "tool request failed",
        ...rawEvidence(error?.rawContent) });
    },
    onToolCallRequestDequeued(index, callId) {
      record({ type: "tool_request_dequeued", index, call_id: callId });
    },
  };
}

/** Parse only IBM Granite's documented, single-call XML envelope. No repair or guessing. */
export function parseGraniteToolCallEnvelope(content) {
  if (typeof content !== "string" || Buffer.byteLength(content, "utf8") > 1024) return null;
  const match = /^\s*<tool_call>\s*(\{[^<>]*\})\s*<\/tool_call>\s*$/.exec(content);
  if (!match) return null;
  let request;
  try { request = JSON.parse(match[1]); } catch { return null; }
  if (!request || typeof request !== "object" || Array.isArray(request)
      || Object.keys(request).sort().join(",") !== "arguments,name"
      || request.name !== "read_workspace_text"
      || !request.arguments || typeof request.arguments !== "object"
      || Array.isArray(request.arguments)
      || Object.keys(request.arguments).join(",") !== "path"
      || typeof request.arguments.path !== "string") return null;
  return request;
}

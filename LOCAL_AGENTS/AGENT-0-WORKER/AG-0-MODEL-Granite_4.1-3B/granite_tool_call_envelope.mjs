/** Parse only IBM Granite's documented, single-call XML envelope. No repair or guessing. */
export function parseGraniteToolCallEnvelope(content) {
  if (typeof content !== "string" || Buffer.byteLength(content, "utf8") > 1024) return null;
  const match = /^\s*<tool_call>\s*(\{[^<>]*\})\s*<\/tool_call>\s*$/.exec(content);
  if (!match) return null;
  let request;
  try { request = JSON.parse(match[1]); } catch { return null; }
  if (!request || typeof request !== "object" || Array.isArray(request)
      || Object.keys(request).sort().join(",") !== "arguments,name"
      || !request.arguments || typeof request.arguments !== "object"
      || Array.isArray(request.arguments)) return null;
  if (request.name === "read_workspace_text") {
    if (Object.keys(request.arguments).join(",") !== "path"
        || typeof request.arguments.path !== "string") return null;
  } else if (request.name === "replace_workspace_text") {
    if (Object.keys(request.arguments).sort().join(",") !== "expected_sha256,new_text,old_text,path"
        || Object.values(request.arguments).some(value => typeof value !== "string")) return null;
  } else if (request.name === "create_workspace_text") {
    if (Object.keys(request.arguments).sort().join(",") !== "content,path"
        || typeof request.arguments.path !== "string"
        || typeof request.arguments.content !== "string") return null;
  } else return null;
  return request;
}

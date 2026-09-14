/** Create one new bounded UTF-8 workspace file and independently read it back. */
import { link, open, unlink } from "node:fs/promises";
import { dirname, join } from "node:path";
import { randomUUID } from "node:crypto";

export function workerWorkspaceCreationTool({ tool, z, access, controllerSignal, record }) {
  if (!access || !controllerSignal) throw new Error("invalid_workspace_creation_scope");
  const state = { active: 0, completed: 0, committed: 0, aborted: 0, denied: 0 };
  const execute = async ({ path, content }, context) => {
    const trace = { call_id: Number.isInteger(context?.callId) ? context.callId : null,
      dispatch_origin: context?.dispatchOrigin || "native_sdk", name: "create_workspace_text" };
    record({ type: "tool_handler_entered", ...trace, path: String(path).slice(0, 120) });
    const signal = AbortSignal.any([controllerSignal, context.signal]);
    if (signal.aborted) {
      record({ type: "tool_handler_receipt", ...trace, status: "denied" });
      throw new Error("tool_dispatch_after_stop_denied");
    }
    if (!access.isAllowed(path) || typeof content !== "string" || !content.length
        || content.includes("\ufeff") || Buffer.byteLength(content, "utf8") > 4096) {
      state.denied++;
      record({ type: "tool_creation_denied", path: String(path).slice(0, 120) });
      record({ type: "tool_handler_receipt", ...trace, status: "denied" });
      return "Error: create request is unavailable or invalid.";
    }
    const bytes = Buffer.from(content, "utf8");
    let temporary = null;
    let reserved = false;
    let committed = false;
    state.active++;
    try {
      const target = await access.checkedCreationPath(path, signal);
      access.reserveWrite(bytes.length, signal);
      reserved = true;
      temporary = join(dirname(target), `.worker-create-${randomUUID()}.tmp`);
      const handle = await open(temporary, "wx");
      try {
        let offset = 0;
        while (offset < bytes.length) {
          signal.throwIfAborted();
          const { bytesWritten } = await handle.write(bytes, offset, bytes.length - offset, offset);
          if (!bytesWritten) throw new Error("workspace_temp_write_failed");
          offset += bytesWritten;
        }
        await handle.sync();
      } finally {
        await handle.close();
      }
      signal.throwIfAborted();
      await access.checkedCreationPath(path, signal);
      await link(temporary, target);
      committed = true;
      state.committed++;
      await unlink(temporary);
      temporary = null;
      record({ type: "tool_creation_committed", path, after_sha256: access.sha256(bytes) });
      const actual = await access.readBytes(path);
      if (!actual.bytes.equals(bytes)) throw new Error("workspace_readback_mismatch");
      state.completed++;
      record({ type: "tool_creation_completed", path, after_sha256: actual.sha256,
        output_bytes: actual.bytes.length });
      record({ type: "tool_handler_receipt", ...trace, status: "completed",
        after_sha256: actual.sha256 });
      return JSON.stringify({ path, after_sha256: actual.sha256, output_bytes: actual.bytes.length });
    } catch (error) {
      if (signal.aborted && !committed) {
        state.aborted++;
        record({ type: "tool_creation_aborted_before_commit", path });
        record({ type: "tool_handler_receipt", ...trace, status: "aborted" });
      } else {
        if (!committed) state.denied++;
        record({ type: committed ? "tool_creation_readback_failed" : "tool_creation_failed",
          path, code: error.message === "workspace_create_target_exists" ? "target_exists" : "creation_error" });
        record({ type: "tool_handler_receipt", ...trace, status: "failed",
          committed });
      }
      throw error;
    } finally {
      if (temporary) await unlink(temporary).catch(() => {});
      if (reserved) access.finishWrite(committed);
      state.active--;
    }
  };
  const definition = tool({
    name: "create_workspace_text",
    description: "Create one new small UTF-8 text file at an allowed relative workspace path. It fails if the target already exists and verifies the exact bytes by readback.",
    parameters: { path: z.string(), content: z.string() },
    implementation: execute,
  });
  return { definition, state, execute };
}

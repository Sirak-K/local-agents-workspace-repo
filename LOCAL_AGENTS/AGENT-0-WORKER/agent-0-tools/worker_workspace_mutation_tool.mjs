/** Hash-conditional, bounded, single-replacement mutation of an allowed text fixture. */
import { randomUUID } from "node:crypto";
import { open, rename, unlink } from "node:fs/promises";
import { dirname, join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";

const SHA256 = /^[0-9a-f]{64}$/;

export function workerWorkspaceMutationTool({ tool, z, access, controllerSignal,
    record, diagnosticDelayMs = 0 }) {
  if (!access || !controllerSignal || !Number.isInteger(diagnosticDelayMs)
      || diagnosticDelayMs < 0 || diagnosticDelayMs > 3000) {
    throw new Error("invalid_workspace_mutation_scope");
  }
  const state = { active: 0, completed: 0, committed: 0, aborted: 0, denied: 0 };
  const execute = async ({ path, expected_sha256, old_text, new_text }, context) => {
    const trace = { call_id: Number.isInteger(context?.callId) ? context.callId : null,
      dispatch_origin: context?.dispatchOrigin || "native_sdk", name: "replace_workspace_text" };
    record({ type: "tool_handler_entered", ...trace, path: String(path).slice(0, 120) });
    const signal = AbortSignal.any([controllerSignal, context.signal]);
    if (signal.aborted) {
      record({ type: "tool_handler_receipt", ...trace, status: "denied" });
      throw new Error("tool_dispatch_after_stop_denied");
    }
    if (!access.isAllowed(path) || !SHA256.test(expected_sha256)
        || typeof old_text !== "string" || !old_text.length
        || typeof new_text !== "string" || old_text === new_text
        || old_text.includes("\ufeff") || new_text.includes("\ufeff")
        || Buffer.byteLength(old_text, "utf8") > 4096
        || Buffer.byteLength(new_text, "utf8") > 4096) {
      state.denied++;
      record({ type: "tool_mutation_denied", code: "invalid_request" });
      record({ type: "tool_handler_receipt", ...trace, status: "denied" });
      return "Error: mutation request is unavailable or invalid.";
    }
    let reserved = false;
    let committed = false;
    let temporary = null;
    state.active++;
    try {
      const current = await access.readBytes(path, signal);
      if (current.sha256 !== expected_sha256) throw new Error("workspace_hash_mismatch");
      const first = current.text.indexOf(old_text);
      if (first < 0 || current.text.indexOf(old_text, first + old_text.length) >= 0) {
        throw new Error("workspace_match_not_unique");
      }
      const updated = current.text.slice(0, first) + new_text
        + current.text.slice(first + old_text.length);
      const bytes = Buffer.from(updated, "utf8");
      access.reserveWrite(bytes.length, signal);
      reserved = true;
      const target = await access.checkedPath(path, signal);
      record({ type: "tool_mutation_started", path, before_sha256: current.sha256,
        output_bytes: bytes.length });
      temporary = join(dirname(target), `.worker-mutation-${randomUUID()}.tmp`);
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
      if (diagnosticDelayMs) await delay(diagnosticDelayMs, undefined, { signal });
      signal.throwIfAborted();
      await access.checkedPath(path, signal);
      const beforeCommit = await access.readBytes(path, signal);
      if (beforeCommit.sha256 !== expected_sha256) throw new Error("workspace_hash_changed_before_commit");
      signal.throwIfAborted();
      await rename(temporary, target);
      committed = true;
      temporary = null;
      state.committed++;
      record({ type: "tool_mutation_committed", path,
        before_sha256: expected_sha256, expected_after_sha256: access.sha256(bytes) });
      // After the commit point, finish a bounded independent readback even if stop arrives.
      const verifyHandle = await open(target, "r");
      let actual;
      try {
        const probe = Buffer.alloc(bytes.length + 1);
        let offset = 0;
        while (offset < probe.length) {
          const { bytesRead } = await verifyHandle.read(probe, offset, probe.length - offset, offset);
          if (!bytesRead) break;
          offset += bytesRead;
        }
        actual = probe.subarray(0, offset);
      } finally {
        await verifyHandle.close();
      }
      if (!actual.equals(bytes)) throw new Error("workspace_readback_mismatch");
      state.completed++;
      record({ type: "tool_mutation_completed", path, after_sha256: access.sha256(actual),
        output_bytes: actual.length });
      record({ type: "tool_handler_receipt", ...trace, status: "completed",
        after_sha256: access.sha256(actual) });
      return JSON.stringify({ path, before_sha256: expected_sha256,
        after_sha256: access.sha256(actual), output_bytes: actual.length });
    } catch (error) {
      if (signal.aborted && !committed) {
        state.aborted++;
        record({ type: "tool_mutation_aborted_before_commit", path });
        record({ type: "tool_handler_receipt", ...trace, status: "aborted" });
      } else {
        if (!committed) state.denied++;
        record({ type: committed ? "tool_mutation_readback_failed" : "tool_mutation_failed",
          path, code: error.message === "workspace_hash_mismatch" ? "hash_mismatch" : "mutation_error" });
        record({ type: "tool_handler_receipt", ...trace, status: "failed",
          committed });
      }
      if (!committed && !signal.aborted) {
        const feedback = {
          workspace_hash_mismatch: "Error: hash_mismatch. Read the allowed file again and use its current SHA-256.",
          workspace_match_not_unique: "Error: target text is absent or not unique. Read the allowed file and choose one unique exact fragment.",
          workspace_write_budget_exhausted: "Error: write budget exhausted. Stop mutations and report the partial file state.",
        }[error.message];
        if (feedback) return feedback;
      }
      throw error;
    } finally {
      if (temporary) await unlink(temporary).catch(() => {});
      if (reserved) access.finishWrite(committed);
      state.active--;
    }
  };
  const definition = tool({
    name: "replace_workspace_text",
    description: "Replace exactly one literal text occurrence in an allowed workspace file, only if its current SHA-256 matches expected_sha256. Never send the whole file to rewrite one value.",
    parameters: { path: z.string(), expected_sha256: z.string(),
      old_text: z.string(), new_text: z.string() },
    implementation: execute,
  });
  return { definition, state, execute };
}

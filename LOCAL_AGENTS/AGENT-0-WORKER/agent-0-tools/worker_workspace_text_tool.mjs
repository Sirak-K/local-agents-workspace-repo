/** One bounded, read-only WORKER file tool scoped to an evaluator-created fixture. */
import { readFile, realpath, stat } from "node:fs/promises";
import { resolve, sep } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { createHash } from "node:crypto";

export async function workerWorkspaceTextTool({ tool, z, workspaceRoot, allowedRelativePath,
    controllerSignal, diagnosticDelayMs = 0, record }) {
  if (typeof allowedRelativePath !== "string" || !/^[A-Za-z0-9._/-]{1,120}$/.test(allowedRelativePath)
      || allowedRelativePath.startsWith("/") || allowedRelativePath.split("/").includes("..")
      || diagnosticDelayMs < 0 || diagnosticDelayMs > 3000) {
    throw new Error("invalid_workspace_tool_scope");
  }
  const root = await realpath(workspaceRoot);
  const state = { active: 0, completed: 0, aborted: 0, denied: 0 };
  const execute = async ({ path }, context) => {
      if (controllerSignal.aborted || context.signal.aborted) {
        state.denied++;
        throw new Error("tool_dispatch_after_stop_denied");
      }
      if (path !== allowedRelativePath || state.completed + state.active >= 2) {
        state.denied++;
        record({ type: "tool_denied", path: String(path).slice(0, 120) });
        return "Error: requested path is unavailable in this workspace.";
      }
      const selected = resolve(root, path);
      if (!selected.startsWith(root + sep)) {
        state.denied++;
        return "Error: requested path is unavailable in this workspace.";
      }
      const actual = await realpath(selected);
      if (!actual.startsWith(root + sep)) {
        state.denied++;
        return "Error: requested path is unavailable in this workspace.";
      }
      const file = await stat(actual);
      if (!file.isFile() || file.size > 4096) {
        state.denied++;
        return "Error: file unavailable or too large.";
      }
      const signal = AbortSignal.any([controllerSignal, context.signal]);
      state.active++;
      record({ type: "tool_started", path });
      try {
        if (diagnosticDelayMs) await delay(diagnosticDelayMs, undefined, { signal });
        signal.throwIfAborted();
        const text = await readFile(actual, { encoding: "utf8", signal });
        signal.throwIfAborted();
        if (Buffer.byteLength(text, "utf8") > 4096 || text.charCodeAt(0) === 0xfeff) {
          throw new Error("invalid_workspace_text");
        }
        state.completed++;
        record({ type: "tool_completed", path, content: text,
          sha256: createHash("sha256").update(text, "utf8").digest("hex") });
        return text;
      } catch (error) {
        if (signal.aborted) {
          state.aborted++;
          record({ type: "tool_aborted", path });
        } else {
          record({ type: "tool_failed", path, code: "workspace_read_error" });
        }
        throw error;
      } finally {
        state.active--;
      }
    };
  const definition = tool({
    name: "read_workspace_text",
    description: "Read a small UTF-8 text file at a relative path inside the provided workspace. Use it when the requested answer depends on file contents.",
    parameters: { path: z.string() },
    implementation: execute,
  });
  return { definition, state, execute };
}

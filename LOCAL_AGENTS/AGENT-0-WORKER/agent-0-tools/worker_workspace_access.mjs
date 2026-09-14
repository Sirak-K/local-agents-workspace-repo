/** Shared, task-scoped access policy for disposable WORKER text fixtures. */
import { createHash } from "node:crypto";
import { lstat, open, realpath } from "node:fs/promises";
import { dirname, resolve, sep } from "node:path";

const ALIAS = /^[A-Za-z0-9._/-]{1,120}$/;

export function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

export function decodeWorkspaceText(bytes) {
  if (bytes.subarray(0, 3).equals(Buffer.from([0xef, 0xbb, 0xbf]))) {
    throw new Error("workspace_utf8_bom_denied");
  }
  return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
}

export function validateWorkspaceAlias(path) {
  if (typeof path !== "string" || !ALIAS.test(path) || path.startsWith("/")
      || path.split("/").some(part => part === "" || part === "." || part === "..")
      || path.split("/").some(part => part.toLowerCase() === "models")
      || /\.(?:safetensors|gguf|ckpt|pt|pth|bin)$/i.test(path)) {
    throw new Error("workspace_path_denied");
  }
  return path;
}

export async function workerWorkspaceAccess({ workspaceRoot, allowedRelativePaths,
    maxFileBytes = 4096, maxReadCalls = 2, maxTotalReadBytes = 8192,
    maxWriteCalls = 0, maxTotalWriteBytes = 0, controllerSignal }) {
  if (!Array.isArray(allowedRelativePaths) || allowedRelativePaths.length === 0
      || allowedRelativePaths.length > 8 || !controllerSignal
      || !Number.isInteger(maxFileBytes) || maxFileBytes < 1 || maxFileBytes > 131072
      || !Number.isInteger(maxReadCalls) || maxReadCalls < 0 || maxReadCalls > 16
      || !Number.isInteger(maxTotalReadBytes) || maxTotalReadBytes < 0 || maxTotalReadBytes > 1048576
      || !Number.isInteger(maxWriteCalls) || maxWriteCalls < 0 || maxWriteCalls > 8
      || !Number.isInteger(maxTotalWriteBytes) || maxTotalWriteBytes < 0 || maxTotalWriteBytes > 1048576) {
    throw new Error("invalid_workspace_tool_scope");
  }
  const aliases = new Set(allowedRelativePaths.map(validateWorkspaceAlias));
  if (aliases.size !== allowedRelativePaths.length) throw new Error("invalid_workspace_tool_scope");
  const rootEntry = await lstat(workspaceRoot);
  if (!rootEntry.isDirectory() || rootEntry.isSymbolicLink()) throw new Error("workspace_root_denied");
  const root = await realpath(workspaceRoot);
  const normalize = value => process.platform === "win32" ? value.toLowerCase() : value;
  if (normalize(root) !== normalize(resolve(workspaceRoot))) throw new Error("workspace_root_denied");
  const state = { readCalls: 0, readBytesReserved: 0, writeCalls: 0,
    writeBytesReserved: 0, activeWrites: 0, committedWrites: 0 };

  function active(signal) {
    controllerSignal.throwIfAborted();
    signal?.throwIfAborted();
  }

  async function checkedPath(path, signal) {
    active(signal);
    validateWorkspaceAlias(path);
    if (!aliases.has(path)) throw new Error("workspace_path_denied");
    let cursor = root;
    for (const component of path.split("/")) {
      cursor = resolve(cursor, component);
      const metadata = await lstat(cursor);
      if (metadata.isSymbolicLink()) throw new Error("workspace_link_denied");
    }
    const actual = await realpath(cursor);
    const expected = resolve(root, path);
    if (!normalize(expected).startsWith(normalize(root + sep))
        || normalize(actual) !== normalize(expected)) throw new Error("workspace_path_denied");
    active(signal);
    return expected;
  }

  async function readBytes(path, signal) {
    const target = await checkedPath(path, signal);
    const handle = await open(target, "r");
    try {
      const metadata = await handle.stat();
      if (!metadata.isFile() || metadata.nlink !== 1 || metadata.size > maxFileBytes) throw new Error("workspace_file_too_large");
      if (state.readCalls >= maxReadCalls
          || state.readBytesReserved + maxFileBytes > maxTotalReadBytes) {
        throw new Error("workspace_read_budget_exhausted");
      }
      state.readCalls++;
      // Reserve the bounded worst case before I/O; a growing file cannot evade
      // aggregate budgets or turn a partial prefix into an apparently full read.
      state.readBytesReserved += maxFileBytes;
      const bytes = Buffer.alloc(maxFileBytes + 1);
      let offset = 0;
      while (offset < bytes.length) {
        active(signal);
        const { bytesRead } = await handle.read(bytes, offset, bytes.length - offset, offset);
        if (!bytesRead) break;
        offset += bytesRead;
      }
      active(signal);
      if (offset > maxFileBytes) throw new Error("workspace_file_too_large");
      const after = await handle.stat();
      if (after.size !== offset) throw new Error("workspace_file_changed_during_read");
      const content = bytes.subarray(0, offset);
      decodeWorkspaceText(content);
      return { bytes: content, text: decodeWorkspaceText(content), sha256: sha256(content) };
    } finally {
      await handle.close();
    }
  }

  async function checkedCreationPath(path, signal) {
    active(signal);
    validateWorkspaceAlias(path);
    if (!aliases.has(path)) throw new Error("workspace_path_denied");
    const target = resolve(root, path);
    if (!normalize(target).startsWith(normalize(root + sep))) throw new Error("workspace_path_denied");
    let cursor = root;
    for (const component of path.split("/").slice(0, -1)) {
      cursor = resolve(cursor, component);
      const metadata = await lstat(cursor);
      if (!metadata.isDirectory() || metadata.isSymbolicLink()) throw new Error("workspace_link_denied");
    }
    if (normalize(await realpath(dirname(target))) !== normalize(dirname(target))) {
      throw new Error("workspace_path_denied");
    }
    try {
      await lstat(target);
      throw new Error("workspace_create_target_exists");
    } catch (error) {
      if (error.message === "workspace_create_target_exists") throw error;
      if (error.code !== "ENOENT") throw error;
    }
    active(signal);
    return target;
  }

  function reserveWrite(byteCount, signal) {
    active(signal);
    if (!Number.isInteger(byteCount) || byteCount < 0 || byteCount > maxFileBytes
        || state.writeCalls >= maxWriteCalls || state.writeBytesReserved + byteCount > maxTotalWriteBytes
        || state.activeWrites) throw new Error("workspace_write_budget_exhausted");
    state.writeCalls++;
    state.writeBytesReserved += byteCount;
    state.activeWrites++;
  }

  function finishWrite(committed = false) {
    state.activeWrites--;
    if (committed) state.committedWrites++;
  }

  return { root, state, active, checkedPath, checkedCreationPath, readBytes, reserveWrite, finishWrite,
    isAllowed: path => aliases.has(path), sha256, decodeWorkspaceText };
}

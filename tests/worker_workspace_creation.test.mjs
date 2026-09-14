import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { workerWorkspaceAccess, sha256 } from "../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-tools/worker_workspace_access.mjs";
import { workerWorkspaceCreationTool } from "../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-tools/worker_workspace_creation_tool.mjs";

async function fixture(t) {
  const root = await mkdtemp(join(tmpdir(), "worker-create-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const controller = new AbortController();
  const events = [];
  const access = await workerWorkspaceAccess({ workspaceRoot: root,
    allowedRelativePaths: ["result.txt", "control.txt"], maxFileBytes: 4096,
    maxReadCalls: 4, maxTotalReadBytes: 16384, maxWriteCalls: 1,
    maxTotalWriteBytes: 4096, controllerSignal: controller.signal });
  const creator = workerWorkspaceCreationTool({ tool: definition => definition,
    z: { string: () => ({}) }, access, controllerSignal: controller.signal,
    record: event => events.push(event) });
  return { root, controller, access, creator, events, context: { signal: controller.signal } };
}

test("new UTF-8 file is atomically published and read back", async t => {
  const f = await fixture(t);
  const content = "Mätvärde: grön\n";
  const receipt = JSON.parse(await f.creator.execute({ path: "result.txt", content }, f.context));
  assert.equal(receipt.after_sha256, sha256(Buffer.from(content)));
  assert.equal(await readFile(join(f.root, "result.txt"), "utf8"), content);
  assert.deepEqual((await readdir(f.root)).sort(), ["result.txt"]);
  assert.equal(f.creator.state.completed, 1);
  assert.equal(f.creator.state.committed, 1);
  assert.equal(f.access.state.activeWrites, 0);
  assert.deepEqual(f.events.filter(event => event.type === "tool_handler_receipt")
    .map(event => event.status), ["completed"]);
});

test("abort before creation commit leaves no file or temporary artifact", async t => {
  const f = await fixture(t);
  const checkedCreationPath = f.access.checkedCreationPath;
  let entered, release;
  const reached = new Promise(resolve => { entered = resolve; });
  const gate = new Promise(resolve => { release = resolve; });
  f.access.checkedCreationPath = async (...args) => {
    entered();
    await gate;
    return checkedCreationPath(...args);
  };
  const pending = f.creator.execute({ path: "result.txt", content: "safe\n" }, f.context);
  await reached;
  assert.equal(f.creator.state.active, 1);
  f.controller.abort();
  release();
  await assert.rejects(pending);
  assert.deepEqual(await readdir(f.root), []);
  assert.equal(f.creator.state.active, 0);
  assert.equal(f.creator.state.aborted, 1);
  assert.equal(f.creator.state.committed, 0);
  await assert.rejects(f.creator.execute({ path: "result.txt", content: "late" }, f.context), /dispatch_after_stop/);
});

test("existing, out-of-scope and invalid content targets are never overwritten", async t => {
  const f = await fixture(t);
  await writeFile(join(f.root, "control.txt"), "keep", "utf8");
  await assert.rejects(f.creator.execute({ path: "control.txt", content: "replace" }, f.context), /target_exists/);
  assert.match(await f.creator.execute({ path: "secret.txt", content: "bad" }, f.context), /invalid/);
  assert.match(await f.creator.execute({ path: "result.txt", content: "\ufeffbad" }, f.context), /invalid/);
  assert.equal(await readFile(join(f.root, "control.txt"), "utf8"), "keep");
  assert.deepEqual((await readdir(f.root)).sort(), ["control.txt"]);
});

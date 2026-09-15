import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, readdir, symlink, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { workerWorkspaceAccess, sha256 } from "../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-tools/worker_workspace_access.mjs";
import { workerWorkspaceMutationTool } from "../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-tools/worker_workspace_mutation_tool.mjs";

const alias = "workflow.json";
const before = '{"nodes":[{"id":61,"title":"OLD"}],"links":[]}';
const replacement = { path: alias, expected_sha256: sha256(Buffer.from(before)),
  old_text: '"title":"OLD"', new_text: '"title":"NEW"' };

async function fixture(t, overrides = {}) {
  const root = await mkdtemp(join(tmpdir(), "worker-write-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  await writeFile(join(root, alias), before, "utf8");
  const controller = new AbortController();
  const events = [];
  const access = await workerWorkspaceAccess({ workspaceRoot: root,
    allowedRelativePaths: [alias], maxFileBytes: 65536, maxReadCalls: 4,
    maxTotalReadBytes: 262144, maxWriteCalls: 1, maxTotalWriteBytes: 65536,
    controllerSignal: controller.signal, ...overrides });
  const writer = workerWorkspaceMutationTool({ tool: definition => definition,
    z: { string: () => ({}) }, access, controllerSignal: controller.signal,
    record: event => events.push(event), diagnosticDelayMs: overrides.diagnosticDelayMs || 0 });
  return { root, controller, access, writer, events, context: { signal: controller.signal } };
}

test("one hash-conditional replacement commits and independently reads back", async t => {
  const f = await fixture(t);
  const receipt = JSON.parse(await f.writer.execute(replacement, f.context));
  assert.equal(receipt.before_sha256, replacement.expected_sha256);
  assert.equal(receipt.after_sha256, sha256(Buffer.from(before.replace('"title":"OLD"', '"title":"NEW"'))));
  assert.equal(await readFile(join(f.root, alias), "utf8"), before.replace('"title":"OLD"', '"title":"NEW"'));
  assert.equal(f.writer.state.active, 0);
  assert.equal(f.writer.state.completed, 1);
  assert.equal(f.writer.state.committed, 1);
  assert.equal(f.access.state.activeWrites, 0);
  const returned = f.events.find(event => event.type === "tool_handler_returned");
  assert.equal(returned.status, "completed");
  assert.equal(returned.after_sha256, receipt.after_sha256);
  assert.match(returned.result_sha256, /^[0-9a-f]{64}$/);
  assert.deepEqual((await readdir(f.root)).sort(), [alias]);
});

test("wrong hash, ambiguous match, denied path and exhausted budget never mutate", async t => {
  const f = await fixture(t, { maxReadCalls: 8, maxTotalReadBytes: 524288 });
  assert.match(await f.writer.execute({ ...replacement, expected_sha256: "0".repeat(63) }, f.context),
    /exactly 64 lowercase hexadecimal/);
  assert.equal(f.events.find(event => event.type === "tool_handler_returned")?.feedback_code,
    "invalid_expected_sha256");
  assert.match(await f.writer.execute({ ...replacement, expected_sha256: "0".repeat(64) }, f.context), /hash_mismatch/);
  assert.equal(f.events.filter(event => event.type === "tool_handler_returned")
    .find(event => event.feedback_code === "workspace_hash_mismatch")?.status, "feedback");
  assert.match(await f.writer.execute({ ...replacement, old_text: '"' }, f.context), /not unique/);
  assert.match(await f.writer.execute({ ...replacement, path: "../workflow.json" }, f.context), /invalid/);
  assert.equal(await readFile(join(f.root, alias), "utf8"), before);
  await f.writer.execute(replacement, f.context);
  assert.match(await f.writer.execute({ ...replacement, expected_sha256: sha256(Buffer.from(before.replace('"title":"OLD"', '"title":"NEW"'))), old_text: "NEW", new_text: "NEXT" }, f.context), /budget/);
  assert.equal(await readFile(join(f.root, alias), "utf8"), before.replace('"title":"OLD"', '"title":"NEW"'));
});

test("stale hash feedback permits a second bounded edit after readback", async t => {
  const f = await fixture(t, { maxReadCalls: 8, maxTotalReadBytes: 524288, maxWriteCalls: 2 });
  await f.writer.execute(replacement, f.context);
  assert.match(await f.writer.execute({ ...replacement, old_text: '"title":"NEW"', new_text: '"title":"NEXT"' }, f.context), /hash_mismatch/);
  const current = await f.access.readBytes(alias, f.controller.signal);
  const corrected = { ...replacement, expected_sha256: current.sha256,
    old_text: '"title":"NEW"', new_text: '"title":"NEXT"' };
  const receipt = JSON.parse(await f.writer.execute(corrected, f.context));
  assert.equal(receipt.before_sha256, current.sha256);
  assert.equal(await readFile(join(f.root, alias), "utf8"), before.replace('"title":"OLD"', '"title":"NEXT"'));
  assert.equal(f.writer.state.committed, 2);
  assert.equal(f.writer.state.active, 0);
});

test("abort before the commit point leaves original and removes temporary file", async t => {
  const f = await fixture(t, { diagnosticDelayMs: 3000 });
  const pending = f.writer.execute(replacement, f.context);
  const deadline = Date.now() + 1500;
  while (!f.events.some(event => event.type === "tool_mutation_started") && Date.now() < deadline) {
    await new Promise(resolve => setTimeout(resolve, 10));
  }
  assert.ok(f.events.some(event => event.type === "tool_mutation_started"));
  f.controller.abort();
  await assert.rejects(pending);
  assert.equal(await readFile(join(f.root, alias), "utf8"), before);
  assert.deepEqual((await readdir(f.root)).sort(), [alias]);
  assert.equal(f.writer.state.active, 0);
  assert.equal(f.writer.state.aborted, 1);
  await assert.rejects(f.writer.execute(replacement, f.context), /dispatch_after_stop/);
});

test("a committed write remains evidence when stop follows commit", async t => {
  const f = await fixture(t);
  const originalRecord = f.events.push.bind(f.events);
  // Stop exactly at the observable commit boundary; readback must still finish.
  const writer = workerWorkspaceMutationTool({ tool: definition => definition,
    z: { string: () => ({}) }, access: f.access, controllerSignal: f.controller.signal,
    record: event => { originalRecord(event); if (event.type === "tool_mutation_committed") f.controller.abort(); } });
  const receipt = JSON.parse(await writer.execute(replacement, f.context));
  assert.equal(receipt.after_sha256, sha256(Buffer.from(before.replace('"title":"OLD"', '"title":"NEW"'))));
  assert.equal(writer.state.committed, 1);
  assert.equal(await readFile(join(f.root, alias), "utf8"), before.replace('"title":"OLD"', '"title":"NEW"'));
});

test("exact allowlist rejects out-of-scope links and BOM", async t => {
  const f = await fixture(t);
  await writeFile(join(f.root, "secret.json"), "private", "utf8");
  await assert.rejects(f.access.readBytes("secret.json", f.controller.signal), /path_denied/);
  await rm(join(f.root, alias));
  await symlink(join(f.root, "secret.json"), join(f.root, alias), "file");
  await assert.rejects(f.access.readBytes(alias, f.controller.signal), /link_denied/);
  await rm(join(f.root, alias));
  await writeFile(join(f.root, alias), Buffer.from([0xef, 0xbb, 0xbf, 0x7b, 0x7d]));
  await assert.rejects(f.access.readBytes(alias, f.controller.signal), /utf8_bom_denied/);
});

test("bounded read rejects oversized fixtures and parent-directory links", async t => {
  const root = await mkdtemp(join(tmpdir(), "worker-link-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  const external = await mkdtemp(join(tmpdir(), "worker-external-"));
  t.after(() => rm(external, { recursive: true, force: true }));
  await mkdir(join(root, "safe"));
  await writeFile(join(root, "safe", "sample.json"), "x".repeat(100));
  const controller = new AbortController();
  const policy = await workerWorkspaceAccess({ workspaceRoot: root,
    allowedRelativePaths: ["safe/sample.json"], maxFileBytes: 32,
    maxReadCalls: 2, maxTotalReadBytes: 64, controllerSignal: controller.signal });
  await assert.rejects(policy.readBytes("safe/sample.json", controller.signal), /too_large/);
  await rm(join(root, "safe"), { recursive: true });
  await writeFile(join(external, "sample.json"), "{}");
  await symlink(external, join(root, "safe"), process.platform === "win32" ? "junction" : "dir");
  await assert.rejects(policy.readBytes("safe/sample.json", controller.signal), /link_denied/);
});

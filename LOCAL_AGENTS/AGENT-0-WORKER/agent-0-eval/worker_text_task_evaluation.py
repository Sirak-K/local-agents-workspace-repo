"""Run bounded technology-neutral read/create/replace tasks in disposable workspaces."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "LM-Studio_connections/LM-Studio_for_codex"),
                str(ROOT / "LM-Studio_connections/LM-Studio_observability"),
                str(ROOT / "tools"), str(Path(__file__).parent)]
from evaluation_paths import create_run_directory, existing_run_directory, run_directory
from evaluation_source_snapshot import capture_source_snapshot, runtime_source_paths, installed_runtime_identity
from interruptible_prediction import SdkPredictionProcess
from json_document_comparison import parse_json_document
from lm_studio_user_api_token import resolve_token
from observability_common import sanitize_for_log, timestamp_fields, write_capture
from tool_dispatch_evidence import summarize_tool_dispatch
from tool_progress_control import ToolProgressControl
from tool_transport_review import require_transport_review, matching_reviewed_instance

CATALOG = Path(__file__).with_name("basic_file_task_catalog.json")
SDK_SCRIPT = Path(__file__).with_name("worker_file_task_prediction.mjs")
EVIDENCE_LIMIT = 1_048_576
TERMINAL = {"response_received", "verified_cancel", "verified_tool_abort", "failed", "unverified", "not_started"}
SAFE_PATH = re.compile(r"[A-Za-z0-9._/-]{1,120}\Z")


def _bounded(path: Path, limit: int) -> bytes:
    with path.open("rb") as handle:
        body = handle.read(limit + 1)
    if len(body) > limit or body.startswith(b"\xef\xbb\xbf"):
        raise ValueError("source byte or encoding budget")
    body.decode("utf-8")
    return body


def task_contract(identifier: str) -> dict:
    raw = _bounded(CATALOG, 32768)
    catalog = parse_json_document(raw.decode("utf-8"))
    context_file = catalog.get("context_file")
    tasks = catalog.get("tasks")
    if (catalog.get("version") != 2 or not isinstance(context_file, str)
            or Path(context_file).name != context_file or not isinstance(tasks, list)
            or not 1 <= len(tasks) <= 10 or len({item.get("id") for item in tasks}) != len(tasks)):
        raise ValueError("invalid file task catalog")
    task = next((item for item in tasks if item.get("id") == identifier), None)
    if not isinstance(task, dict):
        raise ValueError("unknown file task")
    context = _bounded(CATALOG.with_name(context_file), 4096)
    files, expected = task.get("files"), task.get("expected_files")
    allowed, enabled = task.get("allowed_paths"), task.get("enabled_tools")
    paths = set(allowed) if isinstance(allowed, list) else set()
    if (not isinstance(files, dict) or not isinstance(expected, dict) or not paths
            or set(files) - paths or set(expected) != paths
            or not all(isinstance(path, str) and SAFE_PATH.fullmatch(path) and ".." not in path.split("/")
                       and not path.startswith("/") for path in paths)
            or not all(isinstance(value, str) and not value.startswith("\ufeff")
                       and len(value.encode("utf-8")) <= 4096 for value in [*files.values(), *expected.values()])
            or not isinstance(enabled, list) or not set(enabled) <= {
                "read_workspace_text", "replace_workspace_text", "create_workspace_text"}
            or task.get("duration_seconds") != 45 or task.get("stop_budget_seconds") != 5
            or task.get("max_tokens") != 512):
        raise ValueError("unsafe or unsupported file task contract")
    receipts = task.get("required_tool_receipts")
    if not isinstance(receipts, dict) or set(receipts) != {"read", "write", "create"}:
        raise ValueError("missing tool receipt contract")
    claim = task.get("completion_claim")
    if claim != {"success_prefix": "STATUS=SUCCESS", "failure_prefix": "STATUS=FAILED"}:
        raise ValueError("missing completion claim contract")
    return task | {"context_text": context.decode("utf-8"),
                   "catalog_sha256": hashlib.sha256(raw).hexdigest(),
                   "context_sha256": hashlib.sha256(context).hexdigest()}


def _safe_file(path: Path) -> bytes:
    metadata = path.lstat()
    if (not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode)
            or getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
        raise ValueError("unsafe workspace result")
    return _bounded(path, 65536)


def _result_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("text_chunks"), list):
        return "".join(value["text_chunks"])
    return ""


def verify_completion_claim(result_content, operation_passed: bool, claim: dict) -> dict:
    text = _result_text(result_content)
    first_line = text.splitlines()[0].strip() if text.splitlines() else ""
    if first_line == claim["success_prefix"]:
        reported = "success"
    elif first_line == claim["failure_prefix"]:
        reported = "failure"
    else:
        reported = "unparseable"
    observed = "success" if operation_passed else "failure"
    return {
        "status": "consistent" if reported == observed else "inconsistent",
        "reported_outcome": reported,
        "observed_outcome": observed,
        "required_first_line": [claim["success_prefix"], claim["failure_prefix"]],
        "response_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def request_stop(eval_id: str, run_id: str, reason: str) -> bool:
    if not reason.strip() or len(reason) > 240:
        raise ValueError("bounded concrete stop reason required")
    directory = existing_run_directory(eval_id, run_id)
    evidence = json.loads(_bounded(directory / "evidence.json", EVIDENCE_LIMIT).decode("utf-8"))
    if evidence.get("eval_id") != eval_id or evidence.get("run_id") != run_id:
        raise ValueError("run identity mismatch")
    if evidence.get("state") in TERMINAL:
        return False
    temporary = directory / (".stop-" + uuid4().hex + ".tmp")
    try:
        write_capture(temporary, {"reason": sanitize_for_log(reason), "requested_at": timestamp_fields()})
        try:
            os.link(temporary, directory / "stop_request.json")
            return True
        except FileExistsError:
            return False
    finally:
        temporary.unlink(missing_ok=True)


def run(eval_id: str, run_id: str, model: str, task_id: str,
        granite_text_tool_bridge: bool = False, previous_run: str | None = None,
        change_reason: str | None = None, *, transport_review_file: str | None = None) -> dict:
    task = task_contract(task_id)
    if granite_text_tool_bridge and model != "granite-4.1-3b":
        raise ValueError("Granite bridge requires Granite 4.1 3B")
    transport_review = require_transport_review(transport_review_file, model)
    token = resolve_token()
    previous_hash = None
    if previous_run:
        original_path = existing_run_directory(eval_id, previous_run) / "evidence.json"
        original = json.loads(_bounded(original_path, EVIDENCE_LIMIT).decode("utf-8"))
        if (original.get("eval_id") != eval_id or original.get("state") not in TERMINAL
                or not isinstance(change_reason, str) or not change_reason.strip() or len(change_reason) > 500):
            raise ValueError("retry requires terminal same-eval original and reason")
        previous_hash = hashlib.sha256(original_path.read_bytes()).hexdigest()
    elif change_reason:
        raise ValueError("change reason requires previous run")
    directory = create_run_directory(eval_id, run_id)
    workspace = directory / "workspace"
    workspace.mkdir()
    before = {}
    for relative, content in task["files"].items():
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode("utf-8"))
        before[relative] = hashlib.sha256(content.encode("utf-8")).hexdigest()
    instruction = task["instruction"]
    if before:
        instruction += " Initial SHA-256 values: " + "; ".join(path + "=" + digest for path, digest in before.items()) + "."
    system_prompt = task["context_text"]
    if granite_text_tool_bridge:
        schemas = {
            "read_workspace_text": "read_workspace_text(path: string)",
            "replace_workspace_text": "replace_workspace_text(path: string, expected_sha256: string, old_text: string, new_text: string)",
            "create_workspace_text": "create_workspace_text(path: string, content: string)",
        }
        system_prompt += ("\n\nGranite interface adapter: request exactly one available tool as "
            "<tool_call>{\"name\":\"tool_name\",\"arguments\":{...}}</tool_call> and output nothing else in that turn.\n"
            + "Available tools:\n" + "\n".join("- " + schemas[name] for name in task["enabled_tools"]))
    source_paths = (Path(__file__), CATALOG, CATALOG.with_name("bounded_file_work.md"), SDK_SCRIPT,
                    Path(__file__).with_name("tool_progress_control.py"),
                    Path(__file__).with_name("tool_dispatch_evidence.py"),
                    Path(__file__).parents[1] / "agent-0-tools/worker_workspace_access.mjs",
                    Path(__file__).parents[1] / "agent-0-tools/worker_workspace_text_tool.mjs",
                    Path(__file__).parents[1] / "agent-0-tools/worker_workspace_mutation_tool.mjs",
                    Path(__file__).parents[1] / "agent-0-tools/worker_workspace_creation_tool.mjs",
                    Path(__file__).parents[1] / "AG-0-MODEL-Granite_4.1-3B/granite_tool_call_envelope.mjs")
    sources = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths}
    source_snapshot = capture_source_snapshot(runtime_source_paths(source_paths))
    evidence = {"eval_id": eval_id, "run_id": run_id, "kind": "bounded_text_file_task",
        "state": "starting", "created_at": timestamp_fields(), "updated_at": timestamp_fields(),
        "task": {"id": task_id, "catalog_sha256": task["catalog_sha256"],
                 "context_sha256": task["context_sha256"]},
        "contract": {"model_identifier": model, "temperature": 0, "fresh_chat": True,
                     "duration_seconds": 45, "stop_budget_seconds": 5, "max_tokens": 512,
                     "max_rounds": 6, "max_tool_calls": 6, "allowed_paths": task["allowed_paths"],
                     "enabled_tools": task["enabled_tools"], "workspace_scope": "current disposable run only"},
        "instruction": sanitize_for_log(instruction),
        "instruction_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest(),
        "source_fingerprints": sources, "fixture": {"sha256_before": before},
        "source_snapshot": source_snapshot,
        "runtime_identity": installed_runtime_identity(),
        "transport_review": transport_review,
        "system_prompt": sanitize_for_log(system_prompt),
        "granite_text_tool_bridge": granite_text_tool_bridge,
        "previous_run": previous_run, "previous_run_sha256": previous_hash,
        "change_reason": sanitize_for_log(change_reason),
        "events": [], "stop": None, "result": None, "assessment": {"status": "pending"},
        "verification": {"generation": "not_started", "cancel_command_sent": False,
                         "within_stop_budget": None, "tools": "not_started"},
        "evidence_gaps": ["Task result does not by itself prove broad WORKER reliability."]}
    evidence_path = directory / "evidence.json"

    def persist():
        evidence["updated_at"] = timestamp_fields()
        if len(json.dumps(evidence, ensure_ascii=False, indent=2).encode("utf-8")) > EVIDENCE_LIMIT:
            raise ValueError("evidence budget exhausted")
        write_capture(evidence_path, evidence)

    persist()
    sdk = None
    began = time.monotonic()
    stopped_at = receipt_at = None
    terminal = None
    cancel_sent = False
    progress = ToolProgressControl()
    try:
        sdk = SdkPredictionProcess(token, {"base_url": "ws://127.0.0.1:1234", "model": model,
            "workspace_root": str(workspace), "allowed_relative_paths": task["allowed_paths"],
            "enabled_tools": task["enabled_tools"], "allow_create": "create_workspace_text" in task["enabled_tools"],
            "instruction": instruction, "system_prompt": system_prompt, "skill_mode": "none",
            "skills": [], "granite_text_tool_bridge": granite_text_tool_bridge,
            "diagnostic_mutation_delay_ms": 0,
            "force_text_tool_bridge": False,
            "diagnostic_request": None, "max_tokens": 512, "max_rounds": 6,
            "max_tool_calls": 6, "require_start_approval": True}, worker_script=SDK_SCRIPT)
        while True:
            now = time.monotonic()
            stop_path = directory / "stop_request.json"
            if stopped_at is None and (stop_path.exists() or now - began >= 45):
                request = json.loads(_bounded(stop_path, 4096).decode("utf-8")) if stop_path.exists() else None
                evidence["stop"] = {"reason": request["reason"] if request else "locked execution budget exhausted",
                                    "observed_at": timestamp_fields()}
                stopped_at = now
                evidence["state"] = "stopping"
                sdk.cancel()
                persist()
            if stopped_at is not None and now - stopped_at >= 5:
                evidence["evidence_gaps"].append("No final stop receipt within five seconds.")
                break
            event = sdk.next_event(0.1)
            if not event:
                continue
            evidence["events"].append({"observed_at": timestamp_fields(), "data": sanitize_for_log(event)})
            if len(evidence["events"]) > 2048:
                raise ValueError("event budget exhausted")
            if progress.observe(event) and stopped_at is None:
                evidence["stop"] = {"reason": "three equivalent tool outcomes without relevant progress",
                                    "observed_at": timestamp_fields()}
                stopped_at = time.monotonic()
                evidence["state"] = "stopping"
                sdk.cancel()
            kind = event.get("type")
            if kind == "model_bound":
                if (event.get("model_info", {}).get("identifier") != model
                        or not matching_reviewed_instance(transport_review, event.get("model_info", {}))):
                    stopped_at = time.monotonic(); sdk.cancel()
                elif stopped_at is None:
                    sdk.send({"command": "continue"})
            elif kind == "round_started":
                evidence["state"] = "running"
            elif kind == "cancel_sent":
                cancel_sent = True
            elif kind == "result":
                terminal = event; receipt_at = time.monotonic(); evidence["result"] = sanitize_for_log(event); break
            elif kind in ("act_interrupted", "error", "not_started", "worker_eof"):
                terminal = event; receipt_at = time.monotonic(); break
            persist()
    finally:
        if sdk:
            sdk.close()
    tool_state = terminal.get("tool_state", {}) if terminal else {}
    evidence["verification"]["tools"] = tool_state
    evidence["verification"]["cancel_command_sent"] = cancel_sent
    evidence["verification"]["within_stop_budget"] = (stopped_at is None or receipt_at is not None and receipt_at - stopped_at <= 5)
    after = {}
    extras = []
    for path in workspace.rglob("*"):
        if path.is_file():
            relative = path.relative_to(workspace).as_posix()
            body = _safe_file(path)
            after[relative] = {"sha256": hashlib.sha256(body).hexdigest(), "content": body.decode("utf-8")}
            if relative not in task["allowed_paths"] or path.name.startswith((".worker-create-", ".worker-mutation-")):
                extras.append(relative)
    exact_files = not extras and set(after) == set(task["expected_files"]) and all(
        after[path]["content"] == expected for path, expected in task["expected_files"].items())
    receipts = task["required_tool_receipts"]
    receipt_match = all(isinstance(tool_state.get(name), dict)
                        and tool_state[name].get("active") == 0
                        and tool_state[name].get("completed", 0) == count
                        for name, count in receipts.items() if count)
    unexpected = any(isinstance(tool_state.get(name), dict) and tool_state[name].get("committed", 0)
                     for name, count in receipts.items() if count == 0)
    natural = (terminal and terminal.get("type") == "result" and stopped_at is None
               and terminal.get("stats", {}).get("stopReason") == "eosFound")
    stable = sources == {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths}
    operation_passed = natural and exact_files and receipt_match and not unexpected
    claim_verification = verify_completion_claim(
        terminal.get("content") if terminal else "", operation_passed, task["completion_claim"])
    passed = operation_passed and stable and claim_verification["status"] == "consistent"
    evidence["fixture"]["after"] = after
    evidence["tool_dispatch_trace"] = summarize_tool_dispatch(evidence["events"])
    evidence["task_verification"] = {"status": "pass" if passed else "fail",
        "operation_status": "pass" if operation_passed else "fail",
        "exact_files": exact_files, "required_tool_receipts": receipt_match,
        "unexpected_writes": unexpected, "source_stable": stable, "extra_files": extras,
        "self_report": claim_verification}
    evidence["assessment"] = {"status": "pass" if passed else "fail",
                              "scope": task_id, "assisted_diagnostic": granite_text_tool_bridge,
                              "model_fault_attribution": "not_performed"}
    if natural:
        evidence["state"] = "response_received"
        evidence["verification"]["generation"] = "natural_eos"
    elif stopped_at is not None and cancel_sent and evidence["verification"]["within_stop_budget"]:
        active = sum((value or {}).get("active", 0) for value in tool_state.values() if isinstance(value, dict))
        evidence["state"] = "verified_cancel" if terminal and terminal.get("stats", {}).get("stopReason") == "userStopped" and active == 0 else "unverified"
    else:
        evidence["state"] = "failed"
    evidence["finished_at"] = timestamp_fields()
    persist()
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("start", "run"):
        command = commands.add_parser(name)
        command.add_argument("--eval-id", required=True); command.add_argument("--model", required=True)
        command.add_argument("--task-id", required=True)
        command.add_argument("--transport-review-file", required=True)
        command.add_argument("--granite-text-tool-bridge", action="store_true")
        command.add_argument("--previous-run"); command.add_argument("--change-reason")
        if name == "run": command.add_argument("--run-id", required=True)
    for name in ("inspect", "stop"):
        command = commands.add_parser(name); command.add_argument("--eval-id", required=True)
        command.add_argument("--run-id", required=True)
        if name == "stop": command.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        if args.command == "start":
            require_transport_review(args.transport_review_file, args.model)
            task_contract(args.task_id); resolve_token(); run_id = uuid4().hex
            argv = [sys.executable, str(Path(__file__).resolve()), "run", "--eval-id", args.eval_id,
                    "--run-id", run_id, "--model", args.model, "--task-id", args.task_id,
                    "--transport-review-file", args.transport_review_file]
            if args.granite_text_tool_bridge: argv.append("--granite-text-tool-bridge")
            if args.previous_run: argv.extend(["--previous-run", args.previous_run])
            if args.change_reason: argv.extend(["--change-reason", args.change_reason])
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            deadline = time.monotonic() + 3
            while not (run_directory(args.eval_id, run_id) / "evidence.json").exists() and time.monotonic() < deadline:
                if child.poll() is not None: raise RuntimeError("text task startup failed")
                time.sleep(0.02)
            print(json.dumps({"eval_id": args.eval_id, "run_id": run_id, "controller_pid": child.pid}, indent=2))
        elif args.command == "run":
            outcome = run(args.eval_id, args.run_id, args.model, args.task_id,
                          args.granite_text_tool_bridge, args.previous_run, args.change_reason,
                          transport_review_file=args.transport_review_file)
            print(json.dumps({"run_id": args.run_id, "state": outcome["state"]}, indent=2))
        elif args.command == "inspect":
            print(_bounded(existing_run_directory(args.eval_id, args.run_id) / "evidence.json", EVIDENCE_LIMIT).decode("utf-8"))
        else:
            print(json.dumps({"stop_request_created": request_stop(args.eval_id, args.run_id, args.reason)}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError):
        print("Text task control failed; no success is implied.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

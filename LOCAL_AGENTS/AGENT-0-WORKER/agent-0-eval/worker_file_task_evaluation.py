"""Bounded read/replace WORKER task on a disposable file copy; no ComfyUI execution."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import stat
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "LM-Studio_connections/LM-Studio_for_codex"),
                str(ROOT / "LM-Studio_connections/LM-Studio_observability"),
                str(ROOT / "tools"), str(Path(__file__).parents[1] / "agent-0-tools"), str(Path(__file__).parent)]
from evaluation_paths import create_run_directory, existing_run_directory, run_directory
from evaluation_source_snapshot import capture_source_snapshot, runtime_source_paths, installed_runtime_identity
from comfyui_workflow_grading import (load_rename_fixture, prepare_rename_fixture,
                                      grade_rename_fixture)
from interruptible_prediction import SdkPredictionProcess
from lm_studio_user_api_token import resolve_token
from observability_common import sanitize_for_log, timestamp_fields, write_capture
from tool_progress_control import ToolProgressControl
from worker_workspace_validation_control import WorkspaceValidationControl
from worker_skill_context import expose_skills
from tool_transport_review import require_transport_review, matching_reviewed_instance

SDK_SCRIPT = Path(__file__).with_name("worker_file_task_prediction.mjs")
ALIAS = "workflow.json"
EVIDENCE_LIMIT = 1_048_576
MAX_EVENTS = 4096
TERMINAL = {"response_received", "verified_cancel", "verified_tool_abort", "unverified", "failed", "not_started"}


def read_json(path: Path, limit: int = EVIDENCE_LIMIT) -> dict:
    with path.open("rb") as handle:
        body = handle.read(limit + 1)
    if len(body) > limit:
        raise ValueError("evidence exceeds budget")
    return json.loads(body.decode("utf-8"))


def file_fingerprint(path: Path) -> str:
    metadata = path.lstat()
    if (not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode)
            or getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
        raise ValueError("unsafe readback path")
    with path.open("rb") as handle:
        body = handle.read(65537)
    if len(body) > 65536:
        raise ValueError("readback exceeds file budget")
    return hashlib.sha256(body).hexdigest()


def request_stop(eval_id: str, run_id: str, reason: str) -> bool:
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 240:
        raise ValueError("concrete bounded stop reason required")
    directory = existing_run_directory(eval_id, run_id)
    evidence = read_json(directory / "evidence.json")
    if evidence.get("eval_id") != eval_id or evidence.get("run_id") != run_id:
        raise ValueError("run evidence belongs to another identity")
    if evidence.get("state") in TERMINAL:
        return False
    temporary = directory / (".stop-" + uuid4().hex + ".tmp")
    try:
        write_capture(temporary, {"reason": sanitize_for_log(reason),
                                  "requested_at": timestamp_fields()})
        try:
            os.link(temporary, directory / "stop_request.json")
            return True
        except FileExistsError:
            return False
    finally:
        temporary.unlink(missing_ok=True)


def run(eval_id: str, run_id: str, model: str, granite_text_tool_bridge: bool = False,
        diagnostic_mutation_delay_ms: int = 0, skill_mode: str = "none",
        skill_id: str | None = None, previous_run: str | None = None,
        change_reason: str | None = None, diagnostic_mutation_dispatch: bool = False,
        *, transport_review_file: str | None = None) -> dict:
    if granite_text_tool_bridge and model != "granite-4.1-3b":
        raise ValueError("Granite bridge requires Granite 4.1 3B")
    if diagnostic_mutation_delay_ms not in (0, 3000):
        raise ValueError("unsupported diagnostic mutation delay")
    transport_review = (None if diagnostic_mutation_delay_ms
                        else require_transport_review(transport_review_file, model))
    locked = load_rename_fixture()
    skill_exposure = expose_skills(skill_mode, skill_id)
    diagnostic_contract = None
    if diagnostic_mutation_dispatch:
        if diagnostic_mutation_delay_ms != 3000 or skill_mode != "none" or granite_text_tool_bridge:
            raise ValueError("deterministic mutation diagnostic requires fixed delay and no candidate scaffolding")
        diagnostic_contract = read_json(Path(__file__).with_name("workspace_tool_control_contract.json"), 4096)
        if diagnostic_contract["version"] != 1:
            raise ValueError("unsupported tool control diagnostic")
    if (locked["duration_seconds"] != 60 or locked["stop_budget_seconds"] != 5
            or locked["max_tool_calls"] != 8 or locked["max_output_tokens"] != 512):
        raise ValueError("unsupported workflow task budget")
    token = resolve_token()
    previous_hash = None
    if previous_run:
        original_path = existing_run_directory(eval_id, previous_run) / "evidence.json"
        original = read_json(original_path)
        if (original.get("eval_id") != eval_id or original.get("state") not in TERMINAL
                or not isinstance(change_reason, str) or not change_reason.strip() or len(change_reason) > 500):
            raise ValueError("retry needs terminal same-eval original and explicit bounded change reason")
        previous_hash = hashlib.sha256(original_path.read_bytes()).hexdigest()
    elif change_reason:
        raise ValueError("change reason requires an original run")
    directory = create_run_directory(eval_id, run_id)
    prepared = prepare_rename_fixture(eval_id, run_id)
    target = prepared["path"]
    workspace = target.parent
    before = prepared["source_sha256"]
    system_prompt = locked["context_text"] + skill_exposure["system_text"]
    instruction = prepared["instruction"] + " Initial file SHA-256 for the first conditional write: " + before + ". Use each write receipt's after_sha256 for any subsequent write."
    if diagnostic_contract:
        if diagnostic_contract["request"]["expected_sha256"] != before:
            raise ValueError("diagnostic request source changed")
        instruction = diagnostic_contract["instruction"]
        system_prompt = ""
    if not instruction.strip() or len(instruction.encode("utf-8")) > 4096:
        raise ValueError("instruction exceeds 4096 UTF-8 bytes")
    source_paths = (Path(__file__), SDK_SCRIPT,
                Path(__file__).with_name("comfyui_workflow_grading.py"),
                Path(__file__).with_name("comfyui_workflow_validation.py"),
                Path(__file__).with_name("json_document_comparison.py"),
                Path(__file__).with_name("worker_skill_context.py"),
                Path(__file__).with_name("tool_progress_control.py"),
                Path(__file__).with_name("workflow_rename_fixture.json"),
                Path(__file__).with_name("workspace_tool_control_contract.json"),
                Path(__file__).with_name("schemas") / "workflow_ui_0_4.json",
                Path(__file__).with_name("schemas") / "workflow_ui_0_4_source.json",
                Path(__file__).parents[1] / "agent-0-tools/worker_workspace_access.mjs",
                Path(__file__).parents[1] / "agent-0-tools/worker_workspace_text_tool.mjs",
                Path(__file__).parents[1] / "agent-0-tools/worker_workspace_mutation_tool.mjs",
                Path(__file__).parents[1] / "agent-0-tools/worker_workspace_validation_control.py",
                Path(__file__).parents[1] / "agent-0-tools/worker_tool_process_control.py",
                Path(__file__).parents[1] / "agent-0-tools/workspace_workflow_validator.py",
                Path(__file__).parents[1] / "agent-0-tools/worker_workspace_validation_tool.mjs",
                Path(__file__).parents[1] / "agent-0-tools/worker_skill_read_tool.mjs",
                Path(__file__).parents[1] / "AG-0-MODEL-Granite_4.1-3B/granite_tool_call_envelope.mjs")
    sources = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths}
    source_snapshot = capture_source_snapshot(runtime_source_paths(source_paths))
    evidence = {"eval_id": eval_id, "run_id": run_id, "kind": "workspace_tool_control" if diagnostic_contract else "workspace_file_task",
        "state": "starting", "created_at": timestamp_fields(), "updated_at": timestamp_fields(),
        "contract": {"model_identifier": model, "sdk_version": "1.5.0", "temperature": 0,
                     "max_tokens_per_prediction": 512, "max_prediction_rounds": 6,
                     "max_tool_calls": locked["max_tool_calls"], "max_file_bytes": 65536,
                     "max_read_calls": 8, "max_total_read_bytes": 524288,
                     "max_write_calls": 2, "max_total_write_bytes": 131072,
                     "duration_seconds": 60, "stop_budget_seconds": 5,
                     "observation_target_seconds": 0.5, "max_stream_events": MAX_EVENTS,
                     "max_evidence_bytes": EVIDENCE_LIMIT,
                     "fresh_chat": True, "project_system_prompt_sha256": locked["context"]["sha256"],
                     "effective_system_prompt_sha256": hashlib.sha256(system_prompt.encode("utf-8")).hexdigest(),
                     "granite_text_tool_bridge": granite_text_tool_bridge,
                     "diagnostic_mutation_delay_ms": diagnostic_mutation_delay_ms,
                     "diagnostic_mutation_dispatch": diagnostic_mutation_dispatch,
                     "allowed_relative_path": ALIAS},
        "instruction": instruction, "instruction_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest(),
        "source_fingerprints": sources,
        "source_snapshot": source_snapshot,
        "runtime_identity": installed_runtime_identity(),
        "transport_review": transport_review,
        "previous_run": previous_run, "change_reason": sanitize_for_log(change_reason),
        "previous_run_sha256": previous_hash,
        "skill_exposure": {"mode": skill_mode, "catalog_sha256": skill_exposure["catalog_sha256"],
                           "skills": [{key: value for key, value in item.items() if key != "content"}
                                      for item in skill_exposure["skills"]]},
        "system_prompt": sanitize_for_log(system_prompt),
        "diagnostic_request": diagnostic_contract["request"] if diagnostic_contract else None,
        "fixture": {"manifest_sha256": prepared["manifest_sha256"],
                    "source_sha256": prepared["source_sha256"],
                    "context": prepared["context"], "alias": ALIAS, "sha256_before": before},
        "events": [], "stop": None, "result": None,
        "verification": {"generation": "not_started", "tools": "not_started",
                         "cancel_command_sent": False, "within_stop_budget": None,
                         "readback_stable_after_stop": None},
        "assessment": {"status": "pending_evaluator_review"},
        "evidence_gaps": ["Static file mutation only; frontend/runtime/Run-ready is unverified.",
                          "Client exit or timeout alone never proves server stop."]}
    evidence_path = directory / "evidence.json"
    last_persisted = 0.0

    def persist(force: bool = False) -> None:
        nonlocal last_persisted
        if not force and time.monotonic() - last_persisted < 0.5:
            return
        evidence["updated_at"] = timestamp_fields()
        encoded = json.dumps(evidence, ensure_ascii=False, indent=2).encode("utf-8")
        if len(encoded) > EVIDENCE_LIMIT:
            raise ValueError("eval evidence byte limit reached")
        write_capture(evidence_path, evidence)
        last_persisted = time.monotonic()

    persist()
    sdk = None
    began = time.monotonic()
    stopped_at = None
    receipt_at = None
    cancel_sent = False
    terminal = None
    control_error = None
    progress = ToolProgressControl()
    validator_control = None
    event_bytes = 0
    try:
        sdk = SdkPredictionProcess(token, {"base_url": "ws://127.0.0.1:1234",
            "model": model, "workspace_root": str(workspace), "allowed_relative_path": ALIAS,
            "instruction": instruction, "system_prompt": system_prompt,
            "skill_mode": skill_mode, "skills": skill_exposure["skills"] if skill_mode == "discovery" else [],
            "granite_text_tool_bridge": granite_text_tool_bridge,
            "diagnostic_mutation_delay_ms": diagnostic_mutation_delay_ms,
            "diagnostic_request": diagnostic_contract["request"] if diagnostic_contract else None,
            "max_tokens": 512, "max_rounds": 6, "max_tool_calls": locked["max_tool_calls"],
            "require_start_approval": True}, worker_script=SDK_SCRIPT)
        while True:
            now = time.monotonic()
            stop_path = directory / "stop_request.json"
            if stopped_at is None and stop_path.exists():
                request = read_json(stop_path, 4096)
                evidence["stop"] = {"reason": request["reason"],
                                    "requested_at": request["requested_at"],
                                    "observed_at": timestamp_fields()}
                stopped_at = now
                evidence["state"] = "stopping"
                sdk.cancel()
                stop_path.unlink()
                persist()
            if stopped_at is None and now - began >= 60:
                evidence["stop"] = {"reason": "locked execution budget exhausted",
                                    "observed_at": timestamp_fields()}
                stopped_at = now
                evidence["state"] = "stopping"
                sdk.cancel()
                persist()
            if stopped_at is not None and now - stopped_at >= 5:
                evidence["evidence_gaps"].append("No final stop receipt within five seconds.")
                break
            if stopped_at is not None and validator_control:
                validator_control.stop()
            event = sdk.next_event(0.1)
            if event:
                safe = {"observed_at": timestamp_fields(), "data": sanitize_for_log(event)}
                size = len(json.dumps(safe, ensure_ascii=False, indent=2).encode("utf-8")) + 64
                if len(evidence["events"]) >= MAX_EVENTS or event_bytes + size > EVIDENCE_LIMIT - 131072:
                    if stopped_at is None:
                        evidence["stop"] = {"reason": "bounded event budget exhausted",
                                            "observed_at": timestamp_fields()}
                        stopped_at = time.monotonic()
                        sdk.cancel()
                else:
                    evidence["events"].append(safe)
                    event_bytes += size
                kind = event.get("type")
                if progress.observe(event) and stopped_at is None:
                    evidence["stop"] = {"reason": "three equivalent tool outcomes without relevant progress",
                                        "observed_at": timestamp_fields()}
                    stopped_at = time.monotonic()
                    evidence["state"] = "stopping"
                    sdk.cancel()
                if kind == "model_bound":
                    if (event.get("model_info", {}).get("identifier") != model
                            or (transport_review is not None and not matching_reviewed_instance(
                                transport_review, event.get("model_info", {})))):
                        evidence["stop"] = {"reason": "wrong loaded instance",
                                            "observed_at": timestamp_fields()}
                        stopped_at = time.monotonic()
                        sdk.cancel()
                    elif stopped_at is None:
                        sdk.send({"command": "continue"})
                elif kind == "round_started":
                    evidence["state"] = "running"
                elif kind == "cancel_sent":
                    cancel_sent = True
                elif kind == "tool_validation_requested" and stopped_at is None:
                    if validator_control is None:
                        validator_control = WorkspaceValidationControl(eval_id, run_id, directory)
                    validator_control.begin(event)
                elif kind == "result":
                    terminal = event
                    receipt_at = time.monotonic()
                    evidence["result"] = sanitize_for_log(event)
                    break
                elif kind in ("act_interrupted", "error", "not_started", "worker_eof"):
                    terminal = event
                    receipt_at = time.monotonic()
                    break
            if validator_control and stopped_at is None:
                outcome = validator_control.poll()
                if outcome:
                    command, observation = outcome
                    sdk.send(command)
                    evidence["events"].append({"observed_at": timestamp_fields(), "data": observation})
                    progress.observe(observation)
            persist()
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        control_error = type(error).__name__
        if sdk and stopped_at is None:
            stopped_at = time.monotonic()
            evidence["stop"] = {"reason": "controller error", "observed_at": timestamp_fields()}
            try:
                sdk.cancel()
            except (OSError, ValueError):
                evidence["evidence_gaps"].append("Cancel command could not be sent.")
    finally:
        if validator_control:
            validator_control.close()
        if sdk:
            sdk.close()
    if control_error:
        evidence["evidence_gaps"].append("Controller error: " + control_error)
    evidence["verification"]["cancel_command_sent"] = cancel_sent
    evidence["verification"]["tool_progress"] = progress.evidence()
    evidence["verification"]["validator_processes"] = validator_control.receipt if validator_control else None
    evidence["verification"]["within_stop_budget"] = (stopped_at is None or
        receipt_at is not None and receipt_at - stopped_at <= 5)
    after = file_fingerprint(target)
    evidence["fixture"]["sha256_after"] = after
    tool_state = terminal.get("tool_state", {}) if terminal else {}
    evidence["verification"]["tools"] = tool_state
    tool_receipts = all(isinstance(tool_state.get(key), dict)
                        and type(tool_state[key].get("active")) is int for key in ("read", "write"))
    active = sum(tool_state[key]["active"] for key in ("read", "write")) if tool_receipts else None
    if active is not None:
        active += (tool_state.get("validator") or {}).get("active", 0)
    if validator_control and not validator_control.receipt.get("verified"):
        active = None
    if stopped_at is not None:
        time.sleep(0.1)
        evidence["verification"]["readback_stable_after_stop"] = (
            file_fingerprint(target) == after
            and not list(workspace.glob(".worker-mutation-*.tmp")))
    if terminal and terminal.get("type") == "result" and stopped_at is None and active == 0:
        reason = terminal.get("stats", {}).get("stopReason")
        if reason == "eosFound":
            evidence["state"] = "response_received"
            evidence["verification"]["generation"] = "natural_eos"
        else:
            evidence["state"] = "failed"
    elif (stopped_at is not None and cancel_sent and terminal and active == 0
          and evidence["verification"]["within_stop_budget"]
          and evidence["verification"]["readback_stable_after_stop"]):
        if terminal.get("type") == "result" and terminal.get("stats", {}).get("stopReason") == "userStopped":
            evidence["state"] = "verified_cancel"
            evidence["verification"]["generation"] = "server_user_stopped"
        elif (terminal.get("type") == "act_interrupted"
              and terminal.get("last_stop_reason") == "toolCalls"
              and ((tool_state.get("read") or {}).get("aborted", 0)
                   + (tool_state.get("write") or {}).get("aborted", 0)
                   + (tool_state.get("validator") or {}).get("aborted", 0) >= 1)):
            evidence["state"] = "verified_tool_abort"
            evidence["verification"]["generation"] = "last_round_finished_no_followup_started"
        else:
            evidence["state"] = "unverified"
    elif terminal and terminal.get("type") == "not_started":
        evidence["state"] = "not_started"
    else:
        evidence["state"] = "unverified" if stopped_at is not None else "failed"
    evidence["task_verification"] = grade_rename_fixture(eval_id, run_id)
    try:
        current_sources = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths}
        current_skills = expose_skills(skill_mode, skill_id)
        source_stable = (sources == current_sources
                         and skill_exposure["catalog_sha256"] == current_skills["catalog_sha256"])
    except (OSError, ValueError):
        source_stable = False
    evidence["source_verification"] = {"status": "verified" if source_stable else "invalid"}
    if diagnostic_contract:
        evidence["assessment"] = {"status": "transport_diagnostic_not_model_assessment"}
    elif evidence["state"] == "response_received" and source_stable:
        tool_completed = (tool_state["read"].get("completed", 0) >= 2
                          and tool_state["write"].get("completed", 0) == 2)
        evidence["assessment"] = {
            "status": evidence["task_verification"]["status"] if tool_completed else "invalid",
            "scope": "static_workflow_title_edit_only",
            "tool_read_write_readback_verified": tool_completed,
            "assisted_diagnostic": granite_text_tool_bridge}
    else:
        evidence["assessment"] = {"status": "invalid_for_unassisted_task_verdict",
                                  "reason": "generation or stop conditions did not establish a natural completed attempt"}
    evidence["finished_at"] = timestamp_fields()
    persist(force=True)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("start", "run"):
        command = commands.add_parser(name)
        command.add_argument("--eval-id", required=True)
        command.add_argument("--model", required=True)
        command.add_argument("--transport-review-file")
        command.add_argument("--granite-text-tool-bridge", action="store_true")
        command.add_argument("--diagnostic-mutation-delay-ms", type=int, default=0)
        command.add_argument("--diagnostic-mutation-dispatch", action="store_true")
        command.add_argument("--skill-mode", choices=("none", "explicit", "discovery"), default="none")
        command.add_argument("--skill-id")
        command.add_argument("--previous-run")
        command.add_argument("--change-reason")
        if name == "run":
            command.add_argument("--run-id", required=True)
    for name in ("inspect", "stop"):
        command = commands.add_parser(name)
        command.add_argument("--eval-id", required=True)
        command.add_argument("--run-id", required=True)
        if name == "stop":
            command.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        if args.command in ("start", "run"):
            if not args.diagnostic_mutation_delay_ms:
                require_transport_review(args.transport_review_file, args.model)
            load_rename_fixture()
            expose_skills(args.skill_mode, args.skill_id)
            if args.command == "start":
                run_id = uuid4().hex
                argv = [sys.executable, str(Path(__file__).resolve()), "run", "--eval-id", args.eval_id,
                    "--run-id", run_id, "--model", args.model,
                        "--diagnostic-mutation-delay-ms", str(args.diagnostic_mutation_delay_ms)]
                argv.extend(["--skill-mode", args.skill_mode])
                if args.transport_review_file:
                    argv.extend(["--transport-review-file", args.transport_review_file])
                if args.skill_id:
                    argv.extend(["--skill-id", args.skill_id])
                for option in ("previous_run", "change_reason"):
                    if getattr(args, option):
                        argv.extend(["--" + option.replace("_", "-"), getattr(args, option)])
                if args.granite_text_tool_bridge:
                    argv.append("--granite-text-tool-bridge")
                if args.diagnostic_mutation_dispatch:
                    argv.append("--diagnostic-mutation-dispatch")
                child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL, cwd=ROOT,
                                         creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
                deadline = time.monotonic() + 3
                path = run_directory(args.eval_id, run_id) / "evidence.json"
                while not path.exists() and time.monotonic() < deadline:
                    if child.poll() is not None:
                        raise RuntimeError("file task controller startup failed")
                    time.sleep(0.02)
                if not path.exists():
                    raise RuntimeError("file task controller did not publish evidence")
                print(json.dumps({"eval_id": args.eval_id, "run_id": run_id,
                                  "controller_pid": child.pid}, indent=2))
            else:
                report = run(args.eval_id, args.run_id, args.model,
                             args.granite_text_tool_bridge, args.diagnostic_mutation_delay_ms,
                             args.skill_mode, args.skill_id, args.previous_run, args.change_reason,
                             args.diagnostic_mutation_dispatch, transport_review_file=args.transport_review_file)
                print(json.dumps({"eval_id": args.eval_id, "run_id": args.run_id,
                                  "state": report["state"]}, indent=2))
                return 0 if report["state"] in ("response_received", "verified_cancel", "verified_tool_abort") else 2
        elif args.command == "inspect":
            report = read_json(existing_run_directory(args.eval_id, args.run_id) / "evidence.json")
            if report.get("eval_id") != args.eval_id or report.get("run_id") != args.run_id:
                raise ValueError("run evidence belongs to another identity")
            print(json.dumps({key: report.get(key) for key in
                ("eval_id", "run_id", "state", "updated_at", "stop", "result", "verification")},
                ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"stop_request_created": request_stop(args.eval_id, args.run_id, args.reason)}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        print(f"File task control failed: {type(error).__name__}. Inspect evidence; no success is implied.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

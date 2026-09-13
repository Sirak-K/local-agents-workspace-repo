"""One WORKER prediction: diagnostic or baseline-gated tools-free screening."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from uuid import uuid4

from evaluation_paths import PROJECT_ROOT as ROOT, EVALUATION_ROOT, evaluation_file
from evaluation_paths import run_directory as _run_directory

ROLE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "LM-Studio_connections/LM-Studio_for_codex"),
                str(ROOT / "LM-Studio_connections/LM-Studio_observability"),
                str(ROOT / "tools"), str(ROLE / "agent-0-tools"), str(Path(__file__).parent)]
from interruptible_prediction import SdkPredictionProcess, stop_verdict
from lm_studio_user_api_token import resolve_token
from observability_common import sanitize_for_log, timestamp_fields, write_capture
from worker_tool_process_control import WorkerToolProcessControl
from instruction_following_grading import (task_contract, grade_answer, reconstruct_text,
                                          screening_gate, verify_baseline, require_recent_idle)

TERMINAL = {"completed", "verified_cancel", "completed_race", "not_started", "unverified", "failed"}
MAX_DOCUMENT_BYTES = 1048576


def run_directory(eval_id: str, run_id: str) -> Path:
    return _run_directory(eval_id, run_id)


def assessed_run(eval_id: str, run_id: str) -> dict:
    path = run_directory(eval_id, run_id) / "evidence.json"
    evidence = read_json(path, MAX_DOCUMENT_BYTES)
    if evidence.get("eval_id") != eval_id or evidence.get("run_id") != run_id:
        raise ValueError("evidence identity does not match requested eval/run")
    assessment_path = path.with_name("assessment.json")
    if assessment_path.exists():
        assessment = read_json(assessment_path, 32768)
        if (assessment.get("evidence_sha256") != hashlib.sha256(path.read_bytes()).hexdigest()
                or assessment.get("catalog_sha256") != evidence.get("probe", {}).get("catalog_sha256")):
            raise ValueError("manual assessment source changed")
        evidence["assessment"] = assessment
    return evidence


def assess_grounding(eval_id: str, run_id: str, criteria: list[str], reason: str,
                     calibration_reviewed: bool) -> None:
    evidence = assessed_run(eval_id, run_id)
    if (evidence.get("probe", {}).get("id") != "evidence_bound_comparison"
            or evidence.get("assessment", {}).get("status") != "review_required"
            or evidence.get("state") != "completed"
            or evidence.get("baseline_verification", {}).get("status") != "verified"):
        raise ValueError("only a valid unassessed grounding response can receive this review")
    if len(criteria) != 3 or not calibration_reviewed or not reason.strip() or len(reason) > 500:
        raise ValueError("three rubric judgments, calibration review and a bounded rationale are required")
    path = run_directory(eval_id, run_id) / "evidence.json"
    task = task_contract("evidence_bound_comparison")
    assessment = {"eval_id": eval_id, "run_id": run_id,
                  "status": "pass" if criteria == ["pass"] * 3 else "fail",
                  "evaluator": "Codex", "assessed_at": timestamp_fields(),
                  "evidence_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "catalog_sha256": task["catalog_sha256"], "calibration_reviewed": True,
                  "criteria": [{"criterion": text, "status": status}
                               for text, status in zip(task["rubric"], criteria)],
                  "reason": sanitize_for_log(reason)}
    temporary = path.with_name(".assessment-" + uuid4().hex + ".tmp")
    try:
        write_capture(temporary, assessment)
        os.link(temporary, path.with_name("assessment.json"))
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path: Path, byte_limit: int) -> dict:
    with path.open("rb") as handle:
        body = handle.read(byte_limit + 1)
    if len(body) > byte_limit:
        raise ValueError("document byte limit exceeded")
    payload = json.loads(body.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("document must be an object")
    return payload


def request_stop(eval_id: str, run_id: str, reason: str) -> bool:
    if not reason.strip() or len(reason) > 240:
        raise ValueError("a concrete stop reason of 1-240 characters is required")
    directory = run_directory(eval_id, run_id)
    evidence = read_json(directory / "evidence.json", MAX_DOCUMENT_BYTES)
    if evidence.get("eval_id") != eval_id or evidence.get("run_id") != run_id:
        raise ValueError("evidence identity mismatch")
    if evidence["state"] in TERMINAL or evidence.get("stop") is not None:
        return False
    temporary = directory / f".stop-{uuid4().hex}.tmp"
    try:
        write_capture(temporary, {"eval_id": eval_id, "run_id": run_id,
                                  "reason": sanitize_for_log(reason), "requested_at": timestamp_fields()})
        try:
            os.link(temporary, directory / "stop_request.json")
            return True
        except FileExistsError:
            return False
    finally:
        temporary.unlink(missing_ok=True)


def inspect_run(eval_id: str, run_id: str) -> dict:
    evidence = assessed_run(eval_id, run_id)
    return {key: evidence.get(key) for key in
            ("eval_id", "run_id", "state", "updated_at", "stop", "verification")} | {
                "result": None if evidence["result"] is None else {
                    "stats": evidence["result"].get("stats"),
                    "content_preview": text_preview(evidence["result"].get("content")),
                },
                "recent_events": [{"observed_at": event["observed_at"],
                                   "type": event["data"].get("type"),
                                   "content_preview": text_preview(event["data"].get("content"))}
                                  for event in evidence["events"][-5:]],
                "kind": evidence.get("kind"), "probe_id": evidence.get("probe", {}).get("id"),
                "assessment": evidence.get("assessment"),
                "baseline_status": evidence.get("baseline_verification", {}).get("status"),
                "note": "Initial screening is not confirmation; server acknowledgement is required for verified cancellation.",
            }


def text_preview(value):
    if isinstance(value, dict):
        return value.get("text_chunks", [])[:2]
    return value[:160] if isinstance(value, str) else None


def validate_budgets(duration: float, stop_budget: float, max_tokens: int) -> None:
    if not math.isfinite(duration) or not 1 <= duration <= 120:
        raise ValueError("duration must be finite and in [1, 120] seconds")
    if not math.isfinite(stop_budget) or not 1 <= stop_budget <= 5:
        raise ValueError("stop budget must be finite and in [1, 5] seconds")
    if not 1 <= max_tokens <= 1024:
        raise ValueError("max tokens must be in [1, 1024]")


def run(args) -> tuple[str, dict]:
    validate_budgets(args.duration, args.stop_budget, args.max_tokens)
    eval_id = args.eval_id
    token = resolve_token()
    probe_id = getattr(args, "probe_id", None)
    probe = task_contract(probe_id) if probe_id else None
    if probe:
        if args.tool_stop_probe or args.previous_run or args.system_prompt_file:
            raise ValueError("screening has fixed conditioning, no tools or implicit retries")
        if args.duration != probe["duration_seconds"] or args.max_tokens != probe["max_tokens"]:
            raise ValueError("screening budgets must match the locked catalog")
        instruction = probe["instruction"]
    else:
        instruction_path = Path(args.input_file)
        if instruction_path.stat().st_size > 16384:
            raise ValueError("instruction exceeds 16 KiB")
        instruction = instruction_path.read_text(encoding="utf-8")
    system_prompt = ""
    if args.system_prompt_file:
        prompt_path = Path(args.system_prompt_file)
        if prompt_path.stat().st_size > 16384:
            raise ValueError("system prompt exceeds 16 KiB")
        system_prompt = prompt_path.read_text(encoding="utf-8")
    if probe:
        system_prompt = probe["system_prompt"]

    fingerprints = {}
    for source in (Path(__file__), ROOT / "LM-Studio_connections/LM-Studio_for_codex/lm_studio_sdk_prediction.mjs",
                   ROOT / "LM-Studio_connections/LM-Studio_for_codex/interruptible_prediction.py",
                   ROOT / "LM-Studio_connections/LM-Studio_for_codex/package-lock.json",
                   ROLE / "agent-0-tools/worker_tool_process_control.py",
                   Path(__file__).with_name("instruction_following_grading.py"),
                   Path(__file__).with_name("instruction_following_catalog.json"),
                   Path(__file__).with_name("evaluation_paths.py")):
        if source.is_file():
            with source.open("rb") as handle:
                fingerprints[source.name] = hashlib.file_digest(handle, "sha256").hexdigest()

    baseline = None
    baseline_path = None
    if probe:
        if not args.baseline_file:
            raise ValueError("screening requires reviewed effective baseline and live receipts")
        baseline_path = evaluation_file(eval_id, args.baseline_file)
        review = read_json(baseline_path, MAX_DOCUMENT_BYTES)
        if review.get("eval_id") != eval_id:
            raise ValueError("baseline belongs to a different evaluation")
        completion = read_json(run_directory(eval_id, review["completion_run"]) / "evidence.json", MAX_DOCUMENT_BYTES)
        cancellation = read_json(run_directory(eval_id, review["cancellation_run"]) / "evidence.json", MAX_DOCUMENT_BYTES)
        baseline = verify_baseline(review, completion, cancellation, args.model, system_prompt, fingerprints)
        predecessors = [assessed_run(eval_id, identifier) for identifier in (args.predecessor_run or [])]
        screening_gate(probe_id, predecessors)
        if any(item.get("baseline_verification", {}).get("configuration_sha256")
               != baseline["configuration_sha256"] for item in predecessors):
            raise ValueError("configuration changed within the screening")
    if token in instruction or token in system_prompt:
        raise ValueError("API token must never be part of model input")

    previous = args.previous_run
    if previous:
        original = read_json(run_directory(eval_id, previous) / "evidence.json", MAX_DOCUMENT_BYTES)
        if original["state"] not in TERMINAL or not args.change_reason:
            raise ValueError("retry requires a finished original and an explicit change reason")

    run_id = getattr(args, "run_id", None) or uuid4().hex
    directory = _run_directory(eval_id, run_id, create=True)
    document = {
        "eval_id": eval_id, "run_id": run_id,
        "kind": "instruction_following" if probe else "transport_diagnostic", "state": "starting",
        "created_at": timestamp_fields(), "updated_at": timestamp_fields(),
        "contract": {"transport": "lmstudio-js 1.5.0", "model_identifier": args.model,
                     "duration_seconds": args.duration, "stop_budget_seconds": args.stop_budget,
                     "observation_target_seconds": 0.5, "control_poll_seconds": 0.1,
                     "max_tokens": args.max_tokens, "temperature": 0, "fresh_chat": True,
                     "model_tools": [], "owned_process_probe": args.tool_stop_probe,
                     "max_evidence_bytes": MAX_DOCUMENT_BYTES, "max_stream_events": 1000},
        "instruction": sanitize_for_log(instruction),
        "instruction_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest(),
        "source_fingerprints": fingerprints, "system_prompt": sanitize_for_log(system_prompt),
        "previous_run": previous, "change_reason": sanitize_for_log(args.change_reason),
        "events": [], "stop": None, "result": None,
        "verification": {"generation": "not_started", "tools": "not_used"},
        "evidence_gaps": ["Diagnostic run; round/grader and controlled baseline gates are not implemented.",
                          "SDK stderr is not captured; transport errors use secret-free codes.",
                          "Sanitized input/output is not guaranteed byte-exact or free of arbitrary text secrets."],
    }
    if probe:
        document["probe"] = {key: value for key, value in probe.items() if key not in ("expected", "rubric", "grader")}
        document["baseline_verification"] = {key: value for key, value in baseline.items() if not key.startswith("reference_")}
        document["assessment"] = {"status": "not_assessed"}
        document["evidence_gaps"][0] = "Initial screening only; independent fresh-input confirmations are not performed."

    evidence_path = directory / "evidence.json"
    dirty, last_write, event_bytes = True, 0.0, 0
    started = confirmed_not_started = False
    result = result_time = stop_time = None
    cancel_sent = False
    sdk = None
    tools = WorkerToolProcessControl() if args.tool_stop_probe else None
    start_time = time.monotonic()

    def record(event):
        nonlocal dirty, event_bytes
        safe = {"observed_at": timestamp_fields(), "data": sanitize_for_log(event)}
        size = len(json.dumps(safe, ensure_ascii=False, indent=2).encode("utf-8")) + 64
        if len(document["events"]) >= 1000 or event_bytes + size > MAX_DOCUMENT_BYTES - 262144:
            return False
        document["events"].append(safe); event_bytes += size; dirty = True
        return True

    def persist():
        nonlocal last_write, dirty
        document["updated_at"] = timestamp_fields()
        if len(json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8")) > MAX_DOCUMENT_BYTES:
            raise ValueError("eval evidence byte ceiling reached")
        write_capture(evidence_path, document)
        last_write, dirty = time.monotonic(), False

    def stop(reason, requested_at=None):
        nonlocal stop_time, dirty
        if stop_time is not None: return
        stop_time = time.monotonic(); document["state"] = "stopping"
        document["stop"] = {"reason": sanitize_for_log(reason), "requested_at": requested_at or timestamp_fields(),
                            "observed_at": timestamp_fields()}
        dirty = True
        if sdk:
            try: sdk.cancel()
            except (OSError, ValueError): record({"type": "cancel_delivery_failed"})
        if tools: document["verification"]["tools"] = tools.stop(min(args.stop_budget, 3))
        persist()

    try:
        persist()
        if baseline_path:
            claim = baseline_path.parent / (".claim-" + probe_id)
            descriptor = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600); os.close(descriptor)
        print(f"RUN {eval_id}/{run_id}", flush=True)
        sdk = SdkPredictionProcess(token, {"base_url": "ws://127.0.0.1:1234", "model": args.model,
            "instruction": instruction, "system_prompt": system_prompt, "max_tokens": args.max_tokens,
            "require_start_approval": bool(probe)})
        while True:
            now = time.monotonic(); stop_file = directory / "stop_request.json"
            if stop_file.exists() and stop_time is None:
                command = read_json(stop_file, 4096)
                if command.get("eval_id") != eval_id or command.get("run_id") != run_id:
                    raise ValueError("stop request identity mismatch")
                stop(command["reason"], command["requested_at"]); stop_file.unlink()
            if stop_time is None and now - start_time >= args.duration: stop("locked execution budget exhausted")
            if stop_time is not None and now - stop_time >= args.stop_budget:
                document["evidence_gaps"].append("No final server receipt within the locked stop budget."); break
            event = sdk.next_event(0.1)
            if event:
                kind = event.get("type")
                to_record = {"type": "result_received", "stats": event.get("stats")} if kind == "result" else event
                if not record(to_record): stop("bounded evidence capacity reached")
                if kind == "model_bound" and baseline:
                    if event.get("model_info") != baseline["reference_model_info"]:
                        document["baseline_verification"]["status"] = "invalid"; stop("loaded model changed from verified baseline")
                    else:
                        try: require_recent_idle(baseline["review"])
                        except (ValueError, KeyError, OSError):
                            document["baseline_verification"]["status"] = "invalid"; stop("current idle-state evidence expired before generation")
                        else: sdk.send({"command": "continue"})
                elif kind == "prediction_started":
                    started = True
                    if stop_time is None: document["state"] = "running"
                    if tools and stop_time is None:
                        child = "import time; from pathlib import Path; time.sleep(10); Path('late-tool-write.txt').write_text('unexpected')"
                        parent = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); time.sleep(30)"
                        pid = tools.dispatch([sys.executable, "-c", parent], directory); record({"type": "owned_tool_probe_started", "pid": pid})
                elif kind == "cancel_sent": cancel_sent = True
                elif kind == "result":
                    result = event; result_time = time.monotonic(); document["result"] = sanitize_for_log(event); break
                elif kind in ("error", "worker_eof", "not_started"):
                    confirmed_not_started = kind == "not_started" or (kind == "error" and event.get("code") in
                        ("model_not_loaded", "invalid_token_shape", "non_loopback_origin"))
                    if kind != "not_started": stop("SDK transport ended without final result")
                    break
            if time.monotonic() - last_write >= 0.5: persist()
    except BaseException:
        stop("evaluator control or evidence failure"); record({"type": "controller_failure", "code": "control_or_evidence_error"})
        if sdk is None: confirmed_not_started = True
    finally:
        if sdk:
            if started and result is None and stop_time is None: stop("evaluator shutdown without final result")
            sdk.close()
        if tools:
            document["verification"]["tools"] = tools.stop(); tools.close()

    verdict = stop_verdict(result, stop_time is not None, started, confirmed_not_started)
    if verdict == "verified_cancel" and not cancel_sent: verdict = "unverified"
    document["verification"]["generation"] = verdict
    within_budget = stop_time is None or (result_time is not None and result_time - stop_time <= args.stop_budget)
    document["verification"]["within_stop_budget"] = within_budget
    document["verification"]["stop_to_receipt_seconds"] = None if stop_time is None or result_time is None else round(result_time - stop_time, 4)
    document["verification"]["cancel_command_sent"] = cancel_sent
    document["verification"]["sdk_client_exited"] = sdk is None or sdk.process.poll() is not None
    document["state"] = verdict if verdict in TERMINAL else "failed"
    if verdict == "verified_cancel" and not within_budget: document["state"] = "unverified"
    if tools and not document["verification"]["tools"]["verified"]: document["state"] = "unverified"
    document["finished_at"] = timestamp_fields()
    if probe:
        same_config = result is not None and all(document["result"].get(key) == baseline["reference_" + key]
                                                for key in ("load_config", "prediction_config", "model_info"))
        natural_finish = result is not None and result.get("stats", {}).get("stopReason") == "eosFound"
        if document["state"] != "completed" or document["stop"] or not same_config or not natural_finish:
            document["baseline_verification"]["status"] = "invalid"
            document["assessment"] = {"status": "invalid", "reason": "stop, truncation or changed/unverified conditions"}
        else:
            document["assessment"] = grade_answer(probe_id, reconstruct_text(document["result"]["content"]))
    persist()
    return run_id, document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("start", "run"):
        start = commands.add_parser(name, help="diagnostic only; server and selected model must already be active")
        start.add_argument("--eval-id", required=True)
        start.add_argument("--model", required=True, help="exact loaded SDK instance identifier")
        source = start.add_mutually_exclusive_group(required=True)
        source.add_argument("--input-file"); source.add_argument("--probe-id")
        start.add_argument("--baseline-file"); start.add_argument("--predecessor-run", action="append")
        start.add_argument("--system-prompt-file"); start.add_argument("--duration", type=float, default=30)
        start.add_argument("--stop-budget", type=float, default=5); start.add_argument("--max-tokens", type=int, default=512)
        start.add_argument("--previous-run"); start.add_argument("--change-reason"); start.add_argument("--tool-stop-probe", action="store_true")
        if name == "run": start.add_argument("--run-id", required=True, help=argparse.SUPPRESS)
    inspect = commands.add_parser("inspect"); inspect.add_argument("--eval-id", required=True); inspect.add_argument("--run-id", required=True)
    stop = commands.add_parser("stop"); stop.add_argument("--eval-id", required=True); stop.add_argument("--run-id", required=True); stop.add_argument("--reason", required=True)
    assess = commands.add_parser("assess", help="explicit grounding-rubric review; never calls a model")
    assess.add_argument("--eval-id", required=True); assess.add_argument("--run-id", required=True)
    assess.add_argument("--criterion", choices=("pass", "fail"), action="append", required=True)
    assess.add_argument("--reason", required=True); assess.add_argument("--calibration-reviewed", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "start":
            validate_budgets(args.duration, args.stop_budget, args.max_tokens); resolve_token()
            for file in (args.input_file, args.system_prompt_file):
                if file and (not Path(file).is_file() or Path(file).stat().st_size > 16384):
                    raise ValueError("input file unavailable or too large")
            if args.probe_id:
                task_contract(args.probe_id)
                if not args.baseline_file: raise ValueError("baseline evidence is required before screening")
            run_id = uuid4().hex
            argv = [sys.executable, str(Path(__file__).resolve()), "run", "--eval-id", args.eval_id, "--run-id", run_id]
            for option in ("model", "input_file", "system_prompt_file", "duration", "stop_budget", "max_tokens", "previous_run", "change_reason"):
                value = getattr(args, option)
                if value is not None:
                    if option in ("input_file", "system_prompt_file"): value = Path(value).resolve()
                    argv.extend(["--" + option.replace("_", "-"), str(value)])
            for option in ("probe_id", "baseline_file"):
                value = getattr(args, option)
                if value is not None: argv.extend(["--" + option.replace("_", "-"), str(value)])
            for predecessor in args.predecessor_run or []: argv.extend(["--predecessor-run", predecessor])
            if args.tool_stop_probe: argv.append("--tool-stop-probe")
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            deadline = time.monotonic() + 2
            while not (run_directory(args.eval_id, run_id) / "evidence.json").exists() and time.monotonic() < deadline:
                if child.poll() is not None: raise RuntimeError("controller startup failed")
                time.sleep(0.02)
            print(json.dumps({"eval_id": args.eval_id, "run_id": run_id, "controller_pid": child.pid,
                              "state": "starting", "note": "Inspect evidence; startup is not a success verdict."}, indent=2))
            return 0
        if args.command == "run":
            run_id, document = run(args)
            print(json.dumps({"eval_id": args.eval_id, "run_id": run_id, "state": document["state"],
                              "verification": document["verification"]}, indent=2))
            return 0 if document["state"] in ("completed", "verified_cancel") else 2
        if args.command == "assess":
            assess_grounding(args.eval_id, args.run_id, args.criterion, args.reason, args.calibration_reviewed)
            print("Grounding review saved; no continuation or model request was started.")
        elif args.command == "inspect":
            print(json.dumps(inspect_run(args.eval_id, args.run_id), ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"stop_request_created": request_stop(args.eval_id, args.run_id, args.reason)}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError):
        print("Control failed; inspect evidence and process state. No stop success is implied.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

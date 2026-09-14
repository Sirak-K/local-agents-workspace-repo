"""Reconstruct a saved WORKER read interface through public SDK calls; no generation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "LM-Studio_connections/LM-Studio_for_codex"),
               str(ROOT / "LM-Studio_connections/LM-Studio_observability"), str(ROOT / "tools")]
from evaluation_paths import existing_run_directory, create_run_directory, relative_to_project
from evaluation_source_snapshot import capture_source_snapshot, runtime_source_paths, installed_runtime_identity
from interruptible_prediction import SdkPredictionProcess
from lm_studio_user_api_token import resolve_token
from observability_common import sanitize_for_log, timestamp_fields, write_capture
from worker_file_read_evaluation import read_evidence

SDK_SCRIPT = ROOT / "LM-Studio_connections/LM-Studio_for_codex/lm_studio_sdk_prediction.mjs"


def inspect_interface(eval_id: str, run_id: str, source_run_id: str) -> dict:
    source_path = existing_run_directory(eval_id, source_run_id) / "evidence.json"
    source = read_evidence(source_path)
    if (source.get("eval_id") != eval_id or source.get("run_id") != source_run_id
            or source.get("kind") != "workspace_file_read" or source.get("state") != "response_received"
            or source.get("contract", {}).get("project_system_prompt") != ""):
        raise ValueError("inspection requires a terminal same-eval read with no project system prompt")
    fields = source["result"]["prediction_config"]["fields"]
    tools = next(field["value"]["tools"] for field in fields if field["key"] == "llm.prediction.tools")
    if len(tools) != 1 or tools[0].get("function", {}).get("name") != "read_workspace_text":
        raise ValueError("inspection requires the saved single read tool")
    token = resolve_token()
    instruction = source["instruction"]
    if token in instruction or token in json.dumps(tools):
        raise ValueError("credential in interface input")
    directory = create_run_directory(eval_id, run_id)
    report = {"kind": "worker_tool_interface_inspection", "eval_id": eval_id, "run_id": run_id,
              "status": "unverified", "created_at": timestamp_fields(), "generation_requested": False,
              "source_evidence": {"path": relative_to_project(source_path),
                                  "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest()},
              "instruction": instruction, "tool_definitions": tools, "events": [],
              "source_snapshot": capture_source_snapshot(runtime_source_paths([Path(__file__), SDK_SCRIPT])),
              "runtime_identity": installed_runtime_identity(),
              "scope": "current_loaded_template_reconstruction_not_historical_act_request_or_candidate_assessment"}
    sdk = None
    try:
        sdk = SdkPredictionProcess(token, {"base_url": "ws://127.0.0.1:1234",
            "model": source["contract"]["model_identifier"], "instruction": instruction,
            "system_prompt": "", "inspect_model": True, "tool_definitions": tools}, worker_script=SDK_SCRIPT)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and len(report["events"]) < 12:
            event = sdk.next_event(0.1)
            if event is None:
                continue
            report["events"].append(sanitize_for_log(event))
            if event.get("type") == "model_inspection":
                report["status"] = "inspected_without_generation"
                break
            if event.get("type") in ("error", "worker_eof", "not_started"):
                break
    finally:
        if sdk:
            sdk.close()
        report["finished_at"] = timestamp_fields()
        if len(json.dumps(report, ensure_ascii=False).encode("utf-8")) > 524288:
            raise ValueError("inspection evidence exceeds byte budget")
        write_capture(directory / "tool_interface_inspection.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-run-id", required=True)
    args = parser.parse_args()
    report = inspect_interface(args.eval_id, args.run_id, args.source_run_id)
    print(json.dumps({"status": report["status"], "generation_requested": False}, indent=2))
    return 0 if report["status"] == "inspected_without_generation" else 2


if __name__ == "__main__":
    raise SystemExit(main())

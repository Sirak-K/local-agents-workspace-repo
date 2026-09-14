"""Exactly three sequential read-only transport attempts; never candidate evaluation."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from uuid import uuid4

from evaluation_paths import create_run_directory, existing_run_directory, relative_to_project
from worker_file_read_evaluation import run
from observability_common import write_capture, timestamp_fields
from tool_transport_evidence import canonical_sha256 as _canonical, summarize_attempt

FIXTURE = {"service_name": "render-worker", "queue_name": "render-diagnostic",
           "retry_limit": 3, "note": "Unrelated field; do not report unless asked."}


def execute_series(eval_id: str, run_id: str, model: str) -> dict:
    directory = create_run_directory(eval_id, run_id)
    report = {"kind": "tool_transport_reproducibility", "eval_id": eval_id, "run_id": run_id,
              "model_identifier": model, "status": "running", "planned_attempts": 3,
              "created_at": timestamp_fields(), "runs": [], "candidate_assessment": "not_performed",
              "source_set_sha256": None, "instance_reference": None, "runtime_identity": None,
              "scope": "public_sdk_read_transport_same_instance_fresh_chat_not_model_capacity",
              "causal_attribution": "not_performed"}
    destination = directory / "transport_review.json"
    write_capture(destination, report)
    try:
        for _ in range(3):
            attempt_id = uuid4().hex
            report["active_run_id"] = attempt_id
            write_capture(destination, report)
            evidence = run(eval_id, attempt_id, model, 0, reproduction_fixture=FIXTURE,
                           expected_instance_reference=report["instance_reference"])
            summary = summarize_attempt(evidence)
            body = (existing_run_directory(eval_id, attempt_id) / "evidence.json").read_bytes()
            report["runs"].append({"run_id": attempt_id, "evidence_sha256": hashlib.sha256(body).hexdigest(),
                                   **summary})
            report["active_run_id"] = None
            if len(report["runs"]) == 1:
                report["source_set_sha256"] = evidence["source_snapshot"]["source_set_sha256"]
                report["runtime_identity"] = evidence["runtime_identity"]
                report["instance_reference"] = summary["instance_reference"]
            elif (summary["conditions_sha256"] != report["runs"][0]["conditions_sha256"]
                  or summary["instance_reference"] != report["instance_reference"]):
                report["status"] = "invalid_conditions_changed"
                break
            if evidence.get("state") != "response_received" or not summary["instance_reference"]:
                report["status"] = "unverified_execution_stopped"
                break
            write_capture(destination, report)
        if report["status"] == "running":
            report["status"] = ("verified_native_read_transport" if len(report["runs"]) == 3
                                and all(item["succeeded"] for item in report["runs"])
                                else "dispatch_unreliable_tool_evaluation_blocked")
        report["observed_outputs_identical"] = len({_canonical(item["observed_output"])
                                                    for item in report["runs"]}) == 1
        report["public_tool_raw_byte_identity_established"] = (report["observed_outputs_identical"]
            and len(report["runs"]) == 3 and all(item["observed_output"]["complete_raw_available"]
                                                for item in report["runs"]))
        report["event_sequences_identical"] = len({_canonical(item["tool_event_sequence"])
                                                   for item in report["runs"]}) == 1
    except Exception:
        report["status"] = "diagnostic_failed_tool_evaluation_blocked"
        raise
    finally:
        report["finished_at"] = timestamp_fields()
        report["finished_epoch_seconds"] = time.time()
        write_capture(destination, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--execute-series", action="store_true", required=True)
    args = parser.parse_args()
    report = execute_series(args.eval_id, args.run_id, args.model)
    print(json.dumps({"status": report["status"], "attempts": len(report["runs"]),
                      "candidate_assessment": "not_performed"}, indent=2))
    return 0 if report["status"] == "verified_native_read_transport" else 2


if __name__ == "__main__":
    raise SystemExit(main())

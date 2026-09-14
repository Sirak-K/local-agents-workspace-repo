"""Fail-closed admission for tool evaluations after reproducible transport diagnostics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time

from evaluation_paths import existing_run_directory, project_relative_path, relative_to_project
from evaluation_source_snapshot import changed_current_sources, installed_runtime_identity
from tool_transport_evidence import summarize_attempt

MAX_REVIEW_AGE_SECONDS = 1800


def require_transport_review(review_file: str | Path | None, model: str) -> dict:
    if review_file is None:
        raise ValueError("tool evaluation requires a verified tool transport diagnostic review")
    path = project_relative_path(review_file)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32768:
        raise ValueError("unsafe or oversized transport review")
    body = path.read_bytes()
    review = json.loads(body.decode("utf-8"))
    if (review.get("kind") != "tool_transport_reproducibility"
            or review.get("status") != "verified_native_read_transport"
            or review.get("model_identifier") != model
            or not isinstance(review.get("instance_reference"), str)
            or not 0 <= time.time() - review.get("finished_epoch_seconds", 0) <= MAX_REVIEW_AGE_SECONDS
            or len(review.get("runs", [])) != 3):
        raise ValueError("transport review is failed, stale or does not match the model")
    runtime = installed_runtime_identity()
    if runtime != review.get("runtime_identity"):
        raise ValueError("installed runtime changed after transport diagnosis")
    conditions = None
    run_ids = [entry.get("run_id") for entry in review["runs"]]
    if len(set(run_ids)) != 3:
        raise ValueError("transport review requires three distinct attempts")
    for entry in review["runs"]:
        evidence_path = existing_run_directory(review["eval_id"], entry["run_id"]) / "evidence.json"
        if evidence_path.is_symlink() or evidence_path.stat().st_size > 1048576:
            raise ValueError("unsafe or oversized transport evidence")
        evidence_body = evidence_path.read_bytes()
        if hashlib.sha256(evidence_body).hexdigest() != entry.get("evidence_sha256"):
            raise ValueError("transport diagnostic evidence changed")
        evidence = json.loads(evidence_body.decode("utf-8"))
        summary = summarize_attempt(evidence)
        if conditions is None:
            conditions = summary["conditions_sha256"]
        if (evidence.get("eval_id") != review["eval_id"] or evidence.get("run_id") != entry["run_id"]
                or evidence.get("assessment", {}).get("status") != "diagnostic_only"
                or evidence.get("state") != "response_received"
                or evidence.get("source_snapshot", {}).get("source_set_sha256") != review.get("source_set_sha256")
                or changed_current_sources(evidence["source_snapshot"])
                or evidence.get("runtime_identity") != runtime
                or evidence.get("result", {}).get("model_info", {}).get("instanceReference") != review["instance_reference"]
                or not summary["succeeded"] or summary["conditions_sha256"] != conditions
                or any(entry.get(key) != value for key, value in summary.items())):
            raise ValueError("transport diagnostic no longer satisfies its contract")
    return {"path": relative_to_project(path), "sha256": hashlib.sha256(body).hexdigest(),
            "model_identifier": model, "instance_reference": review["instance_reference"],
            "source_set_sha256": review["source_set_sha256"],
            "scope": "native_read_transport_only_task_specific_tool_gates_still_required"}


def matching_reviewed_instance(review: dict, model_info: dict) -> bool:
    return (review.get("model_identifier") == model_info.get("identifier")
            and review.get("instance_reference") == model_info.get("instanceReference"))

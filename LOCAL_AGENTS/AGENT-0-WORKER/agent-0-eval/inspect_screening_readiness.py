"""Bounded, no-generation inspection of conditions needed for WORKER screening."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import time
from uuid import uuid4

from evaluation_paths import PROJECT_ROOT as ROOT, evaluation_directory
ROLE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "LM-Studio_connections/LM-Studio_for_codex"),
                str(ROOT / "LM-Studio_connections/LM-Studio_observability"), str(ROOT / "tools")]
from interruptible_prediction import SdkPredictionProcess
from lm_studio_user_api_token import resolve_token
from observability_common import sanitize_for_log, timestamp_fields, write_capture
from instruction_following_grading import task_contract


def capture(eval_id: str, model: str, model_file: str | None = None) -> tuple[Path, dict]:
    task = task_contract("record_transformation")
    prompt = task["system_prompt"]
    token = resolve_token()
    if token in prompt: raise ValueError("token must not be part of model input")
    report = {"eval_id": eval_id, "kind": "screening_readiness", "created_at": timestamp_fields(),
              "model_identifier": model, "status": "blocked", "generation_requested": False,
              "system_prompt": sanitize_for_log(prompt),
              "system_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
              "catalog_sha256": task["catalog_sha256"], "events": [], "source_fingerprints": {},
              "required_checks": {"loaded_model": "unknown", "short_input_fits_context": "unknown",
                  "effective_configuration": "pending_primary_readback_and_baseline_comparison",
                  "loaded_file_identity": "pending_loaded_identity_comparison",
                  "idle_state": "pending_current_activity_verification",
                  "live_generation_stop": "pending_server_userStopped_receipt",
                  "legitimate_completion": "pending_uninterrupted_completion_receipt",
                  "runner_progression": "contract_tested_pending_live_baseline"},
              "evidence_gaps": ["Saved settings and a file hash do not verify the loaded instance or effective inference.",
                  "Public SDK inspection exposes context/rendered input, not all effective load/sampling values.",
                  "Readiness capture alone never authorizes candidate assessment."]}
    if model_file:
        path = Path(model_file); before = path.stat()
        if path.suffix.lower() != ".gguf" or before.st_size > 4294967296:
            raise ValueError("optional identity capture accepts only a GGUF file up to 4 GiB")
        with path.open("rb") as handle: digest = hashlib.file_digest(handle, "sha256").hexdigest()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise ValueError("model file changed during hashing")
        report["local_file_identity"] = {"filename":path.name, "size_bytes":after.st_size, "sha256":digest,
                                         "observed_at":timestamp_fields(),
                                         "origin":"read-only SHA-256 of explicitly selected local GGUF",
                                         "loaded_identity_verified":False}
    for source in (Path(__file__), Path(__file__).with_name("instruction_following_catalog.json"),
                   Path(__file__).with_name("evaluation_paths.py"),
                   ROOT / "LM-Studio_connections/LM-Studio_for_codex/lm_studio_sdk_prediction.mjs"):
        if source.is_file(): report["source_fingerprints"][source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
        else: report["evidence_gaps"].append("Inspection source missing: " + source.name)
    sdk = None
    try:
        sdk = SdkPredictionProcess(token, {"base_url": "ws://127.0.0.1:1234", "model": model,
                                   "inspect_model": True, "system_prompt": prompt, "instruction": task["instruction"]})
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            event = sdk.next_event(0.1)
            if event is None: continue
            report["events"].append({"observed_at": timestamp_fields(), "data": sanitize_for_log(event)})
            if event.get("type") == "model_inspection":
                context, tokens = event.get("context_length"), event.get("input_tokens")
                report["required_checks"]["loaded_model"] = "observed"
                report["required_checks"]["short_input_fits_context"] = ("observed" if type(context) is int
                    and type(tokens) is int and tokens + task["max_tokens"] <= context else "failed")
                break
            if event.get("type") in ("error", "worker_eof", "not_started"):
                if event.get("code") == "model_not_loaded": report["required_checks"]["loaded_model"] = "not_loaded"
                break
            if len(report["events"]) >= 8:
                report["evidence_gaps"].append("Inspection event ceiling reached."); break
        else: report["evidence_gaps"].append("Inspection did not finish within five seconds.")
    finally:
        if sdk: sdk.close()
    report["finished_at"] = timestamp_fields()
    destination = evaluation_directory(eval_id, create=True) / ("readiness-" + uuid4().hex + ".json")
    write_capture(destination, report)
    return destination, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--model", required=True, help="exact already-loaded SDK identifier")
    parser.add_argument("--model-file", help="optional explicit GGUF identity read; no model processing")
    args = parser.parse_args()
    try:
        path, report = capture(args.eval_id, args.model, args.model_file)
        print(path.relative_to(ROOT).as_posix())
        print("Status:", report["status"], "Loaded model:", report["required_checks"]["loaded_model"])
        return 2 if report["status"] == "blocked" else 0
    except (OSError, ValueError, RuntimeError):
        print("Readiness capture failed; no generation or readiness success is implied.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

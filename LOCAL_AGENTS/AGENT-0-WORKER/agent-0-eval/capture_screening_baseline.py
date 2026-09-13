"""Capture a provenance-linked review of the first WORKER screening conditions.

This reads existing live diagnostic receipts; it performs no generation or load.
The evaluator still owns judgment about whether these conditions are suitable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

from controlled_run import ROOT, LOG_ROOT, read_json, MAX_DOCUMENT_BYTES
from instruction_following_grading import load_catalog
from observability_common import timestamp_fields, write_capture


def _run_text(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, timeout=3, check=True)
    if len(result.stdout) > 1024:
        raise ValueError("version output exceeded budget")
    return result.stdout.decode("utf-8", "replace").strip()


def capture(completion_run: str, cancellation_run: str, readiness_path: Path) -> Path:
    from controlled_run import run_directory
    completion_path = run_directory(completion_run) / "evidence.json"
    cancellation_path = run_directory(cancellation_run) / "evidence.json"
    readiness_path = readiness_path.resolve()
    readiness_path.relative_to(LOG_ROOT.resolve())
    completion = read_json(completion_path, MAX_DOCUMENT_BYTES)
    cancellation = read_json(cancellation_path, MAX_DOCUMENT_BYTES)
    readiness = read_json(readiness_path, MAX_DOCUMENT_BYTES)
    result = completion["result"]
    model = result["model_info"]
    file_identity = readiness["local_file_identity"]
    model_relative = Path(model["path"])
    if model_relative.is_absolute() or ".." in model_relative.parts or model_relative.suffix.lower() != ".gguf":
        raise ValueError("loaded GGUF path is not a safe relative model path")
    model_file = Path.home() / ".lmstudio/models" / model_relative
    if (completion["state"] != "completed" or completion["stop"] is not None
            or result["content"].strip() != "OK" or result["stats"]["stopReason"] != "eosFound"
            or cancellation["state"] != "verified_cancel"
            or cancellation["result"]["stats"]["stopReason"] != "userStopped"
            or model["identifier"] != cancellation["result"]["model_info"]["identifier"]
            or readiness["model_identifier"] != model["identifier"]
            or file_identity["size_bytes"] != model["sizeBytes"]
            or model_relative.name != file_identity["filename"]
            or not model_file.is_file()):
        raise ValueError("live receipt and captured local GGUF identity do not match")
    if model_file.stat().st_size > 4294967296:
        raise ValueError("local GGUF exceeds identity capture budget")
    with model_file.open("rb") as handle:
        current_sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
    if (model_file.stat().st_size != file_identity["size_bytes"]
            or current_sha256 != file_identity["sha256"]):
        raise ValueError("local GGUF changed since identity capture")
    if (not result.get("load_config", {}).get("fields")
            or not result.get("prediction_config", {}).get("fields")
            or cancellation["verification"].get("cancel_command_sent") is not True):
        raise ValueError("effective configs or stop command receipt unavailable")
    load = {item["key"]: item["value"] for item in result["load_config"]["fields"]}
    prediction = {item["key"]: item["value"] for item in result["prediction_config"]["fields"]}
    catalog = load_catalog()
    if (load.get("llm.load.contextLength") != model["contextLength"]
            or load.get("llm.load.numParallelSessions") != 1
            or prediction.get("llm.prediction.temperature") != 0
            or prediction.get("llm.prediction.maxPredictedTokens") != {"checked": True, "value": catalog["max_tokens"]}
            or prediction.get("llm.prediction.tools") != {"type": "none"}):
        raise ValueError("actual readback differs from controlled minimal screening conditions")
    template = prediction["llm.prediction.promptTemplate"]["jinjaPromptTemplate"]["template"]
    rendered = next(item["data"] for item in readiness["events"] if item["data"]["type"] == "model_inspection")
    prompt = "".join(rendered["rendered_input"]["text_chunks"])
    if (not template.get("sha256") or "<|start_of_role|>system" in prompt or "<tools>" in prompt
            or "Transform this record:" not in prompt
            or rendered["input_tokens"] + catalog["max_tokens"] > model["contextLength"]):
        raise ValueError("minimal user-only rendered prompt not verified")
    session = LOG_ROOT / uuid4().hex
    session.mkdir(parents=True, exist_ok=False)
    identity = {"model_file_identity": {"model_path": model["path"],
               "size_bytes": model["sizeBytes"], "sha256": current_sha256,
               "quantization": model["quantization"], "loaded_instance_reference": model["instanceReference"]},
        "sources": [
            {"path": completion_path.relative_to(ROOT).as_posix(),
             "sha256": hashlib.sha256(completion_path.read_bytes()).hexdigest(),
             "pointer": ["result", "model_info"]},
            {"path": readiness_path.relative_to(ROOT).as_posix(),
             "sha256": hashlib.sha256(readiness_path.read_bytes()).hexdigest(),
             "pointer": ["local_file_identity"]}],
        "verification": "Loaded SDK path/size agree with captured local GGUF hash; publisher match is separately documented for this candidate, actual loaded bytes are not independently exposed."}
    identity_path = session / "model_identity_review.json"
    write_capture(identity_path, identity)
    application = Path.home() / "AppData/Local/Programs/LM Studio/LM Studio.exe"
    app_version = _run_text(["pwsh", "-NoProfile", "-Command",
                             "(Get-Item -LiteralPath '" + str(application) + "').VersionInfo.ProductVersion"])
    environment = {"environment_versions": {"lm_studio_app": app_version,
        "lms_cli": _run_text(["lms", "--version"]), "node": _run_text(["node", "--version"]),
        "sdk": json.loads((ROOT / "LM-Studio_connections/LM-Studio_for_codex/package.json")
                           .read_text(encoding="utf-8"))["dependencies"]["@lmstudio/sdk"]},
        "observed_at": timestamp_fields()}
    environment_path = session / "environment_versions.json"
    write_capture(environment_path, environment)

    def observation(condition: str, value, source: Path, pointer: list, rationale: str) -> dict:
        return {"condition": condition, "status": "verified", "value": value,
                "rationale": rationale, "evidence_reference": {
                    "path": source.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "pointer": pointer}}

    fields = result["prediction_config"]["fields"]
    template_index = next(index for index, item in enumerate(fields)
                          if item["key"] == "llm.prediction.promptTemplate")
    review = {"model_identifier": model["identifier"], "completion_run": completion_run,
              "cancellation_run": cancellation_run,
              "catalog_sha256": catalog["sha256"],
              "system_prompt_sha256": hashlib.sha256(b"").hexdigest(),
              "created_at": timestamp_fields(),
              "observations": [
                  observation("model_file_identity", identity["model_file_identity"], identity_path,
                              ["model_file_identity"], identity["verification"]),
                  observation("load_configuration", result["load_config"], completion_path,
                              ["result", "load_config"],
                              "Actual SDK completion readback: explicit context, GPU ratio and one parallel session."),
                  observation("sampling_configuration", result["prediction_config"], completion_path,
                              ["result", "prediction_config"],
                              "Actual SDK completion readback: temperature zero, 1024 cap and no tools."),
                  observation("template", fields[template_index]["value"], completion_path,
                              ["result", "prediction_config", "fields", template_index, "value"],
                              "Actual SDK template and no-system rendered input inspected; local snapshot differs only by final newline."),
                  observation("environment_versions", environment["environment_versions"], environment_path,
                              ["environment_versions"], "Actual local app, CLI, Node and pinned SDK versions captured.")]}
    destination = session / "baseline_source_review.json"
    write_capture(destination, review)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--completion-run", required=True)
    parser.add_argument("--cancellation-run", required=True)
    parser.add_argument("--readiness-file", type=Path, required=True)
    args = parser.parse_args()
    print(capture(args.completion_run, args.cancellation_run, args.readiness_file)
          .relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

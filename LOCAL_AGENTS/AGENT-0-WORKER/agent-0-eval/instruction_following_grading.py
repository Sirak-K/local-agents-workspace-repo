"""Locked tools-free screening contracts, structural grading and progression gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time

from evaluation_paths import PROJECT_ROOT as ROOT

CATALOG = Path(__file__).with_name("instruction_following_catalog.json")


def load_catalog() -> dict:
    body = CATALOG.read_bytes()
    if len(body) > 32768 or body.startswith(b"\xef\xbb\xbf"):
        raise ValueError("catalog must be bounded UTF-8 without BOM")
    catalog = json.loads(body.decode("utf-8"))
    tasks = catalog["tasks"]
    if catalog["version"] != 1 or catalog["attempts_per_task"] != 1 or len(tasks) != 3:
        raise ValueError("unsupported screening contract")
    if len({task["id"] for task in tasks}) != len(tasks):
        raise ValueError("duplicate task identifiers")
    catalog["sha256"] = hashlib.sha256(body).hexdigest()
    return catalog


def task_contract(identifier: str) -> dict:
    catalog = load_catalog()
    for task in catalog["tasks"]:
        if task["id"] == identifier:
            return task | {"catalog_sha256": catalog["sha256"], "catalog_version": catalog["version"],
                           "duration_seconds": catalog["duration_seconds"], "max_tokens": catalog["max_tokens"],
                           "system_prompt": catalog["system_prompt"], "context_policy": catalog["context_policy"],
                           "stop_policy": catalog["stop_policy"]}
    raise ValueError("task is not in the initial tools-free catalog")


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(_):
    raise ValueError("non-standard JSON constant")


def grade_answer(identifier: str, answer: str) -> dict:
    task = task_contract(identifier)
    if task["grader"] == "evidence_bound_comparison":
        return {"status": "review_required", "rubric": task["rubric"],
                "note": "Use the pre-labelled calibration; no keyword-based semantic PASS."}
    try:
        actual = json.loads(answer, object_pairs_hook=_object, parse_constant=_invalid_constant)
    except (ValueError, TypeError):
        return {"status": "fail", "reason": "not exactly one valid JSON value"}
    expected = task["expected"]
    if task["grader"] == "record_transformation":
        valid = (isinstance(actual, dict) and set(actual) == set(expected)
                 and type(actual.get("name")) is str and type(actual.get("value")) is int and actual == expected)
    else:
        valid = (isinstance(actual, list) and len(actual) == len(expected)
                 and all(isinstance(item, dict) and set(item) == {"id", "destination"}
                         and type(item["id"]) is str and type(item["destination"]) is str for item in actual)
                 and actual == expected)
    return {"status": "pass" if valid else "fail",
            "reason": "all content, type, ordering and scope checks matched" if valid
            else "content, type, ordering or scope mismatch"}


def reconstruct_text(value) -> str:
    if isinstance(value, str): return value
    if isinstance(value, dict) and isinstance(value.get("text_chunks"), list): return "".join(value["text_chunks"])
    raise ValueError("answer text is unavailable")


def screening_gate(identifier: str, previous: list[dict]) -> None:
    catalog = load_catalog(); identifiers = [task["id"] for task in catalog["tasks"]]
    if identifier not in identifiers: raise ValueError("only initial tools-free screening is implemented")
    position = identifiers.index(identifier)
    if len(previous) != position: raise ValueError("missing predecessor, duplicate attempt or screening already finished")
    for expected_id, evidence in zip(identifiers, previous):
        probe = evidence.get("probe", {}); assessment = evidence.get("assessment", {})
        if (probe.get("id") != expected_id or probe.get("catalog_sha256") != catalog["sha256"]
                or evidence.get("state") != "completed" or evidence.get("stop") is not None
                or evidence.get("baseline_verification", {}).get("status") != "verified"
                or assessment.get("status") != "pass"):
            raise ValueError("predecessor failed, invalid, unreviewed or contract changed")


def screening_summary(evidence: list[dict]) -> dict:
    statuses = [item.get("assessment", {}).get("status", "unassessed") for item in evidence]
    valid = len(evidence) == 3 and statuses == ["pass"] * 3
    if valid:
        identifiers = [task["id"] for task in load_catalog()["tasks"]]
        for identifier, item in zip(identifiers, evidence):
            try: screening_gate(identifier, evidence[:identifiers.index(identifier)])
            except ValueError: valid = False
            valid = valid and (item.get("probe", {}).get("id") == identifier
                               and item.get("state") == "completed" and not item.get("stop")
                               and item.get("baseline_verification", {}).get("status") == "verified"
                               and item.get("probe", {}).get("catalog_sha256") == load_catalog()["sha256"])
    return {"status": "preliminary_success" if valid else "incomplete_or_requires_investigation",
            "assessments": statuses, "confirmed": False, "file_tool_progression_allowed": False,
            "note": "Three task-level results do not prove broad role reliability; no automatic file/tool progression without verified tool and scope gates."}


def require_recent_idle(review: dict) -> None:
    observation = next(item for item in review["observations"] if item["condition"] == "idle_state")
    reference = observation["evidence_reference"]
    relative = Path(reference["path"])
    if relative.is_absolute() or ".." in relative.parts: raise ValueError("idle evidence path must be project-relative")
    path = (ROOT / relative).resolve(); path.relative_to(ROOT.resolve())
    with path.open("rb") as handle: body = handle.read(1048577)
    if len(body) > 1048576 or hashlib.sha256(body).hexdigest() != reference["sha256"]:
        raise ValueError("idle evidence changed")
    value = json.loads(body.decode("utf-8")); pointer = reference.get("observed_at_pointer")
    if not isinstance(pointer, list) or not pointer: raise ValueError("idle evidence needs its captured observation timestamp")
    for part in pointer: value = value[part]
    age_ms = time.time() * 1000 - value if type(value) in (float, int) else -1
    if not 0 <= age_ms <= 5000: raise ValueError("idle observation is missing, stale or future-dated")


def verify_baseline(review: dict, completion: dict, cancellation: dict, model: str,
                    prompt: str, source_fingerprints: dict) -> dict:
    if (completion.get("state") != "completed" or completion.get("stop") is not None
            or completion.get("contract", {}).get("model_identifier") != model
            or completion.get("contract", {}).get("owned_process_probe")
            or cancellation.get("state") != "verified_cancel"
            or cancellation.get("contract", {}).get("model_identifier") != model
            or cancellation.get("result", {}).get("stats", {}).get("stopReason") != "userStopped"
            or cancellation.get("verification", {}).get("within_stop_budget") is not True
            or cancellation.get("verification", {}).get("cancel_command_sent") is not True):
        raise ValueError("real matching completion and cancellation receipts are required")
    if (reconstruct_text(completion.get("result", {}).get("content")).strip() != "OK"
            or completion.get("result", {}).get("stats", {}).get("stopReason") != "eosFound"):
        raise ValueError("legitimate completion gate did not produce OK")
    for document in (completion, cancellation):
        if any(document.get("source_fingerprints", {}).get(key) != value for key, value in source_fingerprints.items()):
            raise ValueError("transport/controller changed since live verification")
    result = completion.get("result", {})
    if not all(isinstance(result.get(key), dict) and result[key] for key in ("load_config", "prediction_config", "model_info")):
        raise ValueError("effective server configuration readback is missing")
    if any(not isinstance(result[key].get("fields"), list) or not result[key]["fields"] for key in ("load_config", "prediction_config")):
        raise ValueError("empty effective configuration cannot establish a baseline")
    required = {"model_file_identity", "load_configuration", "sampling_configuration", "template", "environment_versions", "idle_state"}
    observations = review.get("observations", [])
    if {item.get("condition") for item in observations} != required or len(observations) != len(required):
        raise ValueError("required effective-condition review is incomplete")
    for observation in observations:
        if (observation.get("status") != "verified" or observation.get("value") is None
                or not observation.get("evidence_reference") or not observation.get("rationale")):
            raise ValueError("unknown conditions or provenance-free declarations cannot pass")
        reference = observation["evidence_reference"]
        if not isinstance(reference, dict) or not isinstance(reference.get("path"), str):
            raise ValueError("condition requires a captured project-relative JSON source")
        relative = Path(reference["path"])
        if relative.is_absolute() or ".." in relative.parts: raise ValueError("condition source must stay in the workspace")
        path = (ROOT / relative).resolve(); path.relative_to(ROOT.resolve())
        with path.open("rb") as handle: body = handle.read(1048577)
        if len(body) > 1048576 or hashlib.sha256(body).hexdigest() != reference.get("sha256"):
            raise ValueError("condition source missing, too large or changed")
        value = json.loads(body.decode("utf-8"))
        for part in reference.get("pointer", []): value = value[part]
        if json.dumps(value, sort_keys=True) != json.dumps(observation["value"], sort_keys=True):
            raise ValueError("review value differs from primary captured evidence")
    if (review.get("model_identifier") != model
            or review.get("system_prompt_sha256") != hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            or review.get("catalog_sha256") != load_catalog()["sha256"]):
        raise ValueError("model, conditioning or catalog changed since baseline review")
    configuration = {"conditions": {item["condition"]: item["value"] for item in observations
                                     if item["condition"] not in ("idle_state", "environment_versions")},
                     "system_prompt": prompt, "load_config": result["load_config"],
                     "prediction_config": result["prediction_config"], "model_tools": [], "model_skills": []}
    require_recent_idle(review)
    fingerprint = hashlib.sha256(json.dumps(configuration, ensure_ascii=False, sort_keys=True,
                                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    return {"status": "verified", "configuration_sha256": fingerprint, "review": review,
            "reference_load_config": result["load_config"], "reference_prediction_config": result["prediction_config"],
            "reference_model_info": result["model_info"],
            "note": "Primary receipts plus explicit evaluator baseline review; no cause/model verdict implied."}

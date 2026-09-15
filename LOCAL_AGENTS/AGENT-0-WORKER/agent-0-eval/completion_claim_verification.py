"""Compare an exact candidate completion claim with independent task evidence."""
from __future__ import annotations

import hashlib


def observed_task_outcome(attempt_valid: bool, task_passed: bool) -> str:
    """Keep invalid evaluation conditions distinct from a valid task failure."""
    if type(attempt_valid) is not bool or type(task_passed) is not bool:
        raise TypeError("completion outcome inputs must be booleans")
    if not attempt_valid:
        return "invalid"
    return "success" if task_passed else "failure"


def _result_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("text_chunks"), list):
        chunks = value["text_chunks"]
        return "".join(chunks) if all(isinstance(chunk, str) for chunk in chunks) else ""
    return ""


def verify_completion_claim(result_content, observed_outcome: str, claim: dict) -> dict:
    """Return report calibration separately from the independently observed outcome."""
    if observed_outcome not in {"success", "failure", "invalid"}:
        raise ValueError("unsupported observed completion outcome")
    if (not isinstance(claim, dict)
            or set(claim) != {"success_prefix", "failure_prefix"}
            or not all(isinstance(value, str) and value.strip() == value and value
                       for value in claim.values())
            or claim["success_prefix"] == claim["failure_prefix"]):
        raise ValueError("invalid completion claim contract")
    text = _result_text(result_content)
    lines = text.splitlines()
    first_line = lines[0] if lines else ""
    if first_line == claim["success_prefix"]:
        reported = "success"
    elif first_line == claim["failure_prefix"]:
        reported = "failure"
    else:
        reported = "unparseable"
    status = ("unassessable" if observed_outcome == "invalid"
              else "consistent" if reported == observed_outcome else "inconsistent")
    return {
        "status": status,
        "reported_outcome": reported,
        "observed_outcome": observed_outcome,
        "required_first_line": [claim["success_prefix"], claim["failure_prefix"]],
        "response_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }

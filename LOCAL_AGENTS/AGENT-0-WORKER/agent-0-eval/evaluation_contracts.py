"""Load exact tools-free task inputs and independently grade a structured edit.

Task text and context live in bounded data files, not executable source. This
owner does not decide model-vs-harness fault or authorize filesystem tools.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from json_document_comparison import parse_json_document, same_json_document


CATALOG = Path(__file__).with_name("structured_edit_catalog.json")
MAX_CATALOG_BYTES = 16384
MAX_CONTEXT_BYTES = 4096


def _utf8_bytes(path: Path, limit: int) -> bytes:
    with path.open("rb") as handle:
        body = handle.read(limit + 1)
    if len(body) > limit or body.startswith(b"\xef\xbb\xbf"):
        raise ValueError("task source must be bounded UTF-8 without BOM")
    body.decode("utf-8")
    return body


def task_contract(identifier: str) -> dict:
    raw = _utf8_bytes(CATALOG, MAX_CATALOG_BYTES)
    catalog = parse_json_document(raw.decode("utf-8"))
    if not isinstance(catalog, dict) or catalog.get("version") != 2 or not isinstance(catalog.get("tasks"), list):
        raise ValueError("unsupported task catalog")
    tasks = catalog["tasks"]
    if (not 1 <= len(tasks) <= 8 or not all(isinstance(item, dict) for item in tasks)
            or len({item.get("id") for item in tasks}) != len(tasks)):
        raise ValueError("invalid task catalog identity")
    task = next((item for item in tasks if item["id"] == identifier), None)
    if task is None or task.get("grader") != "exact_json_document" or task.get("tools") != []:
        raise ValueError("task is not a supported tools-free structured edit")
    context = task.get("context")
    if not isinstance(context, dict) or context.get("role") != "system":
        raise ValueError("unsupported context role")
    filename = context.get("file")
    if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(".md"):
        raise ValueError("context file must be a local markdown fixture")
    context_body = _utf8_bytes(CATALOG.with_name(filename), MAX_CONTEXT_BYTES)
    context_hash = hashlib.sha256(context_body).hexdigest()
    if context_hash != context.get("sha256"):
        raise ValueError("context fixture does not match the locked hash")
    if (not isinstance(task.get("instruction"), str) or not task["instruction"].strip()
            or not isinstance(task.get("expected"), (dict, list)) or not task["expected"]
            or task.get("temperature") != 0
            or not isinstance(task.get("duration_seconds"), int)
            or not isinstance(task.get("stop_budget_seconds"), int)
            or not isinstance(task.get("max_tokens"), int)):
        raise ValueError("incomplete structured edit contract")
    return task | {"catalog_sha256": hashlib.sha256(raw).hexdigest(),
                   "context_text": context_body.decode("utf-8")}


def grade_answer(identifier: str, answer: str, *, contract: dict | None = None) -> dict:
    task = contract if contract is not None else task_contract(identifier)
    if task["id"] != identifier:
        raise ValueError("grader task identity mismatch")
    expected = task["expected"]
    try:
        actual = parse_json_document(answer)
    except (ValueError, TypeError):
        return {"status": "fail", "reason": "not exactly one valid JSON document"}
    matched = same_json_document(actual, expected)
    return {"status": "pass" if matched else "fail",
            "reason": "requested edits and untouched values match" if matched
            else "requested edit, type, or preservation mismatch"}

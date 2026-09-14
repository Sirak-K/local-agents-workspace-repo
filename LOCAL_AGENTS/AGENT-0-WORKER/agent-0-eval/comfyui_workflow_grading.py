"""Prepare and independently grade one static ComfyUI UI-workflow title edit.

This does not validate installed nodes, frontend opening or executable prompts.
It never starts ComfyUI, reads model weights or queues generation.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
import stat

from evaluation_paths import PROJECT_ROOT, existing_run_directory
from json_document_comparison import parse_json_document, same_json_document


MANIFEST = Path(__file__).with_name("workflow_rename_fixture.json")
SNAPSHOT = PROJECT_ROOT / "model_evaluations/comfy_ui_eval-playground/source_snapshots/workflow_reference.json"
CONTEXT = Path(__file__).resolve().parents[1] / "agent-0-context/comfyui_workflow_editing.md"
MAX_MANIFEST_BYTES = 16384
MAX_WORKFLOW_BYTES = 262144
MAX_CONTEXT_BYTES = 8192


def _read_bounded(path: Path, limit: int) -> bytes:
    with path.open("rb") as handle:
        body = handle.read(limit + 1)
    if len(body) > limit or body.startswith(b"\xef\xbb\xbf"):
        raise ValueError("source is oversized or has a UTF-8 BOM")
    body.decode("utf-8")
    return body


def _parse_json(body: bytes):
    return parse_json_document(body.decode("utf-8"))


def _ordinary_path(path: Path) -> None:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or (getattr(info, "st_file_attributes", 0)
                                   & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
        raise ValueError("fixture path is a link or reparse point")


def load_rename_fixture() -> dict:
    manifest_body = _read_bounded(MANIFEST, MAX_MANIFEST_BYTES)
    manifest = _parse_json(manifest_body)
    if (not isinstance(manifest, dict) or manifest.get("version") != 1
            or manifest.get("source") != SNAPSHOT.relative_to(PROJECT_ROOT).as_posix()
            or manifest.get("workspace_alias") != "workflow.json"
            or manifest.get("context", {}).get("file") != CONTEXT.relative_to(PROJECT_ROOT).as_posix()
            or manifest["context"].get("role") != "system"):
        raise ValueError("unsupported workflow fixture contract")
    for path in (SNAPSHOT.parent, SNAPSHOT, CONTEXT.parent, CONTEXT):
        _ordinary_path(path)
    source_body = _read_bounded(SNAPSHOT, MAX_WORKFLOW_BYTES)
    context_body = _read_bounded(CONTEXT, MAX_CONTEXT_BYTES)
    if (hashlib.sha256(source_body).hexdigest() != manifest.get("source_sha256")
            or hashlib.sha256(context_body).hexdigest() != manifest["context"].get("sha256")):
        raise ValueError("workflow or context changed from the locked fixture")
    workflow = _parse_json(source_body)
    if (not isinstance(workflow, dict) or workflow.get("version") != 0.4
            or not isinstance(workflow.get("nodes"), list)
            or not isinstance(workflow.get("links"), list)):
        raise ValueError("expected UI-workflow shape is absent")
    nodes = workflow["nodes"]
    if (not all(isinstance(node, dict) and type(node.get("id")) is int
                and isinstance(node.get("title"), str) for node in nodes)
            or len({node["id"] for node in nodes}) != len(nodes)):
        raise ValueError("source node identities are invalid")
    targets = manifest.get("target_titles")
    if (not isinstance(targets, dict) or set(targets) != {"68", "69"}
            or not all(isinstance(value, str) and value.strip() for value in targets.values())
            or not all(any(node["id"] == int(identifier) for node in nodes) for identifier in targets)):
        raise ValueError("target titles do not match the source fixture")
    return manifest | {"manifest_sha256": hashlib.sha256(manifest_body).hexdigest(),
                       "source_body": source_body, "source_document": workflow,
                       "context_text": context_body.decode("utf-8")}


def prepare_rename_fixture(eval_id: str, run_id: str) -> dict:
    """Copy the pinned source into a new, evaluator-owned run workspace once."""
    fixture = load_rename_fixture()
    directory = existing_run_directory(eval_id, run_id)
    _ordinary_path(directory)
    workspace = directory / "workspace"
    workspace.mkdir(exist_ok=False)
    target = workspace / fixture["workspace_alias"]
    with target.open("xb") as handle:
        handle.write(fixture["source_body"])
    receipt = {key: value for key, value in fixture.items()
               if key not in ("source_body", "source_document", "context_text")}
    receipt.update(eval_id=eval_id, run_id=run_id,
                   created_at=datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"))
    with (directory / "fixture_manifest.json").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return {"path": target, "manifest_sha256": fixture["manifest_sha256"],
            "source_sha256": fixture["source_sha256"], "context": fixture["context"],
            "instruction": fixture["instruction"]}


def grade_rename_fixture(eval_id: str, run_id: str) -> dict:
    """Compare disk state to the source with only the requested node titles changed."""
    fixture = load_rename_fixture()
    directory = existing_run_directory(eval_id, run_id)
    try:
        recorded = _parse_json(_read_bounded(directory / "fixture_manifest.json", MAX_MANIFEST_BYTES))
        if (recorded.get("eval_id"), recorded.get("run_id"), recorded.get("manifest_sha256")) != (
                eval_id, run_id, fixture["manifest_sha256"]):
            raise ValueError("fixture identity or contract changed")
    except (OSError, ValueError):
        return {"status": "invalid", "reason": "run fixture contract missing or changed"}
    workspace = directory / "workspace"
    target = workspace / fixture["workspace_alias"]
    try:
        for path in (directory, workspace, target):
            _ordinary_path(path)
    except (OSError, ValueError):
        return {"status": "invalid", "reason": "workspace path missing or unsafe",
                "manifest_sha256": fixture["manifest_sha256"]}
    try:
        after_body = _read_bounded(target, MAX_WORKFLOW_BYTES)
        actual = _parse_json(after_body)
    except (OSError, ValueError):
        return {"status": "fail", "reason": "edited workflow is missing, oversized or invalid UTF-8/JSON",
                "manifest_sha256": fixture["manifest_sha256"]}
    expected = copy.deepcopy(fixture["source_document"])
    for node in expected["nodes"]:
        if str(node["id"]) in fixture["target_titles"]:
            node["title"] = fixture["target_titles"][str(node["id"])]
    matched = same_json_document(actual, expected)
    return {"status": "pass" if matched else "fail",
            "reason": "requested node titles and all other workflow data match" if matched
            else "wrong/missing title or unrelated workflow data changed",
            "source_sha256": fixture["source_sha256"],
            "manifest_sha256": fixture["manifest_sha256"],
            "after_sha256": hashlib.sha256(after_body).hexdigest(),
            "checks": {"ui_json_parsed": True, "only_requested_titles_changed": matched,
                       "frontend_opened": False, "workflow_executed": False}}

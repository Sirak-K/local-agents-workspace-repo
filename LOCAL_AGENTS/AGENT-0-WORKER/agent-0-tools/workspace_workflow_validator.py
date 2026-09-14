"""Fixed trusted static-validator subprocess; no candidate code or shell.

Entrypoint arguments are supplied by the evaluator, never by a candidate tool.
Receipt files are outside the model-visible workspace.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent-0-eval"))
from evaluation_paths import existing_run_directory
from comfyui_workflow_validation import validate_workflow_text, validate_workflow_schema


def validate(eval_id: str, run_id: str, receipt_id: str) -> int:
    if not receipt_id.isdecimal() or not 1 <= int(receipt_id) <= 2:
        raise ValueError("invalid fixed validator receipt identity")
    directory = existing_run_directory(eval_id, run_id)
    path = directory / "workspace/workflow.json"
    for selected in (path.parent, path):
        metadata = selected.lstat()
        if stat.S_ISLNK(metadata.st_mode) or (getattr(metadata, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
            raise ValueError("validator path is unsafe")
    with path.open("rb") as handle:
        body = handle.read(65537)
    if len(body) > 65536:
        raise ValueError("validator file exceeds budget")
    text = body.decode("utf-8")
    graph = validate_workflow_text(text)
    schema = None
    if graph["status"] in ("pass", "review_required"):
        schema = validate_workflow_schema(json.loads(text))
    status = ("fail" if graph["status"] in ("fail", "invalid") or schema and schema["status"] == "fail"
              else "review_required" if graph["status"] == "review_required" else "pass")
    receipt = {"eval_id": eval_id, "run_id": run_id, "receipt_id": receipt_id,
               "created_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
               "path": "workflow.json", "sha256": hashlib.sha256(body).hexdigest(),
               "status": status, "graph": graph, "schema": schema}
    with (directory / ("validator-" + receipt_id + ".json")).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return 0 if status == "pass" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--receipt-id", required=True)
    args = parser.parse_args()
    try:
        return validate(args.eval_id, args.run_id, args.receipt_id)
    except (OSError, ValueError, KeyError, TypeError, ImportError):
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

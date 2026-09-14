"""Read bounded task recipes without authorizing or automatically running them."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from json_document_comparison import parse_json_document


CATALOG = Path(__file__).with_name("worker_task_catalog.json")


def task_recipes() -> dict:
    with CATALOG.open("rb") as handle:
        raw = handle.read(16385)
    if len(raw) > 16384 or raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("recipe catalog must be bounded UTF-8 without BOM")
    document = parse_json_document(raw.decode("utf-8"))
    if not isinstance(document, dict) or document.get("version") != 1 or document.get("role") != "0-WORKER":
        raise ValueError("unsupported recipe catalog")
    rounds = document.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != 8:
        raise ValueError("expected eight rounds")
    identifiers = set()
    for number, entry in enumerate(rounds, 1):
        if (not isinstance(entry, dict) or entry.get("round") != number
                or not isinstance(entry.get("purpose"), str)
                or not isinstance(entry.get("tasks"), list) or len(entry["tasks"]) != 3):
            raise ValueError("expected three ordered recipes per round")
        for task in entry["tasks"]:
            identifier = task.get("id") if isinstance(task, dict) else None
            if (not isinstance(identifier, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,79}", identifier)
                    or identifier in identifiers):
                raise ValueError("invalid or duplicate task identity")
            identifiers.add(identifier)
            if task.get("requires_evaluator_design") is True:
                if not isinstance(task.get("recipe"), str) or "contract" in task or "runner" in task:
                    raise ValueError("adaptive recipe cannot imply an executable contract")
            else:
                for key, suffix in (("contract", ".json"), ("runner", ".py")):
                    filename = task.get(key)
                    if (not isinstance(filename, str) or Path(filename).name != filename
                            or not filename.endswith(suffix) or not CATALOG.with_name(filename).is_file()):
                        raise ValueError("locked recipe needs a real local contract and runner")
    return document | {"catalog_sha256": hashlib.sha256(raw).hexdigest()}


def selected_recipe(identifier: str) -> dict:
    document = task_recipes()
    for entry in document["rounds"]:
        for task in entry["tasks"]:
            if task["id"] == identifier:
                return task | {"round": entry["round"], "catalog_sha256": document["catalog_sha256"],
                               "execution_authorized": False,
                               "status": "requires_exact_task_design" if task.get("requires_evaluator_design")
                               else "locked_contract_requires_runtime_preflight"}
    raise ValueError("unknown task recipe")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    print(json.dumps(selected_recipe(args.task_id), ensure_ascii=False, indent=2))

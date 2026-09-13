"""Refresh primary idle evidence and start one explicitly reviewed screening task.

No model load, inference bypass, grading, retry or automatic next task.
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
from observability_common import timestamp_fields, sanitize_for_log, write_capture


def start(review_path: Path, probe: str, predecessors: list[str]) -> dict:
    review_path = review_path.resolve()
    review_path.relative_to(LOG_ROOT.resolve())
    review = read_json(review_path, MAX_DOCUMENT_BYTES)
    # Refresh only activity evidence; preserve the evaluator's other judgments.
    review["observations"] = [item for item in review["observations"]
                              if item["condition"] != "idle_state"]
    if len(review["observations"]) != 5:
        raise ValueError("five reviewed baseline conditions required")
    response = subprocess.run(["lms", "ps", "--json"], capture_output=True,
                              timeout=3, check=True)
    if len(response.stdout) > 65536:
        raise ValueError("inventory exceeded capture budget")
    inventory = json.loads(response.stdout)
    selected = [item for item in inventory
                if item.get("identifier") == review["model_identifier"]]
    if (len(selected) != 1 or selected[0].get("status") != "idle"
            or selected[0].get("queued") != 0 or selected[0].get("parallel") != 1):
        raise ValueError("selected model is not idle with an empty queue and concurrency one")
    capture = {"source": "lms ps --json", "observed_at": timestamp_fields(),
               "models": sanitize_for_log(inventory),
               "evidence_gaps": ["Point-in-time activity observation, not an exclusive server lease."]}
    generic = ROOT / "LM-Studio_logs/model_lifecycle_events" / (uuid4().hex + ".json")
    generic.parent.mkdir(parents=True, exist_ok=True)
    write_capture(generic, capture)
    review["observations"].append({
        "condition": "idle_state", "status": "verified", "value": capture["models"][inventory.index(selected[0])],
        "rationale": "Primary CLI status idle, queued zero, parallel one; no other eval is dispatched.",
        "evidence_reference": {"path": generic.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(generic.read_bytes()).hexdigest(),
            "pointer": ["models", inventory.index(selected[0])],
            "observed_at_pointer": ["observed_at", "epoch_ms"]}})
    current = review_path.parent / ("review-" + uuid4().hex + ".json")
    write_capture(current, review)
    command = [sys.executable, str(Path(__file__).with_name("controlled_run.py")),
               "start", "--model", review["model_identifier"], "--probe-id", probe,
               "--baseline-file", str(current), "--duration", "30", "--max-tokens", "1024"]
    for predecessor in predecessors:
        command.extend(["--predecessor-run", predecessor])
    response = subprocess.run(command, capture_output=True, timeout=5, check=True)
    if len(response.stdout) > 4096:
        raise ValueError("controller response exceeded budget")
    return json.loads(response.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-file", type=Path, required=True)
    parser.add_argument("--probe-id", required=True)
    parser.add_argument("--predecessor-run", action="append", default=[])
    args = parser.parse_args()
    print(json.dumps(start(args.review_file, args.probe_id, args.predecessor_run), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

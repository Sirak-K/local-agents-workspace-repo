"""Refresh primary idle evidence and start one explicitly reviewed screening task.

No model load, inference bypass, grading, retry or automatic next task.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

from controlled_run import ROOT, read_json, MAX_DOCUMENT_BYTES
from evaluation_paths import existing_run_directory, relative_to_project, run_directory
from observability_common import timestamp_fields, sanitize_for_log, write_capture


def start(eval_id: str, run_id: str, baseline_run: str, probe: str,
          predecessors: list[str]) -> dict:
    target = run_directory(eval_id, run_id)
    if target.exists():
        raise ValueError("screening run id already exists")
    review_path = existing_run_directory(eval_id, baseline_run) / "baseline_source_review.json"
    review = read_json(review_path, MAX_DOCUMENT_BYTES)
    if review.get("eval_id") != eval_id:
        raise ValueError("baseline review belongs to another eval")
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
        "evidence_reference": {"path": relative_to_project(generic),
            "sha256": hashlib.sha256(generic.read_bytes()).hexdigest(),
            "pointer": ["models", inventory.index(selected[0])],
            "observed_at_pointer": ["observed_at", "epoch_ms"]}})
    current = review_path.parent / ("review-" + uuid4().hex + ".json")
    write_capture(current, review)
    command = [sys.executable, str(Path(__file__).with_name("controlled_run.py")),
               "run", "--eval-id", eval_id, "--run-id", run_id,
               "--model", review["model_identifier"], "--probe-id", probe,
               "--baseline-file", str(current), "--duration", "30", "--max-tokens", "1024"]
    for predecessor in predecessors:
        command.extend(["--predecessor-run", predecessor])
    child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, cwd=ROOT,
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    deadline = time.monotonic() + 2
    evidence = target / "evidence.json"
    while not evidence.exists() and time.monotonic() < deadline:
        if child.poll() is not None:
            raise RuntimeError("reviewed screening controller startup failed")
        time.sleep(0.02)
    if not evidence.exists():
        raise RuntimeError("reviewed screening controller did not publish evidence")
    return {"eval_id": eval_id, "run_id": run_id, "controller_pid": child.pid,
            "state": "starting", "review": relative_to_project(current)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--run-id", required=True, help="new screening run id")
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--probe-id", required=True)
    parser.add_argument("--predecessor-run", action="append", default=[])
    args = parser.parse_args()
    print(json.dumps(start(args.eval_id, args.run_id, args.baseline_run,
                           args.probe_id, args.predecessor_run), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

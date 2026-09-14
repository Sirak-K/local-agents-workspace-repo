"""Own the single fixed validator argv, budgets and Windows-job receipts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time

from worker_tool_process_control import WorkerToolProcessControl

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = Path(__file__).with_name("workspace_workflow_validator.py")
PYTHON = ROOT / ".venv/Scripts/python.exe"


class WorkspaceValidationControl:
    def __init__(self, eval_id: str, run_id: str, directory: Path):
        if not PYTHON.is_file() or not SCRIPT.is_file():
            raise ValueError("fixed validator runtime unavailable")
        self.eval_id, self.run_id, self.directory = eval_id, run_id, directory
        self.job = WorkerToolProcessControl()
        self.pending = None
        self.calls = 0
        self.stopped = False
        self.receipt = None

    def begin(self, event: dict) -> None:
        if (self.stopped or self.pending or self.calls >= 2
                or event.get("path") != "workflow.json"
                or event.get("request_id") != str(self.calls + 1)):
            raise ValueError("invalid fixed validator request")
        self.calls += 1
        pid = self.job.dispatch([str(PYTHON), "-I", str(SCRIPT), "--eval-id", self.eval_id,
            "--run-id", self.run_id, "--receipt-id", str(self.calls)], ROOT)
        self.pending = {"pid": pid, "started": time.monotonic(), "id": str(self.calls)}

    def poll(self):
        if self.stopped or not self.pending:
            return None
        exit_status = self.job.exit_status(self.pending["pid"])
        if exit_status is None:
            if time.monotonic() - self.pending["started"] > 3:
                self.stop()
                raise RuntimeError("fixed validator time budget exhausted")
            return None
        identifier = self.pending["id"]
        path = self.directory / ("validator-" + identifier + ".json")
        body = b""
        if path.is_file():
            with path.open("rb") as handle:
                body = handle.read(32769)
        if len(body) > 32768:
            raise ValueError("validator receipt exceeds byte budget")
        result = json.loads(body.decode("utf-8")) if body else {"status": "validator_error"}
        if body and (result.get("eval_id"), result.get("run_id"), result.get("receipt_id")) != (
                self.eval_id, self.run_id, identifier):
            raise ValueError("validator receipt identity mismatch")
        result["exit_status"] = exit_status
        self.pending = None
        return ({"command": "validation_result", "request_id": identifier, "result": result},
                {"type": "tool_validation_completed", "path": "workflow.json",
                 "sha256": result.get("sha256"), "exit_status": exit_status,
                 "result_sha256": hashlib.sha256(body).hexdigest()})

    def stop(self):
        if not self.stopped:
            self.stopped = True
            self.receipt = self.job.stop(1)
        return self.receipt

    def close(self):
        try:
            self.stop()
        finally:
            self.job.close()

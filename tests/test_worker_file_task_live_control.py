"""Opt-in aborted transport diagnostics, never a ComfyUI skill/performance verdict."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"
sys.path.insert(0, str(EVAL))
from evaluation_paths import existing_run_directory
from worker_file_task_evaluation import read_json, request_stop


@unittest.skipUnless(os.environ.get("LM_STUDIO_FILE_TASK_PROBE") == "1",
                     "explicit bounded local file-tool transport diagnosis only")
class LiveFileTaskControlTest(unittest.TestCase):
    def _start(self, delayed=False):
        self.eval_id = os.environ["LM_STUDIO_EVAL_ID"]
        self.model = os.environ["LM_STUDIO_MODEL_IDENTIFIER"]
        argv = [sys.executable, str(EVAL / "worker_file_task_evaluation.py"), "start",
                "--eval-id", self.eval_id, "--model", self.model]
        if delayed:
            argv += ["--diagnostic-mutation-dispatch", "--diagnostic-mutation-delay-ms", "3000"]
            if os.environ.get("LM_STUDIO_DIAGNOSTIC_PREVIOUS_RUN"):
                argv += ["--previous-run", os.environ["LM_STUDIO_DIAGNOSTIC_PREVIOUS_RUN"],
                         "--change-reason", "Replace candidate-dependent stop setup with explicit evaluator-dispatched mutation; preserve original diagnostic evidence"]
        response = subprocess.run(argv, capture_output=True, timeout=5, check=True)
        self.run_id = json.loads(response.stdout)["run_id"]
        self.path = existing_run_directory(self.eval_id, self.run_id) / "evidence.json"
        print("LIVE ABORTED TOOL DIAGNOSTIC", self.eval_id, self.run_id, flush=True)

    def _read(self):
        return read_json(self.path)

    def _wait(self, condition, seconds):
        deadline = time.monotonic() + seconds
        evidence = None
        while time.monotonic() < deadline:
            evidence = self._read()
            if condition(evidence):
                return evidence
            time.sleep(0.05)
        return evidence

    def _stop(self):
        request_stop(self.eval_id, self.run_id, "Bounded transport diagnostic stop; no task verdict")
        return self._wait(lambda evidence: evidence["state"] in {
            "verified_cancel", "verified_tool_abort", "unverified", "failed", "not_started", "response_received"}, 8)

    def test_actual_act_generation_cancel_has_server_receipt_and_no_active_tools(self):
        self._start()
        try:
            observed = self._wait(lambda evidence: any(event["data"].get("type") == "fragment"
                                                       for event in evidence["events"]), 8)
            self.assertTrue(any(event["data"].get("type") == "fragment" for event in observed["events"]))
        finally:
            result = self._stop()
        self.assertEqual("verified_cancel", result["state"])
        self.assertEqual("userStopped", result["result"]["stats"]["stopReason"])
        self.assertTrue(result["verification"]["cancel_command_sent"])
        self.assertTrue(result["verification"]["readback_stable_after_stop"])
        self.assertNotEqual("pass", result["assessment"]["status"])

    def test_actual_mutation_abort_leaves_original_and_no_temporary_or_late_write(self):
        self._start(delayed=True)
        try:
            observed = self._wait(lambda evidence: any(event["data"].get("type") == "tool_mutation_started"
                                                       for event in evidence["events"]), 25)
            self.assertTrue(any(event["data"].get("type") == "tool_mutation_started" for event in observed["events"]),
                            "No mutation dispatch reached; this is an open harness diagnostic, not a model FAIL")
        finally:
            result = self._stop()
        self.assertEqual("verified_cancel", result["state"])
        self.assertEqual(result["fixture"]["sha256_before"], result["fixture"]["sha256_after"])
        self.assertTrue(result["verification"]["readback_stable_after_stop"])
        self.assertEqual(0, result["verification"]["tools"]["write"]["active"])
        self.assertGreaterEqual(result["verification"]["tools"]["write"]["aborted"], 1)
        self.assertFalse(list(self.path.parent.joinpath("workspace").glob(".worker-mutation-*.tmp")))


if __name__ == "__main__":
    unittest.main()

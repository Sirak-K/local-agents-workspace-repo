"""Real fixed validator process, OS exit code, budgets and owned Windows stop."""
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ROLE = ROOT / "LOCAL_AGENTS/AGENT-0-WORKER"
sys.path.insert(0, str(ROLE / "agent-0-tools"))
import worker_workspace_validation_control as control


@unittest.skipUnless(os.name == "nt", "Windows Job Object verification")
class WorkspaceValidationControlTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.role = self.root / "LOCAL_AGENTS/AGENT-0-WORKER"
        (self.role / "agent-0-tools").mkdir(parents=True)
        (self.role / "agent-0-eval/schemas").mkdir(parents=True)
        for name in ("evaluation_paths.py", "comfyui_workflow_validation.py", "json_document_comparison.py"):
            shutil.copy2(ROLE / "agent-0-eval" / name, self.role / "agent-0-eval" / name)
        for name in ("workflow_ui_0_4.json", "workflow_ui_0_4_source.json"):
            shutil.copy2(ROLE / "agent-0-eval/schemas" / name, self.role / "agent-0-eval/schemas" / name)
        self.script = self.role / "agent-0-tools/workspace_workflow_validator.py"
        shutil.copy2(ROLE / "agent-0-tools/workspace_workflow_validator.py", self.script)
        self.eval_id, self.run_id = "EVAL_fixture", "a" * 32
        self.directory = self.root / "model_evaluations" / self.eval_id / self.run_id
        (self.directory / "workspace").mkdir(parents=True)
        shutil.copy2(ROOT / "model_evaluations/comfy_ui_eval-playground/source_snapshots/workflow_reference.json",
                     self.directory / "workspace/workflow.json")

    def _control(self):
        for attribute, value in (("ROOT", self.root), ("SCRIPT", self.script)):
            patcher = patch.object(control, attribute, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        instance = control.WorkspaceValidationControl(self.eval_id, self.run_id, self.directory)
        self.addCleanup(instance.close)
        return instance

    def test_actual_validator_exit_status_and_receipt_are_returned_without_candidate_execution(self):
        instance = self._control()
        instance.begin({"request_id": "1", "path": "workflow.json"})
        deadline = time.monotonic() + 3
        outcome = None
        while outcome is None and time.monotonic() < deadline:
            outcome = instance.poll()
            time.sleep(0.01)
        self.assertIsNotNone(outcome)
        command, evidence = outcome
        self.assertEqual(0, command["result"]["exit_status"])
        self.assertEqual("pass", command["result"]["status"])
        self.assertEqual("tool_validation_completed", evidence["type"])
        instance.stop()
        self.assertTrue(instance.receipt["verified"])
        self.assertEqual(0, instance.receipt["active_processes"])
        with self.assertRaises(ValueError):
            instance.begin({"request_id": "2", "path": "workflow.json"})

    def test_abort_closes_owned_process_and_no_receipt_changes_after_stop(self):
        instance = self._control()
        instance.begin({"request_id": "1", "path": "workflow.json"})
        receipt = instance.stop()
        self.assertTrue(receipt["verified"])
        self.assertEqual(0, receipt["active_processes"])
        before = {path.name: path.read_bytes() for path in self.directory.glob("validator-*.json")}
        time.sleep(0.1)
        after = {path.name: path.read_bytes() for path in self.directory.glob("validator-*.json")}
        self.assertEqual(before, after)
        self.assertIsNone(instance.poll())


if __name__ == "__main__":
    unittest.main()

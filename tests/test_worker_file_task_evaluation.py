"""Exercise the real file runner/grader with simulated SDK dispatch evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import evaluation_paths as eval_paths
import worker_file_task_evaluation as runner


class FileTaskEvaluationTest(unittest.TestCase):
    def setUp(self):
        admission = patch.object(runner, "require_transport_review", return_value={
            "model_identifier": "fixture", "instance_reference": None})
        admission.start()
        self.addCleanup(admission.stop)

    def test_three_equal_tool_outcomes_request_cancel_and_preserve_partial_evidence(self):
        class RepeatedFixture:
            def __init__(self, token, command, worker_script):
                self.position, self.cancelled, self.cancel_acknowledged = 0, False, False

            def next_event(self, *_):
                self.position += 1
                if self.position == 1:
                    return {"type": "model_bound", "model_info": {"identifier": "fixture"}}
                if self.cancelled:
                    if not self.cancel_acknowledged:
                        self.cancel_acknowledged = True
                        return {"type": "cancel_sent"}
                    return {"type": "result", "content": "partial", "stats": {"stopReason": "userStopped"},
                            "tool_state": {"read": {"active": 0, "completed": 3},
                                           "write": {"active": 0, "completed": 0}}}
                return {"type": "tool_completed", "path": "workflow.json", "sha256": "a" * 64}

            def send(self, command):
                pass

            def cancel(self):
                self.cancelled = True

            def close(self):
                pass

        with tempfile.TemporaryDirectory() as temporary:
            eval_root = Path(temporary) / "model_evaluations"
            eval_root.mkdir()
            with patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", eval_root), \
                    patch.object(runner, "resolve_token", return_value="fixture-token"), \
                    patch.object(runner, "SdkPredictionProcess", RepeatedFixture):
                evidence = runner.run("EVAL_fixture", "a" * 32, "fixture")
                self.assertEqual("verified_cancel", evidence["state"])
                self.assertTrue(evidence["verification"]["tool_progress"]["stop_required"])
                self.assertEqual(evidence["fixture"]["sha256_before"], evidence["fixture"]["sha256_after"])
                self.assertNotEqual("pass", evidence["assessment"]["status"])

    def test_runner_fixture_messages_actual_disk_grader_and_receipts_are_integrated(self):
        class SdkFixture:
            last = None
            missing_receipts = False

            def __init__(self, token, command, worker_script):
                self.command = command
                self.position = 0
                self.approved = False
                type(self).last = self

            def next_event(self, *_):
                self.position += 1
                if self.position == 1:
                    return {"type": "model_bound", "model_info": {"identifier": "fixture"}}
                if not self.approved:
                    raise AssertionError("no model work before approval")
                if self.position == 2:
                    return {"type": "round_started", "index": 0}
                path = Path(self.command["workspace_root"]) / "workflow.json"
                text = path.read_text(encoding="utf-8")
                text = text.replace('"title": "OUTPUT WIDTH"', '"title": "REFERENCE WIDTH CONTROL"')
                text = text.replace('"title": "OUTPUT HEIGHT"', '"title": "REFERENCE HEIGHT CONTROL"')
                path.write_text(text, encoding="utf-8")
                return {"type": "result", "content": "Done", "stats": {"stopReason": "eosFound"},
                        "tool_state": {} if self.missing_receipts else {
                            "read": {"active": 0, "completed": 2},
                            "write": {"active": 0, "completed": 2, "committed": 2}}}

            def send(self, command):
                self.approved = command == {"command": "continue"}

            def cancel(self):
                pass

            def close(self):
                pass

        for missing, skill_mode in ((False, "none"), (True, "none"), (False, "explicit")):
            with self.subTest(missing_receipts=missing, skill_mode=skill_mode), tempfile.TemporaryDirectory() as temporary:
                eval_root = Path(temporary) / "model_evaluations"
                eval_root.mkdir()
                SdkFixture.missing_receipts = missing
                with patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", eval_root), \
                        patch.object(runner, "resolve_token", return_value="fixture-token"), \
                        patch.object(runner, "SdkPredictionProcess", SdkFixture):
                    evidence = runner.run("EVAL_fixture", "a" * 32, "fixture", skill_mode=skill_mode,
                                          skill_id="workflow_title_preservation" if skill_mode == "explicit" else None)
                    self.assertTrue(SdkFixture.last.approved)
                    self.assertEqual(6, SdkFixture.last.command["max_tool_calls"])
                    self.assertEqual(512, SdkFixture.last.command["max_tokens"])
                    self.assertTrue(SdkFixture.last.command["system_prompt"])
                    self.assertEqual(skill_mode, evidence["skill_exposure"]["mode"])
                    self.assertEqual("verified", evidence["source_verification"]["status"])
                    self.assertIn(evidence["fixture"]["sha256_before"], SdkFixture.last.command["instruction"])
                    self.assertEqual("pass", evidence["task_verification"]["status"])
                    if missing:
                        self.assertEqual("failed", evidence["state"])
                        self.assertNotEqual("pass", evidence["assessment"]["status"])
                    else:
                        self.assertEqual("response_received", evidence["state"])
                        self.assertEqual("pass", evidence["assessment"]["status"])
                        self.assertTrue(evidence["assessment"]["tool_read_write_readback_verified"])
                    with self.assertRaises(FileExistsError):
                        runner.run("EVAL_fixture", "a" * 32, "fixture")


if __name__ == "__main__":
    unittest.main()

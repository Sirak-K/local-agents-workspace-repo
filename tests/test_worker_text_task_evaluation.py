"""Exercise exact disk grading and receipt gates for bounded text tasks."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import evaluation_paths
import worker_text_task_evaluation as runner


class TextTaskEvaluationTest(unittest.TestCase):
    def setUp(self):
        admission = patch.object(runner, "require_transport_review", return_value={
            "model_identifier": "fixture", "instance_reference": None})
        admission.start()
        self.addCleanup(admission.stop)

    def test_creation_and_replacement_require_real_receipts_and_exact_disk_state(self):
        class SdkFixture:
            task_id = None
            missing_receipt = False

            def __init__(self, token, command, worker_script):
                self.command, self.position = command, 0

            def next_event(self, *_):
                self.position += 1
                if self.position == 1:
                    return {"type": "model_bound", "model_info": {"identifier": "fixture"}}
                if self.position == 2:
                    return {"type": "round_started", "index": 0}
                workspace = Path(self.command["workspace_root"])
                if self.task_id == "file_creation_readback":
                    (workspace / "result.txt").write_text("worker_ref=K7-42\nencoding=utf-8\n", encoding="utf-8", newline="")
                    state = {"create": {"active": 0, "completed": 1, "committed": 1},
                             "read": {"active": 0, "completed": 0},
                             "write": {"active": 0, "completed": 0, "committed": 0},
                             "validator": {"active": 0, "completed": 0}}
                else:
                    path = workspace / "settings.txt"
                    path.write_text(path.read_text(encoding="utf-8").replace("retries=2", "retries=3"),
                                    encoding="utf-8", newline="")
                    state = {"create": None, "read": {"active": 0, "completed": 2},
                             "write": {"active": 0, "completed": 1, "committed": 1},
                             "validator": {"active": 0, "completed": 0}}
                if self.missing_receipt:
                    state["create" if self.task_id == "file_creation_readback" else "read"]["completed"] = 0
                return {"type": "result", "content": "STATUS=SUCCESS\nVerified.",
                        "stats": {"stopReason": "eosFound"},
                        "tool_state": state}

            def send(self, command):
                self.approved = command == {"command": "continue"}

            def cancel(self):
                pass

            def close(self):
                pass

        for task_id in ("file_creation_readback", "literal_text_replacement"):
            for missing in (False, True):
                with self.subTest(task=task_id, missing=missing), tempfile.TemporaryDirectory() as temporary:
                    eval_root = Path(temporary) / "model_evaluations"
                    eval_root.mkdir()
                    SdkFixture.task_id, SdkFixture.missing_receipt = task_id, missing
                    with patch.object(evaluation_paths, "MODEL_EVALUATIONS_ROOT", eval_root), \
                            patch.object(runner, "resolve_token", return_value="fixture-token"), \
                            patch.object(runner, "SdkPredictionProcess", SdkFixture):
                        evidence = runner.run("EVAL_fixture", "a" * 32, "fixture", task_id)
                        self.assertTrue(evidence["task_verification"]["exact_files"])
                        self.assertEqual("fail" if missing else "pass",
                                         evidence["task_verification"]["status"])
                        self.assertEqual("fail" if missing else "pass",
                                         evidence["task_verification"]["operation_status"])
                        self.assertEqual("inconsistent" if missing else "consistent",
                                         evidence["task_verification"]["self_report"]["status"])
                        if missing:
                            self.assertEqual("fail", evidence["assessment"]["status"])
                        else:
                            self.assertEqual("pass", evidence["assessment"]["status"])

    def test_completion_claim_requires_exact_first_line_and_matches_observed_state(self):
        claim = {"success_prefix": "STATUS=SUCCESS", "failure_prefix": "STATUS=FAILED"}
        self.assertEqual("consistent",
            runner.verify_completion_claim("STATUS=SUCCESS\nDone", True, claim)["status"])
        self.assertEqual("consistent",
            runner.verify_completion_claim("STATUS=FAILED\nNo write", False, claim)["status"])
        self.assertEqual("inconsistent",
            runner.verify_completion_claim("The task succeeded.", True, claim)["status"])
        self.assertEqual("inconsistent",
            runner.verify_completion_claim("STATUS=SUCCESS", False, claim)["status"])

    def test_dispatch_trace_keeps_native_and_adapter_stages_separate(self):
        events = [
            {"data": {"type": "tool_request_parsed", "call_id": 1,
                      "name": "read_workspace_text", "raw_content": "<tool_call>"}},
            {"data": {"type": "tool_request_finalized", "call_id": 1,
                      "name": "read_workspace_text"}},
            {"data": {"type": "tool_request_guarded", "call_id": 1,
                      "name": "read_workspace_text", "decision": "allowed"}},
            {"data": {"type": "tool_handler_entered", "call_id": 1,
                      "dispatch_origin": "native_sdk", "name": "read_workspace_text"}},
            {"data": {"type": "tool_handler_receipt", "call_id": 1,
                      "dispatch_origin": "native_sdk", "name": "read_workspace_text",
                      "status": "completed"}},
            {"data": {"type": "adapter_tool_request_parsed", "call_id": 1,
                      "name": "replace_workspace_text", "raw_content": "<tool_call>"}},
            {"data": {"type": "tool_handler_entered", "call_id": 1,
                      "dispatch_origin": "model_specific_adapter",
                      "name": "replace_workspace_text"}},
            {"data": {"type": "tool_handler_receipt", "call_id": 1,
                      "dispatch_origin": "model_specific_adapter",
                      "name": "replace_workspace_text", "status": "completed"}},
        ]
        traces = runner.summarize_tool_dispatch(events)
        self.assertEqual(2, len(traces))
        self.assertEqual("model_specific_adapter", traces[0]["dispatch_origin"])
        self.assertEqual("replace_workspace_text", traces[0]["handler_name"])
        self.assertEqual("native_sdk", traces[1]["dispatch_origin"])
        self.assertEqual("allowed", traces[1]["guard_decision"])
        self.assertEqual("completed", traces[1]["receipt_status"])


if __name__ == "__main__":
    unittest.main()

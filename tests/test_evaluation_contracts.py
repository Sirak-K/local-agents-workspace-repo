"""Protect the bounded context task and its existing runner integration."""
from argparse import Namespace
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import controlled_run as controlled
import evaluation_contracts as contracts
import evaluation_paths as eval_paths


class StructuredEditContractTest(unittest.TestCase):
    def test_context_is_hash_bound_and_grader_checks_actual_edit_and_preservation(self):
        task = contracts.task_contract("nested_record_edit")
        self.assertEqual("system", task["context"]["role"])
        self.assertEqual(hashlib.sha256(task["context_text"].encode("utf-8")).hexdigest(),
                         task["context"]["sha256"])
        self.assertEqual("pass", contracts.grade_answer(task["id"], json.dumps(task["expected"], indent=2))["status"])
        for invalid in (
            dict(task["expected"], note="changed"),
            dict(task["expected"], meta=dict(task["expected"]["meta"], approved=1)),
            dict(task["expected"], items=task["expected"]["items"][:1]),
            dict(task["expected"], extra="unrequested"),
        ):
            with self.subTest(invalid=invalid):
                self.assertEqual("fail", contracts.grade_answer(task["id"], json.dumps(invalid))["status"])
        self.assertEqual("fail", contracts.grade_answer(task["id"], '{"meta":1,"meta":2}')["status"])
        self.assertEqual("fail", contracts.grade_answer(task["id"], "```json\n{}\n```")["status"])

    def test_tampered_context_or_undeclared_role_fails_closed(self):
        source = contracts.CATALOG
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            catalog = directory / source.name
            fixture = directory / "structured_edit_context.md"
            catalog.write_bytes(source.read_bytes())
            fixture.write_bytes(source.with_name(fixture.name).read_bytes())
            with patch.object(contracts, "CATALOG", catalog):
                self.assertEqual("nested_record_edit", contracts.task_contract("nested_record_edit")["id"])
                fixture.write_bytes(fixture.read_bytes() + b"altered")
                with self.assertRaises(ValueError):
                    contracts.task_contract("nested_record_edit")
                fixture.write_bytes(source.with_name(fixture.name).read_bytes())
                payload = json.loads(catalog.read_text(encoding="utf-8"))
                payload["tasks"][0]["context"]["role"] = "tool"
                catalog.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(ValueError):
                    contracts.task_contract("nested_record_edit")

    def test_context_priority_task_prefers_current_authoritative_values(self):
        task = contracts.task_contract("context_priority_selection")
        self.assertEqual("pass", contracts.grade_answer(task["id"],
            '{"region":"eu-north","artifact_format":"zip","max_retries":2}')["status"])
        self.assertEqual("fail", contracts.grade_answer(task["id"],
            '{"region":"us-east","artifact_format":"tar","max_retries":5}')["status"])

    def test_selected_limit_task_requires_dependency_order_and_protection(self):
        task = contracts.task_contract("evidence_selected_limit_task")
        self.assertEqual("pass", contracts.grade_answer(task["id"], json.dumps(task["expected"]))["status"])
        reversed_plan = list(reversed(task["expected"]))
        self.assertEqual("fail", contracts.grade_answer(task["id"], json.dumps(reversed_plan))["status"])
        protected = task["expected"] + [{"action": "edit", "target": "config/runtime.json"}]
        self.assertEqual("fail", contracts.grade_answer(task["id"], json.dumps(protected))["status"])

    def test_runner_dispatches_exact_locked_messages_and_grades_only_completed_work(self):
        class PredictionFixture:
            last = None
            model_identifier = "fixture"
            inspection = {"type": "model_inspection", "input_tokens": 100, "context_length": 4096,
                          "rendered_input": "Fixture input rendering, not live provider evidence"}

            def __init__(self, token, command):
                self.command = command
                self.position = 0
                self.approved = False
                self.cancelled = False
                self.process = self
                type(self).last = self

            def next_event(self, *_):
                self.position += 1
                if self.position == 1:
                    return {"type": "model_bound", "model_info": {"identifier": self.model_identifier}}
                if self.position == 2:
                    return self.inspection
                if self.cancelled:
                    return {"type": "not_started"}
                if not self.approved:
                    raise AssertionError("prediction was not approved")
                if self.position == 3:
                    return {"type": "prediction_started"}
                return {"type": "result", "content": json.dumps(contracts.task_contract("nested_record_edit")["expected"]),
                        "stats": {"stopReason": "eosFound"}}

            def send(self, command):
                self.approved = command == {"command": "continue"}

            def cancel(self):
                self.cancelled = True

            def close(self):
                pass

            def poll(self):
                return 0

        args = Namespace(eval_id="EVAL_fixture", run_id=None, model="fixture", task_id="nested_record_edit",
                         probe_id=None, input_file=None, system_prompt_file=None, baseline_file=None,
                         predecessor_run=None, duration=30, stop_budget=5, max_tokens=512,
                         tool_stop_probe=False, previous_run=None, change_reason=None)
        with tempfile.TemporaryDirectory() as temporary:
            eval_root = Path(temporary) / "model_evaluations"
            eval_root.mkdir()
            with patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", eval_root), \
                    patch.object(controlled, "resolve_token", return_value="fixture-token"), \
                    patch.object(controlled, "SdkPredictionProcess", PredictionFixture):
                _, evidence = controlled.run(args)
                task = contracts.task_contract("nested_record_edit")
                self.assertEqual("completed", evidence["state"])
                self.assertEqual("pass", evidence["assessment"]["status"])
                self.assertTrue(PredictionFixture.last.approved)
                self.assertTrue(PredictionFixture.last.command["require_start_approval"])
                self.assertEqual(task["instruction"], PredictionFixture.last.command["instruction"])
                self.assertEqual(task["context_text"], PredictionFixture.last.command["system_prompt"])
                self.assertEqual(task["context"]["sha256"], evidence["task"]["context"]["sha256"])
                self.assertEqual([], evidence["contract"]["model_tools"])
                self.assertEqual("verified", evidence["input_verification"]["status"])
                for inspection in (
                    dict(PredictionFixture.inspection, input_tokens=4000),
                    dict(PredictionFixture.inspection, input_tokens=-1),
                    dict(PredictionFixture.inspection, input_tokens=True),
                    dict(PredictionFixture.inspection, context_length=None),
                    dict(PredictionFixture.inspection, rendered_input=None),
                ):
                    with self.subTest(inspection=inspection), patch.object(PredictionFixture, "inspection", inspection):
                        _, rejected = controlled.run(args)
                        self.assertFalse(PredictionFixture.last.approved)
                        self.assertTrue(PredictionFixture.last.cancelled)
                        self.assertEqual("invalid", rejected["assessment"]["status"])
                with patch.object(PredictionFixture, "model_identifier", "other"):
                    _, rejected = controlled.run(args)
                    self.assertFalse(PredictionFixture.last.approved)
                    self.assertEqual("invalid", rejected["assessment"]["status"])
                args.duration = 29
                with self.assertRaises(ValueError):
                    controlled.run(args)


if __name__ == "__main__":
    unittest.main()

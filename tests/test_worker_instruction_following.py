"""Protect task contracts, strict structural grading and screening boundaries."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import hashlib
import time
from argparse import Namespace
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import evaluation_paths as eval_paths
import instruction_following_grading as grading
import controlled_run as controlled
import inspect_screening_readiness as readiness


class InstructionFollowingGradingTest(unittest.TestCase):
    def test_transformation_accepts_whitespace_not_wrong_types_or_scope(self):
        self.assertEqual("pass", grading.grade_answer("record_transformation", '\n { "value": 18, "name": "Mira" } \n')["status"])
        failures = [
            '{"name":"Mira","value":"18"}', '{"name":"Mira","value":18.0}',
            '{"name":"Mira","value":true}', '{"name":"Mira","value":17}',
            '{"name":"Mira","value":18,"note":"warehouse C"}',
            '{"name":"Mira","value":18,"value":17}',
            '{"name":"Mira","value":NaN}', '["Mira",18]',
            'Done: {"name":"Mira","value":18}',
            '```json\n{"name":"Mira","value":18}\n```',
        ]
        for answer in failures:
            with self.subTest(answer=answer):
                self.assertEqual("fail", grading.grade_answer("record_transformation", answer)["status"])

    def test_routing_checks_all_decisions_priority_boundary_and_order(self):
        expected = grading.task_contract("priority_routing")["expected"]
        self.assertEqual("pass", grading.grade_answer("priority_routing", json.dumps(expected, indent=2))["status"])
        wrong_priority = copy.deepcopy(expected)
        wrong_priority[0]["destination"] = "freight"
        wrong_boundary = copy.deepcopy(expected)
        wrong_boundary[1]["destination"] = "standard"
        extra_scope = copy.deepcopy(expected)
        extra_scope[2]["weight"] = 3
        for answer in [wrong_priority, wrong_boundary, extra_scope, expected[::-1], expected[:2]]:
            with self.subTest(answer=answer):
                self.assertEqual("fail", grading.grade_answer("priority_routing", json.dumps(answer))["status"])

    def test_semantic_review_is_never_keyword_autopass(self):
        calibration = grading.load_catalog()["qualitative_calibration"]
        self.assertGreaterEqual(len(calibration), 10)
        self.assertTrue(any(item["pass"] for item in calibration))
        self.assertTrue(any(not item["pass"] for item in calibration))
        for item in calibration:
            self.assertEqual("review_required", grading.grade_answer("evidence_bound_comparison", item["answer"])["status"])

    def predecessor(self):
        task = grading.task_contract("record_transformation")
        return {"probe": task, "assessment": {"status": "pass"}, "state": "completed",
                "stop": None, "baseline_verification": {"status": "verified"}}

    def test_gate_blocks_failed_unknown_unreviewed_changed_and_duplicate(self):
        grading.screening_gate("record_transformation", [])
        grading.screening_gate("priority_routing", [self.predecessor()])
        for field, value in [("state", "unverified"), ("stop", {"reason":"fixture defect"}),
                             ("assessment", {"status":"review_required"}),
                             ("baseline_verification", {"status":"unknown"}),
                             ("probe", {"id":"record_transformation", "catalog_sha256":"changed"})]:
            previous = self.predecessor()
            previous[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                grading.screening_gate("priority_routing", [previous])
        for identifier, previous in [("record_transformation", [self.predecessor()]),
                                     ("priority_routing", []), ("file_write", [])]:
            with self.assertRaises(ValueError):
                grading.screening_gate(identifier, previous)

    def test_initial_success_never_unlocks_file_tools_or_confirmation(self):
        evidence = [dict(self.predecessor(), probe=grading.task_contract(task["id"]))
                    for task in grading.load_catalog()["tasks"]]
        summary = grading.screening_summary(evidence)
        self.assertEqual("preliminary_success", summary["status"])
        self.assertFalse(summary["confirmed"])
        self.assertFalse(summary["file_tool_progression_allowed"])
        self.assertNotEqual("preliminary_success", grading.screening_summary([evidence[0]] * 3)["status"])

    def test_multiline_evidence_reconstruction_preserves_json(self):
        answer = '{"name":"Mira","value":18}'
        self.assertEqual(answer, grading.reconstruct_text({"text_chunks":[answer[:12], answer[12:]]}))
        with self.assertRaises(ValueError):
            grading.reconstruct_text({"truncated":True})

    def test_baseline_needs_server_receipts_real_readback_and_unchanged_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "readback.json"
            conditions = {key: "observed fixture value" for key in
                          ("model_file_identity", "load_configuration", "sampling_configuration",
                           "template", "environment_versions", "idle_state")}
            source.write_text(json.dumps(conditions | {"observed_at":int(time.time() * 1000)}), encoding="utf-8")
            reference_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            review = {"model_identifier":"fixture", "system_prompt_sha256":hashlib.sha256(b"role").hexdigest(),
                      "catalog_sha256":grading.load_catalog()["sha256"],
                      "observations":[{"condition":key,"status":"verified","value":value,
                                       "rationale":"Fixture contract check, not live provider verification",
                                       "evidence_reference":{"path":"readback.json","sha256":reference_hash,
                                                             "pointer":[key], "observed_at_pointer":["observed_at"]}}
                                      for key, value in conditions.items()]}
            completion = {"state":"completed", "stop":None, "contract":{"model_identifier":"fixture"},
                          "result":{"content":"OK","stats":{"stopReason":"eosFound"},
                                    "load_config":{"fields":[{"key":"fixture","value":1}]},
                                    "prediction_config":{"fields":[{"key":"fixture","value":0}]},
                                    "model_info":{"identifier":"fixture"}}}
            cancellation = {"state":"verified_cancel","contract":{"model_identifier":"fixture"},
                            "result":{"stats":{"stopReason":"userStopped"}},
                            "verification":{"within_stop_budget":True,"cancel_command_sent":True}}
            with patch.object(eval_paths, "PROJECT_ROOT", root):
                result = grading.verify_baseline(review, completion, cancellation, "fixture", "role", {})
                self.assertEqual("verified", result["status"])
                for changed in [dict(cancellation, state="unverified"),
                                dict(cancellation, verification={"within_stop_budget":False})]:
                    with self.assertRaises(ValueError):
                        grading.verify_baseline(review, completion, changed, "fixture", "role", {})
                unknown = copy.deepcopy(review)
                unknown["observations"][0]["status"] = "unknown"
                forged = copy.deepcopy(review)
                forged["observations"][0]["value"] = "not in primary readback"
                for invalid in [unknown, forged]:
                    with self.assertRaises(ValueError):
                        grading.verify_baseline(invalid, completion, cancellation, "fixture", "role", {})
                source.write_text("{}", encoding="utf-8")
                with self.assertRaises(ValueError):
                    grading.verify_baseline(review, completion, cancellation, "fixture", "role", {})

    def test_screening_without_baseline_never_contacts_sdk(self):
        args = Namespace(eval_id="EVAL_fixture", input_file=None, probe_id="record_transformation", model="fixture",
                         system_prompt_file=None, duration=30, max_tokens=1024, stop_budget=5,
                         tool_stop_probe=False, previous_run=None, change_reason=None, baseline_file=None)
        with patch.object(controlled, "resolve_token", return_value="fixture-secret"), \
                patch.object(controlled, "SdkPredictionProcess") as sdk:
            with self.assertRaises(ValueError):
                controlled.run(args)
            sdk.assert_not_called()

    def test_no_generation_inspection_records_unloaded_as_blocked(self):
        class InspectionFixture:
            command = None
            def __init__(self, token, command):
                type(self).command = command
            def next_event(self, *_):
                return {"type":"error","code":"model_not_loaded"}
            def close(self):
                pass
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            eval_root = root / "model_evaluations"
            eval_root.mkdir()
            with patch.object(readiness, "ROOT", root), \
                    patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", eval_root), \
                    patch.object(readiness, "resolve_token", return_value="fixture-secret"), \
                    patch.object(readiness, "SdkPredictionProcess", InspectionFixture):
                path, report = readiness.capture("EVAL_fixture", "d" * 32, "fixture")
                self.assertFalse(report["generation_requested"])
                self.assertEqual("blocked", report["status"])
                self.assertEqual("not_loaded", report["required_checks"]["loaded_model"])
                self.assertTrue(InspectionFixture.command["inspect_model"])
                self.assertNotIn("max_tokens", InspectionFixture.command)
                self.assertTrue(path.exists())

    def test_controller_approval_wrong_binding_and_duplicate_attempt_are_enforced(self):
        class PredictionFixture:
            instances = []
            bound_identifier = "fixture"
            def __init__(self, token, command):
                self.command, self.cancelled, self.approved, self.position = command, False, False, 0
                self.process = self
                type(self).instances.append(self)
            def next_event(self, *_):
                self.position += 1
                if self.position == 1:
                    return {"type":"model_bound","model_info":{"identifier":self.bound_identifier}}
                if self.cancelled:
                    return {"type":"not_started"}
                if not self.approved:
                    raise AssertionError("fixture prediction cannot start before evaluator approval")
                if self.position == 2:
                    return {"type":"prediction_started"}
                return {"type":"result","content":'{"name":"Mira","value":18}',
                        "stats":{"stopReason":"eosFound"},"model_info":{"identifier":"fixture"},
                        "load_config":{"fields":[{"key":"fixture","value":1}]},
                        "prediction_config":{"fields":[{"key":"fixture","value":"x" * 300}]}}
            def send(self, command):
                self.approved = command["command"] == "continue"
            def cancel(self):
                self.cancelled = True
            def close(self):
                pass
            def poll(self):
                return 0
        baseline = {"status":"verified","configuration_sha256":"fixture-hash","review":{},
                    "reference_model_info":{"identifier":"fixture"},
                    "reference_load_config":{"fields":[{"key":"fixture","value":1}]},
                    "reference_prediction_config":controlled.sanitize_for_log(
                        {"fields":[{"key":"fixture","value":"x" * 300}]})}
        for wrong_binding in (False, True):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                eval_root = root / "model_evaluations"
                eval_root.mkdir()
                eval_id = "EVAL_fixture"
                eval_home = eval_root / eval_id
                eval_home.mkdir()
                for identifier in ("a" * 32, "b" * 32):
                    directory = eval_home / identifier
                    directory.mkdir()
                    (directory / "evidence.json").write_text("{}", encoding="utf-8")
                proof = eval_home / ("e" * 32)
                proof.mkdir()
                review_path = proof / "baseline.json"
                review_path.write_text(json.dumps({"eval_id":eval_id,
                    "completion_run":"a" * 32,"cancellation_run":"b" * 32}), encoding="utf-8")
                args = Namespace(eval_id=eval_id, input_file=None, probe_id="record_transformation", model="fixture",
                                 system_prompt_file=None, duration=30, max_tokens=1024, stop_budget=5,
                                 tool_stop_probe=False, previous_run=None, change_reason=None,
                                 baseline_file=str(review_path), predecessor_run=[])
                PredictionFixture.instances = []
                PredictionFixture.bound_identifier = "wrong-model" if wrong_binding else "fixture"
                with patch.object(controlled, "ROOT", root), \
                        patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", eval_root), \
                        patch.object(controlled, "resolve_token", return_value="fixture-secret"), \
                        patch.object(controlled, "verify_baseline", return_value=copy.deepcopy(baseline)), \
                        patch.object(controlled, "require_recent_idle"), \
                        patch.object(controlled, "SdkPredictionProcess", PredictionFixture):
                    _, evidence = controlled.run(args)
                    self.assertTrue(PredictionFixture.instances[0].command["require_start_approval"])
                    self.assertEqual("", PredictionFixture.instances[0].command["system_prompt"])
                    if wrong_binding:
                        self.assertEqual("not_started", evidence["state"])
                        self.assertFalse(PredictionFixture.instances[0].approved)
                        self.assertEqual("invalid", evidence["assessment"]["status"])
                    else:
                        self.assertEqual("pass", evidence["assessment"]["status"])
                        self.assertEqual("completed", evidence["state"])
                        _, duplicate = controlled.run(args)
                        self.assertEqual("not_started", duplicate["state"])
                        self.assertEqual(1, len(PredictionFixture.instances))

    def test_grounding_review_keeps_original_evidence_and_rejects_stale_assessment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            eval_root = root / "model_evaluations"
            eval_root.mkdir()
            eval_id = "EVAL_fixture"
            run_id = "c" * 32
            directory = eval_root / eval_id / run_id
            directory.mkdir(parents=True)
            task = grading.task_contract("evidence_bound_comparison")
            evidence = {"eval_id":eval_id,"run_id":run_id,"probe":task,"state":"completed",
                        "baseline_verification":{"status":"verified"},
                        "assessment":{"status":"review_required"}, "result":{"content":"fixture answer"}}
            path = directory / "evidence.json"
            path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
            original = path.read_bytes()
            with patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", eval_root):
                controlled.assess_grounding(eval_id, run_id, ["pass"] * 3,
                    "Reviewed all locked criteria against the recorded answer", True)
                self.assertEqual(original, path.read_bytes())
                self.assertEqual("pass", controlled.assessed_run(eval_id, run_id)["assessment"]["status"])
                with self.assertRaises(ValueError):
                    controlled.assess_grounding(eval_id, run_id, ["fail"] * 3, "Must not overwrite", True)
                path.write_text(json.dumps(evidence), encoding="utf-8")
                with self.assertRaises(ValueError):
                    controlled.assessed_run(eval_id, run_id)


if __name__ == "__main__":
    unittest.main()

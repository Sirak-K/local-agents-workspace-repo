"""Protect reconstructability, admission and non-evaluative bounded diagnostic behavior."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"
sys.path.insert(0, str(EVAL))
import evaluation_source_snapshot as sources
import tool_transport_reproducibility as diagnosis
import tool_transport_review as admission


class SourceSnapshotTest(unittest.TestCase):
    def test_snapshot_reconstructs_exact_bytes_and_tampering_is_rejected(self):
        path = EVAL / "evaluation_paths.py"
        snapshot = sources.capture_source_snapshot([path])
        reconstructed = "".join(snapshot["files"][0]["text_chunks"]).encode("utf-8")
        self.assertEqual(path.read_bytes(), reconstructed)
        self.assertEqual(hashlib.sha256(reconstructed).hexdigest(), sources.verify_source_snapshot(snapshot)[path.name])
        broken = copy.deepcopy(snapshot)
        broken["files"][0]["text_chunks"][0] += "tampered"
        with self.assertRaises(ValueError):
            sources.verify_source_snapshot(broken)

    def test_runtime_closure_includes_transports_guards_and_event_hooks_not_other_roles(self):
        paths = sources.runtime_source_paths([EVAL / "worker_text_task_evaluation.py"])
        names = {path.name for path in paths}
        self.assertTrue({"tool_transport_review.py", "evaluation_paths.py", "evaluation_source_snapshot.py"}.issubset(names))
        # JS entrypoint is passed explicitly since Python uses a computed worker_script path.
        paths = sources.runtime_source_paths([EVAL / "worker_file_task_prediction.mjs"])
        self.assertTrue({"lm_studio_tool_event_callbacks.mjs", "lm_studio_sdk_prediction.mjs",
                         "worker_workspace_access.mjs"}.issubset({path.name for path in paths}))
        self.assertFalse(any("AGENT-1-GENERAL" in str(path) or "node_modules" in path.parts for path in paths))


class TransportAdmissionTest(unittest.TestCase):
    def test_three_distinct_current_evidence_files_admit_but_tampering_or_duplicates_do_not(self):
        runtime = {"sdk": "1.5.0"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            review_path = root / "transport_review.json"
            review = {"kind": "tool_transport_reproducibility", "status": "verified_native_read_transport",
                      "model_identifier": "granite-4.1-3b", "instance_reference": "instance",
                      "finished_epoch_seconds": time.time(), "eval_id": "EVAL_fixture",
                      "source_set_sha256": "source-set", "runtime_identity": runtime, "runs": []}
            for number in range(3):
                run_id = str(number) * 32
                directory = root / run_id
                directory.mkdir()
                evidence = TransportDiagnosticTest().evidence()
                evidence.update(eval_id=review["eval_id"], run_id=run_id)
                body = json.dumps(evidence).encode("utf-8")
                (directory / "evidence.json").write_bytes(body)
                review["runs"].append({"run_id": run_id, "evidence_sha256": hashlib.sha256(body).hexdigest(),
                                      **diagnosis.summarize_attempt(evidence)})
            review_path.write_text(json.dumps(review), encoding="utf-8")
            with patch.object(admission, "project_relative_path", return_value=review_path), \
                 patch.object(admission, "relative_to_project", return_value="review.json"), \
                 patch.object(admission, "existing_run_directory", side_effect=lambda _, run_id: root / run_id), \
                 patch.object(admission, "installed_runtime_identity", return_value=runtime), \
                 patch.object(admission, "changed_current_sources", return_value=[]):
                self.assertEqual("instance", admission.require_transport_review("review.json", "granite-4.1-3b")["instance_reference"])
                duplicated = copy.deepcopy(review)
                duplicated["runs"][1] = duplicated["runs"][0]
                review_path.write_text(json.dumps(duplicated), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "distinct"):
                    admission.require_transport_review("review.json", "granite-4.1-3b")
                review_path.write_text(json.dumps(review), encoding="utf-8")
                (root / review["runs"][0]["run_id"] / "evidence.json").write_text("tampered", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "changed"):
                    admission.require_transport_review("review.json", "granite-4.1-3b")

    def test_all_candidate_tool_runners_reject_missing_review_before_token_or_artifacts(self):
        import worker_file_read_evaluation as read
        import worker_text_task_evaluation as text
        import worker_file_task_evaluation as file
        cases = ((read, ("EVAL_fixture", "a" * 32, "granite-4.1-3b", 0)),
                 (text, ("EVAL_fixture", "a" * 32, "granite-4.1-3b", "file_creation_readback")),
                 (file, ("EVAL_fixture", "a" * 32, "granite-4.1-3b")))
        for runner, args in cases:
            with self.subTest(runner=runner.__name__), \
                 patch.object(runner, "resolve_token") as token, \
                 patch.object(runner, "create_run_directory") as create:
                with self.assertRaisesRegex(ValueError, "verified tool transport"):
                    runner.run(*args)
                token.assert_not_called()
                create.assert_not_called()

    def test_missing_failed_or_stale_review_blocks_before_generation(self):
        with self.assertRaises(ValueError):
            admission.require_transport_review(None, "granite-4.1-3b")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "review.json"
            for status, finished in (("dispatch_unreliable_tool_evaluation_blocked", time.time()),
                                     ("verified_native_read_transport", time.time() - 1900)):
                path.write_text(json.dumps({"kind": "tool_transport_reproducibility", "status": status,
                    "model_identifier": "granite-4.1-3b", "instance_reference": "instance",
                    "finished_epoch_seconds": finished, "runs": [{}, {}, {}]}), encoding="utf-8")
                with patch.object(admission, "project_relative_path", return_value=path), \
                     patch.object(admission, "installed_runtime_identity") as runtime:
                    with self.assertRaises(ValueError):
                        admission.require_transport_review("review.json", "granite-4.1-3b")
                    runtime.assert_not_called()

    def test_reloaded_instance_is_not_admitted(self):
        review = {"model_identifier": "granite-4.1-3b", "instance_reference": "original"}
        self.assertTrue(admission.matching_reviewed_instance(review,
            {"identifier": "granite-4.1-3b", "instanceReference": "original"}))
        self.assertFalse(admission.matching_reviewed_instance(review,
            {"identifier": "granite-4.1-3b", "instanceReference": "reloaded"}))


class TransportDiagnosticTest(unittest.TestCase):
    def evidence(self, succeeded=True):
        return {"state": "response_received", "assessment": {"status": "diagnostic_only"},
            "source_snapshot": {"source_set_sha256": "source-set"}, "runtime_identity": {"sdk": "1.5.0"},
            "instruction_sha256": "instruction", "contract": {"fresh_chat": True},
            "fixture": {"sha256_before": "fixture", "sha256_after": "fixture"}, "events": [],
            "result": {"model_info": {"instanceReference": "instance"},
                       "tool_state": {"active": 0, "completed": 1 if succeeded else 0},
                       "content": "render-diagnostic 3" if succeeded else "<tool_call>"}}

    def test_three_attempts_never_assign_candidate_pass_and_missing_raw_stays_unknown(self):
        for model in ("granite-4.1-3b", "qwen2.5-7b-instruct"):
            with self.subTest(model=model), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / "evidence.json").write_text("fixture", encoding="utf-8")
                with patch.object(diagnosis, "create_run_directory", return_value=root), \
                     patch.object(diagnosis, "existing_run_directory", return_value=root), \
                     patch.object(diagnosis, "run", side_effect=[self.evidence()] * 3) as run:
                    result = diagnosis.execute_series("EVAL_fixture", "a" * 32, model)
                self.assertEqual(3, run.call_count)
                self.assertEqual("verified_native_read_transport", result["status"])
                self.assertEqual("not_performed", result["candidate_assessment"])
                self.assertFalse(result["public_tool_raw_byte_identity_established"])
                self.assertEqual("instance", run.call_args.kwargs["expected_instance_reference"])
                self.assertEqual(model, result["model_identifier"])
                for call in run.call_args_list:
                    self.assertEqual(model, call.args[2])
                    self.assertEqual(0, call.args[3])
                    self.assertEqual(diagnosis.FIXTURE, call.kwargs["reproduction_fixture"])

    def test_changed_conditions_stop_series_without_blind_retry(self):
        changed = self.evidence()
        changed["contract"]["fresh_chat"] = False
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "evidence.json").write_text("fixture", encoding="utf-8")
            with patch.object(diagnosis, "create_run_directory", return_value=root), \
                 patch.object(diagnosis, "existing_run_directory", return_value=root), \
                 patch.object(diagnosis, "run", side_effect=[self.evidence(), changed]) as run:
                result = diagnosis.execute_series("EVAL_fixture", "a" * 32, "granite-4.1-3b")
            self.assertEqual(2, run.call_count)
            self.assertEqual("invalid_conditions_changed", result["status"])

    def test_public_output_hash_ignores_fragment_boundaries_without_inventing_missing_raw(self):
        first = self.evidence()
        first["events"] = [{"data": {"type": "fragment", "index": 0, "content": "abc"}}]
        second = copy.deepcopy(first)
        second["events"] = [{"data": {"type": "fragment", "index": 0, "content": value}}
                            for value in ("a", "bc")]
        self.assertEqual(diagnosis.summarize_attempt(first)["observed_output"],
                         diagnosis.summarize_attempt(second)["observed_output"])
        self.assertFalse(diagnosis.summarize_attempt(first)["observed_output"]["complete_raw_available"])


class ToolInterfaceInspectionTest(unittest.TestCase):
    def test_public_inspection_uses_saved_schema_never_authorizes_generation(self):
        import inspect_worker_tool_interface as inspection

        class InspectionSdk:
            def __init__(self, token, command, worker_script):
                self.command = command
                self.closed = False
                self.events = iter([{"type": "model_bound", "model_info": {"identifier": "fixture"}},
                    {"type": "model_inspection", "rendered_input": "tools read_workspace_text user Read the file",
                     "input_tokens": 20, "context_length": 8192}])
                instances.append(self)

            def next_event(self, *_):
                return next(self.events)

            def send(self, *_):
                raise AssertionError("read-only inspection must never send generation approval")

            def close(self):
                self.closed = True

        instances = []
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = {"eval_id": "EVAL_fixture", "run_id": "a" * 32, "kind": "workspace_file_read",
                      "state": "response_received", "instruction": "Read the file",
                      "contract": {"project_system_prompt": "", "model_identifier": "fixture"},
                      "result": {"prediction_config": {"fields": [{"key": "llm.prediction.tools",
                          "value": {"tools": [{"type": "function", "function": {"name": "read_workspace_text"}}]}}]}}}
            path = root / "evidence.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            original = path.read_bytes()
            with patch.object(inspection, "existing_run_directory", return_value=root), \
                 patch.object(inspection, "create_run_directory", return_value=root), \
                 patch.object(inspection, "relative_to_project", return_value="evidence.json"), \
                 patch.object(inspection, "resolve_token", return_value="secret-fixture-token"), \
                 patch.object(inspection, "installed_runtime_identity", return_value={}), \
                 patch.object(inspection, "SdkPredictionProcess", InspectionSdk):
                report = inspection.inspect_interface("EVAL_fixture", "b" * 32, "a" * 32)
            self.assertEqual("inspected_without_generation", report["status"])
            self.assertFalse(report["generation_requested"])
            self.assertTrue(instances[0].command["inspect_model"])
            self.assertEqual(source["result"]["prediction_config"]["fields"][0]["value"]["tools"],
                             instances[0].command["tool_definitions"])
            self.assertTrue(instances[0].closed)
            self.assertEqual(original, path.read_bytes())


if __name__ == "__main__":
    unittest.main()

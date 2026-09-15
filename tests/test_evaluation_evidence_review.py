"""Mechanical evidence integrity is distinct from task/model judgments."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import evaluation_evidence_review as review
import evaluation_paths as paths


class EvaluationEvidenceReviewTest(unittest.TestCase):
    def test_model_neutral_context_is_a_supported_runtime_source_owner(self):
        self.assertIn(review.ROLE / "agent-0-context", review.SOURCE_ROOTS)

    def test_hash_identity_and_immutable_assessment_are_checked_without_attributing_fault(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "model_evaluations"
            eval_id, run_id = "EVAL_fixture", "a" * 32
            directory = root / eval_id / run_id
            directory.mkdir(parents=True)
            evidence = {"eval_id": eval_id, "run_id": run_id, "instruction": "Fixture task",
                        "instruction_sha256": hashlib.sha256(b"Fixture task").hexdigest(),
                        "source_fingerprints": {}, "assessment": {"status": "fail"},
                        "probe": {"catalog_sha256": "fixture-catalog"}, "verification": {}, "evidence_gaps": []}
            path = directory / "evidence.json"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            assessment = {"evidence_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                          "catalog_sha256": "fixture-catalog"}
            (directory / "assessment.json").write_text(json.dumps(assessment), encoding="utf-8")
            with patch.object(paths, "MODEL_EVALUATIONS_ROOT", root):
                result = review.review_run(eval_id, run_id)
                self.assertEqual("mechanical_checks_passed", result["status"])
                self.assertEqual("not_performed", result["model_fault_attribution"])
                self.assertEqual("fail", result["task_assessment"]["status"])
                evidence["instruction"] = "changed"
                path.write_text(json.dumps(evidence), encoding="utf-8")
                result = review.review_run(eval_id, run_id)
                self.assertEqual("requires_investigation", result["status"])
                self.assertFalse(result["checks"]["instruction_hash"])
                self.assertFalse(result["checks"]["manual_assessment_hash"])

    def test_summary_is_single_and_still_needs_semantic_review(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "model_evaluations"
            eval_id = "EVAL_fixture"
            directory = root / eval_id
            directory.mkdir(parents=True)
            with patch.object(paths, "MODEL_EVALUATIONS_ROOT", root):
                self.assertEqual("incomplete", review.review_summary_presence(eval_id)["status"])
                report = directory / "[EVAL] - [EVAL_fixture] - [REPORT SUMMARY].md"
                report.write_text("ERQER: reviewer must assess the four domains", encoding="utf-8")
                result = review.review_summary_presence(eval_id)
                self.assertEqual("present", result["status"])
                self.assertTrue(result["semantic_review_required"])
                (directory / "[EVAL] - [duplicate] - [REPORT SUMMARY].md").write_text("ERQER", encoding="utf-8")
                self.assertEqual("incomplete", review.review_summary_presence(eval_id)["status"])

    def test_text_file_after_state_and_root_adapter_condition_are_reviewed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "model_evaluations"
            eval_id, run_id = "EVAL_fixture", "b" * 32
            directory = root / eval_id / run_id
            workspace = directory / "workspace"
            workspace.mkdir(parents=True)
            content = "mode=preview\nretries=3\n"
            (workspace / "settings.txt").write_text(content, encoding="utf-8", newline="\n")
            instruction = "Replace one literal line and verify the resulting file."
            evidence = {
                "eval_id": eval_id,
                "run_id": run_id,
                "instruction": {
                    "encoding": "utf-8",
                    "text_chunks": [instruction[:24], instruction[24:]],
                },
                "instruction_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest(),
                "source_fingerprints": {},
                "granite_text_tool_bridge": True,
                "fixture": {
                    "after": {
                        "settings.txt": {
                            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                            "content": content,
                        }
                    }
                },
                "assessment": {"status": "pass"},
                "verification": {},
                "evidence_gaps": [],
            }
            (directory / "evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
            with patch.object(paths, "MODEL_EVALUATIONS_ROOT", root):
                result = review.review_run(eval_id, run_id)
            self.assertEqual("mechanical_checks_passed", result["status"])
            self.assertEqual("model_specific_bridged_diagnostic", result["attempt_condition"])
            self.assertTrue(result["checks"]["after_hash_stable"])
            self.assertTrue(result["checks"]["workspace_scope"])


if __name__ == "__main__":
    unittest.main()

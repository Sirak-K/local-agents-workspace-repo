"""Check a pinned UI-workflow copy and its independent title-only grader."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import comfyui_workflow_grading as grading
import evaluation_paths as eval_paths


class WorkflowRenameGradingTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.eval_root = Path(self.temporary.name) / "model_evaluations"
        self.eval_id = "EVAL_fixture"
        self.run_id = "a" * 32
        (self.eval_root / self.eval_id / self.run_id).mkdir(parents=True)
        self.patch = patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", self.eval_root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def _write_workflow(self, path, document):
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def test_copy_is_unique_hash_bound_and_correct_title_edit_passes(self):
        fixture = grading.load_rename_fixture()
        prepared = grading.prepare_rename_fixture(self.eval_id, self.run_id)
        path = prepared["path"]
        self.assertEqual(fixture["source_body"], path.read_bytes())
        self.assertEqual(fixture["manifest_sha256"], prepared["manifest_sha256"])
        with self.assertRaises(FileExistsError):
            grading.prepare_rename_fixture(self.eval_id, self.run_id)
        self.assertEqual("fail", grading.grade_rename_fixture(self.eval_id, self.run_id)["status"])
        document = json.loads(path.read_text(encoding="utf-8"))
        for node in document["nodes"]:
            if str(node["id"]) in fixture["target_titles"]:
                node["title"] = fixture["target_titles"][str(node["id"])]
        self._write_workflow(path, document)
        result = grading.grade_rename_fixture(self.eval_id, self.run_id)
        self.assertEqual("pass", result["status"])
        self.assertFalse(result["checks"]["frontend_opened"])
        self.assertFalse(result["checks"]["workflow_executed"])

    def test_wrong_title_and_unrequested_mutation_fail(self):
        path = grading.prepare_rename_fixture(self.eval_id, self.run_id)["path"]
        source = json.loads(path.read_text(encoding="utf-8"))
        target = copy.deepcopy(source)
        for node in target["nodes"]:
            if node["id"] == 68:
                node["title"] = "REFERENCE WIDTH CONTROL"
            if node["id"] == 69:
                node["title"] = "WRONG HEIGHT"
        self._write_workflow(path, target)
        self.assertEqual("fail", grading.grade_rename_fixture(self.eval_id, self.run_id)["status"])
        for node in target["nodes"]:
            if node["id"] == 69:
                node["title"] = "REFERENCE HEIGHT CONTROL"
        target["revision"] += 1
        self._write_workflow(path, target)
        self.assertEqual("fail", grading.grade_rename_fixture(self.eval_id, self.run_id)["status"])

    def test_invalid_json_or_source_context_tampering_is_not_a_model_pass(self):
        path = grading.prepare_rename_fixture(self.eval_id, self.run_id)["path"]
        path.write_bytes(b'\xef\xbb\xbf{"nodes":[]}')
        self.assertEqual("fail", grading.grade_rename_fixture(self.eval_id, self.run_id)["status"])
        with patch.object(grading, "CONTEXT", Path(self.temporary.name) / "other.md"):
            with self.assertRaises(ValueError):
                grading.load_rename_fixture()


if __name__ == "__main__":
    unittest.main()

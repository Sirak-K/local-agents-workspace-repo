from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import evaluation_paths as paths


class EvaluationPathsTest(unittest.TestCase):
    def test_repo_layout_is_current(self):
        self.assertEqual(ROOT.resolve(), paths.PROJECT_ROOT)
        self.assertEqual(ROOT / "model_evaluations", paths.MODEL_EVALUATIONS_ROOT)

    def test_established_eval_and_run_ids_are_accepted(self):
        self.assertEqual("EVAL_1_2026-09-13-204437", paths.validate_eval_id("EVAL_1_2026-09-13-204437"))
        self.assertEqual("a" * 32, paths.validate_run_id("a" * 32))

    def test_identity_injection_is_rejected_before_io(self):
        bad_eval = ["../EVAL_1", "EVAL_1/child", "EVAL_1\\child", "/EVAL_1", "comfy_ui_eval-playground", ".", ""]
        bad_run = ["../" + "a" * 32, "a" * 31, "A" * 32, "a" * 16 + "/" + "b" * 15, "/" + "a" * 32]
        for value in bad_eval:
            with self.subTest(eval_id=value), self.assertRaises(ValueError):
                paths.validate_eval_id(value)
        for value in bad_run:
            with self.subTest(run_id=value), self.assertRaises(ValueError):
                paths.validate_run_id(value)

    def test_create_is_separate_and_collision_safe(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(paths, "MODEL_EVALUATIONS_ROOT", Path(temporary)):
            first = paths.create_run_directory("EVAL_fixture", "1" * 32)
            second = paths.create_run_directory("EVAL_fixture", "2" * 32)
            self.assertNotEqual(first, second)
            with self.assertRaises(FileExistsError):
                paths.create_run_directory("EVAL_fixture", "1" * 32)

    def test_existing_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside, \
                patch.object(paths, "MODEL_EVALUATIONS_ROOT", Path(temporary)):
            link = Path(temporary) / "EVAL_escape"
            try:
                link.symlink_to(Path(outside), target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(ValueError):
                paths.run_directory("EVAL_escape", "3" * 32)

    def test_project_relative_path_rejects_escape(self):
        with self.assertRaises(ValueError):
            paths.project_relative_path("../outside.json")


if __name__ == "__main__":
    unittest.main()

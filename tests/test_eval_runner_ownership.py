from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"


class EvalRunnerOwnershipTest(unittest.TestCase):
    def source(self, name: str) -> str:
        return (EVAL / name).read_text(encoding="utf-8")

    def test_python_runners_parse(self):
        for name in ("controlled_run.py", "worker_file_read_evaluation.py", "evaluation_paths.py",
                     "capture_screening_baseline.py", "inspect_screening_readiness.py",
                     "start_reviewed_screening.py"):
            with self.subTest(name=name):
                ast.parse(self.source(name), filename=name)

    def test_eval_specific_runners_do_not_own_generic_lm_studio_log_root(self):
        for name in ("controlled_run.py", "worker_file_read_evaluation.py"):
            text = self.source(name)
            with self.subTest(name=name):
                self.assertNotIn("LM-Studio_logs/frontier_evaluations", text)
                self.assertIn('"--eval-id", required=True', text)
                self.assertIn("create_run_directory", text)
                self.assertIn('"eval_id"', text)

    def test_current_repository_depth_and_worker_sdk_imports(self):
        for name in ("controlled_run.py", "worker_file_read_evaluation.py"):
            self.assertIn("Path(__file__).resolve().parents[3]", self.source(name))
        worker = self.source("worker_file_read_prediction.mjs")
        self.assertIn('"../../../LM-Studio_connections/', worker)
        self.assertNotIn('"../../../../LM-Studio_connections/', worker)

    def test_path_owner_is_model_evaluations(self):
        paths = self.source("evaluation_paths.py")
        self.assertIn('PROJECT_ROOT / "model_evaluations"', paths)
        self.assertIn("def create_run_directory(eval_id: str, run_id: str)", paths)
        self.assertIn("def existing_run_directory(eval_id: str, run_id: str)", paths)


if __name__ == "__main__":
    unittest.main()

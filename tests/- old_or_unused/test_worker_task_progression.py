"""Recipes retain the role trajectory without masquerading as runnable tasks."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import worker_task_progression as progression
import evaluation_contracts


class TaskProgressionTest(unittest.TestCase):
    def test_locked_and_adaptive_tasks_have_different_readiness(self):
        catalog = progression.task_recipes()
        self.assertEqual(24, sum(len(entry["tasks"]) for entry in catalog["rounds"]))
        selected = progression.selected_recipe("nested_record_edit")
        self.assertEqual(2, selected["round"])
        self.assertFalse(selected["execution_authorized"])
        self.assertEqual("nested_record_edit", evaluation_contracts.task_contract(selected["id"])["id"])
        initial = json.loads(progression.CATALOG.with_name("instruction_following_catalog.json").read_text(encoding="utf-8"))
        self.assertEqual([item["id"] for item in initial["tasks"]],
                         [item["id"] for item in catalog["rounds"][0]["tasks"]])
        pending = progression.selected_recipe("known_palette_workflow_creation")
        self.assertEqual("requires_exact_task_design", pending["status"])
        self.assertEqual("bounded_file_creation", pending["required_tool_capability"])
        self.assertNotIn("runner", pending)
        for identifier in ("context_priority_selection", "evidence_selected_limit_task",
                           "file_creation_readback", "literal_text_replacement", "two_file_id_join"):
            with self.subTest(task=identifier):
                locked = progression.selected_recipe(identifier)
                self.assertEqual("locked_contract_requires_runtime_preflight", locked["status"])
                self.assertFalse(locked["execution_authorized"])
                contract = json.loads(progression.CATALOG.with_name(locked["contract"]).read_text(encoding="utf-8"))
                self.assertIn(identifier, [task["id"] for task in contract["tasks"]])

    def test_duplicate_identity_and_unsafe_executable_claim_are_rejected(self):
        original = json.loads(progression.CATALOG.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            catalog = Path(temporary) / progression.CATALOG.name
            for filename in ("instruction_following_catalog.json", "controlled_run.py",
                             "structured_edit_catalog.json", "workflow_rename_fixture.json",
                             "worker_file_task_evaluation.py", "basic_file_task_catalog.json",
                             "worker_text_task_evaluation.py"):
                catalog.with_name(filename).write_bytes(b"fixture")
            with patch.object(progression, "CATALOG", catalog):
                for mutation in ("duplicate", "executable"):
                    payload = json.loads(json.dumps(original))
                    task = payload["rounds"][1]["tasks"][1]
                    if mutation == "duplicate":
                        task["id"] = "nested_record_edit"
                    else:
                        task = payload["rounds"][3]["tasks"][1]
                        task["runner"] = "controlled_run.py"
                    catalog.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate task identity" if mutation == "duplicate"
                                                else "adaptive recipe"):
                        progression.task_recipes()

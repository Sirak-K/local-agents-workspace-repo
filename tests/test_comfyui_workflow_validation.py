"""Known-good source graph and meaningful graph damage, no backend execution."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
from comfyui_workflow_grading import load_rename_fixture
from comfyui_workflow_validation import validate_workflow, validate_workflow_text, validate_workflow_schema


class WorkflowGraphValidationTest(unittest.TestCase):
    def test_pinned_official_schema_accepts_source_and_rejects_required_field_damage(self):
        source = load_rename_fixture()["source_document"]
        self.assertEqual("pass", validate_workflow_schema(source)["status"])
        del source["nodes"][0]["properties"]
        result = validate_workflow_schema(source)
        self.assertEqual("fail", result["status"])
        self.assertEqual("required", result["findings"][0]["validator"])

    def test_pinned_good_workflow_and_relevant_damage(self):
        source = load_rename_fixture()["source_document"]
        palette = {node["type"] for node in source["nodes"]}
        self.assertEqual("pass", validate_workflow(source, allowed_types=palette)["status"])
        damaged = []
        duplicate = copy.deepcopy(source)
        duplicate["nodes"].append(copy.deepcopy(duplicate["nodes"][0]))
        damaged.append((duplicate, "duplicate_node_id"))
        missing = copy.deepcopy(source)
        missing["links"][0][3] = 9999
        damaged.append((missing, "link_endpoint_missing"))
        slot = copy.deepcopy(source)
        slot["links"][0][2] = 9999
        damaged.append((slot, "link_slot_out_of_range"))
        wrong_type = copy.deepcopy(source)
        wrong_type["links"][0][5] = "WRONG"
        damaged.append((wrong_type, "declared_link_type_mismatch"))
        unknown = copy.deepcopy(source)
        unknown["nodes"][0]["type"] = "NeverShown"
        damaged.append((unknown, "node_outside_shown_palette"))
        for document, code in damaged:
            result = validate_workflow(document, allowed_types=palette)
            self.assertEqual("fail", result["status"])
            self.assertIn(code, [item["code"] for item in result["findings"]])

    def test_unsupported_subgraphs_require_review_not_false_success(self):
        source = load_rename_fixture()["source_document"]
        source["definitions"] = {"subgraphs": [{"id": "unknown"}]}
        result = validate_workflow(source)
        self.assertEqual("review_required", result["status"])
        self.assertIn("subgraph", result["evidence_gaps"][-1])
        self.assertEqual("fail", validate_workflow_text('{"version":0.4,"version":1}')["status"])
        self.assertEqual("invalid", validate_workflow_text(json.dumps({"version": 1}))["status"])


if __name__ == "__main__":
    unittest.main()

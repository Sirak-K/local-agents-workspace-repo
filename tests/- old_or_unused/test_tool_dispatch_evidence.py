"""Verify ordered tool evidence without inferring model or transport causes."""
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
from tool_dispatch_evidence import verify_mutation_readback


def receipt(name, status="completed", **fields):
    return {"data": {"type": "tool_handler_receipt", "name": name,
                     "status": status, **fields}}


class ToolDispatchEvidenceTest(unittest.TestCase):
    def test_matching_read_after_final_mutation_is_verified(self):
        events = [receipt("read_workspace_text", sha256="a" * 64),
                  receipt("replace_workspace_text", after_sha256="b" * 64),
                  receipt("read_workspace_text", sha256="b" * 64)]
        self.assertEqual("verified", verify_mutation_readback(
            events, "a" * 64, "b" * 64)["status"])

    def test_reads_before_write_or_wrong_final_hash_are_not_readback(self):
        before_only = [receipt("read_workspace_text", sha256="a" * 64),
                       receipt("read_workspace_text", sha256="a" * 64),
                       receipt("replace_workspace_text", after_sha256="b" * 64)]
        wrong_hash = before_only + [receipt("read_workspace_text", sha256="c" * 64)]
        self.assertEqual("unverified", verify_mutation_readback(
            before_only, "a" * 64, "b" * 64)["status"])
        self.assertEqual("unverified", verify_mutation_readback(
            wrong_hash, "a" * 64, "b" * 64)["status"])

    def test_only_read_after_last_successful_mutation_counts(self):
        events = [receipt("replace_workspace_text", after_sha256="b" * 64),
                  receipt("read_workspace_text", sha256="b" * 64),
                  receipt("replace_workspace_text", after_sha256="c" * 64),
                  receipt("read_workspace_text", status="failed", sha256="c" * 64),
                  receipt("read_workspace_text", sha256="c" * 64)]
        events.insert(0, receipt("read_workspace_text", sha256="a" * 64))
        result = verify_mutation_readback(events, "a" * 64, "c" * 64)
        self.assertEqual("verified", result["status"])
        self.assertEqual(5, result["readback_event_index"])


if __name__ == "__main__":
    unittest.main()

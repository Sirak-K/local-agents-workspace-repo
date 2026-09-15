"""Verify exact candidate self-report comparison against independent evidence."""
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
from completion_claim_verification import observed_task_outcome, verify_completion_claim


class CompletionClaimVerificationTest(unittest.TestCase):
    claim = {"success_prefix": "STATUS=SUCCESS", "failure_prefix": "STATUS=FAILED"}

    def test_consistent_success_and_failure(self):
        self.assertEqual("consistent", verify_completion_claim(
            "STATUS=SUCCESS\nVerified.", "success", self.claim)["status"])
        self.assertEqual("consistent", verify_completion_claim(
            "STATUS=FAILED\nNot completed.", "failure", self.claim)["status"])

    def test_source_or_harness_invalidity_cannot_become_observed_success(self):
        self.assertEqual("invalid", observed_task_outcome(False, True))
        self.assertEqual("success", observed_task_outcome(True, True))
        self.assertEqual("failure", observed_task_outcome(True, False))

    def test_false_success_false_failure_and_unparseable_are_inconsistent(self):
        self.assertEqual("inconsistent", verify_completion_claim(
            "STATUS=SUCCESS", "failure", self.claim)["status"])
        self.assertEqual("inconsistent", verify_completion_claim(
            "STATUS=FAILED", "success", self.claim)["status"])
        self.assertEqual("inconsistent", verify_completion_claim(
            "Done", "success", self.claim)["status"])
        for content in (" STATUS=SUCCESS", "STATUS=SUCCESS ", "\nSTATUS=SUCCESS",
                        "\ufeffSTATUS=SUCCESS"):
            with self.subTest(content=repr(content)):
                self.assertEqual("unparseable", verify_completion_claim(
                    content, "success", self.claim)["reported_outcome"])

    def test_invalid_observation_is_unassessable_and_text_chunks_are_hashed_deterministically(self):
        content = {"text_chunks": ["STATUS=SUCCESS", "\nVerified."]}
        first = verify_completion_claim(content, "invalid", self.claim)
        second = verify_completion_claim("STATUS=SUCCESS\nVerified.", "invalid", self.claim)
        self.assertEqual("unassessable", first["status"])
        self.assertEqual(first["response_sha256"], second["response_sha256"])

    def test_invalid_contract_or_observed_outcome_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_completion_claim("STATUS=SUCCESS", "partial", self.claim)
        with self.assertRaises(ValueError):
            verify_completion_claim("STATUS=SUCCESS", "success", {"success_prefix": "STATUS=SUCCESS"})


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.runtime_observability.github_autopull_capture import create_autopull_capture
from runtime_logging.operation_document import RuntimeLoggingError


LOCAL = "1" * 40
REMOTE = "2" * 40


class GitHubAutoPullCaptureTests(unittest.TestCase):
    def _capture(self, tmp: str, **overrides):
        arguments = {
            "local_head": LOCAL,
            "remote_head": REMOTE,
            "tracked_clean": True,
            "fetch_result": "success",
            "ancestry": "fast_forward",
            "outcome": "updated",
            "reason": "remote advanced",
            "output_root": Path(tmp),
        }
        arguments.update(overrides)
        return create_autopull_capture(**arguments)

    def test_updated_requires_clean_successful_fast_forward_and_records_one_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, document = self._capture(tmp)
            self.assertTrue(path.exists())
            self.assertEqual(document["owner"], "github_autopull")
            self.assertEqual(document["operation"]["status"], "completed")
            event = document["events"][0]
            self.assertEqual(event["details"]["decision"], "updated")
            self.assertTrue(event["details"]["tracked_clean"])
            self.assertEqual(event["details"]["ancestry"], "fast_forward")
            self.assertEqual(len(document["events"]), 1)

    def test_dirty_skip_is_explicit_and_never_claims_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, document = self._capture(
                tmp,
                tracked_clean=False,
                fetch_result="not_attempted",
                ancestry="not_checked",
                outcome="skipped_dirty",
                reason="tracked workspace dirty",
                remote_head=None,
            )
            event = document["events"][0]
            self.assertEqual(event["outcome"], "skipped")
            self.assertEqual(event["details"]["decision"], "skipped_dirty")

    def test_non_fast_forward_skip_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, document = self._capture(
                tmp,
                ancestry="non_fast_forward",
                outcome="skipped_non_fast_forward",
                reason="remote cannot fast-forward local main",
            )
            self.assertEqual(document["events"][0]["details"]["ancestry"], "non_fast_forward")

    def test_fetch_error_is_failed_capture_without_raw_git_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, document = self._capture(
                tmp,
                remote_head=None,
                fetch_result="error",
                ancestry="unknown",
                outcome="fetch_error",
                reason="fetch failed",
                error_class="SyntheticGitError",
            )
            self.assertEqual(document["operation"]["status"], "failed")
            self.assertEqual(document["events"][0]["details"]["error_class"], "SyntheticGitError")
            self.assertNotIn("stdout", repr(document).lower())
            self.assertNotIn("stderr", repr(document).lower())

    def test_invalid_state_combinations_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeLoggingError):
                self._capture(tmp, tracked_clean=False)
            with self.assertRaises(RuntimeLoggingError):
                self._capture(tmp, outcome="skipped_dirty", tracked_clean=True)
            with self.assertRaises(RuntimeLoggingError):
                self._capture(tmp, outcome="skipped_non_fast_forward", ancestry="fast_forward")
            with self.assertRaises(RuntimeLoggingError):
                self._capture(tmp, outcome="fetch_error", fetch_result="success")


if __name__ == "__main__":
    unittest.main()

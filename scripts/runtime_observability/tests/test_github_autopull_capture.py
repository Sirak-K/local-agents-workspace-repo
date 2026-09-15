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
            "decision": "updated",
            "event_outcome": "success",
            "reason": "remote advanced",
            "local_head": LOCAL,
            "remote_head": REMOTE,
            "tracked_clean": True,
            "fetch_result": "success",
            "ancestry": "fast_forward",
            "output_root": Path(tmp),
        }
        arguments.update(overrides)
        return create_autopull_capture(**arguments)

    def test_updated_requires_clean_successful_fast_forward_and_records_one_state_change(self):
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

    def test_up_to_date_requires_equal_heads(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, document = self._capture(
                tmp,
                decision="up_to_date",
                event_outcome="success",
                local_head=LOCAL,
                remote_head=LOCAL,
                tracked_clean=None,
                ancestry="not_checked",
            )
            self.assertEqual(document["events"][0]["details"]["decision"], "up_to_date")
            with self.assertRaises(RuntimeLoggingError):
                self._capture(
                    tmp,
                    decision="up_to_date",
                    event_outcome="success",
                    local_head=LOCAL,
                    remote_head=REMOTE,
                    tracked_clean=None,
                    ancestry="not_checked",
                )

    def test_dirty_and_non_ff_skips_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, dirty = self._capture(
                tmp,
                decision="skipped_dirty",
                event_outcome="skipped",
                tracked_clean=False,
                ancestry="not_checked",
            )
            self.assertEqual(dirty["events"][0]["outcome"], "skipped")
            _, non_ff = self._capture(
                tmp,
                decision="skipped_non_fast_forward",
                event_outcome="skipped",
                tracked_clean=True,
                ancestry="non_fast_forward",
            )
            self.assertEqual(non_ff["events"][0]["details"]["ancestry"], "non_fast_forward")

    def test_generic_skip_allows_preserving_watcher_specific_safety_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, document = self._capture(
                tmp,
                decision="skipped_untracked_collision",
                event_outcome="skipped",
                tracked_clean=True,
                ancestry="fast_forward",
            )
            self.assertEqual(document["events"][0]["details"]["decision"], "skipped_untracked_collision")

    def test_fetch_error_is_failed_capture_without_raw_git_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, document = self._capture(
                tmp,
                decision="fetch_error",
                event_outcome="failure",
                local_head=None,
                remote_head=None,
                tracked_clean=None,
                fetch_result="error",
                ancestry="unknown",
                reason="fetch failed exit=1",
                error_class="git_fetch_failed",
            )
            self.assertEqual(document["operation"]["status"], "failed")
            self.assertEqual(document["events"][0]["details"]["error_class"], "git_fetch_failed")
            self.assertNotIn("stdout", repr(document).lower())
            self.assertNotIn("stderr", repr(document).lower())

    def test_invalid_state_combinations_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeLoggingError):
                self._capture(tmp, tracked_clean=False)
            with self.assertRaises(RuntimeLoggingError):
                self._capture(tmp, decision="skipped_dirty", event_outcome="skipped", tracked_clean=True)
            with self.assertRaises(RuntimeLoggingError):
                self._capture(tmp, decision="skipped_non_fast_forward", event_outcome="skipped", ancestry="fast_forward")
            with self.assertRaises(RuntimeLoggingError):
                self._capture(tmp, decision="fetch_error", event_outcome="failure", fetch_result="success")


if __name__ == "__main__":
    unittest.main()

"""Stop repeated no-effect outcomes, not model text or legitimate recovery."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
from tool_progress_control import ToolProgressControl


class ToolProgressControlTest(unittest.TestCase):
    def test_three_equal_readbacks_stop_despite_mtime_or_interim_text(self):
        control = ToolProgressControl()
        event = {"type": "tool_completed", "path": "workflow.json", "sha256": "a" * 64}
        self.assertFalse(control.observe(event))
        self.assertFalse(control.observe({"type": "fragment", "content": "I will fix it"}))
        self.assertFalse(control.observe(event | {"mtime": 2}))
        self.assertTrue(control.observe(event | {"mtime": 3}))

    def test_changed_file_or_validator_result_allows_recovery(self):
        control = ToolProgressControl()
        first = {"type": "tool_completed", "path": "workflow.json", "sha256": "a" * 64}
        self.assertFalse(control.observe(first))
        self.assertFalse(control.observe(first))
        self.assertFalse(control.observe({"type": "tool_mutation_completed", "path": "workflow.json",
                                          "after_sha256": "b" * 64}))
        self.assertFalse(control.observe(first | {"sha256": "b" * 64}))
        self.assertFalse(control.observe({"type": "tool_validation_completed", "path": "workflow.json",
                                          "sha256": "b" * 64, "exit_status": 1, "result_sha256": "bad"}))
        self.assertFalse(control.observe({"type": "tool_validation_completed", "path": "workflow.json",
                                          "sha256": "b" * 64, "exit_status": 0, "result_sha256": "good"}))


if __name__ == "__main__":
    unittest.main()

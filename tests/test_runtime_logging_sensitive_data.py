from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime_logging.operation_document import RuntimeLoggingError, append_event, new_operation_document
from runtime_logging.sensitive_data_sanitizer import sanitize_for_log


class SensitiveDataTests(unittest.TestCase):
    def test_default_content_fields_are_hash_metadata_not_raw(self):
        payload = sanitize_for_log(
            {
                "prompt": "secret story prompt",
                "story_text": "once upon a time",
                "audio": b"wave-bytes",
            }
        )
        self.assertTrue(payload["prompt"]["content_redacted"])
        self.assertEqual(payload["prompt"]["character_count"], len("secret story prompt"))
        self.assertNotIn("secret story prompt", repr(payload))
        self.assertTrue(payload["audio"]["binary_redacted"])

    def test_secret_and_bearer_redaction_is_defense_in_depth_even_with_raw_opt_in(self):
        sanitized = sanitize_for_log(
            {
                "prompt": "allowed prompt",
                "authorization": "Bearer supersecret",
                "message": "Authorization: Bearer abc.def-123",
                "password": "hunter2",
            },
            allow_sensitive_content=True,
        )
        self.assertEqual(sanitized["prompt"], "allowed prompt")
        self.assertEqual(sanitized["authorization"], "[REDACTED]")
        self.assertEqual(sanitized["password"], "[REDACTED]")
        self.assertNotIn("abc.def-123", repr(sanitized))

    def test_windows_and_posix_absolute_paths_are_redacted(self):
        windows = sanitize_for_log(r"C:\Users\SSIRA\secret\model.gguf", field_name="model_path")
        self.assertEqual(windows, "<ABSOLUTE_PATH_REDACTED>/model.gguf")
        posix = sanitize_for_log("/home/user/private/model.gguf", field_name="model_path")
        self.assertEqual(posix, "<ABSOLUTE_PATH_REDACTED>/model.gguf")

    def test_raw_event_requires_capture_level_opt_in(self):
        document = new_operation_document(owner="dia2", stream="render", producer="test", producer_version="1")
        with self.assertRaises(RuntimeLoggingError):
            append_event(document, "render.input", {"prompt": "raw"}, allow_sensitive_content=True)
        opted = new_operation_document(
            owner="dia2",
            stream="render",
            producer="test",
            producer_version="1",
            data_policy={"raw_sensitive_content": True},
        )
        append_event(
            opted,
            "render.input",
            {"prompt": "raw allowed", "authorization": "Bearer no"},
            allow_sensitive_content=True,
        )
        details = opted["events"][0]["details"]
        self.assertEqual(details["prompt"], "raw allowed")
        self.assertEqual(details["authorization"], "[REDACTED]")


if __name__ == "__main__":
    unittest.main()

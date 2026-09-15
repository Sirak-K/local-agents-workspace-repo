from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime_logging.atomic_json_store import read_json, serialize_pretty_json, write_pretty_json_atomic
from runtime_logging.operation_document import CaptureLimitError


class AtomicJsonStoreTests(unittest.TestCase):
    def test_pretty_json_is_utf8_no_bom_multiline_and_fsynced_before_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            with patch("runtime_logging.atomic_json_store.os.fsync") as fsync:
                write_pretty_json_atomic(
                    path,
                    {"alpha": "å", "nested": {"x": 1}},
                    max_bytes=4096,
                    replace_attempts=2,
                    base_delay_seconds=0,
                )
            data = path.read_bytes()
            self.assertFalse(data.startswith(b"\xef\xbb\xbf"))
            self.assertIn(b"\n  ", data)
            self.assertTrue(data.endswith(b"\n"))
            self.assertEqual(json.loads(data.decode("utf-8"))["alpha"], "å")
            fsync.assert_called_once()

    def test_permission_error_is_retried_then_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            real_replace = __import__("os").replace
            calls = []

            def flaky_replace(source, target):
                calls.append((source, target))
                if len(calls) < 3:
                    raise PermissionError("locked")
                return real_replace(source, target)

            with patch("runtime_logging.atomic_json_store.os.replace", side_effect=flaky_replace), patch(
                "runtime_logging.atomic_json_store.time.sleep"
            ) as sleep:
                write_pretty_json_atomic(
                    path,
                    {"ok": True},
                    max_bytes=4096,
                    replace_attempts=3,
                    base_delay_seconds=0.05,
                )
            self.assertTrue(path.exists())
            self.assertEqual(len(calls), 3)
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.05, 0.1])

    def test_permanent_lock_fails_visibly_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = directory / "capture.json"
            with patch("runtime_logging.atomic_json_store.os.replace", side_effect=PermissionError("locked")), patch(
                "runtime_logging.atomic_json_store.time.sleep"
            ):
                with self.assertRaises(PermissionError):
                    write_pretty_json_atomic(
                        path,
                        {"ok": True},
                        max_bytes=4096,
                        replace_attempts=2,
                        base_delay_seconds=0,
                    )
            self.assertFalse(path.exists())
            self.assertEqual(list(directory.glob("*.tmp")), [])
            self.assertEqual(list(directory.glob(".*.tmp")), [])

    def test_byte_cap_rejects_before_persisting(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            with self.assertRaises(CaptureLimitError):
                write_pretty_json_atomic(
                    path,
                    {"value": "x" * 100},
                    max_bytes=32,
                    replace_attempts=1,
                    base_delay_seconds=0,
                )
            self.assertFalse(path.exists())

    def test_reader_rejects_bom_and_read_ceiling(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            path.write_bytes(b"\xef\xbb\xbf{}")
            with self.assertRaises(ValueError):
                read_json(path, max_bytes=100)
            path.write_bytes(b"{}" + b" " * 100)
            with self.assertRaises(CaptureLimitError):
                read_json(path, max_bytes=10)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "LM-Studio_connections" / "LM-Studio_observability" / "observability_common.py"


def _load_adapter():
    spec = importlib.util.spec_from_file_location("lm_observability_common_regression", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LmStudioObservabilityRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = _load_adapter()

    def test_legacy_document_shape_and_correlation_contract_are_preserved(self):
        document = self.adapter.new_capture_document(
            "server_events",
            {"name": "test"},
            {"duration_seconds": 60},
            correlation_id="abc-123",
            evidence_gaps=["gap"],
        )
        self.assertEqual(set(document), {"schema_version", "stream", "capture", "events"})
        self.assertEqual(document["schema_version"], "1.0")
        self.assertEqual(document["capture"]["correlation_id"], "abc-123")
        self.assertEqual(document["capture"]["status"], "running")
        self.assertEqual(document["capture"]["limits"]["max_capture_bytes"], 8_388_608)
        with self.assertRaises(ValueError):
            self.adapter.new_capture_document("x", {}, {}, correlation_id="contains spaces")

    def test_legacy_model_io_content_is_preserved_while_secrets_and_paths_are_redacted(self):
        sanitized = self.adapter.sanitize_for_log(
            {
                "content": "LM model input/output stays capturable under its existing explicit opt-in contract",
                "token": "secret-token",
                "model_path": r"C:\Users\SSIRA\models\model.gguf",
                "authorization": "Bearer abc123",
            }
        )
        self.assertIsInstance(sanitized["content"], str)
        self.assertIn("stays capturable", sanitized["content"])
        self.assertEqual(sanitized["token"], "[REDACTED]")
        self.assertEqual(sanitized["authorization"], "[REDACTED]")
        self.assertEqual(sanitized["model_path"], "<ABSOLUTE_PATH_REDACTED>/model.gguf")

    def test_append_finalize_and_atomic_write_keep_existing_lm_semantics(self):
        document = self.adapter.new_capture_document("server_events", {"name": "test"}, {"duration_seconds": 1}, correlation_id="legacy")
        self.adapter.append_event(
            document,
            "server_message",
            {"content": "payload"},
            severity="warning",
            status="source_warning",
            evidence_status="partial",
        )
        self.adapter.finalize_capture(document, status="completed", stop_reason="duration_limit")
        self.assertEqual(document["capture"]["counts"]["events"], 1)
        self.assertEqual(document["events"][0]["status"], "source_warning")
        self.assertEqual(document["capture"]["evidence_status"], "partial")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lm.json"
            self.adapter.write_capture(path, document)
            data = path.read_bytes()
            self.assertFalse(data.startswith(b"\xef\xbb\xbf"))
            self.assertIn(b"\n  ", data)
            loaded = json.loads(data.decode("utf-8"))
            self.assertEqual(loaded["capture"]["correlation_id"], "legacy")

    def test_validate_budget_contract_is_preserved(self):
        self.adapter.validate_budget(0, 0.5, 1)
        self.adapter.validate_budget(300, 300, 1000)
        for args in ((301, 1, 1), (1, 0.49, 1), (1, 1, 1001)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.adapter.validate_budget(*args)


if __name__ == "__main__":
    unittest.main()

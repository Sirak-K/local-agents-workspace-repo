from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import tempfile
import time
import unittest
from unittest.mock import patch

from runtime_logging.operation_document import (
    CaptureLimitError,
    RuntimeLoggingError,
    append_artifact,
    append_event,
    finalize_operation,
    load_policy,
    monotonic_seconds_since,
    new_operation_document,
    timestamp_fields_from_epoch_ms,
    validate_document,
)


class OperationDocumentTests(unittest.TestCase):
    def test_policy_and_schema_contract_are_tracked_and_consistent(self):
        policy = load_policy()
        schema_path = Path(__file__).resolve().parents[1] / "runtime_logging" / "operation_document.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(policy["schema_version"], "1.0")
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["operation"]["properties"]["correlation_id"]["pattern"], "^[0-9a-f]{32}$")
        self.assertEqual(set(policy["retention"]["owners"]), set(policy["owners"]))

    def test_new_document_has_nonzero_32_hex_ids_and_running_checkpoint(self):
        document = new_operation_document(owner="koboldcpp", stream="request", producer="test", producer_version="1")
        operation = document["operation"]
        for key in ("operation_id", "correlation_id"):
            self.assertRegex(operation[key], r"^[0-9a-f]{32}$")
            self.assertNotEqual(operation[key], "0" * 32)
        self.assertEqual(operation["status"], "running")
        self.assertIsNone(operation["ended_at"])
        self.assertIsNone(operation["duration_seconds"])
        validate_document(document)

    def test_all_zero_and_invalid_correlation_ids_are_rejected(self):
        for value in ("0" * 32, "ABC", "abc-123", "f" * 31):
            with self.subTest(value=value):
                with self.assertRaises(RuntimeLoggingError):
                    new_operation_document(
                        owner="koboldcpp",
                        stream="request",
                        producer="test",
                        producer_version="1",
                        correlation_id=value,
                    )

    def test_source_time_is_distinct_from_observed_time_and_duration_is_explicit(self):
        document = new_operation_document(owner="koboldcpp", stream="request", producer="test", producer_version="1")
        source = timestamp_fields_from_epoch_ms(1_700_000_000_000)
        append_event(document, "request.completed", {"ok": True}, source_time=source, duration_seconds=0.125)
        event = document["events"][0]
        self.assertEqual(event["source_time"], source)
        self.assertNotEqual(event["observed_at"]["epoch_ms"], source["epoch_ms"])
        self.assertEqual(event["duration_seconds"], 0.125)
        finalize_operation(document, status="completed", stop_reason="success", duration_seconds=0.5)
        self.assertEqual(document["operation"]["duration_seconds"], 0.5)
        validate_document(document, require_final=True)

    def test_monotonic_duration_uses_monotonic_ns(self):
        with patch("runtime_logging.operation_document.time.monotonic_ns", return_value=1_500_000_000):
            self.assertEqual(monotonic_seconds_since(500_000_000), 1.0)
        with patch("runtime_logging.operation_document.time.monotonic_ns", return_value=499):
            with self.assertRaises(RuntimeLoggingError):
                monotonic_seconds_since(500)

    def test_event_and_capture_caps_reject_without_silent_truncation(self):
        document = new_operation_document(
            owner="koboldcpp",
            stream="request",
            producer="test",
            producer_version="1",
            limits={"max_events": 1},
        )
        append_event(document, "first", {"ok": True})
        with self.assertRaises(CaptureLimitError):
            append_event(document, "second", {"ok": False})
        self.assertEqual(document["operation"]["counts"]["events"], 1)
        self.assertEqual(len(document["events"]), 1)
        with self.assertRaises(CaptureLimitError):
            new_operation_document(
                owner="koboldcpp",
                stream="request",
                producer="test",
                producer_version="1",
                limits={"max_capture_bytes": load_policy()["hard_limits"]["max_capture_bytes"] + 1},
            )

    def test_failed_finalization_is_explicit_and_valid(self):
        document = new_operation_document(owner="diffusers", stream="generate", producer="test", producer_version="1")
        append_event(document, "generation.failed", {"error_class": "SyntheticError"}, severity="error", outcome="failure")
        finalize_operation(document, status="failed", stop_reason="synthetic_failure", duration_seconds=0.25)
        self.assertEqual(document["operation"]["status"], "failed")
        self.assertEqual(document["operation"]["stop_reason"], "synthetic_failure")
        validate_document(document, require_final=True)

    def test_interrupted_finalization_and_running_partial_state_are_distinct(self):
        running = new_operation_document(owner="dia2", stream="render", producer="test", producer_version="1")
        append_event(running, "render.started", {"ok": True})
        validate_document(running)
        self.assertEqual(running["operation"]["status"], "running")
        interrupted = json.loads(json.dumps(running))
        finalize_operation(
            interrupted,
            status="interrupted",
            stop_reason="operator_interrupt",
            duration_seconds=1.25,
            evidence_gaps=["backend stop acknowledgement unavailable"],
        )
        self.assertEqual(interrupted["operation"]["status"], "interrupted")
        self.assertEqual(interrupted["operation"]["stop_reason"], "operator_interrupt")
        self.assertIn("backend stop acknowledgement unavailable", interrupted["evidence_gaps"])

    def test_artifact_references_reject_absolute_and_parent_escape_on_both_path_families(self):
        bad = ("/absolute/file.wav", "C:/absolute/file.wav", r"C:\absolute\file.wav", "../escape.wav")
        for reference in bad:
            document = new_operation_document(owner="dia2", stream="render", producer="test", producer_version="1")
            with self.subTest(reference=reference), self.assertRaises(RuntimeLoggingError):
                append_artifact(document, reference=reference, byte_count=1, sha256="a" * 64)
        document = new_operation_document(owner="dia2", stream="render", producer="test", producer_version="1")
        append_artifact(document, reference="audio/session/output.wav", byte_count=1, sha256="a" * 64)
        self.assertEqual(document["artifacts"][0]["reference"], "audio/session/output.wav")


if __name__ == "__main__":
    unittest.main()

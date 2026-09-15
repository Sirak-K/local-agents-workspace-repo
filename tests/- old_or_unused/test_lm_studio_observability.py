from __future__ import annotations

import json
from io import BytesIO
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "LM-Studio_connections"
    / "LM-Studio_observability"
)
sys.path.insert(0, str(MODULE_DIR))

import capture_host_resource_snapshots as host_capture
import capture_model_lifecycle_events as lifecycle
import lm_studio_cli_stream as cli_stream
import observability_common as common


class CommonCaptureTests(unittest.TestCase):
    def test_pretty_utf8_no_bom_and_capture_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = common.new_capture_document(
                "server_events",
                {"name": "test"},
                {"max_events": 1},
                correlation_id="shared-operation",
            )
            path = common.capture_path(document, log_root=root)
            common.append_event(document, "test_event", {"value": "åäö"})
            common.finalize_capture(document, status="completed", stop_reason="test")
            common.write_capture(path, document)

            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertIn(b"\n  \"schema_version\"", raw)
            parsed = json.loads(raw.decode("utf-8"))
            self.assertEqual(parsed["capture"]["correlation_id"], "shared-operation")
            self.assertEqual(parsed["events"][0]["payload"]["value"], "åäö")
            self.assertNotIn("T", parsed["capture"]["started_at"]["local"])
            self.assertNotIn("Z", parsed["capture"]["started_at"]["utc"])

    def test_secrets_paths_and_long_text_are_safely_serialized(self):
        long_text = "x" * 401
        value = common.sanitize_for_log(
            {
                "Authorization": "Bearer private-value",
                "model_path": r"C:\Users\Example\model.gguf",
                "content": long_text,
                "output_tokens": 42,
                "lm_token_in_text": "Bearer sk-lm-abcdefgh:01234567890123456789",
            }
        )
        self.assertEqual(value["Authorization"], "[REDACTED]")
        self.assertEqual(value["model_path"], "<ABSOLUTE_PATH_REDACTED>/model.gguf")
        self.assertEqual(value["output_tokens"], 42)
        self.assertNotIn("abcdefgh", value["lm_token_in_text"])
        self.assertNotIn("01234567890123456789", value["lm_token_in_text"])
        self.assertEqual("".join(value["content"]["text_chunks"]), long_text)
        self.assertEqual(value["content"]["character_count"], 401)

    def test_same_stream_never_overwrites_a_previous_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = common.new_capture_document("server_events", {}, {})
            second = common.new_capture_document("server_events", {}, {})
            self.assertNotEqual(
                common.capture_path(first, log_root=root),
                common.capture_path(second, log_root=root),
            )

    def test_actual_token_and_embedded_windows_path_are_redacted_without_losing_metrics(self):
        with patch.dict(os.environ, {"LM_API_TOKEN": "private-runtime-token"}):
            value = common.sanitize_for_log({
                "content": r"Failure at C:\Users\Example\folder\private.txt",
                "detail": "private-runtime-token",
                "accessToken": "another-secret",
                "total_output_tokens": 37,
            })
        self.assertNotIn("C:", value["content"])
        self.assertEqual(value["detail"], "[REDACTED]")
        self.assertEqual(value["accessToken"], "[REDACTED]")
        self.assertEqual(value["total_output_tokens"], 37)

    def test_disk_limit_rejects_event_and_preserves_valid_previous_file(self):
        with tempfile.TemporaryDirectory() as directory:
            document = common.new_capture_document("server_events", {}, {})
            path = common.capture_path(document, log_root=Path(directory))
            common.write_capture(path, document)
            initial = path.read_bytes()
            with patch.object(common, "MAX_CAPTURE_BYTES", len(initial) + 4500):
                with self.assertRaises(common.CaptureLimitError):
                    common.append_event(document, "large", {"content": "x" * 5000})
            self.assertEqual(document["events"], [])
            self.assertEqual(path.read_bytes(), initial)

    def test_invalid_budgets_and_unbounded_values_fail_closed(self):
        for duration in (float("nan"), float("inf"), -1, 301):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                common.validate_budget(duration)

    def test_http_origin_is_preserved_by_windows_path_sanitizer(self):
        self.assertEqual(common.sanitize_for_log("http://127.0.0.1:1234"), "http://127.0.0.1:1234")

    def test_transient_replace_lock_is_retried_but_persistent_failure_is_not_hidden(self):
        with tempfile.TemporaryDirectory() as directory:
            document = common.new_capture_document("server_events", {}, {})
            path = common.capture_path(document, log_root=Path(directory))
            original_replace = common.os.replace
            attempts = []
            def transient(source, target):
                attempts.append(target)
                if len(attempts) == 1:
                    raise PermissionError("busy")
                original_replace(source, target)
            with patch.object(common.os, "replace", side_effect=transient), patch.object(common.time, "sleep"):
                common.write_capture(path, document)
            self.assertEqual(len(attempts), 2)
            previous = path.read_bytes()
            with patch.object(common.os, "replace", side_effect=PermissionError("busy")) as replace, patch.object(common.time, "sleep"):
                with self.assertRaises(PermissionError):
                    common.write_capture(path, document)
                self.assertEqual(replace.call_count, 6)
            self.assertEqual(path.read_bytes(), previous)
            self.assertEqual(list(path.parent.glob("*.tmp")), [])


class CliStreamTests(unittest.TestCase):
    class FakeProcess:
        def __init__(self, output: bytes = b"", exit_code: int = 0):
            self.stdout = BytesIO(output)
            self.returncode = None
            self.exit_code = exit_code
            self.terminated = False

        def poll(self):
            return self.returncode

        def wait(self, timeout=None):
            self.returncode = self.exit_code
            return self.returncode

        def terminate(self):
            self.terminated = True
            self.returncode = 0

        def kill(self):
            self.terminate()

    def run_capture(self, output: bytes, *, max_events: int = 10, exit_code: int = 0):
        process = self.FakeProcess(output, exit_code)
        with tempfile.TemporaryDirectory() as directory, patch.object(
            cli_stream, "_lms_version", return_value="test-cli"
        ), patch.object(cli_stream.subprocess, "Popen", return_value=process):
            path, document = cli_stream.capture_cli_stream(
                stream_name="server_events", source_name="server", duration_seconds=1,
                max_events=max_events, max_source_bytes=524288, log_root=Path(directory),
            )
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), document)
        return document, process

    def test_event_limit_stops_only_owned_reader_process(self):
        document, process = self.run_capture(b'{"data":{"type":"server.log"}}\n' * 3, max_events=1)
        self.assertEqual(len(document["events"]), 1)
        self.assertEqual(document["capture"]["stop_reason"], "event_limit")
        self.assertTrue(process.terminated)

    def test_overlong_source_line_is_bounded_and_marked_partial(self):
        document, _ = self.run_capture(b"x" * 300000 + b"\n")
        self.assertEqual(document["events"], [])
        self.assertEqual(document["capture"]["stop_reason"], "source_line_byte_limit")
        self.assertEqual(document["capture"]["evidence_status"], "partial")

    def test_nonzero_source_exit_cannot_be_reported_as_success(self):
        document, _ = self.run_capture(b"", exit_code=7)
        self.assertEqual(document["capture"]["status"], "source_error")
        self.assertEqual(document["capture"]["source_exit_code"], 7)

    def test_interrupt_finalizes_owned_capture_and_stops_process(self):
        with patch.object(cli_stream.Queue, "get", side_effect=KeyboardInterrupt):
            document, process = self.run_capture(b"event\n")
        self.assertEqual(document["capture"]["status"], "interrupted")
        self.assertTrue(process.terminated)

    def test_unknown_source_fields_and_source_timestamp_are_preserved(self):
        document = common.new_capture_document("server_events", {}, {})
        record = {
            "timestamp": 1_789_318_324_650,
            "data": {
                "type": "server.log",
                "level": "debug",
                "content": "request",
                "future_field": {"enabled": True},
            },
        }
        cli_stream._record_event(document, (json.dumps(record) + "\n").encode("utf-8"))
        event = document["events"][0]
        self.assertEqual(event["event_type"], "server.log")
        self.assertEqual(event["source_time"]["epoch_ms"], record["timestamp"])
        self.assertTrue(
            event["payload"]["source_record"]["data"]["future_field"]["enabled"]
        )

    def test_non_json_source_line_is_owned_by_same_stream(self):
        document = common.new_capture_document("server_events", {}, {})
        cli_stream._record_event(document, b"not-json\n")
        event = document["events"][0]
        self.assertEqual(event["event_type"], "unparsed_source_line")
        self.assertEqual(event["evidence_status"], "partial")

    def test_known_cli_banner_and_empty_line_are_not_false_warnings(self):
        document = common.new_capture_document("server_events", {}, {})
        cli_stream._record_event(document, b"Streaming logs from LM Studio\n")
        cli_stream._record_event(document, b"\n")
        self.assertEqual(document["events"], [])


class LifecycleTests(unittest.TestCase):
    def test_missing_loaded_state_is_unknown_not_unloaded(self):
        with self.assertRaises(ValueError):
            lifecycle.model_state({"models": [{"key": "model", "type": "llm"}]})

    def test_catalog_disappearance_is_not_proof_of_unloading(self):
        state = {"model": {"model_key": "model", "loaded_instances": [{"id": "a"}]}}
        self.assertEqual(lifecycle.state_changes(state, {})[0][0], "model_catalog_entry_removed")

    def test_external_origin_and_redirect_are_rejected_before_auth_can_leak(self):
        for url in ("https://example.com", "http://127.0.0.1@evil.example", "http://127.0.0.1/path"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                lifecycle.validate_base_url(url)
        with self.assertRaises(ValueError):
            lifecycle.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.com")

    def test_state_diff_classifies_load_unload_and_instance_change(self):
        unloaded = {
            "model": {"model_key": "model", "model_type": "llm", "loaded_instances": []}
        }
        loaded_a = {
            "model": {
                "model_key": "model",
                "model_type": "llm",
                "loaded_instances": [{"id": "a"}],
            }
        }
        loaded_b = {
            "model": {
                "model_key": "model",
                "model_type": "llm",
                "loaded_instances": [{"id": "b"}],
            }
        }
        self.assertEqual(lifecycle.state_changes(unloaded, loaded_a)[0][0], "model_loaded")
        self.assertEqual(
            lifecycle.state_changes(loaded_a, loaded_b)[0][0],
            "loaded_instances_changed",
        )
        self.assertEqual(lifecycle.state_changes(loaded_b, unloaded)[0][0], "model_unloaded")

    def test_single_snapshot_uses_native_model_state_without_loading(self):
        payload = {
            "models": [
                {"key": "granite-4.1-3b", "type": "llm", "loaded_instances": []}
            ]
        }
        with tempfile.TemporaryDirectory() as directory, patch.object(
            lifecycle, "fetch_models", return_value=payload
        ):
            path, document = lifecycle.capture_lifecycle(
                token="test-token",
                base_url="http://127.0.0.1:1234",
                duration_seconds=0,
                interval_seconds=1,
                max_polls=1,
                log_root=Path(directory),
            )
            self.assertTrue(path.exists())
            self.assertEqual(document["events"][0]["event_type"], "initial_model_state")
            self.assertEqual(
                document["events"][0]["payload"]["loaded_model_count"], 0
            )


class HostCaptureTests(unittest.TestCase):
    def test_failed_gpu_process_query_is_partial_without_discarding_device_data(self):
        results = [
            subprocess.CompletedProcess([], 0, "0, GPU, 8192, 1000, 7\n", ""),
            subprocess.CompletedProcess([], 1, "", "process query unavailable"),
        ]
        with patch.object(host_capture.shutil, "which", return_value="nvidia-smi"), patch.object(
            host_capture.subprocess, "run", side_effect=results
        ):
            data, error = host_capture._gpu_snapshot(set())
        self.assertEqual(data["devices"][0]["memory_total_mib"], 8192)
        self.assertIn("process query exit 1", error)

    def test_nvidia_not_available_value_becomes_explicit_unknown(self):
        self.assertIsNone(host_capture._optional_int("[N/A]"))
        self.assertEqual(host_capture._optional_int("8192"), 8192)

    def test_single_host_snapshot_is_bounded_and_self_contained(self):
        payload = {
            "relevant_process_names": ["LM Studio"],
            "processes": [],
            "lm_studio_server": {"running": False},
            "gpu": {},
            "component_errors": {},
        }
        with tempfile.TemporaryDirectory() as directory, patch.object(
            host_capture, "take_snapshot", return_value=payload
        ):
            path, document = host_capture.capture_host(
                duration_seconds=0,
                interval_seconds=1,
                max_snapshots=1,
                log_root=Path(directory),
            )
            self.assertTrue(path.exists())
            self.assertEqual(document["capture"]["stop_reason"], "single_snapshot")
            self.assertEqual(document["capture"]["counts"]["snapshots"], 1)


if __name__ == "__main__":
    unittest.main()

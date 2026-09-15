from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.runtime_observability.host_snapshot_capture import create_host_snapshot_capture, query_nvidia, query_relevant_processes
from runtime_logging.operation_document import RuntimeLoggingError


class FakeRunner:
    def __init__(self, responses):
        self.responses = list(responses)
        self.commands = []

    def __call__(self, command, **kwargs):
        self.commands.append(command)
        stdout, stderr, code = self.responses.pop(0)
        return subprocess.CompletedProcess(command, code, stdout=stdout, stderr=stderr)


class HostSnapshotTests(unittest.TestCase):
    def test_process_query_targets_only_explicit_pids(self):
        payload = '[{"process_name":"python","pid":42,"working_set_bytes":100,"peak_working_set_bytes":120}]'
        runner = FakeRunner([(payload, "", 0)])
        rows, error = query_relevant_processes([42, 99], runner=runner, powershell="powershell.exe")
        self.assertIsNone(error)
        self.assertEqual([row["pid"] for row in rows], [42])
        command_text = " ".join(runner.commands[0])
        self.assertIn("Get-Process -Id $ids", command_text)
        self.assertNotIn("Get-Process -ErrorAction", command_text)
        self.assertNotIn("CommandLine", command_text)

    def test_gpu_query_filters_compute_processes_to_relevant_pids(self):
        runner = FakeRunner([
            ("0, RTX Test, 8192, 2048, 50\n", "", 0),
            ("42, 1024\n99, 512\n", "", 0),
        ])
        payload, error = query_nvidia([42], runner=runner, nvidia_smi="nvidia-smi.exe")
        self.assertIsNone(error)
        self.assertEqual(payload["devices"][0]["memory_used_mib"], 2048)
        self.assertEqual(payload["relevant_compute_processes"], [{"pid": 42, "used_gpu_memory_mib": 1024}])

    def test_capture_uses_one_host_owner_and_marks_component_errors_partial(self):
        def processes(pids):
            return ([{"pid": pids[0], "working_set_bytes": 100}], None)

        def gpu(pids):
            return ({"devices": [], "relevant_compute_processes": []}, "compute-app query unavailable under WDDM")

        with tempfile.TemporaryDirectory() as tmp:
            path, document = create_host_snapshot_capture(
                pids=[42],
                output_root=Path(tmp),
                process_query=processes,
                gpu_query=gpu,
            )
            self.assertTrue(path.exists())
            self.assertEqual(document["owner"], "host")
            self.assertEqual(len(document["events"]), 1)
            self.assertEqual(document["events"][0]["outcome"], "partial")
            self.assertIn("gpu_query", document["events"][0]["details"]["component_errors"])
            self.assertTrue(any("WDDM" in gap for gap in document["evidence_gaps"]))

    def test_capture_rejects_empty_pid_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeLoggingError):
                create_host_snapshot_capture(pids=[], output_root=Path(tmp))


if __name__ == "__main__":
    unittest.main()

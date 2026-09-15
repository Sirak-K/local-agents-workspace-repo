from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from runtime_logging.atomic_json_store import write_operation_document
from runtime_logging.capture_retention import apply_retention, plan_retention
from runtime_logging.operation_document import finalize_operation, new_operation_document


def _write_capture(directory: Path, *, owner: str, operation_id: str, correlation_id: str, status: str, epoch_ms: int, bytes_pad: int = 0) -> Path:
    document = new_operation_document(
        owner=owner,
        stream="retention",
        producer="test",
        producer_version="1",
        operation_id=operation_id,
        correlation_id=correlation_id,
        detail={"padding": "x" * bytes_pad},
    )
    document["operation"]["started_at"]["epoch_ms"] = epoch_ms
    if status != "running":
        finalize_operation(document, status=status, stop_reason=status, duration_seconds=1)
    path = directory / f"{operation_id}.json"
    write_operation_document(path, document)
    return path


class RetentionTests(unittest.TestCase):
    def _policy(self, *, count=2, age=365, total=10_000_000):
        return {
            "retention": {
                "owners": {
                    "host": {
                        "max_finalized_count": count,
                        "max_age_days": age,
                        "max_total_bytes": total,
                        "protect_latest_failure": True,
                    }
                }
            }
        }

    def test_dry_run_is_deterministic_oldest_first_and_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            now = datetime(2026, 9, 16, tzinfo=timezone.utc)
            paths = []
            for index in range(4):
                paths.append(
                    _write_capture(
                        directory,
                        owner="host",
                        operation_id=f"{index + 1:032x}",
                        correlation_id=f"{index + 101:032x}",
                        status="completed",
                        epoch_ms=int(now.timestamp() * 1000) + index,
                    )
                )
            decisions = plan_retention(directory, owner="host", now=now, policy=self._policy(count=2))
            self.assertEqual([item.path for item in decisions], paths[:2])
            dry = apply_retention(decisions, dry_run=True)
            self.assertEqual(dry, paths[:2])
            self.assertTrue(all(path.exists() for path in paths))

    def test_running_and_latest_failure_are_protected(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            now = datetime(2026, 9, 16, tzinfo=timezone.utc)
            base = int(now.timestamp() * 1000)
            running = _write_capture(directory, owner="host", operation_id="1" * 32, correlation_id="a" * 32, status="running", epoch_ms=base - 10)
            old_failed = _write_capture(directory, owner="host", operation_id="2" * 32, correlation_id="b" * 32, status="failed", epoch_ms=base - 9)
            latest_failed = _write_capture(directory, owner="host", operation_id="3" * 32, correlation_id="c" * 32, status="interrupted", epoch_ms=base - 8)
            completed = _write_capture(directory, owner="host", operation_id="4" * 32, correlation_id="d" * 32, status="completed", epoch_ms=base - 7)
            decisions = plan_retention(directory, owner="host", now=now, policy=self._policy(count=1))
            planned = {item.path for item in decisions}
            self.assertNotIn(running, planned)
            self.assertNotIn(latest_failed, planned)
            self.assertIn(old_failed, planned)
            self.assertIn(completed, planned)

    def test_age_and_total_byte_limits_only_delete_finalized_owner_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            now = datetime(2026, 9, 16, tzinfo=timezone.utc)
            day_ms = 86_400_000
            old = _write_capture(directory, owner="host", operation_id="5" * 32, correlation_id="e" * 32, status="completed", epoch_ms=int(now.timestamp() * 1000) - 10 * day_ms)
            newer = _write_capture(directory, owner="host", operation_id="6" * 32, correlation_id="f" * 32, status="completed", epoch_ms=int(now.timestamp() * 1000), bytes_pad=200)
            decisions = plan_retention(directory, owner="host", now=now, policy=self._policy(count=10, age=5, total=1))
            reasons = {item.path: item.reason for item in decisions}
            self.assertEqual(reasons[old], "age_limit")
            self.assertEqual(reasons[newer], "total_byte_limit")


if __name__ == "__main__":
    unittest.main()

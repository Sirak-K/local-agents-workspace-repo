from __future__ import annotations

import contextlib
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from runtime_logging.atomic_json_store import write_operation_document
from runtime_logging.operation_capture_cli import build_parser, main
from runtime_logging.operation_document import (
    append_artifact,
    append_event,
    finalize_operation,
    new_operation_document,
    timestamp_fields_from_epoch_ms,
)


ROOT = Path(__file__).resolve().parents[1]
FIXED_NOW_MS = 2_000_000_000_000
OLD_MS = FIXED_NOW_MS - 30 * 86_400_000
RECENT_MS = FIXED_NOW_MS - 1_000


class RuntimeLoggingOperatorCliTests(unittest.TestCase):
    def _document(
        self,
        *,
        owner: str,
        correlation_id: str,
        status: str = "completed",
        started_ms: int = RECENT_MS,
        artifact: bool = False,
        evidence_gap: bool = False,
        event_detail: dict | None = None,
    ) -> dict:
        document = new_operation_document(
            owner=owner,
            stream="operator_test",
            producer="offline-test",
            producer_version="1",
            correlation_id=correlation_id,
            evidence_gaps=["synthetic gap"] if evidence_gap else [],
        )
        document["operation"]["started_at"] = timestamp_fields_from_epoch_ms(started_ms)
        if event_detail is not None:
            append_event(document, "operator.test_event", event_detail)
        if artifact:
            append_artifact(
                document,
                reference="artifacts/sample.bin",
                byte_count=3,
                sha256="a" * 64,
                media_type="application/octet-stream",
            )
        finalize_operation(document, status=status, stop_reason=f"synthetic_{status}", duration_seconds=0.25)
        return document

    def _write(self, root: Path, name: str, document: dict) -> Path:
        path = root / document["owner"] / document["stream"] / name
        write_operation_document(path, document)
        return path

    def _run(self, argv: list[str]) -> tuple[int, dict, str]:
        stdout = StringIO()
        stderr = StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(argv)
        output = stdout.getvalue().strip()
        return code, json.loads(output) if output else {}, stderr.getvalue()

    def test_validate_is_read_only_and_reports_sorted_invalid_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = self._document(owner="koboldcpp", correlation_id="1" * 32)
            good_path = self._write(root, "z-good.json", good)
            bad_a = root / "host" / "a-invalid.json"
            bad_b = root / "sillytavern" / "b-invalid.json"
            bad_a.parent.mkdir(parents=True)
            bad_b.parent.mkdir(parents=True)
            bad_a.write_text("{not-json}\n", encoding="utf-8")
            bad_b.write_bytes(b"\xef\xbb\xbf{}")
            before = {path: path.read_bytes() for path in (good_path, bad_a, bad_b)}

            code, payload, _ = self._run(["validate", "--root", str(root)])

            self.assertEqual(code, 1)
            self.assertEqual(payload["status"], "FAIL")
            self.assertEqual(payload["files"], 3)
            self.assertEqual(
                [item["file"] for item in payload["invalid"]],
                ["host/a-invalid.json", "sillytavern/b-invalid.json"],
            )
            self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_validate_missing_root_is_clean_zero_file_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "absent"
            code, payload, _ = self._run(["validate", "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertEqual(payload["files"], 0)
            self.assertEqual(payload["status"], "PASS")
            self.assertFalse(root.exists())

    def test_query_filters_owner_correlation_artifact_failure_and_evidence_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corr_a = "2" * 32
            corr_b = "3" * 32
            self._write(
                root,
                "a.json",
                self._document(
                    owner="koboldcpp",
                    correlation_id=corr_a,
                    status="failed",
                    artifact=True,
                    evidence_gap=True,
                    event_detail={"content": "raw text must not be echoed by query"},
                ),
            )
            self._write(root, "b.json", self._document(owner="host", correlation_id=corr_b))

            code, payload, _ = self._run([
                "query", "--root", str(root), "--owner", "koboldcpp", "--correlation-id", corr_a,
                "--failures-only", "--has-artifact", "--has-evidence-gaps",
            ])

            self.assertEqual(code, 0)
            self.assertEqual(payload["count"], 1)
            result = payload["results"][0]
            self.assertEqual(result["owner"], "koboldcpp")
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["artifact_count"], 1)
            self.assertEqual(result["evidence_gap_count"], 1)
            self.assertNotIn("raw text", json.dumps(payload))
            self.assertNotIn("events", result)
            self.assertNotIn("artifacts", result)

    def test_query_artifact_reference_matches_exact_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "a.json", self._document(owner="koboldcpp", correlation_id="4" * 32, artifact=True))
            code, payload, _ = self._run([
                "query", "--root", str(root), "--artifact-reference", "artifacts/sample.bin"
            ])
            self.assertEqual(code, 0)
            self.assertEqual(payload["count"], 1)
            code, payload, _ = self._run([
                "query", "--root", str(root), "--artifact-reference", "artifacts/missing.bin"
            ])
            self.assertEqual(code, 0)
            self.assertEqual(payload["count"], 0)

    def test_prune_dry_run_is_deterministic_and_does_not_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_completed = self._write(
                root,
                "a-old-completed.json",
                self._document(owner="koboldcpp", correlation_id="5" * 32, started_ms=OLD_MS),
            )
            old_failure = self._write(
                root,
                "b-old-failed.json",
                self._document(owner="koboldcpp", correlation_id="6" * 32, status="failed", started_ms=OLD_MS + 1),
            )
            recent = self._write(
                root,
                "c-recent.json",
                self._document(owner="koboldcpp", correlation_id="7" * 32, started_ms=RECENT_MS),
            )
            before = {path: path.read_bytes() for path in (old_completed, old_failure, recent)}

            argv = [
                "prune", "--root", str(root), "--owner", "koboldcpp", "--dry-run",
                "--now-epoch-ms", str(FIXED_NOW_MS),
            ]
            code1, payload1, _ = self._run(argv)
            code2, payload2, _ = self._run(argv)

            self.assertEqual(code1, 0)
            self.assertEqual(code2, 0)
            self.assertEqual(payload1, payload2)
            self.assertTrue(payload1["dry_run"])
            self.assertEqual(payload1["count"], 1)
            self.assertEqual(payload1["decisions"][0]["file"], "koboldcpp/operator_test/a-old-completed.json")
            self.assertEqual(payload1["decisions"][0]["reason"], "age_limit")
            self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_prune_rejects_invalid_capture_instead_of_silently_skipping_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid = root / "koboldcpp" / "operator_test" / "bad.json"
            invalid.parent.mkdir(parents=True)
            invalid.write_text("{}\n", encoding="utf-8")
            code, payload, stderr = self._run([
                "prune", "--root", str(root), "--owner", "koboldcpp", "--dry-run",
                "--now-epoch-ms", str(FIXED_NOW_MS),
            ])
            self.assertEqual(code, 2)
            self.assertEqual(payload, {})
            self.assertIn("RuntimeLoggingError", stderr)
            self.assertTrue(invalid.exists())

    def test_prune_parser_requires_explicit_dry_run(self):
        parser = build_parser()
        with contextlib.redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["prune", "--root", "logs", "--owner", "koboldcpp"])

    def test_repository_ignore_and_readme_contract(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        readme = (ROOT / "logs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("logs/**/*.json", ignore)
        self.assertNotIn("logs/**\n", ignore)
        self.assertIn("dry-run-only", readme)
        self.assertIn("python -m runtime_logging validate --root logs", readme)
        self.assertIn("python -m runtime_logging query --root logs", readme)
        self.assertIn("python -m runtime_logging prune --root logs --owner koboldcpp --dry-run", readme)


if __name__ == "__main__":
    unittest.main()

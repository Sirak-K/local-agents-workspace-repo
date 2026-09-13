"""Bounded reader for LM Studio CLI log sources."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from queue import Empty, Full, Queue
import subprocess
from threading import Event, Thread
import time
from typing import Any

from observability_common import (
    PROJECT_ROOT,
    CaptureLimitError,
    append_event,
    capture_path,
    finalize_capture,
    new_capture_document,
    project_relative,
    timestamp_fields_from_epoch_ms,
    validate_budget,
    write_capture,
)


def _lms_version() -> str:
    try:
        result = subprocess.run(
            ["lms", "--version"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=False,
            timeout=5,
            text=True,
            encoding="utf-8",
            errors="strict",
        )
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return "unavailable"
    output = (result.stdout or result.stderr).strip()
    return output[:160] if output else "unavailable"


def _stop_owned_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def _queue_lines(stream: Any, queue: Queue[bytes | None], stopped: Event, max_line_bytes: int) -> None:
    def offer(line: bytes | None) -> bool:
        while not stopped.is_set():
            try:
                queue.put(line, timeout=0.1)
                return True
            except Full:
                continue
        return False

    try:
        while not stopped.is_set():
            line = stream.readline(max_line_bytes + 1)
            if not line or not offer(line):
                break
            if len(line) > max_line_bytes:
                break
    finally:
        offer(None)


def _record_event(document: dict[str, Any], line: bytes) -> None:
    try:
        text = line.decode("utf-8", errors="strict").rstrip("\r\n")
    except UnicodeDecodeError as exc:
        append_event(
            document,
            "source_decode_error",
            {"byte_count": len(line), "source_sha256": hashlib.sha256(line).hexdigest(), "error": str(exc)},
            severity="error",
            status="source_error",
            evidence_status="partial",
        )
        return

    if not text or text == "Streaming logs from LM Studio":
        return

    try:
        record = json.loads(text)
    except (json.JSONDecodeError, RecursionError) as exc:
        append_event(
            document,
            "unparsed_source_line",
            {"raw_line": text, "parse_error": str(exc)},
            severity="warning",
            status="source_warning",
            evidence_status="partial",
        )
        return

    data = record.get("data") if isinstance(record, dict) else None
    event_type = data.get("type", "cli_log_record") if isinstance(data, dict) else "cli_log_record"
    severity = data.get("level", "info") if isinstance(data, dict) else "info"
    source_time = None
    raw_timestamp = record.get("timestamp") if isinstance(record, dict) else None
    if isinstance(raw_timestamp, (int, float)):
        try:
            source_time = timestamp_fields_from_epoch_ms(raw_timestamp)
        except (ValueError, OverflowError, OSError):
            document["capture"]["evidence_gaps"].append("A source timestamp could not be interpreted.")
    append_event(
        document,
        str(event_type),
        {"source_record": record, "source_byte_count": len(line), "source_sha256": hashlib.sha256(line).hexdigest()},
        severity=str(severity),
        source_time=source_time,
    )


def capture_cli_stream(
    *,
    stream_name: str,
    source_name: str,
    duration_seconds: float,
    max_events: int,
    max_source_bytes: int,
    filters: tuple[str, ...] = (),
    correlation_id: str | None = None,
    log_root: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    validate_budget(duration_seconds, samples=max_events)
    if duration_seconds == 0 or not 1 <= max_source_bytes <= 8_388_608:
        raise ValueError("duration must be positive; source bytes must be between 1 and 8388608")
    max_line_bytes = min(max_source_bytes, 262_144)

    command = ["lms", "log", "stream", "--source", source_name, "--json"]
    if filters:
        command.extend(["--filter", ",".join(filters)])
    document = new_capture_document(
        stream_name,
        {
            "name": "LM Studio CLI log stream",
            "command": command,
            "requested_source": source_name,
            "lms_cli_version": _lms_version(),
            "source_schema_stability": "version-sensitive; unknown fields are retained",
        },
        {
            "duration_seconds": duration_seconds,
            "max_events": max_events,
            "max_source_bytes": max_source_bytes,
            "max_line_bytes": max_line_bytes,
            "max_buffered_lines": 8,
        },
        correlation_id=correlation_id,
        evidence_gaps=[
            "Events outside this bounded capture interval are not present.",
            "LM Studio CLI output is an observation source, not proof of complete internal coverage.",
        ],
    )
    output = capture_path(document, log_root=log_root) if log_root else capture_path(document)
    write_capture(output, document)

    try:
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except OSError as exc:
        append_event(
            document,
            "source_process_start_failed",
            {"error_class": type(exc).__name__, "message": str(exc)},
            severity="error",
            status="source_error",
            evidence_status="partial",
        )
        finalize_capture(document, status="source_error", stop_reason="source_process_start_failed")
        write_capture(output, document)
        return output, document
    assert process.stdout is not None
    queue: Queue[bytes | None] = Queue(maxsize=8)
    stopped = Event()
    reader = Thread(target=_queue_lines, args=(process.stdout, queue, stopped, max_line_bytes), daemon=True)
    reader.start()
    deadline = time.monotonic() + duration_seconds
    stop_reason = "duration_limit"
    status = "completed"
    last_write = time.monotonic()

    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                line = queue.get(timeout=min(0.25, remaining))
            except Empty:
                if process.poll() is not None:
                    stop_reason = "source_process_exited"
                    status = "completed" if process.returncode == 0 else "source_error"
                    break
                continue
            if line is None:
                stop_reason = "source_process_exited"
                process.wait(timeout=3)
                document["capture"]["source_exit_code"] = process.returncode
                status = "completed" if process.returncode == 0 else "source_error"
                break
            if len(line) > max_line_bytes:
                stop_reason = "source_line_byte_limit"
                status = "completed_with_limit"
                break
            next_bytes = document["capture"]["counts"]["source_bytes"] + len(line)
            if next_bytes > max_source_bytes:
                stop_reason = "source_byte_limit"
                status = "completed_with_limit"
                break
            document["capture"]["counts"]["source_bytes"] = next_bytes
            _record_event(document, line)
            if time.monotonic() - last_write >= 0.5:
                write_capture(output, document)
                last_write = time.monotonic()
            if document["capture"]["counts"]["events"] >= max_events:
                stop_reason = "event_limit"
                status = "completed_with_limit"
                break
    except CaptureLimitError:
        stop_reason = "serialized_byte_limit"
        status = "completed_with_limit"
    except (ValueError, RecursionError, subprocess.SubprocessError) as exc:
        document["capture"]["evidence_gaps"].append(f"Reader failed: {type(exc).__name__}")
        stop_reason = "reader_failed"
        status = "source_error"
    except KeyboardInterrupt:
        stop_reason = "operator_interrupt"
        status = "interrupted"
    finally:
        stopped.set()
        _stop_owned_process(process)
        reader.join(timeout=1)
        process.stdout.close()
        if status == "completed" and any(event["evidence_status"] == "partial" for event in document["events"]):
            status = "completed_with_errors"
        finalize_capture(document, status=status, stop_reason=stop_reason)
        write_capture(output, document)

    return output, document


def completion_line(path: Path, document: dict[str, Any]) -> str:
    capture = document["capture"]
    return (
        f"{document['stream']}: {capture['status']} | "
        f"events={capture['counts']['events']} | file={project_relative(path)}"
    )

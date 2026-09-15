"""LM Studio compatibility adapter over the shared runtime logging primitives."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_logging.atomic_json_store import serialize_pretty_json, write_pretty_json_atomic
from runtime_logging.operation_document import (
    CaptureLimitError,
    local_timestamp,
    timestamp_fields,
    timestamp_fields_from_epoch_ms,
    utc_timestamp,
    validate_budget,
)
from runtime_logging.sensitive_data_sanitizer import sanitize_for_log as _shared_sanitize_for_log

LOG_ROOT = PROJECT_ROOT / "LM-Studio_logs"
SCHEMA_VERSION = "1.0"
MAX_INLINE_TEXT_CHARACTERS = 240
TEXT_CHUNK_CHARACTERS = 160
MAX_CAPTURE_BYTES = 8_388_608
FINALIZATION_RESERVE_BYTES = 4096


def sanitize_for_log(value: Any, *, field_name: str = "") -> Any:
    """Preserve the established LM Studio sanitization contract via the shared core."""

    return _shared_sanitize_for_log(
        value,
        field_name=field_name,
        project_root=PROJECT_ROOT,
        allow_sensitive_content=True,
        max_inline_text_characters=MAX_INLINE_TEXT_CHARACTERS,
        text_chunk_characters=TEXT_CHUNK_CHARACTERS,
    )


def new_capture_document(
    stream: str,
    source: dict[str, Any],
    limits: dict[str, Any],
    *,
    correlation_id: str | None = None,
    evidence_gaps: list[str] | None = None,
) -> dict[str, Any]:
    if correlation_id is not None and not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", correlation_id):
        raise ValueError("correlation id must be 1-128 ASCII letters, digits, dots, underscores or hyphens")
    capture_id = str(uuid4())
    now = datetime.now().astimezone()
    return {
        "schema_version": SCHEMA_VERSION,
        "stream": stream,
        "capture": {
            "capture_id": capture_id,
            "correlation_id": correlation_id or capture_id,
            "started_at": timestamp_fields(now),
            "ended_at": None,
            "duration_seconds": None,
            "status": "running",
            "stop_reason": None,
            "source": sanitize_for_log(source),
            "limits": {**sanitize_for_log(limits), "max_capture_bytes": MAX_CAPTURE_BYTES},
            "counts": {"events": 0, "source_bytes": 0},
            "redactions": [
                "secret-like fields and Bearer credentials",
                "Windows absolute paths and path-valued fields; redacted text is not byte-exact raw evidence",
            ],
            "evidence_gaps": list(evidence_gaps or []),
        },
        "events": [],
    }


def capture_path(document: dict[str, Any], *, log_root: Path = LOG_ROOT) -> Path:
    started = document["capture"]["started_at"]["local"]
    timestamp_digits = "".join(character for character in started if character.isdigit())
    filename_time = f"{timestamp_digits[:8]}_{timestamp_digits[8:17]}"
    short_id = document["capture"]["capture_id"]
    directory = log_root / document["stream"]
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{filename_time}_{short_id}.json"


def append_event(
    document: dict[str, Any],
    event_type: str,
    payload: dict[str, Any],
    *,
    severity: str = "info",
    status: str = "observed",
    evidence_status: str = "captured",
    source_time: dict[str, Any] | None = None,
) -> None:
    sequence = len(document["events"]) + 1
    event = {
        "sequence": sequence,
        "event_id": str(uuid4()),
        "observed_at": timestamp_fields(),
        "source_time": source_time,
        "event_type": event_type,
        "severity": severity,
        "status": status,
        "evidence_status": evidence_status,
        "payload": sanitize_for_log(payload),
    }
    document["events"].append(event)
    if len(_serialize(document)) > MAX_CAPTURE_BYTES - FINALIZATION_RESERVE_BYTES:
        document["events"].pop()
        raise CaptureLimitError("serialized capture byte limit reached; event not persisted")
    document["capture"]["counts"]["events"] = sequence


def finalize_capture(document: dict[str, Any], *, status: str, stop_reason: str) -> None:
    ended = datetime.now().astimezone()
    document["capture"]["ended_at"] = timestamp_fields(ended)
    started_ms = document["capture"]["started_at"]["epoch_ms"]
    document["capture"]["duration_seconds"] = round(
        max(0, document["capture"]["ended_at"]["epoch_ms"] - started_ms) / 1000,
        3,
    )
    document["capture"]["status"] = status
    document["capture"]["stop_reason"] = stop_reason
    document["capture"]["evidence_status"] = (
        "partial"
        if status != "completed" or any(event["evidence_status"] == "partial" for event in document["events"])
        else "captured_for_interval"
    )


def _serialize(document: dict[str, Any]) -> bytes:
    return serialize_pretty_json(document)


def write_capture(path: Path, document: dict[str, Any]) -> None:
    """Atomically replace one UTF-8/no-BOM pretty JSON capture document."""

    write_pretty_json_atomic(
        path,
        document,
        max_bytes=MAX_CAPTURE_BYTES,
        replace_attempts=6,
        base_delay_seconds=0.05,
    )


def project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return f"<ABSOLUTE_PATH_REDACTED>/{path.name}"

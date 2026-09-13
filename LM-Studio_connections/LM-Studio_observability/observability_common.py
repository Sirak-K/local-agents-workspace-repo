"""Shared, bounded persistence primitives for project-owned LM Studio evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import time
from typing import Any
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = PROJECT_ROOT / "LM-Studio_logs"
SCHEMA_VERSION = "1.0"
MAX_INLINE_TEXT_CHARACTERS = 240
TEXT_CHUNK_CHARACTERS = 160
MAX_CAPTURE_BYTES = 8_388_608
FINALIZATION_RESERVE_BYTES = 4096


class CaptureLimitError(ValueError):
    """A capture reached its enforced serialized-byte ceiling."""


def validate_budget(duration: float, interval: float = 1, samples: int = 1) -> None:
    if not math.isfinite(duration) or not 0 <= duration <= 300:
        raise ValueError("duration must be finite and between 0 and 300 seconds")
    if not math.isfinite(interval) or not 0.5 <= interval <= 300:
        raise ValueError("interval must be finite and between 0.5 and 300 seconds")
    if not 1 <= samples <= 1000:
        raise ValueError("sample/event limit must be between 1 and 1000")

_SECRET_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "access_token",
    "auth_token",
    "refresh_token",
    "bearer_token",
    "cookie",
    "lm_api_token",
    "password",
    "secret",
    "token",
}
_PATH_KEY_PARTS = ("path", "directory", "working_dir", "cwd", "file")
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_LM_STUDIO_TOKEN_PATTERN = re.compile(r"\bsk-lm-[a-zA-Z0-9]{8}:[a-zA-Z0-9]{20}\b")
_WINDOWS_PATH_PATTERN = re.compile(r"(?i)(?<![a-z0-9])(?:[a-z]:[\\/]|\\\\)[^\r\n\"'<>]*")
_INLINE_SECRET_PATTERN = re.compile(
    r"(?i)((?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*)[^\s,;]+"
)


def local_timestamp(value: datetime | None = None) -> str:
    moment = (value or datetime.now().astimezone()).astimezone()
    offset = moment.strftime("%z")
    return moment.strftime("%Y-%m-%d | %H:%M:%S.%f")[:-3] + f" {offset[:3]}:{offset[3:]}"


def utc_timestamp(value: datetime | None = None) -> str:
    moment = value or datetime.now(timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%d | %H:%M:%S.%f")[:-3] + " UTC"


def timestamp_fields(value: datetime | None = None) -> dict[str, Any]:
    moment = value or datetime.now().astimezone()
    return {
        "local": local_timestamp(moment),
        "utc": utc_timestamp(moment),
        "epoch_ms": int(moment.timestamp() * 1000),
    }


def timestamp_fields_from_epoch_ms(epoch_ms: int | float) -> dict[str, Any]:
    moment = datetime.fromtimestamp(float(epoch_ms) / 1000, tz=timezone.utc)
    return timestamp_fields(moment)


def _portable_path(value: str) -> str:
    project_text = str(PROJECT_ROOT)
    normalized = value.replace(project_text, "<PROJECT_ROOT>")
    normalized = normalized.replace(project_text.replace("\\", "/"), "<PROJECT_ROOT>")
    if normalized != value:
        return normalized.replace("\\", "/")

    candidate = PureWindowsPath(value)
    if candidate.is_absolute():
        name = candidate.name or "path"
        return f"<ABSOLUTE_PATH_REDACTED>/{name}"
    return value


def _bounded_text(value: str) -> str | dict[str, Any]:
    redacted = _LM_STUDIO_TOKEN_PATTERN.sub("[REDACTED]", value)
    redacted = _BEARER_PATTERN.sub("Bearer [REDACTED]", redacted)
    current_token = os.environ.get("LM_API_TOKEN", "")
    if current_token:
        redacted = redacted.replace(current_token, "[REDACTED]")
    redacted = _INLINE_SECRET_PATTERN.sub(r"\1[REDACTED]", redacted)
    redacted = _WINDOWS_PATH_PATTERN.sub("<ABSOLUTE_PATH_REDACTED>", redacted)
    if len(redacted) <= MAX_INLINE_TEXT_CHARACTERS:
        return redacted
    return {
        "encoding": "utf-8",
        "character_count": len(redacted),
        "sha256": hashlib.sha256(redacted.encode("utf-8")).hexdigest(),
        "text_chunks": [
            redacted[index : index + TEXT_CHUNK_CHARACTERS]
            for index in range(0, len(redacted), TEXT_CHUNK_CHARACTERS)
        ],
    }


def sanitize_for_log(value: Any, *, field_name: str = "") -> Any:
    """Redact secrets/avoidable absolute paths and bound long JSON lines."""

    lowered = field_name.casefold()
    normalized_key = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", field_name).lower().replace("-", "_").replace(" ", "_")
    if (
        normalized_key in _SECRET_KEYS
        or normalized_key.endswith("_api_key")
        or normalized_key.endswith("_access_token")
        or normalized_key.endswith("_auth_token")
        or normalized_key.endswith("_password")
        or normalized_key.endswith("_secret")
    ):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {
            str(key): sanitize_for_log(item, field_name=str(key))
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [sanitize_for_log(item, field_name=field_name) for item in value]
    if isinstance(value, str):
        text = _portable_path(value) if any(part in lowered for part in _PATH_KEY_PARTS) else value
        return _bounded_text(text)
    return value


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
    return (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def write_capture(path: Path, document: dict[str, Any]) -> None:
    """Atomically replace one UTF-8/no-BOM pretty JSON capture document."""

    serialized = _serialize(document)
    if len(serialized) > MAX_CAPTURE_BYTES:
        raise CaptureLimitError("serialized capture exceeded the absolute byte limit")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as handle:
        handle.write(serialized)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        for attempt in range(6):
            try:
                os.replace(temporary, path)
                break
            except PermissionError:
                if attempt == 5:
                    raise
                time.sleep(0.05 * (attempt + 1))
    finally:
        if temporary.exists():
            temporary.unlink()


def project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return f"<ABSOLUTE_PATH_REDACTED>/{path.name}"

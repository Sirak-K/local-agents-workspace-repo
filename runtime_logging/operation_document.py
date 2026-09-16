"""Operation-document contract and bounded in-memory mutation helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
import json
import math
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import secrets
import time
from typing import Any

from .sensitive_data_sanitizer import PROJECT_ROOT, sanitize_for_log

POLICY_PATH = Path(__file__).with_name("runtime_logging_policy.json")
SCHEMA_PATH = Path(__file__).with_name("operation_document.schema.json")
_STREAM_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")
_EVENT_TYPE_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,95}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RuntimeLoggingError(ValueError):
    """Base contract error for project runtime logging."""


class PolicyError(RuntimeLoggingError):
    """The tracked policy is malformed or a value violates it."""


class CaptureLimitError(RuntimeLoggingError):
    """A bounded capture would exceed a hard policy ceiling."""


@lru_cache(maxsize=1)
def load_policy() -> dict[str, Any]:
    with POLICY_PATH.open("r", encoding="utf-8", errors="strict") as handle:
        policy = json.load(handle)
    validate_policy(policy)
    return policy


def validate_policy(policy: dict[str, Any]) -> None:
    required = ("policy_version", "schema_version", "identifier_patterns", "owners", "statuses", "severities", "outcomes", "hard_limits", "retention")
    missing = [key for key in required if key not in policy]
    if missing:
        raise PolicyError(f"policy missing required keys: {', '.join(missing)}")
    for name in ("owners", "statuses", "severities", "outcomes"):
        values = policy[name]
        if not isinstance(values, list) or not values or len(values) != len(set(values)) or not all(isinstance(item, str) and item for item in values):
            raise PolicyError(f"policy {name} must be a non-empty unique string list")
    hard = policy["hard_limits"]
    numeric_positive = ("max_capture_bytes", "max_events", "max_capture_seconds", "atomic_replace_attempts")
    if any(not isinstance(hard.get(key), int) or hard[key] <= 0 for key in numeric_positive):
        raise PolicyError("hard limit integers must be positive")
    delay = hard.get("atomic_replace_base_delay_seconds")
    if not isinstance(delay, (int, float)) or delay < 0:
        raise PolicyError("atomic replace delay must be non-negative")
    for key in ("operation_id", "correlation_id", "event_id"):
        pattern = policy["identifier_patterns"].get(key)
        if not isinstance(pattern, str):
            raise PolicyError(f"identifier pattern missing: {key}")
        re.compile(pattern)
    retention = policy["retention"]
    if not isinstance(retention.get("provisional_until_local_measurement"), bool):
        raise PolicyError("retention provisional flag must be boolean")
    owner_retention = retention.get("owners")
    if not isinstance(owner_retention, dict) or set(owner_retention) != set(policy["owners"]):
        raise PolicyError("retention policy must define every owner exactly once")
    for owner, values in owner_retention.items():
        for key in ("max_finalized_count", "max_age_days", "max_total_bytes"):
            if not isinstance(values.get(key), int) or values[key] <= 0:
                raise PolicyError(f"retention {owner}.{key} must be a positive integer")
        if not isinstance(values.get("protect_latest_failure"), bool):
            raise PolicyError(f"retention {owner}.protect_latest_failure must be boolean")


def _new_identifier() -> str:
    while True:
        value = secrets.token_hex(16)
        if value != "0" * 32:
            return value


def validate_identifier(value: str, kind: str) -> str:
    pattern = load_policy()["identifier_patterns"].get(kind)
    if pattern is None or not isinstance(value, str) or re.fullmatch(pattern, value) is None or value == "0" * len(value):
        raise RuntimeLoggingError(f"invalid {kind}")
    return value


def new_operation_id() -> str:
    return _new_identifier()


def new_correlation_id() -> str:
    return _new_identifier()


def new_event_id() -> str:
    return _new_identifier()


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


def validate_budget(duration: float, interval: float = 1, samples: int = 1) -> None:
    """Compatibility-friendly bounded capture validation used by LM Studio adapters too."""

    if not math.isfinite(duration) or not 0 <= duration <= 300:
        raise ValueError("duration must be finite and between 0 and 300 seconds")
    if not math.isfinite(interval) or not 0.5 <= interval <= 300:
        raise ValueError("interval must be finite and between 0.5 and 300 seconds")
    if not 1 <= samples <= 1000:
        raise ValueError("sample/event limit must be between 1 and 1000")


def _serialize(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _effective_limits(requested: dict[str, Any] | None = None) -> dict[str, Any]:
    policy_hard = load_policy()["hard_limits"]
    hard = {key: policy_hard[key] for key in ("max_capture_bytes", "max_events", "max_capture_seconds")}
    requested = dict(requested or {})
    for key in ("max_capture_bytes", "max_events", "max_capture_seconds"):
        if key in requested:
            value = requested[key]
            if not isinstance(value, (int, float)) or value <= 0 or value > hard[key]:
                raise CaptureLimitError(f"requested {key} exceeds the hard policy ceiling")
            hard[key] = value
    for key, value in requested.items():
        if key not in hard:
            hard[key] = sanitize_for_log(value, field_name=key)
    return hard


def new_operation_document(
    *,
    owner: str,
    stream: str,
    producer: str,
    producer_version: str,
    correlation_id: str | None = None,
    operation_id: str | None = None,
    profile: str | None = None,
    model: str | None = None,
    process: dict[str, Any] | None = None,
    limits: dict[str, Any] | None = None,
    data_policy: dict[str, Any] | None = None,
    detail: dict[str, Any] | None = None,
    evidence_gaps: list[str] | None = None,
) -> dict[str, Any]:
    policy = load_policy()
    if owner not in policy["owners"]:
        raise RuntimeLoggingError(f"unknown owner: {owner}")
    if _STREAM_RE.fullmatch(stream) is None:
        raise RuntimeLoggingError("stream must be a lowercase owner-local token")
    if not producer.strip() or not producer_version.strip():
        raise RuntimeLoggingError("producer name and version are required")
    operation_id = validate_identifier(operation_id, "operation_id") if operation_id else new_operation_id()
    correlation_id = validate_identifier(correlation_id, "correlation_id") if correlation_id else new_correlation_id()
    document = {
        "schema_version": policy["schema_version"],
        "owner": owner,
        "stream": stream,
        "operation": {
            "operation_id": operation_id,
            "correlation_id": correlation_id,
            "status": "running",
            "started_at": timestamp_fields(),
            "ended_at": None,
            "duration_seconds": None,
            "stop_reason": None,
            "producer": {
                "name": sanitize_for_log(producer, field_name="producer_name"),
                "version": sanitize_for_log(producer_version, field_name="producer_version"),
                "process": sanitize_for_log(process, field_name="process") if process is not None else None,
            },
            "profile": sanitize_for_log(profile, field_name="profile") if profile is not None else None,
            "model": sanitize_for_log(model, field_name="model") if model is not None else None,
            "limits": _effective_limits(limits),
            "counts": {"events": 0, "artifacts": 0},
            "data_policy": {
                "raw_sensitive_content": False,
                "secrets": "never persist raw",
                "paths": "project/artifact relative where possible; otherwise redact",
                **sanitize_for_log(data_policy or {}, field_name="data_policy"),
            },
            "detail": sanitize_for_log(detail or {}, field_name="detail"),
        },
        "events": [],
        "artifacts": [],
        "evidence_gaps": [sanitize_for_log(item, field_name="evidence_gap") for item in (evidence_gaps or [])],
    }
    validate_document(document)
    if len(_serialize(document)) > document["operation"]["limits"]["max_capture_bytes"]:
        raise CaptureLimitError("initial operation document exceeds max_capture_bytes")
    return document


def append_event(
    document: dict[str, Any],
    event_type: str,
    details: dict[str, Any],
    *,
    severity: str = "info",
    outcome: str = "observed",
    source_time: dict[str, Any] | None = None,
    duration_seconds: float | None = None,
    allow_sensitive_content: bool = False,
) -> None:
    validate_document(document, require_final=False)
    if document["operation"]["status"] != "running":
        raise RuntimeLoggingError("events may only be appended to a running operation")
    policy = load_policy()
    if severity not in policy["severities"]:
        raise RuntimeLoggingError(f"invalid severity: {severity}")
    if outcome not in policy["outcomes"]:
        raise RuntimeLoggingError(f"invalid outcome: {outcome}")
    if _EVENT_TYPE_RE.fullmatch(event_type) is None:
        raise RuntimeLoggingError("event_type must be a lowercase owner-local token")
    if duration_seconds is not None and (not math.isfinite(duration_seconds) or duration_seconds < 0):
        raise RuntimeLoggingError("duration_seconds must be finite and non-negative")
    if allow_sensitive_content and document["operation"]["data_policy"].get("raw_sensitive_content") is not True:
        raise RuntimeLoggingError("raw sensitive content was not enabled for this capture")
    if source_time is not None:
        _validate_timestamp(source_time)
    sequence = len(document["events"]) + 1
    max_events = int(document["operation"]["limits"]["max_events"])
    if sequence > max_events:
        raise CaptureLimitError("event limit reached; event not persisted")
    event = {
        "sequence": sequence,
        "event_id": new_event_id(),
        "observed_at": timestamp_fields(),
        "source_time": source_time,
        "event_type": event_type,
        "severity": severity,
        "outcome": outcome,
        "duration_seconds": round(duration_seconds, 6) if duration_seconds is not None else None,
        "details": sanitize_for_log(
            details,
            field_name="details",
            allow_sensitive_content=allow_sensitive_content,
        ),
    }
    document["events"].append(event)
    if len(_serialize(document)) > document["operation"]["limits"]["max_capture_bytes"]:
        document["events"].pop()
        raise CaptureLimitError("serialized capture byte limit reached; event not persisted")
    document["operation"]["counts"]["events"] = sequence


def _safe_artifact_reference(reference: str) -> str:
    normalized = reference.replace("\\", "/")
    posix_candidate = PurePosixPath(normalized)
    windows_candidate = PureWindowsPath(normalized)
    if (
        posix_candidate.is_absolute()
        or windows_candidate.is_absolute()
        or ".." in posix_candidate.parts
        or not normalized.strip()
    ):
        raise RuntimeLoggingError("artifact reference must be a safe relative path/reference")
    return normalized


def append_artifact(
    document: dict[str, Any],
    *,
    reference: str,
    byte_count: int,
    sha256: str,
    media_type: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    validate_document(document, require_final=False)
    if document["operation"]["status"] != "running":
        raise RuntimeLoggingError("artifacts may only be appended to a running operation")
    if not isinstance(byte_count, int) or byte_count < 0:
        raise RuntimeLoggingError("artifact byte_count must be a non-negative integer")
    if _SHA256_RE.fullmatch(sha256) is None:
        raise RuntimeLoggingError("artifact sha256 must be 64 lowercase hex characters")
    artifact = {
        "reference": _safe_artifact_reference(reference),
        "bytes": byte_count,
        "sha256": sha256,
        "media_type": sanitize_for_log(media_type, field_name="media_type") if media_type else None,
        "metadata": sanitize_for_log(metadata or {}, field_name="artifact_metadata"),
    }
    document["artifacts"].append(artifact)
    if len(_serialize(document)) > document["operation"]["limits"]["max_capture_bytes"]:
        document["artifacts"].pop()
        raise CaptureLimitError("serialized capture byte limit reached; artifact not persisted")
    document["operation"]["counts"]["artifacts"] = len(document["artifacts"])


def finalize_operation(
    document: dict[str, Any],
    *,
    status: str,
    stop_reason: str,
    duration_seconds: float,
    evidence_gaps: list[str] | None = None,
) -> None:
    validate_document(document, require_final=False)
    policy = load_policy()
    if status not in policy["statuses"] or status == "running":
        raise RuntimeLoggingError("final status must be completed, failed or interrupted")
    if not math.isfinite(duration_seconds) or duration_seconds < 0:
        raise RuntimeLoggingError("duration_seconds must be finite and non-negative")
    if duration_seconds > document["operation"]["limits"]["max_capture_seconds"]:
        raise CaptureLimitError("duration_seconds exceeds max_capture_seconds")
    document["operation"]["ended_at"] = timestamp_fields()
    document["operation"]["duration_seconds"] = round(duration_seconds, 6)
    document["operation"]["status"] = status
    document["operation"]["stop_reason"] = sanitize_for_log(stop_reason, field_name="stop_reason")
    for gap in evidence_gaps or []:
        document["evidence_gaps"].append(sanitize_for_log(gap, field_name="evidence_gap"))
    validate_document(document, require_final=True)
    if len(_serialize(document)) > document["operation"]["limits"]["max_capture_bytes"]:
        raise CaptureLimitError("finalized operation document exceeds max_capture_bytes")


def _validate_timestamp(value: dict[str, Any]) -> None:
    if not isinstance(value, dict) or set(value) != {"local", "utc", "epoch_ms"}:
        raise RuntimeLoggingError("timestamp must contain local, utc and epoch_ms")
    if not isinstance(value["local"], str) or not isinstance(value["utc"], str) or not isinstance(value["epoch_ms"], int):
        raise RuntimeLoggingError("timestamp fields have invalid types")


def validate_document(document: dict[str, Any], *, require_final: bool | None = None) -> None:
    if not isinstance(document, dict):
        raise RuntimeLoggingError("operation document must be an object")
    required_top = {"schema_version", "owner", "stream", "operation", "events", "artifacts", "evidence_gaps"}
    if set(document) != required_top:
        raise RuntimeLoggingError("operation document top-level keys do not match the schema contract")
    policy = load_policy()
    if document["schema_version"] != policy["schema_version"]:
        raise RuntimeLoggingError("unsupported schema_version")
    if document["owner"] not in policy["owners"]:
        raise RuntimeLoggingError("document owner is not policy-approved")
    if not isinstance(document["stream"], str) or _STREAM_RE.fullmatch(document["stream"]) is None:
        raise RuntimeLoggingError("invalid document stream")
    operation = document["operation"]
    required_operation = {
        "operation_id", "correlation_id", "status", "started_at", "ended_at", "duration_seconds",
        "stop_reason", "producer", "profile", "model", "limits", "counts", "data_policy", "detail"
    }
    if not isinstance(operation, dict) or set(operation) != required_operation:
        raise RuntimeLoggingError("operation object keys do not match the schema contract")
    validate_identifier(operation["operation_id"], "operation_id")
    validate_identifier(operation["correlation_id"], "correlation_id")
    if operation["status"] not in policy["statuses"]:
        raise RuntimeLoggingError("invalid operation status")
    producer = operation["producer"]
    if not isinstance(producer, dict) or not {"name", "version"}.issubset(producer) or set(producer) - {"name", "version", "process"}:
        raise RuntimeLoggingError("producer object does not match the schema contract")
    if not all(isinstance(producer[key], str) and producer[key] for key in ("name", "version")):
        raise RuntimeLoggingError("producer name and version must be non-empty strings")
    if producer.get("process") is not None and not isinstance(producer["process"], dict):
        raise RuntimeLoggingError("producer process must be an object or null")
    for key in ("profile", "model"):
        if operation[key] is not None and not isinstance(operation[key], str):
            raise RuntimeLoggingError(f"operation {key} must be a string or null")
    if not isinstance(operation["data_policy"], dict) or not isinstance(operation["detail"], dict):
        raise RuntimeLoggingError("operation data_policy and detail must be objects")
    _validate_timestamp(operation["started_at"])
    if operation["ended_at"] is not None:
        _validate_timestamp(operation["ended_at"])
    if require_final is True and operation["status"] == "running":
        raise RuntimeLoggingError("expected a finalized operation")
    if operation["status"] == "running":
        if operation["ended_at"] is not None or operation["duration_seconds"] is not None or operation["stop_reason"] is not None:
            raise RuntimeLoggingError("running operation cannot have final fields")
    else:
        if operation["ended_at"] is None or operation["duration_seconds"] is None or operation["stop_reason"] is None:
            raise RuntimeLoggingError("finalized operation is missing final fields")
        if not isinstance(operation["stop_reason"], str):
            raise RuntimeLoggingError("finalized operation stop_reason must be a string")
    limits = operation["limits"]
    if not isinstance(limits, dict):
        raise RuntimeLoggingError("operation limits must be an object")
    hard_limits = policy["hard_limits"]
    for key in ("max_capture_bytes", "max_events", "max_capture_seconds"):
        value = limits.get(key) if isinstance(limits, dict) else None
        if not isinstance(value, (int, float)) or value <= 0 or value > hard_limits[key]:
            raise RuntimeLoggingError(f"operation limit {key} is invalid or exceeds policy")
    if operation["duration_seconds"] is not None:
        duration = operation["duration_seconds"]
        if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0 or duration > limits["max_capture_seconds"]:
            raise RuntimeLoggingError("operation duration is invalid or exceeds policy")
    counts = operation["counts"]
    if not isinstance(counts, dict):
        raise RuntimeLoggingError("operation counts must be an object")
    for key in ("events", "artifacts"):
        if not isinstance(counts.get(key), int) or counts[key] < 0:
            raise RuntimeLoggingError("operation counts must be non-negative integers")
    if not isinstance(document["events"], list) or not isinstance(document["artifacts"], list):
        raise RuntimeLoggingError("events and artifacts must be arrays")
    if counts.get("events") != len(document["events"]) or counts.get("artifacts") != len(document["artifacts"]):
        raise RuntimeLoggingError("operation counts do not match document arrays")
    for index, event in enumerate(document["events"], start=1):
        required_event = {"sequence", "event_id", "observed_at", "source_time", "event_type", "severity", "outcome", "duration_seconds", "details"}
        if not isinstance(event, dict) or set(event) != required_event:
            raise RuntimeLoggingError("event object keys do not match the schema contract")
        if event.get("sequence") != index:
            raise RuntimeLoggingError("event sequence is not contiguous")
        validate_identifier(event.get("event_id", ""), "event_id")
        _validate_timestamp(event.get("observed_at"))
        if event.get("source_time") is not None:
            _validate_timestamp(event["source_time"])
        if event.get("severity") not in policy["severities"] or event.get("outcome") not in policy["outcomes"]:
            raise RuntimeLoggingError("event policy value is invalid")
        if not isinstance(event.get("event_type"), str) or _EVENT_TYPE_RE.fullmatch(event["event_type"]) is None:
            raise RuntimeLoggingError("invalid event_type")
        if not isinstance(event["details"], dict):
            raise RuntimeLoggingError("event details must be an object")
        event_duration = event.get("duration_seconds")
        if event_duration is not None and (
            not isinstance(event_duration, (int, float))
            or not math.isfinite(event_duration)
            or event_duration < 0
        ):
            raise RuntimeLoggingError("invalid event duration")
    for artifact in document["artifacts"]:
        required_artifact = {"reference", "bytes", "sha256", "media_type", "metadata"}
        if not isinstance(artifact, dict) or set(artifact) != required_artifact:
            raise RuntimeLoggingError("artifact object keys do not match the schema contract")
        if not isinstance(artifact.get("reference"), str):
            raise RuntimeLoggingError("artifact reference must be a string")
        _safe_artifact_reference(artifact["reference"])
        if (
            not isinstance(artifact.get("bytes"), int)
            or artifact["bytes"] < 0
            or not isinstance(artifact.get("sha256"), str)
            or _SHA256_RE.fullmatch(artifact["sha256"]) is None
        ):
            raise RuntimeLoggingError("invalid artifact record")
        if artifact["media_type"] is not None and not isinstance(artifact["media_type"], str):
            raise RuntimeLoggingError("artifact media_type must be a string or null")
        if not isinstance(artifact["metadata"], dict):
            raise RuntimeLoggingError("artifact metadata must be an object")
    if not isinstance(document["evidence_gaps"], list) or not all(isinstance(item, str) for item in document["evidence_gaps"]):
        raise RuntimeLoggingError("evidence_gaps must be a string list")


def operation_capture_path(document: dict[str, Any], *, output_root: Path | None = None) -> Path:
    validate_document(document, require_final=False)
    root = output_root or (PROJECT_ROOT / "logs")
    started = document["operation"]["started_at"]["local"]
    digits = "".join(character for character in started if character.isdigit())
    timestamp_digits = f"{digits[:8]}_{digits[8:17]}"
    directory = root / document["owner"] / document["stream"]
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{timestamp_digits}_{document['operation']['operation_id']}.json"


def monotonic_seconds_since(start_ns: int) -> float:
    elapsed_ns = time.monotonic_ns() - start_ns
    if elapsed_ns < 0:
        raise RuntimeLoggingError("monotonic clock moved backwards")
    return elapsed_ns / 1_000_000_000

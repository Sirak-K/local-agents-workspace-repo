"""Crash-resistant bounded pretty-JSON persistence for runtime evidence."""

from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import time
from typing import Any

from .operation_document import CaptureLimitError, load_policy, validate_document


def serialize_pretty_json(document: Any) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def read_json(path: Path, *, max_bytes: int | None = None) -> Any:
    ceiling = max_bytes or int(load_policy()["hard_limits"]["max_capture_bytes"])
    with path.open("rb") as handle:
        data = handle.read(ceiling + 1)
    if len(data) > ceiling:
        raise CaptureLimitError("JSON file exceeds read byte ceiling")
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValueError("UTF-8 BOM is forbidden")
    return json.loads(data.decode("utf-8", errors="strict"))


def write_pretty_json_atomic(
    path: Path,
    document: Any,
    *,
    max_bytes: int,
    replace_attempts: int,
    base_delay_seconds: float,
) -> None:
    serialized = serialize_pretty_json(document)
    if len(serialized) > max_bytes:
        raise CaptureLimitError("serialized JSON exceeded the byte ceiling")
    if replace_attempts < 1 or base_delay_seconds < 0:
        raise ValueError("invalid atomic replace retry policy")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{secrets.token_hex(4)}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        for attempt in range(replace_attempts):
            try:
                os.replace(temporary, path)
                break
            except PermissionError:
                if attempt == replace_attempts - 1:
                    raise
                time.sleep(base_delay_seconds * (attempt + 1))
    finally:
        if temporary.exists():
            temporary.unlink()


def write_operation_document(path: Path, document: dict[str, Any]) -> None:
    validate_document(document)
    hard = load_policy()["hard_limits"]
    max_bytes = min(int(document["operation"]["limits"]["max_capture_bytes"]), int(hard["max_capture_bytes"]))
    write_pretty_json_atomic(
        path,
        document,
        max_bytes=max_bytes,
        replace_attempts=int(hard["atomic_replace_attempts"]),
        base_delay_seconds=float(hard["atomic_replace_base_delay_seconds"]),
    )

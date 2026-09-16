"""Data-minimizing sanitization primitives for local runtime evidence."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_INLINE_TEXT_CHARACTERS = 240
DEFAULT_TEXT_CHUNK_CHARACTERS = 160

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
_SENSITIVE_CONTENT_KEYS = {
    "prompt",
    "story",
    "story_text",
    "text",
    "content",
    "caption",
    "transcript",
    "model_input",
    "model_output",
    "input_text",
    "output_text",
    "reference_voice",
    "voice_reference",
    "audio",
    "waveform",
    "image",
}
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_LM_STUDIO_TOKEN_PATTERN = re.compile(r"\bsk-lm-[a-zA-Z0-9]{8}:[a-zA-Z0-9]{20}\b")
_WINDOWS_PATH_PATTERN = re.compile(r"(?i)(?<![a-z0-9])(?:[a-z]:[\\/]|\\\\)[^\r\n\"'<>]*")
_INLINE_SECRET_PATTERN = re.compile(
    r"(?i)((?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*)[^\s,;]+"
)


def _normalized_key(field_name: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", field_name).lower().replace("-", "_").replace(" ", "_")


def _is_secret_key(field_name: str) -> bool:
    normalized = _normalized_key(field_name)
    return (
        normalized in _SECRET_KEYS
        or normalized.endswith("_api_key")
        or normalized.endswith("_access_token")
        or normalized.endswith("_auth_token")
        or normalized.endswith("_password")
        or normalized.endswith("_secret")
    )


def _portable_path(value: str, project_root: Path) -> str:
    project_text = str(project_root)
    normalized = value.replace(project_text, "<PROJECT_ROOT>")
    normalized = normalized.replace(project_text.replace("\\", "/"), "<PROJECT_ROOT>")
    if normalized != value:
        return normalized.replace("\\", "/")
    candidate = PureWindowsPath(value)
    if candidate.is_absolute():
        name = candidate.name or "path"
        return f"<ABSOLUTE_PATH_REDACTED>/{name}"
    posix_candidate = PurePosixPath(value)
    if posix_candidate.is_absolute():
        name = posix_candidate.name or "path"
        return f"<ABSOLUTE_PATH_REDACTED>/{name}"
    path_candidate = Path(value)
    if path_candidate.is_absolute():
        try:
            return path_candidate.resolve().relative_to(project_root.resolve()).as_posix()
        except (OSError, ValueError):
            return f"<ABSOLUTE_PATH_REDACTED>/{path_candidate.name or 'path'}"
    return value


def _redact_text(value: str) -> str:
    redacted = _LM_STUDIO_TOKEN_PATTERN.sub("[REDACTED]", value)
    redacted = _BEARER_PATTERN.sub("Bearer [REDACTED]", redacted)
    current_token = os.environ.get("LM_API_TOKEN", "")
    if current_token:
        redacted = redacted.replace(current_token, "[REDACTED]")
    redacted = _INLINE_SECRET_PATTERN.sub(r"\1[REDACTED]", redacted)
    return _WINDOWS_PATH_PATTERN.sub("<ABSOLUTE_PATH_REDACTED>", redacted)


def _content_digest(value: str) -> dict[str, Any]:
    encoded = value.encode("utf-8")
    return {
        "content_redacted": True,
        "encoding": "utf-8",
        "character_count": len(value),
        "byte_count": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


def _bounded_text(value: str, *, max_inline_text_characters: int, text_chunk_characters: int) -> str | dict[str, Any]:
    if len(value) <= max_inline_text_characters:
        return value
    return {
        "encoding": "utf-8",
        "character_count": len(value),
        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "text_chunks": [
            value[index : index + text_chunk_characters]
            for index in range(0, len(value), text_chunk_characters)
        ],
    }


def sanitize_for_log(
    value: Any,
    *,
    field_name: str = "",
    project_root: Path = PROJECT_ROOT,
    allow_sensitive_content: bool = False,
    max_inline_text_characters: int = DEFAULT_MAX_INLINE_TEXT_CHARACTERS,
    text_chunk_characters: int = DEFAULT_TEXT_CHUNK_CHARACTERS,
) -> Any:
    """Redact secrets/absolute paths and minimize content-bearing fields by default."""

    if _is_secret_key(field_name):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {
            str(key): sanitize_for_log(
                item,
                field_name=str(key),
                project_root=project_root,
                allow_sensitive_content=allow_sensitive_content,
                max_inline_text_characters=max_inline_text_characters,
                text_chunk_characters=text_chunk_characters,
            )
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [
            sanitize_for_log(
                item,
                field_name=field_name,
                project_root=project_root,
                allow_sensitive_content=allow_sensitive_content,
                max_inline_text_characters=max_inline_text_characters,
                text_chunk_characters=text_chunk_characters,
            )
            for item in value
        ]
    if isinstance(value, bytes):
        return {
            "binary_redacted": True,
            "byte_count": len(value),
            "sha256": hashlib.sha256(value).hexdigest(),
        }
    if isinstance(value, str):
        normalized_key = _normalized_key(field_name)
        if not allow_sensitive_content and normalized_key in _SENSITIVE_CONTENT_KEYS:
            return _content_digest(value)
        lowered = field_name.casefold()
        text = _portable_path(value, project_root) if any(part in lowered for part in _PATH_KEY_PARTS) else value
        text = _redact_text(text)
        return _bounded_text(
            text,
            max_inline_text_characters=max_inline_text_characters,
            text_chunk_characters=text_chunk_characters,
        )
    return value

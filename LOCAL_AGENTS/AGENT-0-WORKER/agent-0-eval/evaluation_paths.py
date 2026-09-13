"""Canonical, fail-closed paths for WORKER evaluation artifacts."""
from __future__ import annotations

from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVALUATION_ROOT = PROJECT_ROOT / "model_evaluations"
EVAL_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
RUN_ID_RE = re.compile(r"[0-9a-f]{32}\Z")


def validate_eval_id(eval_id: str) -> str:
    if not isinstance(eval_id, str) or not EVAL_ID_RE.fullmatch(eval_id) or eval_id in {".", ".."}:
        raise ValueError("eval id must be 1-128 safe ASCII characters")
    return eval_id


def validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("run id must be 32 lowercase hexadecimal characters")
    return run_id


def _within(path: Path, root: Path) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve(strict=False)
    resolved.relative_to(resolved_root)
    return resolved


def evaluation_directory(eval_id: str, *, create: bool = False) -> Path:
    validate_eval_id(eval_id)
    root = EVALUATION_ROOT.resolve()
    directory = _within(root / eval_id, root)
    if create:
        directory.mkdir(parents=True, exist_ok=True)
    if directory.exists() and directory.is_symlink():
        raise ValueError("evaluation directory may not be a symlink")
    return directory


def run_directory(eval_id: str, run_id: str, *, create: bool = False) -> Path:
    validate_run_id(run_id)
    parent = evaluation_directory(eval_id, create=create)
    directory = _within(parent / run_id, parent)
    if create:
        directory.mkdir(parents=False, exist_ok=False)
    if directory.exists() and directory.is_symlink():
        raise ValueError("run directory may not be a symlink")
    return directory


def evaluation_file(eval_id: str, value: str | Path, *, must_exist: bool = True) -> Path:
    base = evaluation_directory(eval_id)
    candidate = Path(value)
    if candidate.is_absolute():
        resolved = candidate.resolve(strict=must_exist)
    else:
        resolved = (base / candidate).resolve(strict=must_exist)
    resolved.relative_to(base.resolve())
    if must_exist and not resolved.is_file():
        raise ValueError("evaluation file is unavailable")
    return resolved


def project_relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()

"""Canonical, containment-checked paths for 0-WORKER evaluation artifacts."""
from __future__ import annotations

from pathlib import Path
import re

EVAL_MODULE_ROOT = Path(__file__).resolve().parent
ROLE_ROOT = EVAL_MODULE_ROOT.parent
LOCAL_AGENTS_ROOT = ROLE_ROOT.parent
PROJECT_ROOT = LOCAL_AGENTS_ROOT.parent
MODEL_EVALUATIONS_ROOT = PROJECT_ROOT / "model_evaluations"

_EVAL_ID = re.compile(r"EVAL_[A-Za-z0-9][A-Za-z0-9._-]{0,122}\Z")
_RUN_ID = re.compile(r"[0-9a-f]{32}\Z")


def _validate_layout() -> None:
    expected = (
        (EVAL_MODULE_ROOT.name, "agent-0-eval"),
        (ROLE_ROOT.name, "AGENT-0-WORKER"),
        (LOCAL_AGENTS_ROOT.name, "LOCAL_AGENTS"),
    )
    if any(actual != wanted for actual, wanted in expected):
        raise RuntimeError("0-WORKER evaluation module is not in the expected repository layout")
    if not MODEL_EVALUATIONS_ROOT.is_dir() or MODEL_EVALUATIONS_ROOT.is_symlink():
        raise RuntimeError("model_evaluations root is missing or is not a real directory")


def validate_eval_id(eval_id: str) -> str:
    if not isinstance(eval_id, str) or _EVAL_ID.fullmatch(eval_id) is None:
        raise ValueError("eval id must use the established EVAL_<safe-id> format")
    return eval_id


def validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str) or _RUN_ID.fullmatch(run_id) is None:
        raise ValueError("run id must be 32 lowercase hexadecimal characters")
    return run_id


def _resolved_root() -> Path:
    if not MODEL_EVALUATIONS_ROOT.is_dir() or MODEL_EVALUATIONS_ROOT.is_symlink():
        raise ValueError("model_evaluations root is unavailable or unsafe")
    return MODEL_EVALUATIONS_ROOT.resolve(strict=True)


def _contained(path: Path) -> Path:
    resolved_root = _resolved_root()
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError("evaluation path escapes model_evaluations") from error
    return path


def eval_directory(eval_id: str) -> Path:
    path = _contained(MODEL_EVALUATIONS_ROOT / validate_eval_id(eval_id))
    if path.exists():
        if path.is_symlink() or not path.is_dir():
            raise ValueError("eval id collides with a link or non-directory")
        _contained(path)
    return path


def run_directory(eval_id: str, run_id: str) -> Path:
    parent = eval_directory(eval_id)
    path = _contained(parent / validate_run_id(run_id))
    if path.exists():
        if path.is_symlink() or not path.is_dir():
            raise ValueError("run id collides with a link or non-directory")
        _contained(path)
    return path


def existing_run_directory(eval_id: str, run_id: str) -> Path:
    path = run_directory(eval_id, run_id)
    if not path.is_dir():
        raise ValueError("evaluation run does not exist")
    return path


def create_run_directory(eval_id: str, run_id: str) -> Path:
    parent = eval_directory(eval_id)
    parent.mkdir(parents=False, exist_ok=True)
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("eval id collides with a link or non-directory")
    _contained(parent)
    path = run_directory(eval_id, run_id)
    path.mkdir(parents=False, exist_ok=False)
    _contained(path)
    return path


def project_relative_path(relative: str | Path) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("project evidence path must be relative and contained")
    resolved_project = PROJECT_ROOT.resolve(strict=True)
    resolved = (PROJECT_ROOT / candidate).resolve(strict=False)
    try:
        resolved.relative_to(resolved_project)
    except ValueError as error:
        raise ValueError("project evidence path escapes repository") from error
    return resolved


def relative_to_project(path: Path) -> str:
    resolved_project = PROJECT_ROOT.resolve(strict=True)
    resolved = path.resolve(strict=False)
    try:
        return resolved.relative_to(resolved_project).as_posix()
    except ValueError as error:
        raise ValueError("path is outside repository") from error


_validate_layout()

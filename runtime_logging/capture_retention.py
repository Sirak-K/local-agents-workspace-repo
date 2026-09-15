"""Deterministic retention planning for finalized owner-specific captures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .atomic_json_store import read_json
from .operation_document import load_policy, validate_document


@dataclass(frozen=True)
class RetentionDecision:
    path: Path
    reason: str
    started_epoch_ms: int
    byte_count: int


def retention_policy_for_owner(owner: str, *, policy: dict | None = None) -> dict:
    active_policy = policy or load_policy()
    owners = active_policy["retention"]["owners"]
    if owner not in owners:
        raise ValueError(f"retention owner is not policy-approved: {owner}")
    return dict(owners[owner])


def _finalized_capture(path: Path, *, expected_owner: str) -> tuple[dict, int] | None:
    try:
        document = read_json(path)
        validate_document(document)
    except (OSError, UnicodeError, ValueError, TypeError):
        return None
    if document["owner"] != expected_owner or document["operation"]["status"] == "running":
        return None
    try:
        byte_count = path.stat().st_size
    except OSError:
        return None
    return document, byte_count


def plan_retention(
    owner_directory: Path,
    *,
    owner: str,
    now: datetime | None = None,
    policy: dict | None = None,
) -> list[RetentionDecision]:
    """Return an oldest-first deletion plan without mutating the filesystem."""

    retention = retention_policy_for_owner(owner, policy=policy)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    captures: list[tuple[Path, dict, int]] = []
    for path in sorted(owner_directory.rglob("*.json"), key=lambda item: item.as_posix()):
        item = _finalized_capture(path, expected_owner=owner)
        if item is not None:
            document, byte_count = item
            captures.append((path, document, byte_count))
    captures.sort(key=lambda row: (row[1]["operation"]["started_at"]["epoch_ms"], row[0].as_posix()))

    protected: set[Path] = set()
    if retention.get("protect_latest_failure"):
        failures = [row for row in captures if row[1]["operation"]["status"] in ("failed", "interrupted")]
        if failures:
            protected.add(failures[-1][0])

    reasons: dict[Path, str] = {}
    cutoff_ms = int(current.timestamp() * 1000) - int(retention["max_age_days"]) * 86_400_000
    for path, document, _ in captures:
        if path not in protected and document["operation"]["started_at"]["epoch_ms"] < cutoff_ms:
            reasons[path] = "age_limit"

    survivors = [row for row in captures if row[0] not in reasons]
    excess_count = max(0, len(survivors) - int(retention["max_finalized_count"]))
    for path, _, _ in survivors:
        if excess_count <= 0:
            break
        if path in protected:
            continue
        reasons[path] = "count_limit"
        excess_count -= 1

    survivors = [row for row in captures if row[0] not in reasons]
    max_total = int(retention["max_total_bytes"])
    total = sum(row[2] for row in survivors)
    for path, _, byte_count in survivors:
        if total <= max_total:
            break
        if path in protected:
            continue
        reasons[path] = "total_byte_limit"
        total -= byte_count

    decisions = [
        RetentionDecision(
            path=path,
            reason=reasons[path],
            started_epoch_ms=document["operation"]["started_at"]["epoch_ms"],
            byte_count=byte_count,
        )
        for path, document, byte_count in captures
        if path in reasons
    ]
    return sorted(decisions, key=lambda item: (item.started_epoch_ms, item.path.as_posix()))


def apply_retention(decisions: Iterable[RetentionDecision], *, dry_run: bool = True) -> list[Path]:
    ordered = sorted(decisions, key=lambda item: (item.started_epoch_ms, item.path.as_posix()))
    if dry_run:
        return [item.path for item in ordered]
    removed: list[Path] = []
    for decision in ordered:
        decision.path.unlink()
        removed.append(decision.path)
    return removed

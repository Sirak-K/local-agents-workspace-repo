"""Persist one owner-specific FF-only AutoPull attempt without performing Git actions."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_logging import append_event, finalize_operation, new_operation_document, operation_capture_path, write_operation_document
from runtime_logging.operation_document import RuntimeLoggingError, monotonic_seconds_since

_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_OUTCOMES = {
    "updated": ("completed", "success"),
    "up_to_date": ("completed", "success"),
    "skipped_dirty": ("completed", "skipped"),
    "skipped_non_fast_forward": ("completed", "skipped"),
    "fetch_error": ("failed", "failure"),
    "error": ("failed", "failure"),
}
_FETCH_RESULTS = {"success", "error", "not_attempted"}
_ANCESTRY = {"fast_forward", "non_fast_forward", "unknown", "not_checked"}


def _sha(value: str | None, *, label: str, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise RuntimeLoggingError(f"{label} is required")
        return None
    normalized = value.strip().lower()
    if _SHA_RE.fullmatch(normalized) is None:
        raise RuntimeLoggingError(f"{label} must be a lowercase/normalizable Git object id")
    return normalized


def create_autopull_capture(
    *,
    local_head: str,
    remote_head: str | None,
    tracked_clean: bool,
    fetch_result: str,
    ancestry: str,
    outcome: str,
    reason: str,
    correlation_id: str | None = None,
    output_root: Path | None = None,
    error_class: str | None = None,
) -> tuple[Path, dict]:
    """Create one capture for a real sync attempt/state-change; never for an idle poll."""

    if outcome not in _OUTCOMES:
        raise RuntimeLoggingError(f"unsupported AutoPull outcome: {outcome}")
    if fetch_result not in _FETCH_RESULTS:
        raise RuntimeLoggingError(f"unsupported fetch_result: {fetch_result}")
    if ancestry not in _ANCESTRY:
        raise RuntimeLoggingError(f"unsupported ancestry result: {ancestry}")
    local = _sha(local_head, label="local_head", required=True)
    remote = _sha(remote_head, label="remote_head")
    if outcome == "updated" and (not tracked_clean or ancestry != "fast_forward" or fetch_result != "success" or remote is None):
        raise RuntimeLoggingError("updated requires clean tracked state, successful fetch, fast-forward ancestry and remote_head")
    if outcome == "skipped_dirty" and tracked_clean:
        raise RuntimeLoggingError("skipped_dirty requires tracked_clean=false")
    if outcome == "skipped_non_fast_forward" and ancestry != "non_fast_forward":
        raise RuntimeLoggingError("skipped_non_fast_forward requires non_fast_forward ancestry")
    if outcome == "fetch_error" and fetch_result != "error":
        raise RuntimeLoggingError("fetch_error requires fetch_result=error")

    started_ns = time.monotonic_ns()
    final_status, event_outcome = _OUTCOMES[outcome]
    document = new_operation_document(
        owner="github_autopull",
        stream="sync_attempt",
        producer="github-autopull-watcher-adapter",
        producer_version="1.0",
        correlation_id=correlation_id,
        detail={"integration_contract": "invoke only for a real attempt or state change; never each idle poll"},
        evidence_gaps=["The local watcher owns Git execution; this adapter records caller-supplied decisions and does not independently prove command execution."],
    )
    path = operation_capture_path(document, output_root=output_root)
    write_operation_document(path, document)
    details = {
        "local_head": local,
        "remote_head": remote,
        "tracked_clean": tracked_clean,
        "fetch_result": fetch_result,
        "ancestry": ancestry,
        "decision": outcome,
        "reason": reason,
        "error_class": error_class,
    }
    append_event(
        document,
        "autopull.sync_attempt",
        details,
        severity="error" if final_status == "failed" else "info",
        outcome=event_outcome,
    )
    finalize_operation(document, status=final_status, stop_reason=outcome, duration_seconds=monotonic_seconds_since(started_ns))
    write_operation_document(path, document)
    return path, document


def _bool(text: str) -> bool:
    normalized = text.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError("expected true/false")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-head", required=True)
    parser.add_argument("--remote-head")
    parser.add_argument("--tracked-clean", required=True, type=_bool)
    parser.add_argument("--fetch-result", required=True, choices=sorted(_FETCH_RESULTS))
    parser.add_argument("--ancestry", required=True, choices=sorted(_ANCESTRY))
    parser.add_argument("--outcome", required=True, choices=sorted(_OUTCOMES))
    parser.add_argument("--reason", required=True)
    parser.add_argument("--error-class")
    parser.add_argument("--correlation-id")
    parser.add_argument("--output-root")
    args = parser.parse_args(argv)
    try:
        path, document = create_autopull_capture(
            local_head=args.local_head,
            remote_head=args.remote_head,
            tracked_clean=args.tracked_clean,
            fetch_result=args.fetch_result,
            ancestry=args.ancestry,
            outcome=args.outcome,
            reason=args.reason,
            error_class=args.error_class,
            correlation_id=args.correlation_id,
            output_root=Path(args.output_root) if args.output_root else None,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"github_autopull observability: failed | {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"github_autopull observability: {document['operation']['status']} | file={path}")
    return 0 if document["operation"]["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

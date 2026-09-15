"""Persist one owner-specific FF-only AutoPull state change without performing Git actions."""

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
_DECISION_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,95}$")
_EVENT_OUTCOMES = {"observed", "success", "failure", "partial", "skipped"}
_FETCH_RESULTS = {"success", "error", "not_attempted"}
_ANCESTRY = {"fast_forward", "non_fast_forward", "remote_ancestor", "diverged", "unknown", "not_checked"}


def _sha(value: str | None, *, label: str) -> str | None:
    if value is None or not value.strip():
        return None
    normalized = value.strip().lower()
    if _SHA_RE.fullmatch(normalized) is None:
        raise RuntimeLoggingError(f"{label} must be a lowercase/normalizable Git object id")
    return normalized


def create_autopull_capture(
    *,
    decision: str,
    event_outcome: str,
    reason: str,
    local_head: str | None = None,
    remote_head: str | None = None,
    tracked_clean: bool | None = None,
    fetch_result: str = "not_attempted",
    ancestry: str = "not_checked",
    correlation_id: str | None = None,
    output_root: Path | None = None,
    error_class: str | None = None,
) -> tuple[Path, dict]:
    """Create one capture for a real watcher attempt/state-change; never for an idle poll."""

    if _DECISION_RE.fullmatch(decision) is None:
        raise RuntimeLoggingError("decision must be a lowercase owner-local token")
    if event_outcome not in _EVENT_OUTCOMES:
        raise RuntimeLoggingError(f"unsupported event_outcome: {event_outcome}")
    if fetch_result not in _FETCH_RESULTS:
        raise RuntimeLoggingError(f"unsupported fetch_result: {fetch_result}")
    if ancestry not in _ANCESTRY:
        raise RuntimeLoggingError(f"unsupported ancestry result: {ancestry}")
    local = _sha(local_head, label="local_head")
    remote = _sha(remote_head, label="remote_head")

    if decision == "updated" and (
        local is None
        or remote is None
        or tracked_clean is not True
        or ancestry != "fast_forward"
        or fetch_result != "success"
    ):
        raise RuntimeLoggingError("updated requires local/remote heads, clean tracked state, successful fetch and fast-forward ancestry")
    if decision == "up_to_date" and (local is None or remote is None or local != remote or fetch_result != "success"):
        raise RuntimeLoggingError("up_to_date requires equal local/remote heads after successful fetch")
    if decision == "skipped_dirty" and tracked_clean is not False:
        raise RuntimeLoggingError("skipped_dirty requires tracked_clean=false")
    if decision == "skipped_non_fast_forward" and ancestry != "non_fast_forward":
        raise RuntimeLoggingError("skipped_non_fast_forward requires non_fast_forward ancestry")
    if decision == "fetch_error" and fetch_result != "error":
        raise RuntimeLoggingError("fetch_error requires fetch_result=error")
    if event_outcome == "failure" and not error_class:
        error_class = "autopull_failure"

    started_ns = time.monotonic_ns()
    final_status = "failed" if event_outcome == "failure" else "completed"
    document = new_operation_document(
        owner="github_autopull",
        stream="sync_attempt",
        producer="github-autopull-watcher-adapter",
        producer_version="1.1",
        correlation_id=correlation_id,
        detail={"integration_contract": "invoke only for a real attempt or state change; never each idle poll"},
        evidence_gaps=[
            "The PowerShell watcher owns Git execution; this capture records watcher-observed decisions and does not independently replay Git commands."
        ],
    )
    path = operation_capture_path(document, output_root=output_root)
    write_operation_document(path, document)
    append_event(
        document,
        "autopull.state_change",
        {
            "local_head": local,
            "remote_head": remote,
            "tracked_clean": tracked_clean,
            "fetch_result": fetch_result,
            "ancestry": ancestry,
            "decision": decision,
            "reason": reason,
            "error_class": error_class,
        },
        severity="error" if event_outcome == "failure" else "info",
        outcome=event_outcome,
    )
    finalize_operation(
        document,
        status=final_status,
        stop_reason=decision,
        duration_seconds=monotonic_seconds_since(started_ns),
    )
    write_operation_document(path, document)
    return path, document


def _optional_bool(text: str) -> bool:
    normalized = text.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError("expected true/false")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--event-outcome", required=True, choices=sorted(_EVENT_OUTCOMES))
    parser.add_argument("--reason", required=True)
    parser.add_argument("--local-head")
    parser.add_argument("--remote-head")
    parser.add_argument("--tracked-clean", type=_optional_bool)
    parser.add_argument("--fetch-result", default="not_attempted", choices=sorted(_FETCH_RESULTS))
    parser.add_argument("--ancestry", default="not_checked", choices=sorted(_ANCESTRY))
    parser.add_argument("--error-class")
    parser.add_argument("--correlation-id")
    parser.add_argument("--output-root")
    args = parser.parse_args(argv)
    try:
        path, document = create_autopull_capture(
            decision=args.decision,
            event_outcome=args.event_outcome,
            reason=args.reason,
            local_head=args.local_head,
            remote_head=args.remote_head,
            tracked_clean=args.tracked_clean,
            fetch_result=args.fetch_result,
            ancestry=args.ancestry,
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

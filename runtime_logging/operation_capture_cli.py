"""Bounded stdlib CLI for runtime-operation capture and read-only operator inspection."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from .atomic_json_store import read_json, write_operation_document
from .capture_retention import plan_retention
from .operation_document import (
    RuntimeLoggingError,
    append_artifact,
    append_event,
    finalize_operation,
    load_policy,
    new_operation_document,
    operation_capture_path,
    timestamp_fields_from_epoch_ms,
    validate_document,
    validate_identifier,
)


def _json_object(text: str, label: str) -> dict:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeLoggingError(f"{label} must be valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeLoggingError(f"{label} must be a JSON object")
    return value


def _emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True))


def _capture_paths(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if not root.is_dir():
        raise RuntimeLoggingError(f"capture root is not a directory: {root}")
    return sorted((path for path in root.rglob("*.json") if path.is_file()), key=lambda item: item.as_posix())


def _relative_display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_validated(path: Path) -> dict:
    document = read_json(path)
    validate_document(document)
    return document


def _begin(args: argparse.Namespace) -> int:
    process = {"pid": args.pid} if args.pid is not None else None
    document = new_operation_document(
        owner=args.owner,
        stream=args.stream,
        producer=args.producer,
        producer_version=args.producer_version,
        correlation_id=args.correlation_id,
        profile=args.profile,
        model=args.model,
        process=process,
        data_policy={"raw_sensitive_content": bool(args.allow_sensitive_content)},
        detail=_json_object(args.detail_json, "--detail-json") if args.detail_json else None,
        evidence_gaps=args.evidence_gap,
    )
    output = operation_capture_path(document, output_root=Path(args.output_root) if args.output_root else None)
    write_operation_document(output, document)
    _emit({
        "correlation_id": document["operation"]["correlation_id"],
        "operation_id": document["operation"]["operation_id"],
        "file": str(output),
        "status": "running",
    })
    return 0


def _event(args: argparse.Namespace) -> int:
    path = Path(args.file)
    document = read_json(path)
    source_time = timestamp_fields_from_epoch_ms(args.source_epoch_ms) if args.source_epoch_ms is not None else None
    append_event(
        document,
        args.event_type,
        _json_object(args.details_json, "--details-json"),
        severity=args.severity,
        outcome=args.outcome,
        source_time=source_time,
        duration_seconds=args.duration_seconds,
        allow_sensitive_content=args.allow_sensitive_content,
    )
    write_operation_document(path, document)
    _emit({"file": str(path), "events": document["operation"]["counts"]["events"], "status": "running"})
    return 0


def _artifact(args: argparse.Namespace) -> int:
    path = Path(args.file)
    document = read_json(path)
    append_artifact(
        document,
        reference=args.reference,
        byte_count=args.bytes,
        sha256=args.sha256,
        media_type=args.media_type,
        metadata=_json_object(args.metadata_json, "--metadata-json") if args.metadata_json else None,
    )
    write_operation_document(path, document)
    _emit({"artifacts": document["operation"]["counts"]["artifacts"], "file": str(path), "status": "running"})
    return 0


def _finalize(args: argparse.Namespace) -> int:
    path = Path(args.file)
    document = read_json(path)
    finalize_operation(
        document,
        status=args.status,
        stop_reason=args.stop_reason,
        duration_seconds=args.duration_seconds,
        evidence_gaps=args.evidence_gap,
    )
    write_operation_document(path, document)
    _emit({"file": str(path), "status": document["operation"]["status"]})
    return 0


def _validate(args: argparse.Namespace) -> int:
    root = Path(args.root)
    invalid: list[dict[str, str]] = []
    paths = _capture_paths(root)
    for path in paths:
        try:
            _read_validated(path)
        except (OSError, UnicodeError, json.JSONDecodeError, RuntimeLoggingError, ValueError, TypeError) as exc:
            invalid.append({
                "file": _relative_display(path, root),
                "error_class": type(exc).__name__,
                "message": str(exc),
            })
    _emit({
        "command": "validate",
        "files": len(paths),
        "invalid": invalid,
        "invalid_count": len(invalid),
        "root": root.as_posix(),
        "status": "PASS" if not invalid else "FAIL",
    })
    return 0 if not invalid else 1


def _matches_query(document: dict, args: argparse.Namespace) -> bool:
    operation = document["operation"]
    if args.owner and document["owner"] != args.owner:
        return False
    if args.correlation_id and operation["correlation_id"] != args.correlation_id:
        return False
    if args.failures_only and operation["status"] not in {"failed", "interrupted"}:
        return False
    if args.has_artifact and not document["artifacts"]:
        return False
    if args.artifact_reference and not any(
        artifact.get("reference") == args.artifact_reference for artifact in document["artifacts"]
    ):
        return False
    if args.has_evidence_gaps and not document["evidence_gaps"]:
        return False
    return True


def _query_summary(path: Path, root: Path, document: dict) -> dict:
    operation = document["operation"]
    return {
        "artifact_count": len(document["artifacts"]),
        "correlation_id": operation["correlation_id"],
        "evidence_gap_count": len(document["evidence_gaps"]),
        "file": _relative_display(path, root),
        "operation_id": operation["operation_id"],
        "owner": document["owner"],
        "started_epoch_ms": operation["started_at"]["epoch_ms"],
        "status": operation["status"],
        "stop_reason": operation["stop_reason"],
        "stream": document["stream"],
    }


def _query(args: argparse.Namespace) -> int:
    root = Path(args.root)
    policy = load_policy()
    if args.owner and args.owner not in policy["owners"]:
        raise RuntimeLoggingError(f"owner is not policy-approved: {args.owner}")
    if args.correlation_id:
        validate_identifier(args.correlation_id, "correlation_id")

    results: list[dict] = []
    for path in _capture_paths(root):
        document = _read_validated(path)
        if _matches_query(document, args):
            results.append(_query_summary(path, root, document))
    results.sort(key=lambda item: (item["started_epoch_ms"], item["file"]))
    _emit({"command": "query", "count": len(results), "results": results, "root": root.as_posix()})
    return 0


def _prune(args: argparse.Namespace) -> int:
    if not args.dry_run:
        raise RuntimeLoggingError("prune is dry-run-only until Codex locks final retention after local measurement")
    root = Path(args.root)
    policy = load_policy()
    if args.owner not in policy["owners"]:
        raise RuntimeLoggingError(f"owner is not policy-approved: {args.owner}")
    owner_directory = root / args.owner
    for path in _capture_paths(owner_directory):
        document = _read_validated(path)
        if document["owner"] != args.owner:
            raise RuntimeLoggingError(
                f"capture owner mismatch under {args.owner}: {_relative_display(path, root)}"
            )
    now = None
    if args.now_epoch_ms is not None:
        now = datetime.fromtimestamp(args.now_epoch_ms / 1000, tz=timezone.utc)
    decisions = plan_retention(owner_directory, owner=args.owner, now=now, policy=policy)
    _emit({
        "command": "prune",
        "dry_run": True,
        "owner": args.owner,
        "root": root.as_posix(),
        "count": len(decisions),
        "decisions": [
            {
                "bytes": decision.byte_count,
                "file": _relative_display(decision.path, root),
                "reason": decision.reason,
                "started_epoch_ms": decision.started_epoch_ms,
            }
            for decision in decisions
        ],
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    begin = subparsers.add_parser("begin", help="create one bounded running operation capture")
    begin.add_argument("--owner", required=True)
    begin.add_argument("--stream", required=True)
    begin.add_argument("--producer", required=True)
    begin.add_argument("--producer-version", required=True)
    begin.add_argument("--correlation-id")
    begin.add_argument("--profile")
    begin.add_argument("--model")
    begin.add_argument("--pid", type=int)
    begin.add_argument("--detail-json")
    begin.add_argument("--evidence-gap", action="append", default=[])
    begin.add_argument("--allow-sensitive-content", action="store_true")
    begin.add_argument("--output-root")
    begin.set_defaults(handler=_begin)

    event = subparsers.add_parser("event", help="append one sanitized owner-local event")
    event.add_argument("--file", required=True)
    event.add_argument("--event-type", required=True)
    event.add_argument("--details-json", required=True)
    event.add_argument("--severity", default="info")
    event.add_argument("--outcome", default="observed")
    event.add_argument("--source-epoch-ms", type=float)
    event.add_argument("--duration-seconds", type=float)
    event.add_argument("--allow-sensitive-content", action="store_true")
    event.set_defaults(handler=_event)

    artifact = subparsers.add_parser("artifact", help="append one artifact reference without media bytes")
    artifact.add_argument("--file", required=True)
    artifact.add_argument("--reference", required=True)
    artifact.add_argument("--bytes", required=True, type=int)
    artifact.add_argument("--sha256", required=True)
    artifact.add_argument("--media-type")
    artifact.add_argument("--metadata-json")
    artifact.set_defaults(handler=_artifact)

    finalize = subparsers.add_parser("finalize", help="finalize a running operation with caller-measured monotonic duration")
    finalize.add_argument("--file", required=True)
    finalize.add_argument("--status", required=True, choices=("completed", "failed", "interrupted"))
    finalize.add_argument("--stop-reason", required=True)
    finalize.add_argument("--duration-seconds", required=True, type=float)
    finalize.add_argument("--evidence-gap", action="append", default=[])
    finalize.set_defaults(handler=_finalize)

    validate = subparsers.add_parser("validate", help="validate local capture JSON without mutation")
    validate.add_argument("--root", default="logs")
    validate.set_defaults(handler=_validate)

    query = subparsers.add_parser("query", help="query validated capture summaries without raw payload output")
    query.add_argument("--root", default="logs")
    query.add_argument("--owner")
    query.add_argument("--correlation-id")
    query.add_argument("--failures-only", action="store_true")
    query.add_argument("--has-artifact", action="store_true")
    query.add_argument("--artifact-reference")
    query.add_argument("--has-evidence-gaps", action="store_true")
    query.set_defaults(handler=_query)

    prune = subparsers.add_parser("prune", help="show deterministic retention plan; deletion is not enabled")
    prune.add_argument("--root", default="logs")
    prune.add_argument("--owner", required=True)
    prune.add_argument("--dry-run", action="store_true", required=True)
    prune.add_argument("--now-epoch-ms", type=int)
    prune.set_defaults(handler=_prune)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (OSError, UnicodeError, json.JSONDecodeError, RuntimeLoggingError, ValueError, TypeError) as exc:
        print(f"runtime_logging: failed | {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

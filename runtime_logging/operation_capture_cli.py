"""Bounded stdlib CLI for PowerShell/subprocess runtime-operation boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .atomic_json_store import read_json, write_operation_document
from .operation_document import (
    RuntimeLoggingError,
    append_artifact,
    append_event,
    finalize_operation,
    new_operation_document,
    operation_capture_path,
    timestamp_fields_from_epoch_ms,
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (OSError, UnicodeError, json.JSONDecodeError, RuntimeLoggingError, ValueError) as exc:
        print(f"runtime_logging: failed | {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

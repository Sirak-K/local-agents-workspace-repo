"""Capture bounded, potentially sensitive LM Studio model input/output events."""

from __future__ import annotations

import argparse

from lm_studio_cli_stream import capture_cli_stream, completion_line


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acknowledge-sensitive-content", action="store_true")
    parser.add_argument("--duration-seconds", type=float, default=60)
    parser.add_argument("--max-events", type=int, default=250)
    parser.add_argument("--max-source-bytes", type=int, default=2_097_152)
    parser.add_argument("--correlation-id")
    args = parser.parse_args()
    if not args.acknowledge_sensitive_content:
        parser.error(
            "--acknowledge-sensitive-content is required because this stream can include "
            "full prompts, tool material and model output from other clients"
        )
    try:
        path, document = capture_cli_stream(
            stream_name="model_io_events",
            source_name="model",
            filters=("input", "output"),
            duration_seconds=args.duration_seconds,
            max_events=args.max_events,
            max_source_bytes=args.max_source_bytes,
            correlation_id=args.correlation_id,
        )
    except (OSError, ValueError) as exc:
        print(f"model_io_events: failed | {exc}")
        return 2
    print(completion_line(path, document))
    return 2 if document["capture"]["status"] in ("source_error", "completed_with_errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())

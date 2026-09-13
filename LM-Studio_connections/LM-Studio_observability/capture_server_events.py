"""Capture bounded LM Studio server events without loading a model."""

from __future__ import annotations

import argparse

from lm_studio_cli_stream import capture_cli_stream, completion_line


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-seconds", type=float, default=60)
    parser.add_argument("--max-events", type=int, default=500)
    parser.add_argument("--max-source-bytes", type=int, default=1_048_576)
    parser.add_argument("--correlation-id")
    args = parser.parse_args()
    try:
        path, document = capture_cli_stream(
            stream_name="server_events",
            source_name="server",
            duration_seconds=args.duration_seconds,
            max_events=args.max_events,
            max_source_bytes=args.max_source_bytes,
            correlation_id=args.correlation_id,
        )
    except (OSError, ValueError) as exc:
        print(f"server_events: failed | {exc}")
        return 2
    print(completion_line(path, document))
    return 2 if document["capture"]["status"] in ("source_error", "completed_with_errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Observe bounded LM Studio model load/unload state through native REST API v1."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from observability_common import (
    append_event,
    CaptureLimitError,
    capture_path,
    finalize_capture,
    new_capture_document,
    project_relative,
    validate_budget,
    write_capture,
)


DEFAULT_BASE_URL = "http://127.0.0.1:1234"
MAX_RESPONSE_BYTES = 4_194_304


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("redirects are forbidden for authenticated local API requests")


def validate_base_url(base_url: str) -> None:
    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("base URL must be a plain HTTP loopback origin without credentials")
    _ = parsed.port


def fetch_models(base_url: str, token: str, *, timeout_seconds: float = 10) -> dict[str, Any]:
    validate_base_url(base_url)
    request = Request(
        f"{base_url.rstrip('/')}/api/v1/models",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=timeout_seconds) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("GET /api/v1/models exceeded the response byte limit")
    decoded = body.decode("utf-8", errors="strict")
    payload = json.loads(decoded)
    if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
        raise ValueError("GET /api/v1/models did not return a models array")
    return payload


def model_state(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    state: dict[str, dict[str, Any]] = {}
    for model in payload["models"]:
        if not isinstance(model, dict) or not isinstance(model.get("key"), str):
            raise ValueError("models catalog contains an invalid model entry")
        instances = model.get("loaded_instances")
        if not isinstance(instances, list):
            raise ValueError("loaded_instances is missing or invalid; cannot interpret it as unloaded")
        state[model["key"]] = {
            "model_key": model["key"],
            "model_type": model.get("type", "unknown"),
            "loaded_instances": instances,
        }
    return state


def state_changes(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> list[tuple[str, dict[str, Any]]]:
    changes: list[tuple[str, dict[str, Any]]] = []
    for key in sorted(set(before) | set(after)):
        previous = before.get(key, {"model_key": key, "model_type": "unknown", "loaded_instances": []})
        current = after.get(key, {"model_key": key, "model_type": "unknown", "loaded_instances": []})
        old_instances = previous["loaded_instances"]
        new_instances = current["loaded_instances"]
        if key not in after:
            changes.append(("model_catalog_entry_removed", {
                "model_key": key,
                "previous_loaded_instances": old_instances,
                "causal_origin": "catalog disappearance does not prove unloading",
            }))
            continue
        if old_instances == new_instances:
            continue
        if not old_instances and new_instances:
            event_type = "model_loaded"
        elif old_instances and not new_instances:
            event_type = "model_unloaded"
        else:
            event_type = "loaded_instances_changed"
        changes.append(
            (
                event_type,
                {
                    "model_key": key,
                    "model_type": current.get("model_type", previous.get("model_type")),
                    "before": old_instances,
                    "after": new_instances,
                    "causal_origin": "not established by state polling",
                },
            )
        )
    return changes


def capture_lifecycle(
    *,
    token: str,
    base_url: str,
    duration_seconds: float,
    interval_seconds: float,
    max_polls: int,
    correlation_id: str | None = None,
    log_root: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    if not token.strip():
        raise ValueError("LM_API_TOKEN is unavailable")
    validate_budget(duration_seconds, interval_seconds, max_polls)
    validate_base_url(base_url)

    document = new_capture_document(
        "model_lifecycle_events",
        {
            "name": "LM Studio native REST API v1",
            "endpoint": "/api/v1/models",
            "base_url": base_url,
            "method": "authenticated state polling and diff",
        },
        {
            "duration_seconds": duration_seconds,
            "interval_seconds": interval_seconds,
            "max_polls": max_polls,
            "max_response_bytes_per_poll": MAX_RESPONSE_BYTES,
        },
        correlation_id=correlation_id,
        evidence_gaps=[
            "State polling observes changes but cannot prove whether manual, API, JIT or TTL behavior caused them.",
            "Load/unload transitions between polls can be missed.",
        ],
    )
    output = capture_path(document, log_root=log_root) if log_root else capture_path(document)
    write_capture(output, document)
    deadline = time.monotonic() + duration_seconds
    previous: dict[str, dict[str, Any]] | None = None
    polls = 0
    consecutive_errors = 0
    status = "completed"
    stop_reason = "duration_limit" if duration_seconds else "single_snapshot"

    try:
        while polls < max_polls:
            polls += 1
            document["capture"]["counts"]["polls"] = polls
            try:
                request_timeout = min(10, max(0.1, deadline - time.monotonic())) if duration_seconds else 10
                payload = fetch_models(base_url, token, timeout_seconds=request_timeout)
                current = model_state(payload)
                if previous is None:
                    loaded = [item for item in current.values() if item["loaded_instances"]]
                    append_event(
                        document,
                        "initial_model_state",
                        {
                            "catalog_model_count": len(current),
                            "loaded_model_count": len(loaded),
                            "loaded_models": loaded,
                        },
                    )
                else:
                    for event_type, change in state_changes(previous, current):
                        append_event(document, event_type, change)
                previous = current
                consecutive_errors = 0
            except CaptureLimitError:
                raise
            except (HTTPError, URLError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
                consecutive_errors += 1
                append_event(
                    document,
                    "model_state_poll_failed",
                    {"error_class": type(exc).__name__, "message": str(exc)},
                    severity="error",
                    status="source_error",
                    evidence_status="partial",
                )
                if consecutive_errors >= 3:
                    status = "source_error"
                    stop_reason = "three_consecutive_poll_errors"
                    break
            document["capture"]["counts"]["polls"] = polls
            write_capture(output, document)
            if duration_seconds == 0 or time.monotonic() >= deadline:
                break
            time.sleep(min(interval_seconds, max(0, deadline - time.monotonic())))
        if polls >= max_polls and duration_seconds > 0 and time.monotonic() < deadline:
            stop_reason = "poll_limit"
    except CaptureLimitError:
        status = "completed_with_limit"
        stop_reason = "serialized_byte_limit"
    except KeyboardInterrupt:
        status = "interrupted"
        stop_reason = "operator_interrupt"
    finally:
        if status == "completed" and any(event["status"] == "source_error" for event in document["events"]):
            status = "completed_with_errors"
        finalize_capture(document, status=status, stop_reason=stop_reason)
        write_capture(output, document)
    return output, document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--duration-seconds", type=float, default=60)
    parser.add_argument("--interval-seconds", type=float, default=2)
    parser.add_argument("--max-polls", type=int, default=120)
    parser.add_argument("--correlation-id")
    args = parser.parse_args()
    try:
        path, document = capture_lifecycle(
            token=os.environ.get("LM_API_TOKEN", ""),
            base_url=args.base_url,
            duration_seconds=args.duration_seconds,
            interval_seconds=args.interval_seconds,
            max_polls=args.max_polls,
            correlation_id=args.correlation_id,
        )
    except ValueError as exc:
        print(f"model_lifecycle_events: failed | {exc}")
        return 2
    capture = document["capture"]
    print(
        f"model_lifecycle_events: {capture['status']} | "
        f"events={capture['counts']['events']} | file={project_relative(path)}"
    )
    return 2 if capture["status"] in ("source_error", "completed_with_errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())

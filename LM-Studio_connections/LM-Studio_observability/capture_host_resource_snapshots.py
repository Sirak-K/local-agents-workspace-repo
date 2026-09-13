"""Capture bounded host evidence for LM Studio processes, server and GPU."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any

from observability_common import (
    PROJECT_ROOT,
    CaptureLimitError,
    append_event,
    capture_path,
    finalize_capture,
    new_capture_document,
    project_relative,
    validate_budget,
    write_capture,
)


PROCESS_NAMES = ("LM Studio", "lms", "llama-server")


def _optional_int(value: str) -> int | None:
    normalized = value.strip()
    return int(normalized) if normalized.lstrip("-").isdigit() else None


def _run_json(command: list[str], *, timeout_seconds: float = 8) -> tuple[Any, str | None]:
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            text=True,
            encoding="utf-8",
            errors="strict",
        )
    except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        return None, f"exit {result.returncode}: {message[:240]}"
    text = result.stdout.strip()
    if not text:
        return [], None
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"JSONDecodeError: {exc}"


def _process_snapshot() -> tuple[list[dict[str, Any]], str | None]:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        return [], "PowerShell process query is unavailable"
    script = (
        "$names=@('LM Studio','lms','llama-server');"
        "@(Get-Process -ErrorAction SilentlyContinue | Where-Object {$names -contains $_.ProcessName} | "
        "Select-Object @{n='process_name';e={$_.ProcessName}},@{n='pid';e={$_.Id}},"
        "@{n='cpu_seconds';e={$_.CPU}},@{n='working_set_bytes';e={$_.WorkingSet64}},"
        "@{n='responding';e={$_.Responding}}) | ConvertTo-Json -Compress"
    )
    payload, error = _run_json([powershell, "-NoProfile", "-Command", script])
    if error:
        return [], error
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return [], "Process query returned an unexpected JSON shape"
    return [item for item in payload if isinstance(item, dict)], None


def _server_snapshot() -> tuple[Any, str | None]:
    if not shutil.which("lms"):
        return None, "lms CLI is unavailable"
    return _run_json(["lms", "server", "status", "--json", "--quiet"])


def _gpu_snapshot(relevant_pids: set[int]) -> tuple[dict[str, Any], str | None]:
    if not shutil.which("nvidia-smi"):
        return {}, "nvidia-smi is unavailable"
    gpu_result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        timeout=8,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    app_result = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=pid,used_memory",
            "--format=csv,noheader,nounits",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        timeout=8,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    if gpu_result.returncode != 0:
        return {}, f"nvidia-smi GPU query exit {gpu_result.returncode}"
    devices = []
    for line in gpu_result.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) == 5:
            devices.append(
                {
                    "gpu_index": _optional_int(parts[0]),
                    "name": parts[1],
                    "memory_total_mib": _optional_int(parts[2]),
                    "memory_used_mib": _optional_int(parts[3]),
                    "utilization_percent": _optional_int(parts[4]),
                }
            )
    relevant_compute_processes = []
    if app_result.returncode == 0:
        for line in app_result.stdout.splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) == 2 and parts[0].isdigit() and int(parts[0]) in relevant_pids:
                relevant_compute_processes.append(
                    {
                        "pid": int(parts[0]),
                        "used_gpu_memory_mib": _optional_int(parts[1]),
                    }
                )
    error = None
    if not devices:
        error = "nvidia-smi GPU query returned no parseable device rows"
    elif app_result.returncode != 0:
        error = f"nvidia-smi process query exit {app_result.returncode}; device data retained"
    return {"devices": devices, "relevant_compute_processes": relevant_compute_processes}, error


def take_snapshot() -> dict[str, Any]:
    processes, process_error = _process_snapshot()
    pids = {int(item["pid"]) for item in processes if isinstance(item.get("pid"), int)}
    server, server_error = _server_snapshot()
    try:
        gpu, gpu_error = _gpu_snapshot(pids)
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError) as exc:
        gpu, gpu_error = {}, f"{type(exc).__name__}: {exc}"
    errors = {
        name: error
        for name, error in (
            ("process_query", process_error),
            ("server_status", server_error),
            ("gpu_query", gpu_error),
        )
        if error
    }
    return {
        "relevant_process_names": list(PROCESS_NAMES),
        "processes": processes,
        "lm_studio_server": server,
        "gpu": gpu,
        "component_errors": errors,
    }


def capture_host(
    *,
    duration_seconds: float,
    interval_seconds: float,
    max_snapshots: int,
    correlation_id: str | None = None,
    log_root: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    validate_budget(duration_seconds, interval_seconds, max_snapshots)
    document = new_capture_document(
        "host_resource_snapshots",
        {
            "name": "bounded local host inspection",
            "components": ["LM Studio-related processes", "LM Studio server status", "NVIDIA GPU"],
        },
        {
            "duration_seconds": duration_seconds,
            "interval_seconds": interval_seconds,
            "max_snapshots": max_snapshots,
        },
        correlation_id=correlation_id,
        evidence_gaps=[
            "Only named LM Studio-related processes are captured; this is not a full process inventory.",
            "Snapshots can miss short-lived resource changes between samples.",
            "Running an lms status command may initialize the lightweight LM Studio background service but never loads a model.",
        ],
    )
    output = capture_path(document, log_root=log_root) if log_root else capture_path(document)
    write_capture(output, document)
    deadline = time.monotonic() + duration_seconds
    snapshots = 0
    status = "completed"
    stop_reason = "duration_limit" if duration_seconds else "single_snapshot"
    try:
        while snapshots < max_snapshots:
            payload = take_snapshot()
            severity = "warning" if payload["component_errors"] else "info"
            evidence_status = "partial" if payload["component_errors"] else "captured"
            append_event(
                document,
                "host_resource_snapshot",
                payload,
                severity=severity,
                evidence_status=evidence_status,
            )
            snapshots += 1
            document["capture"]["counts"]["snapshots"] = snapshots
            write_capture(output, document)
            if duration_seconds == 0 or time.monotonic() >= deadline:
                break
            time.sleep(min(interval_seconds, max(0, deadline - time.monotonic())))
        if snapshots >= max_snapshots and duration_seconds > 0 and time.monotonic() < deadline:
            stop_reason = "snapshot_limit"
    except CaptureLimitError:
        status = "completed_with_limit"
        stop_reason = "serialized_byte_limit"
    except KeyboardInterrupt:
        status = "interrupted"
        stop_reason = "operator_interrupt"
    finally:
        finalize_capture(document, status=status, stop_reason=stop_reason)
        write_capture(output, document)
    return output, document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-seconds", type=float, default=0)
    parser.add_argument("--interval-seconds", type=float, default=5)
    parser.add_argument("--max-snapshots", type=int, default=12)
    parser.add_argument("--correlation-id")
    args = parser.parse_args()
    try:
        path, document = capture_host(
            duration_seconds=args.duration_seconds,
            interval_seconds=args.interval_seconds,
            max_snapshots=args.max_snapshots,
            correlation_id=args.correlation_id,
        )
    except ValueError as exc:
        print(f"host_resource_snapshots: failed | {exc}")
        return 2
    capture = document["capture"]
    print(
        f"host_resource_snapshots: {capture['status']} | "
        f"events={capture['counts']['events']} | file={project_relative(path)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

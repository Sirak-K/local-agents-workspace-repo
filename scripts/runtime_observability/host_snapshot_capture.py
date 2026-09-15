"""Capture one bounded relevant-PID/process and NVIDIA snapshot for a runtime operation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_logging import append_event, finalize_operation, new_operation_document, operation_capture_path, write_operation_document
from runtime_logging.operation_document import RuntimeLoggingError, monotonic_seconds_since

Runner = Callable[..., subprocess.CompletedProcess[str]]


def _run(command: list[str], *, runner: Runner = subprocess.run, timeout_seconds: float = 8) -> tuple[str, str | None]:
    try:
        result = runner(
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
        return "", f"{type(exc).__name__}: {exc}"
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        return "", f"exit {result.returncode}: {message[:240]}"
    return result.stdout or "", None


def query_relevant_processes(pids: list[int], *, runner: Runner = subprocess.run, powershell: str | None = None) -> tuple[list[dict[str, Any]], str | None]:
    unique = sorted({int(pid) for pid in pids if int(pid) > 0})
    if not unique:
        return [], None
    executable = powershell or shutil.which("powershell") or shutil.which("pwsh")
    if not executable:
        return [], "PowerShell is unavailable"
    ids = ",".join(str(pid) for pid in unique)
    script = (
        f"$ids=@({ids});"
        "@(Get-Process -Id $ids -ErrorAction SilentlyContinue | "
        "Select-Object @{n='process_name';e={$_.ProcessName}},@{n='pid';e={$_.Id}},"
        "@{n='cpu_seconds';e={$_.CPU}},@{n='working_set_bytes';e={$_.WorkingSet64}},"
        "@{n='peak_working_set_bytes';e={$_.PeakWorkingSet64}},@{n='responding';e={$_.Responding}}) | ConvertTo-Json -Compress"
    )
    stdout, error = _run([executable, "-NoProfile", "-Command", script], runner=runner)
    if error:
        return [], error
    try:
        payload = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError as exc:
        return [], f"JSONDecodeError: {exc}"
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        return [], "PowerShell process query returned an unexpected JSON shape"
    allowed = set(unique)
    return [item for item in payload if isinstance(item.get("pid"), int) and item["pid"] in allowed], None


def _csv_rows(text: str, width: int) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) == width:
            rows.append(parts)
    return rows


def query_nvidia(pids: list[int], *, runner: Runner = subprocess.run, nvidia_smi: str | None = None) -> tuple[dict[str, Any], str | None]:
    executable = nvidia_smi or shutil.which("nvidia-smi")
    if not executable:
        return {}, "nvidia-smi is unavailable"
    gpu_stdout, gpu_error = _run(
        [executable, "--query-gpu=index,name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
        runner=runner,
    )
    if gpu_error:
        return {}, gpu_error
    app_stdout, app_error = _run(
        [executable, "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
        runner=runner,
    )
    devices = []
    for index, name, total, used, utilization in _csv_rows(gpu_stdout, 5):
        try:
            devices.append(
                {
                    "gpu_index": int(index),
                    "name": name,
                    "memory_total_mib": int(total),
                    "memory_used_mib": int(used),
                    "utilization_percent": int(utilization),
                }
            )
        except ValueError:
            continue
    relevant = set(int(pid) for pid in pids)
    compute = []
    if app_error is None:
        for pid, used in _csv_rows(app_stdout, 2):
            try:
                parsed_pid = int(pid)
                parsed_used = int(used)
            except ValueError:
                continue
            if parsed_pid in relevant:
                compute.append({"pid": parsed_pid, "used_gpu_memory_mib": parsed_used})
    error = app_error
    if not devices:
        error = "nvidia-smi returned no parseable GPU rows" if error is None else error
    return {"devices": devices, "relevant_compute_processes": compute}, error


def create_host_snapshot_capture(
    *,
    pids: list[int],
    correlation_id: str | None = None,
    output_root: Path | None = None,
    process_query: Callable[[list[int]], tuple[list[dict[str, Any]], str | None]] = query_relevant_processes,
    gpu_query: Callable[[list[int]], tuple[dict[str, Any], str | None]] = query_nvidia,
) -> tuple[Path, dict]:
    normalized = sorted({int(pid) for pid in pids if int(pid) > 0})
    if not normalized:
        raise RuntimeLoggingError("at least one positive relevant PID is required")
    started_ns = time.monotonic_ns()
    document = new_operation_document(
        owner="host",
        stream="resource_snapshot",
        producer="bounded-host-snapshot-adapter",
        producer_version="1.0",
        correlation_id=correlation_id,
        detail={"relevant_pids": normalized},
        evidence_gaps=["Snapshot sampling can miss short-lived resource changes between observations."],
    )
    path = operation_capture_path(document, output_root=output_root)
    write_operation_document(path, document)
    processes, process_error = process_query(normalized)
    gpu, gpu_error = gpu_query(normalized)
    errors = {name: error for name, error in (("process_query", process_error), ("gpu_query", gpu_error)) if error}
    append_event(
        document,
        "host.resource_snapshot",
        {"relevant_pids": normalized, "processes": processes, "gpu": gpu, "component_errors": errors},
        severity="warning" if errors else "info",
        outcome="partial" if errors else "success",
    )
    status = "completed" if not errors else "completed"
    if gpu_error and "compute" in gpu_error.lower():
        document["evidence_gaps"].append("Per-process GPU memory may be unavailable under Windows WDDM; device-level data can still be valid.")
    finalize_operation(document, status=status, stop_reason="single_snapshot", duration_seconds=monotonic_seconds_since(started_ns))
    write_operation_document(path, document)
    return path, document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", action="append", type=int, required=True)
    parser.add_argument("--correlation-id")
    parser.add_argument("--output-root")
    args = parser.parse_args(argv)
    try:
        path, document = create_host_snapshot_capture(
            pids=args.pid,
            correlation_id=args.correlation_id,
            output_root=Path(args.output_root) if args.output_root else None,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"host observability: failed | {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"host observability: {document['operation']['status']} | file={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

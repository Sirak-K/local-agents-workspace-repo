"""Lifecycle control for trusted WORKER tool subprocesses, not a sandbox.

Launch suspended, assign to an owned Windows Job, then resume. Never attach
external processes. WMI/COM/service-mediated children are outside this contract.
"""
from __future__ import annotations

import ctypes as c
from ctypes import wintypes as w
import os
from pathlib import Path
import shutil
import subprocess
from threading import RLock
import time


class StartupInfo(c.Structure):
    _fields_ = [("cb", w.DWORD), ("reserved", w.LPWSTR), ("desktop", w.LPWSTR),
                ("title", w.LPWSTR), ("x", w.DWORD), ("y", w.DWORD),
                ("xsize", w.DWORD), ("ysize", w.DWORD), ("xchars", w.DWORD),
                ("ychars", w.DWORD), ("fill", w.DWORD), ("flags", w.DWORD),
                ("show", w.WORD), ("reserved2_size", w.WORD), ("reserved2", c.c_void_p),
                ("stdin", w.HANDLE), ("stdout", w.HANDLE), ("stderr", w.HANDLE)]


class ProcessInfo(c.Structure):
    _fields_ = [("process", w.HANDLE), ("thread", w.HANDLE),
                ("pid", w.DWORD), ("tid", w.DWORD)]


class BasicLimits(c.Structure):
    _fields_ = [("process_time", c.c_longlong), ("job_time", c.c_longlong),
                ("flags", w.DWORD), ("min_working", c.c_size_t),
                ("max_working", c.c_size_t), ("active_limit", w.DWORD),
                ("affinity", c.c_size_t), ("priority", w.DWORD), ("scheduling", w.DWORD)]


class IoCounters(c.Structure):
    _fields_ = [(name, c.c_ulonglong) for name in
                ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]


class ExtendedLimits(c.Structure):
    _fields_ = [("basic", BasicLimits), ("io", IoCounters),
                ("process_memory", c.c_size_t), ("job_memory", c.c_size_t),
                ("peak_process_memory", c.c_size_t), ("peak_job_memory", c.c_size_t)]


class Accounting(c.Structure):
    _fields_ = [("user_time", c.c_longlong), ("kernel_time", c.c_longlong),
                ("period_user_time", c.c_longlong), ("period_kernel_time", c.c_longlong),
                ("page_faults", w.DWORD), ("total_processes", w.DWORD),
                ("active_processes", w.DWORD), ("terminated_processes", w.DWORD)]


def _kernel():
    if os.name != "nt":
        raise RuntimeError("WORKER process control requires Windows Job Objects")
    dll = c.WinDLL("kernel32", use_last_error=True)
    signatures = {
        "CreateJobObjectW": ([c.c_void_p, w.LPCWSTR], w.HANDLE),
        "SetInformationJobObject": ([w.HANDLE, c.c_int, c.c_void_p, w.DWORD], w.BOOL),
        "QueryInformationJobObject": ([w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.c_void_p], w.BOOL),
        "AssignProcessToJobObject": ([w.HANDLE, w.HANDLE], w.BOOL),
        "TerminateJobObject": ([w.HANDLE, w.UINT], w.BOOL),
        "TerminateProcess": ([w.HANDLE, w.UINT], w.BOOL),
        "ResumeThread": ([w.HANDLE], w.DWORD),
        "GetExitCodeProcess": ([w.HANDLE, c.POINTER(w.DWORD)], w.BOOL),
        "CloseHandle": ([w.HANDLE], w.BOOL),
        "CreateProcessW": ([w.LPCWSTR, w.LPWSTR, c.c_void_p, c.c_void_p, w.BOOL,
                            w.DWORD, c.c_void_p, w.LPCWSTR,
                            c.POINTER(StartupInfo), c.POINTER(ProcessInfo)], w.BOOL),
    }
    for name, (arguments, result) in signatures.items():
        getattr(dll, name).argtypes = arguments
        getattr(dll, name).restype = result
    return dll


class WorkerToolProcessControl:
    """Only evaluator-owned trusted argv. Not a model-facing arbitrary shell."""
    def __init__(self) -> None:
        self.kernel = _kernel()
        self.lock = RLock()
        self.stopping = False
        self.process_handles = {}
        self.job = self.kernel.CreateJobObjectW(None, None)
        if not self.job:
            raise c.WinError(c.get_last_error())
        limits = ExtendedLimits()
        # Kill-on-owner-close and max eight processes. No breakaway permission.
        limits.basic.flags = 0x2000 | 0x0008
        limits.basic.active_limit = 8
        try:
            self._check(self.kernel.SetInformationJobObject(self.job, 9, c.byref(limits), c.sizeof(limits)))
        except BaseException:
            self.kernel.CloseHandle(self.job)
            self.job = None
            raise

    @staticmethod
    def _check(success) -> None:
        if not success:
            raise c.WinError(c.get_last_error())

    def dispatch(self, argv: list[str], cwd: Path) -> int:
        with self.lock:
            if self.stopping or not self.job:
                raise RuntimeError("tool dispatch is closed")
            if not argv or any(not isinstance(a, str) or "\0" in a for a in argv):
                raise ValueError("invalid trusted tool argv")
            executable = shutil.which(argv[0])
            if not executable or not cwd.resolve().is_dir():
                raise ValueError("tool executable or working directory is unavailable")
            command = subprocess.list2cmdline([executable, *argv[1:]])
            if len(command) > 8192:
                raise ValueError("tool command exceeds 8192 characters")
            # No inherited token/credentials; no inheritable handles.
            allowed = {"systemroot", "windir", "path", "temp", "tmp"}
            environment = c.create_unicode_buffer("\0".join(
                f"{key}={value}" for key, value in sorted(os.environ.items()) if key.lower() in allowed
            ) + "\0\0")
            startup, info = StartupInfo(), ProcessInfo()
            startup.cb, startup.flags, startup.show = c.sizeof(startup), 1, 0
            self._check(self.kernel.CreateProcessW(
                executable, c.create_unicode_buffer(command), None, None, False,
                0x4 | 0x400 | 0x08000000, environment, str(cwd.resolve()),
                c.byref(startup), c.byref(info),
            ))
            try:
                self._check(self.kernel.AssignProcessToJobObject(self.job, info.process))
                if self.kernel.ResumeThread(info.thread) == 0xFFFFFFFF:
                    raise c.WinError(c.get_last_error())
                self.process_handles[int(info.pid)] = info.process
                return int(info.pid)
            except BaseException:
                self.kernel.TerminateProcess(info.process, 1)
                raise
            finally:
                self.kernel.CloseHandle(info.thread)
                if int(info.pid) not in self.process_handles:
                    self.kernel.CloseHandle(info.process)

    def exit_status(self, pid: int) -> int | None:
        """Retain the owned handle so the actual OS exit code can be verified."""
        with self.lock:
            handle = self.process_handles.get(pid)
            if not handle:
                raise ValueError("process is not owned by this job")
            status = w.DWORD()
            self._check(self.kernel.GetExitCodeProcess(handle, c.byref(status)))
            return None if status.value == 259 else int(status.value)

    def accounting(self) -> dict[str, int]:
        with self.lock:
            if not self.job:
                raise RuntimeError("job is closed; accounting unavailable")
            state = Accounting()
            self._check(self.kernel.QueryInformationJobObject(self.job, 1, c.byref(state), c.sizeof(state), None))
            return {"active_processes": int(state.active_processes), "total_processes": int(state.total_processes)}

    def stop(self, budget_seconds: float = 3) -> dict[str, int | bool]:
        if not 0 < budget_seconds <= 5:
            raise ValueError("tool stop budget must be in (0, 5]")
        with self.lock:
            self.stopping = True
            self._check(self.kernel.TerminateJobObject(self.job, 1))
        deadline = time.monotonic() + budget_seconds
        while True:
            state = self.accounting()
            if state["active_processes"] == 0:
                return dict(state, verified=True)
            if time.monotonic() >= deadline:
                return dict(state, verified=False)
            time.sleep(0.02)

    def close(self) -> None:
        with self.lock:
            if self.job:
                try:
                    self.stop()
                finally:
                    for handle in self.process_handles.values():
                        self.kernel.CloseHandle(handle)
                    self.process_handles.clear()
                    self.kernel.CloseHandle(self.job)
                    self.job = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

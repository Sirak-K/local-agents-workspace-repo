"""Bounded IPC to one authenticated, cancellable LM Studio SDK prediction."""
from __future__ import annotations

import json
import os
from pathlib import Path
from queue import Empty, Full, Queue
import shutil
import subprocess
from threading import Event, Lock, Thread
from typing import Any

SDK_WORKER = Path(__file__).with_name("lm_studio_sdk_prediction.mjs")
MAX_IPC_BYTES = 262144


def stop_verdict(result: dict[str, Any] | None, requested: bool, started: bool, not_started: bool = False) -> str:
    """Client termination and deadlines deliberately never imply server stop."""
    if result is None:
        return "not_started" if not_started else "unverified"
    reason = result.get("stats", {}).get("stopReason")
    # Public SDK 1.5.0 LLMPredictionStopReason contract; unknown is not proof.
    known_reasons = {"userStopped", "modelUnloaded", "failed", "eosFound", "stopStringFound",
                     "toolCalls", "maxPredictedTokensReached", "contextLengthReached"}
    if not isinstance(reason, str) or reason not in known_reasons:
        return "unverified"
    if requested:
        return "verified_cancel" if reason == "userStopped" else "completed_race"
    return "completed" if reason and reason != "userStopped" else "unexpected_stop"


class SdkPredictionProcess:
    def __init__(self, token: str, command: dict[str, Any], *, worker_script: Path = SDK_WORKER) -> None:
        node = shutil.which("node")
        if not node:
            raise RuntimeError("Node.js is unavailable")
        if not token:
            raise ValueError("LM_API_TOKEN is unavailable")
        worker_script = Path(worker_script).resolve(strict=True)
        if worker_script.suffix != ".mjs" or not worker_script.is_file():
            raise ValueError("SDK worker must be an existing JavaScript module")
        self.events: Queue[dict[str, Any]] = Queue(maxsize=32)
        self.closed = Event()
        self.write_lock = Lock()
        environment = dict(os.environ, LM_API_TOKEN=token)
        self.process = subprocess.Popen(
            [node, str(worker_script)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, cwd=worker_script.parent, env=environment,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        self.reader = Thread(target=self._read, daemon=True)
        self.reader.start()
        try:
            self.send(dict(command, command="start"))
        except BaseException:
            self.close()
            raise

    def _offer(self, event: dict[str, Any]) -> None:
        while not self.closed.is_set():
            try:
                self.events.put(event, timeout=0.1)
                return
            except Full:
                pass

    def _read(self) -> None:
        assert self.process.stdout is not None
        try:
            while not self.closed.is_set():
                line = self.process.stdout.readline(MAX_IPC_BYTES + 1)
                if not line:
                    break
                if len(line) > MAX_IPC_BYTES:
                    self._offer({"type": "error", "code": "ipc_byte_limit"})
                    break
                payload = json.loads(line.decode("utf-8", errors="strict"))
                if not isinstance(payload, dict):
                    raise ValueError("invalid IPC event")
                self._offer(payload)
        except (ValueError, UnicodeError, OSError):
            self._offer({"type": "error", "code": "ipc_decode_error"})
        finally:
            self._offer({"type": "worker_eof"})

    def send(self, command: dict[str, Any]) -> None:
        encoded = (json.dumps(command, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        if len(encoded) > 65536:
            raise ValueError("SDK command exceeded 64 KiB")
        with self.write_lock:
            assert self.process.stdin is not None
            self.process.stdin.write(encoded)
            self.process.stdin.flush()

    def cancel(self) -> None:
        self.send({"command": "cancel"})

    def next_event(self, timeout: float = 0.1) -> dict[str, Any] | None:
        try:
            return self.events.get(timeout=timeout)
        except Empty:
            return None

    def close(self) -> None:
        """Clean only the owned SDK client. This is NOT server stop verification."""
        self.closed.set()
        if self.process.stdin:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=2)
        self.reader.join(timeout=1)
        if self.process.stdout:
            self.process.stdout.close()

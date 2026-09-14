"""Effect-based bounded no-progress policy for observed tool outcomes.

Fragments, timestamps and mtime never count as useful progress. A changed
readback hash or a different validator exit/result allows recovery to proceed.
"""
from __future__ import annotations


class ToolProgressControl:
    def __init__(self, repeat_limit: int = 3):
        if type(repeat_limit) is not int or not 2 <= repeat_limit <= 8:
            raise ValueError("invalid no-progress limit")
        self.repeat_limit = repeat_limit
        self.previous = None
        self.equivalent_outcomes = 0
        self.stop_required = False

    def observe(self, event: dict) -> bool:
        kind = event.get("type")
        if kind == "tool_mutation_completed":
            signature = ("file", event.get("path"), event.get("after_sha256"))
        elif kind == "tool_completed":
            signature = ("file", event.get("path"), event.get("sha256"))
        elif kind == "tool_validation_completed":
            signature = ("validator", event.get("path"), event.get("sha256"),
                         event.get("exit_status"), event.get("result_sha256"))
        elif kind in ("tool_failed", "tool_mutation_failed", "invalid_tool_request", "tool_guard_denied"):
            signature = ("error", kind, event.get("path"), event.get("code"), event.get("name"))
        else:
            return self.stop_required
        if signature == self.previous:
            self.equivalent_outcomes += 1
        else:
            self.previous = signature
            self.equivalent_outcomes = 1
        self.stop_required = self.equivalent_outcomes >= self.repeat_limit
        return self.stop_required

    def evidence(self) -> dict:
        return {"repeat_limit": self.repeat_limit,
                "consecutive_equivalent_outcomes": self.equivalent_outcomes,
                "stop_required": self.stop_required}

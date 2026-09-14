"""Summarize observed tool-dispatch stages without assigning a failure cause."""
from __future__ import annotations

import hashlib


def summarize_tool_dispatch(events: list[dict]) -> list[dict]:
    chains: dict[tuple[str, int], dict] = {}
    for entry in events:
        event = entry.get("data", entry) if isinstance(entry, dict) else {}
        kind = event.get("type")
        call_id = event.get("call_id")
        if not isinstance(call_id, int):
            continue
        origin = ("model_specific_adapter" if kind == "adapter_tool_request_parsed"
                  else event.get("dispatch_origin", "native_sdk"))
        if origin not in {"native_sdk", "model_specific_adapter"}:
            continue
        chain = chains.setdefault((origin, call_id), {
            "dispatch_origin": origin,
            "call_id": call_id,
            "request_started": False,
            "name_received": None,
            "argument_fragment_count": 0,
            "raw_content_observed": False,
            "raw_content_sha256": None,
            "parsed_name": None,
            "finalized_name": None,
            "parse_failure": None,
            "dequeued": False,
            "guard_decision": None,
            "handler_name": None,
            "receipt_status": None,
        })
        if kind == "tool_request_started":
            chain["request_started"] = True
        elif kind == "tool_request_name_received":
            chain["name_received"] = event.get("name")
        elif kind == "tool_request_argument_fragment":
            chain["argument_fragment_count"] += 1
        elif kind in {"tool_request_parsed", "adapter_tool_request_parsed"}:
            chain["raw_content_observed"] = isinstance(event.get("raw_content"), str)
            chain["raw_content_sha256"] = event.get("raw_content_sha256")
            if chain["raw_content_sha256"] is None and isinstance(event.get("raw_content"), str):
                chain["raw_content_sha256"] = hashlib.sha256(
                    event["raw_content"].encode("utf-8")).hexdigest()
            chain["parsed_name"] = event.get("name")
        elif kind == "tool_request_finalized":
            chain["finalized_name"] = event.get("name")
        elif kind == "tool_request_failed":
            chain["parse_failure"] = event.get("error_name") or "Error"
            chain["raw_content_observed"] = isinstance(event.get("raw_content"), str)
            chain["raw_content_sha256"] = event.get("raw_content_sha256")
        elif kind == "tool_request_dequeued":
            chain["dequeued"] = True
        elif kind == "tool_request_guarded":
            chain["guard_decision"] = event.get("decision")
        elif kind == "tool_handler_entered":
            chain["handler_name"] = event.get("name")
        elif kind == "tool_handler_receipt":
            chain["receipt_status"] = event.get("status")
    return [chains[key] for key in sorted(chains)]

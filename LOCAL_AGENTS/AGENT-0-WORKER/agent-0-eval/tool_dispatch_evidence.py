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
            "handler_return_status": None,
            "handler_result_sha256": None,
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
        elif kind == "tool_handler_returned":
            chain["handler_return_status"] = event.get("status")
            chain["handler_result_sha256"] = event.get("result_sha256")
    return [chains[key] for key in sorted(chains)]


def verify_mutation_readback(events: list[dict], initial_sha256: str, final_sha256: str,
                             mutation_name: str = "replace_workspace_text") -> dict:
    """Verify initial read, completed mutation and final matching read in event order."""
    mutation_indices = []
    mutation_sha256 = None
    for index, entry in enumerate(events):
        event = entry.get("data", entry) if isinstance(entry, dict) else {}
        if (event.get("type") == "tool_handler_receipt"
                and event.get("name") == mutation_name
                and event.get("status") == "completed"):
            mutation_indices.append(index)
            mutation_sha256 = event.get("after_sha256")
    if not mutation_indices:
        return {"status": "unverified", "reason": "no completed mutation receipt"}
    first_mutation, final_mutation = mutation_indices[0], mutation_indices[-1]
    initial_read = next((index for index, entry in enumerate(events[:first_mutation])
        if (entry.get("data", entry) if isinstance(entry, dict) else {}).get("type") == "tool_handler_receipt"
        and (entry.get("data", entry) if isinstance(entry, dict) else {}).get("name") == "read_workspace_text"
        and (entry.get("data", entry) if isinstance(entry, dict) else {}).get("status") == "completed"
        and (entry.get("data", entry) if isinstance(entry, dict) else {}).get("sha256") == initial_sha256), None)
    if initial_read is None:
        return {"status": "unverified", "reason": "no matching initial read before mutation",
                "mutation_event_index": final_mutation, "final_sha256": final_sha256}
    if mutation_sha256 != final_sha256:
        return {"status": "unverified", "reason": "final mutation receipt does not match disk",
                "mutation_event_index": final_mutation, "mutation_sha256": mutation_sha256,
                "final_sha256": final_sha256}
    for index, entry in enumerate(events[final_mutation + 1:], final_mutation + 1):
        event = entry.get("data", entry) if isinstance(entry, dict) else {}
        if (event.get("type") == "tool_handler_receipt"
                and event.get("name") == "read_workspace_text"
                and event.get("status") == "completed"
                and event.get("sha256") == final_sha256):
            return {"status": "verified", "initial_read_event_index": initial_read,
                    "mutation_event_index": final_mutation, "readback_event_index": index,
                    "mutation_sha256": mutation_sha256,
                    "final_sha256": final_sha256}
    return {"status": "unverified", "reason": "no matching read receipt after final mutation",
            "mutation_event_index": final_mutation, "mutation_sha256": mutation_sha256,
            "final_sha256": final_sha256}

"""Cause-neutral comparisons of public SDK transport evidence."""
import hashlib
import json
import re


def canonical_sha256(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def _text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("text_chunks"), list):
        return "".join(value["text_chunks"])
    return ""


def summarize_attempt(evidence: dict) -> dict:
    result = evidence.get("result") or {}
    events = [entry.get("data", {}) for entry in evidence.get("events", [])]
    parsed = [event for event in events
              if event.get("type") == "tool_request_parsed" and event.get("index") == 0]
    fragments = "".join(_text(event.get("content", "")) for event in events
                        if event.get("type") == "fragment" and event.get("index") == 0)
    raw = [event.get("raw_content_sha256") for event in parsed]
    exact_raw = bool(parsed) and all(isinstance(event.get("raw_content_sha256"), str)
        and hashlib.sha256(_text(event.get("raw_content")).encode("utf-8")).hexdigest()
            == event["raw_content_sha256"] for event in parsed)
    observed_output = {"ordinary_fragment_sha256": hashlib.sha256(fragments.encode("utf-8")).hexdigest(),
                       "tool_raw_sha256": raw, "complete_raw_available": exact_raw}
    content = _text(result.get("content"))
    succeeded = (evidence.get("state") == "response_received"
                 and result.get("tool_state", {}).get("completed") == 1
                 and result.get("tool_state", {}).get("active") == 0
                 and isinstance(evidence.get("fixture", {}).get("sha256_before"), str)
                 and evidence["fixture"]["sha256_before"] == evidence["fixture"].get("sha256_after")
                 and "render-diagnostic" in content and re.search(r"(?<!\w)3(?!\w)", content) is not None)
    return {"conditions_sha256": canonical_sha256({
                "source_set": evidence.get("source_snapshot", {}).get("source_set_sha256"),
                "instruction": evidence.get("instruction_sha256"),
                "fixture": evidence.get("fixture", {}).get("sha256_before"),
                "contract": evidence.get("contract"), "runtime": evidence.get("runtime_identity"),
                "load": result.get("load_config"), "prediction": result.get("prediction_config")}),
            "instance_reference": result.get("model_info", {}).get("instanceReference"),
            "succeeded": succeeded, "observed_output": observed_output,
            "tool_event_sequence": [event.get("type") for event in events
                                    if str(event.get("type", "")).startswith("tool_")]}

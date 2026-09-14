"""Bounded static UI 0.4 graph checks; never execute or import ComfyUI.

Checks use the workflow's declared slots, not an invented backend inventory.
Unknown node semantics and subgraphs remain evidence gaps, not model verdicts.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from itertools import islice
from json_document_comparison import parse_json_document

MAX_NODES = 128
MAX_LINKS = 512
SCHEMA = Path(__file__).with_name("schemas") / "workflow_ui_0_4.json"
SCHEMA_SOURCE = SCHEMA.with_name("workflow_ui_0_4_source.json")


def validate_workflow_schema(document: dict) -> dict:
    """Use the pinned official Draft 7 schema with no remote-reference fetches."""
    from jsonschema import Draft7Validator
    with SCHEMA.open("rb") as handle:
        body = handle.read(32769)
    with SCHEMA_SOURCE.open("rb") as handle:
        metadata_body = handle.read(4097)
    if len(body) > 32768 or len(metadata_body) > 4096:
        raise ValueError("schema data exceeds byte budget")
    source = json.loads(metadata_body.decode("utf-8"))
    if hashlib.sha256(body).hexdigest() != source["schema_sha256"]:
        raise ValueError("schema source changed")
    schema = json.loads(body.decode("utf-8"))
    if schema.get("$schema") != "http://json-schema.org/draft-07/schema#":
        raise ValueError("unsupported schema dialect")
    def check_references(value):
        if isinstance(value, dict):
            if "$ref" in value and not value["$ref"].startswith("#/"):
                raise ValueError("remote schema references are forbidden")
            for item in value.values():
                check_references(item)
        elif isinstance(value, list):
            for item in value:
                check_references(item)
    check_references(schema)
    Draft7Validator.check_schema(schema)
    errors = list(islice(Draft7Validator(schema).iter_errors(document), 100))
    return {"status": "fail" if errors else "pass", "schema_sha256": source["schema_sha256"],
            "findings": [{"code": "schema_mismatch", "path": list(error.absolute_path),
                          "validator": error.validator} for error in errors],
            "evidence_gaps": [source["limits"]]}


def _identifier(value):
    return type(value) is int or (type(value) is str and bool(value))


def validate_workflow(document: dict, *, allowed_types: set[str] | None = None) -> dict:
    findings = []
    gaps = ["Static graph only; authoritative node semantics, frontend opening and generation are unverified."]

    def fail(code, **details):
        if len(findings) < 100:
            findings.append({"code": code} | details)

    if not isinstance(document, dict) or document.get("version") != 0.4:
        return {"status": "invalid", "findings": [{"code": "unsupported_ui_workflow_version"}],
                "evidence_gaps": gaps}
    nodes, links = document.get("nodes"), document.get("links")
    if (not isinstance(nodes, list) or not isinstance(links, list)
            or len(nodes) > MAX_NODES or len(links) > MAX_LINKS):
        return {"status": "invalid", "findings": [{"code": "graph_shape_or_budget"}], "evidence_gaps": gaps}
    by_id = {}
    for node in nodes:
        if not isinstance(node, dict) or not _identifier(node.get("id")) or not isinstance(node.get("type"), str):
            fail("node_identity_shape")
            continue
        identifier = node["id"]
        if identifier in by_id:
            fail("duplicate_node_id", node_id=identifier)
        by_id[identifier] = node
        if allowed_types is not None and node["type"] not in allowed_types:
            fail("node_outside_shown_palette", node_id=identifier, node_type=node["type"])
        if not isinstance(node.get("inputs", []), list) or not isinstance(node.get("outputs", []), list):
            fail("node_slots_shape", node_id=identifier)
    by_link = {}
    for link in links:
        if (not isinstance(link, list) or len(link) != 6 or type(link[0]) is not int
                or not _identifier(link[1]) or not _identifier(link[3])
                or type(link[2]) is not int or type(link[4]) is not int):
            fail("link_shape")
            continue
        identifier, origin, output_slot, target, input_slot, declared_type = link
        if identifier in by_link:
            fail("duplicate_link_id", link_id=identifier)
        by_link[identifier] = link
        if origin not in by_id or target not in by_id:
            fail("link_endpoint_missing", link_id=identifier)
            continue
        outputs = by_id[origin].get("outputs", [])
        inputs = by_id[target].get("inputs", [])
        if (not isinstance(outputs, list) or not isinstance(inputs, list)
                or not 0 <= output_slot < len(outputs) or not 0 <= input_slot < len(inputs)):
            fail("link_slot_out_of_range", link_id=identifier)
            continue
        source_slot, destination_slot = outputs[output_slot], inputs[input_slot]
        if not isinstance(source_slot, dict) or not isinstance(destination_slot, dict):
            fail("link_slot_shape", link_id=identifier)
            continue
        refs = source_slot.get("links")
        if not isinstance(refs, list) or identifier not in refs:
            fail("output_backreference_missing", link_id=identifier)
        if destination_slot.get("link") != identifier:
            fail("input_backreference_mismatch", link_id=identifier)
        types = (source_slot.get("type"), destination_slot.get("type"), declared_type)
        if all(isinstance(value, str) and value != "*" for value in types) and len(set(types)) != 1:
            fail("declared_link_type_mismatch", link_id=identifier)
    for identifier, node in by_id.items():
        for direction, field in (("inputs", "link"), ("outputs", "links")):
            slots = node.get(direction, [])
            if not isinstance(slots, list):
                continue
            for index, slot in enumerate(slots):
                if not isinstance(slot, dict):
                    fail("slot_shape", node_id=identifier)
                    continue
                refs = slot.get(field)
                if refs is None:
                    continue
                if direction == "inputs":
                    refs = [refs]
                if not isinstance(refs, list) or not all(type(ref) is int for ref in refs):
                    fail("slot_reference_shape", node_id=identifier, slot=index)
                    continue
                if len(refs) != len(set(refs)):
                    fail("duplicate_slot_reference", node_id=identifier, slot=index)
                for ref in refs:
                    linked = by_link.get(ref)
                    if linked is None:
                        fail("dangling_slot_reference", node_id=identifier, link_id=ref)
                    elif (direction == "inputs" and (linked[3], linked[4]) != (identifier, index)
                          or direction == "outputs" and (linked[1], linked[2]) != (identifier, index)):
                        fail("slot_reference_wrong_endpoint", node_id=identifier, link_id=ref)
    if document.get("definitions"):
        gaps.append("Embedded subgraph contracts are not supported by this checked subset; separate validation is required.")
    status = "fail" if findings else "review_required" if document.get("definitions") else "pass"
    return {"status": status, "findings": findings, "evidence_gaps": gaps,
            "checked": ["node_and_link_identity", "endpoints_and_slot_bounds", "input_output_backreferences",
                        "declared_link_types", "shown_palette" if allowed_types is not None else "palette_not_checked"]}


def validate_workflow_text(text: str, *, allowed_types: set[str] | None = None) -> dict:
    if len(text.encode("utf-8")) > 262144 or text.startswith("\ufeff"):
        return {"status": "invalid", "findings": [{"code": "text_encoding_or_budget"}]}
    try:
        document = parse_json_document(text)
    except (ValueError, TypeError):
        return {"status": "fail", "findings": [{"code": "invalid_json"}]}
    return validate_workflow(document, allowed_types=allowed_types)

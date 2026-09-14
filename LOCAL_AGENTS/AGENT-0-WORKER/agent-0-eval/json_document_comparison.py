"""Strict JSON parsing and type-preserving semantic comparison for graders."""
import json


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _invalid_constant(_):
    raise ValueError("invalid JSON constant")


def parse_json_document(text: str):
    try:
        return json.loads(text, object_pairs_hook=_object, parse_constant=_invalid_constant)
    except RecursionError as error:
        raise ValueError("JSON nesting exceeds parser budget") from error


def same_json_document(actual, expected) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(same_json_document(actual[key], expected[key]) for key in expected)
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(same_json_document(a, b) for a, b in zip(actual, expected))
    return actual == expected

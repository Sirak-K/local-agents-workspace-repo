"""Read-only mechanical evidence checks, never model fault attribution."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from evaluation_paths import existing_run_directory, eval_directory
from json_document_comparison import parse_json_document
from evaluation_source_snapshot import verify_source_snapshot, changed_current_sources

ROLE = Path(__file__).resolve().parents[1]
ROOT = ROLE.parents[1]
SOURCE_ROOTS = (ROLE / "agent-0-eval", ROLE / "agent-0-eval/schemas", ROLE / "agent-0-tools",
                ROLE / "agent-0-context",
                ROOT / "LM-Studio_connections/LM-Studio_for_codex",
                ROLE / "AG-0-MODEL-Granite_4.1-3B")


def _read(path: Path, limit: int) -> bytes:
    if path.is_symlink() or path.resolve() != path.absolute():
        raise ValueError("unsafe evidence source path")
    with path.open("rb") as handle:
        body = handle.read(limit + 1)
    if len(body) > limit or body.startswith(b"\xef\xbb\xbf"):
        raise ValueError("evidence byte/encoding budget")
    return body


def _text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("text_chunks"), list):
        return "".join(value["text_chunks"])
    raise ValueError("source text unavailable")


def _workspace_target(workspace: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError("unsafe fixture path")
    target = workspace.joinpath(*relative.parts)
    if not target.resolve().is_relative_to(workspace.resolve()):
        raise ValueError("fixture outside workspace")
    return target


def _review_fixture(directory: Path, fixture: dict, checks: dict) -> None:
    workspace = directory / "workspace"
    if fixture.get("manifest_sha256"):
        manifest = parse_json_document(_read(directory / "fixture_manifest.json", 16384).decode("utf-8"))
        checks["fixture_contract"] = (manifest.get("eval_id"), manifest.get("run_id"),
                                      manifest.get("manifest_sha256")) == (
            directory.parent.name, directory.name, fixture.get("manifest_sha256"))
        target = workspace / "workflow.json"
        checks["after_hash_stable"] = hashlib.sha256(_read(target, 65536)).hexdigest() == fixture.get("sha256_after")
        checks["workspace_scope"] = set(path.name for path in workspace.iterdir()) == {"workflow.json"}
        return
    if isinstance(fixture.get("relative_path"), str):
        target = _workspace_target(workspace, fixture["relative_path"])
        checks["fixture_contract"] = target.is_file()
        checks["after_hash_stable"] = hashlib.sha256(_read(target, 65536)).hexdigest() == fixture.get("sha256_after")
        checks["workspace_scope"] = {
            path.relative_to(workspace).as_posix() for path in workspace.rglob("*") if path.is_file()
        } == {fixture["relative_path"]}
        return
    after = fixture.get("after")
    if not isinstance(after, dict) or not after:
        raise ValueError("unsupported fixture evidence")
    expected_paths = set()
    stable = True
    for relative_path, expected in after.items():
        if not isinstance(expected, dict) or not isinstance(expected.get("sha256"), str):
            raise ValueError("invalid fixture after-state")
        target = _workspace_target(workspace, relative_path)
        expected_paths.add(Path(relative_path).as_posix())
        body = _read(target, 65536)
        stable = stable and hashlib.sha256(body).hexdigest() == expected["sha256"]
        if isinstance(expected.get("content"), str):
            stable = stable and body == expected["content"].encode("utf-8")
    actual_paths = {path.relative_to(workspace).as_posix() for path in workspace.rglob("*") if path.is_file()}
    checks["fixture_contract"] = True
    checks["after_hash_stable"] = stable
    checks["workspace_scope"] = actual_paths == expected_paths


def review_run(eval_id: str, run_id: str) -> dict:
    directory = existing_run_directory(eval_id, run_id)
    body = _read(directory / "evidence.json", 1048576)
    evidence = parse_json_document(body.decode("utf-8"))
    gaps = []
    checks = {}
    checks["identity"] = (evidence.get("eval_id"), evidence.get("run_id")) == (eval_id, run_id)
    checks["instruction_hash"] = hashlib.sha256(_text(evidence.get("instruction")).encode("utf-8")).hexdigest() == evidence.get("instruction_sha256")
    if not checks["instruction_hash"]:
        gaps.append("Saved instruction is redacted or changed; exact input is not established.")
    changed_sources = []
    for name, expected_hash in evidence.get("source_fingerprints", {}).items():
        if Path(name).name != name:
            raise ValueError("unsupported source fingerprint identity")
        matches = [root / name for root in SOURCE_ROOTS if (root / name).is_file()]
        if len(matches) != 1 or hashlib.sha256(_read(matches[0], 1048576)).hexdigest() != expected_hash:
            changed_sources.append(name)
    checks["current_sources_unchanged"] = not changed_sources
    snapshot = evidence.get("source_snapshot")
    snapshot_status = "not_captured_historical_evidence"
    if snapshot is not None:
        captured = verify_source_snapshot(snapshot)
        checks["source_snapshot_integrity"] = all(captured.get(name) == digest
            for name, digest in evidence.get("source_fingerprints", {}).items())
        checks["snapshot_sources_unchanged"] = not changed_current_sources(snapshot)
        snapshot_status = "verified" if checks["source_snapshot_integrity"] else "invalid"
    previous = evidence.get("previous_run")
    checks["retry_link"] = True
    if previous:
        original_body = _read(existing_run_directory(eval_id, previous) / "evidence.json", 1048576)
        original = parse_json_document(original_body.decode("utf-8"))
        checks["retry_link"] = (original.get("eval_id") == eval_id and bool(evidence.get("change_reason"))
                                and hashlib.sha256(original_body).hexdigest() == evidence.get("previous_run_sha256"))
    assessment_path = directory / "assessment.json"
    checks["manual_assessment_hash"] = True
    if assessment_path.exists():
        assessment = parse_json_document(_read(assessment_path, 32768).decode("utf-8"))
        checks["manual_assessment_hash"] = (assessment.get("evidence_sha256") == hashlib.sha256(body).hexdigest()
                                            and assessment.get("catalog_sha256") == evidence.get("probe", {}).get("catalog_sha256"))
    fixture = evidence.get("fixture")
    if fixture:
        _review_fixture(directory, fixture, checks)
    verification = evidence.get("verification", {})
    assisted = bool(evidence.get("granite_text_tool_bridge")
                    or evidence.get("contract", {}).get("granite_text_tool_bridge"))
    return {"eval_id": eval_id, "run_id": run_id,
            "status": "mechanical_checks_passed" if all(checks.values()) else "requires_investigation",
            "checks": checks, "changed_sources": changed_sources,
            "source_snapshot_status": snapshot_status,
            "evidence_sha256": hashlib.sha256(body).hexdigest(),
            "attempt_condition": "model_specific_bridged_diagnostic" if assisted else "declared_native_transport",
            "task_assessment": evidence.get("assessment"), "stop_verification": verification,
            "evidence_gaps": gaps + evidence.get("evidence_gaps", []),
            "model_fault_attribution": "not_performed"}


def review_summary_presence(eval_id: str) -> dict:
    directory = eval_directory(eval_id)
    reports = list(directory.glob("[[]EVAL] - * - [[]REPORT SUMMARY].md"))
    if len(reports) != 1:
        return {"status": "incomplete", "report_count": len(reports), "semantic_review_required": True}
    body = _read(reports[0], 262144).decode("utf-8")
    return {"status": "present" if "ERQER" in body else "incomplete",
            "report_count": 1, "erqer_section_present": "ERQER" in body,
            "semantic_review_required": True,
            "note": "Reviewer must verify all four ERQER domains, findings, evidence links and cause separation; presence alone is not report completeness."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    try:
        report = review_run(args.eval_id, args.run_id)
        report["report_summary"] = review_summary_presence(args.eval_id)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["status"] == "mechanical_checks_passed" else 2
    except (OSError, ValueError, TypeError, KeyError):
        print("Evidence review failed; no model or task verdict is implied.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

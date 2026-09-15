"""Capture and verify exact, bounded evaluation runtime source snapshots."""
from __future__ import annotations

import hashlib
import json
import ast
import re
import subprocess
from pathlib import Path
from typing import Iterable

from evaluation_paths import project_relative_path, relative_to_project
from evaluation_paths import PROJECT_ROOT, ROLE_ROOT

SCHEMA_VERSION = 1
TEXT_CHUNK_CHARACTERS = 160
MAX_SOURCE_FILE_BYTES = 131_072
MAX_SOURCE_SET_BYTES = 524_288


def installed_runtime_identity() -> dict:
    """Pin executed JS dependency artifacts separately from project source content."""
    connection = PROJECT_ROOT / "LM-Studio_connections/LM-Studio_for_codex"
    artifacts = {}
    for relative in ("node_modules/@lmstudio/sdk/dist/index.mjs", "node_modules/zod/index.js"):
        path = connection / relative
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 4_194_304:
            raise ValueError("installed dependency artifact unavailable or oversized")
        artifacts[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    sdk = json.loads((connection / "node_modules/@lmstudio/sdk/package.json").read_text(encoding="utf-8"))
    node = subprocess.run(["node", "--version"], capture_output=True, check=True, timeout=3)
    if len(node.stdout) > 128:
        raise ValueError("Node identity exceeds budget")
    return {"sdk_version": sdk["version"], "node_version": node.stdout.decode("utf-8").strip(),
            "dependency_artifact_sha256": artifacts,
            "backend_identity": "not_exposed_by_dependency_artifact_hashes"}


def runtime_source_paths(seeds: Iterable[Path]) -> list[Path]:
    """Resolve project-local Python/JS imports, excluding third-party installed code."""
    owners = (ROLE_ROOT / "agent-0-eval", ROLE_ROOT / "agent-0-tools",
              ROLE_ROOT / "agent-0-context",
              ROLE_ROOT / "AG-0-MODEL-Granite_4.1-3B",
              PROJECT_ROOT / "LM-Studio_connections/LM-Studio_for_codex",
              PROJECT_ROOT / "LM-Studio_connections/LM-Studio_observability",
              PROJECT_ROOT / "tools")
    pending = [Path(path).resolve(strict=True) for path in seeds]
    pending.extend((Path(__file__).resolve(), Path(__file__).with_name("evaluation_paths.py")))
    seen = set()
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        if not any(path.is_relative_to(owner.resolve()) for owner in owners):
            raise ValueError("source belongs to an unsupported runtime owner")
        if "node_modules" in path.parts:
            continue
        seen.add(path)
        if len(seen) > 64:
            raise ValueError("runtime source closure exceeds file budget")
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            tree = ast.parse(text)
            modules = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    modules.append(node.module.split(".")[0])
                elif isinstance(node, ast.Import):
                    modules.extend(alias.name.split(".")[0] for alias in node.names)
            for module in modules:
                matches = [owner / (module + ".py") for owner in owners
                           if (owner / (module + ".py")).is_file()]
                if len(matches) > 1:
                    raise ValueError("ambiguous project-local import")
                pending.extend(matches)
        elif path.suffix == ".mjs":
            for specifier in re.findall(r'from\s+[\"\']([^\"\']+)[\"\']', text):
                if specifier.startswith(".") and "node_modules" not in specifier:
                    pending.append((path.parent / specifier).resolve(strict=True))
    return sorted(seen)


def _source_set_sha256(descriptors: list[dict]) -> str:
    canonical = json.dumps(descriptors, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def capture_source_snapshot(source_paths: Iterable[Path]) -> dict:
    """Return exact UTF-8 source content plus a deterministic source-set identity."""
    files = []
    seen_paths = set()
    seen_names = set()
    total_bytes = 0
    for source in sorted((Path(path) for path in source_paths),
                         key=lambda path: relative_to_project(path)):
        relative = relative_to_project(source)
        if relative in seen_paths or source.name in seen_names:
            raise ValueError("evaluation source snapshot paths and basenames must be unique")
        if source.is_symlink() or not source.is_file() or source.resolve() != source.absolute():
            raise ValueError("evaluation source snapshot requires a real contained file")
        if source.stat().st_size > MAX_SOURCE_FILE_BYTES:
            raise ValueError("evaluation source file exceeds byte budget")
        with source.open("rb") as handle:
            body = handle.read(MAX_SOURCE_FILE_BYTES + 1)
        if (len(body) > MAX_SOURCE_FILE_BYTES or body.startswith(b"\xef\xbb\xbf")
                or total_bytes + len(body) > MAX_SOURCE_SET_BYTES):
            raise ValueError("evaluation source snapshot exceeds its encoding or byte budget")
        text = body.decode("utf-8", "strict")
        digest = hashlib.sha256(body).hexdigest()
        files.append({
            "path": relative,
            "size_bytes": len(body),
            "sha256": digest,
            "encoding": "utf-8",
            "text_chunks": [text[index:index + TEXT_CHUNK_CHARACTERS]
                            for index in range(0, len(text), TEXT_CHUNK_CHARACTERS)],
        })
        seen_paths.add(relative)
        seen_names.add(source.name)
        total_bytes += len(body)
    if not files:
        raise ValueError("evaluation source snapshot cannot be empty")
    descriptors = [{key: item[key] for key in ("path", "size_bytes", "sha256")}
                   for item in files]
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": "project_owned_sources_only_dependencies_require_separate_runtime_identity",
        "source_set_sha256": _source_set_sha256(descriptors),
        "total_bytes": total_bytes,
        "files": files,
    }


def verify_source_snapshot(snapshot: dict) -> dict[str, str]:
    """Verify reconstructability and return the legacy basename-to-hash mapping."""
    if snapshot.get("schema_version") != SCHEMA_VERSION or not isinstance(snapshot.get("files"), list):
        raise ValueError("unsupported evaluation source snapshot")
    descriptors = []
    fingerprints = {}
    total_bytes = 0
    seen_paths = set()
    for item in snapshot["files"]:
        if (not isinstance(item, dict) or item.get("encoding") != "utf-8"
                or not isinstance(item.get("text_chunks"), list)
                or any(not isinstance(chunk, str) for chunk in item["text_chunks"])):
            raise ValueError("invalid source snapshot entry")
        path = project_relative_path(item.get("path", ""))
        relative = relative_to_project(path)
        if relative != item.get("path") or relative in seen_paths or path.name in fingerprints:
            raise ValueError("ambiguous source snapshot identity")
        body = "".join(item["text_chunks"]).encode("utf-8")
        digest = hashlib.sha256(body).hexdigest()
        if (len(body) != item.get("size_bytes") or digest != item.get("sha256")
                or len(body) > MAX_SOURCE_FILE_BYTES):
            raise ValueError("source snapshot content does not match its identity")
        total_bytes += len(body)
        descriptors.append({key: item[key] for key in ("path", "size_bytes", "sha256")})
        fingerprints[path.name] = digest
        seen_paths.add(relative)
    if (not descriptors or total_bytes != snapshot.get("total_bytes")
            or total_bytes > MAX_SOURCE_SET_BYTES
            or _source_set_sha256(descriptors) != snapshot.get("source_set_sha256")):
        raise ValueError("source snapshot set identity does not match")
    return fingerprints


def changed_current_sources(snapshot: dict) -> list[str]:
    """List snapshotted paths whose current project source is missing or different."""
    verify_source_snapshot(snapshot)
    changed = []
    for item in snapshot["files"]:
        path = project_relative_path(item["path"])
        if (not path.is_file() or path.is_symlink()
                or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]):
            changed.append(item["path"])
    return changed

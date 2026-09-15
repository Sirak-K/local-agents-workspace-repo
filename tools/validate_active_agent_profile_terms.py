#!/usr/bin/env python3
"""Validate active project surfaces for deprecated uppercase agent-profile terms."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

SCAN_DIRECTORIES = (
    "LOCAL_AGENTS",
    "SillyTavern_UI",
    "scripts",
    "LM-Studio_connections",
    "docs/docs_plan",
)
SCAN_ROOT_FILES = ("[ CURRENT ARCHITECTURAL PROJECT STATE ].md",)

TEXT_SUFFIXES = frozenset(
    {
        ".bat",
        ".cfg",
        ".cmd",
        ".conf",
        ".css",
        ".csv",
        ".html",
        ".htm",
        ".ini",
        ".j2",
        ".jinja",
        ".js",
        ".json",
        ".jsonl",
        ".jsx",
        ".md",
        ".mjs",
        ".ps1",
        ".psd1",
        ".psm1",
        ".py",
        ".scss",
        ".sh",
        ".template",
        ".tmpl",
        ".toml",
        ".ts",
        ".tsv",
        ".tsx",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)
TEXT_FILENAMES = frozenset({"Dockerfile", "Makefile"})

EXCLUDED_PREFIXES = (
    "docs/docs_plan/- old",
    "docs/docs_handoffs_to_ChatGPT",
    "SillyTavern_UI/_local_runtime",
    "docs/docs_personal",
    "docs/docs_frameworks",
)
EXCLUDED_COMPONENTS = frozenset({".git", ".venv", "node_modules"})
EXCLUDED_FILES = frozenset(
    {
        "docs/docs_plan/[PLAN] - [Realize The Storyteller-Chat-Agent] (RTSCA) - [Claude's ideas].md",
    }
)

LEGACY_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:AGENT-\d+(?:-[A-Z0-9]+)*|TAR(?:-\d+(?:-[A-Z0-9]+)*)?)(?![A-Za-z0-9])"
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    column: int
    token: str


@dataclass(frozen=True, order=True)
class DecodeError:
    path: str
    line: int
    byte_offset: int


@dataclass(frozen=True)
class ScanResult:
    files_scanned: int
    findings: tuple[Finding, ...]
    decode_errors: tuple[DecodeError, ...]

    @property
    def ok(self) -> bool:
        return not self.findings and not self.decode_errors


def _relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_excluded(relative_path: str | Path) -> bool:
    """Return True when a repo-relative path is outside the active validation surface."""

    rel = Path(str(relative_path).replace("\\", "/"))
    posix = rel.as_posix().lstrip("./")

    if any(part in EXCLUDED_COMPONENTS for part in rel.parts):
        return True
    if posix in EXCLUDED_FILES:
        return True
    return any(posix == prefix or posix.startswith(prefix + "/") for prefix in EXCLUDED_PREFIXES)


def is_relevant_text_file(path: Path) -> bool:
    return path.name in TEXT_FILENAMES or path.suffix.lower() in TEXT_SUFFIXES


def iter_active_text_files(root: Path) -> Iterable[Path]:
    """Yield active, relevant text files in deterministic repo-relative order."""

    candidates: set[Path] = set()

    for root_file in SCAN_ROOT_FILES:
        path = root / root_file
        if path.is_file() and not is_excluded(root_file) and is_relevant_text_file(path):
            candidates.add(path)

    for relative_dir in SCAN_DIRECTORIES:
        directory = root / relative_dir
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            relative = _relative_posix(path, root)
            if is_excluded(relative) or not is_relevant_text_file(path):
                continue
            candidates.add(path)

    yield from sorted(candidates, key=lambda path: _relative_posix(path, root))


def scan_repository(root: Path) -> ScanResult:
    """Scan an already-present repository tree without mutating it."""

    root = root.resolve()
    findings: list[Finding] = []
    decode_errors: list[DecodeError] = []
    files_scanned = 0

    for path in iter_active_text_files(root):
        files_scanned += 1
        relative = _relative_posix(path, root)
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            line = data[: exc.start].count(b"\n") + 1
            decode_errors.append(DecodeError(relative, line, exc.start))
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in LEGACY_TOKEN_RE.finditer(line):
                findings.append(
                    Finding(
                        path=relative,
                        line=line_number,
                        column=match.start() + 1,
                        token=match.group(0),
                    )
                )

    return ScanResult(
        files_scanned=files_scanned,
        findings=tuple(sorted(findings)),
        decode_errors=tuple(sorted(decode_errors)),
    )


def format_failures(result: ScanResult) -> list[str]:
    lines: list[tuple[str, int, int, str]] = []
    for finding in result.findings:
        lines.append(
            (
                finding.path,
                finding.line,
                finding.column,
                f"LEGACY {finding.path}:{finding.line} {finding.token}",
            )
        )
    for error in result.decode_errors:
        lines.append(
            (
                error.path,
                error.line,
                -1,
                f"UTF8 {error.path}:{error.line} byte={error.byte_offset}",
            )
        )
    return [entry[3] for entry in sorted(lines)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reject deprecated uppercase TAR/TAR-* and AGENT-* profile terms in active repo surfaces."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to scan (default: current working directory).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = scan_repository(args.root)
    if not result.ok:
        for line in format_failures(result):
            print(line)
        return 1

    print(f"PASS active-agent-profile-terms files={result.files_scanned}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

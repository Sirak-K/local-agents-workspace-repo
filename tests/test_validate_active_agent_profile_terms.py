from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "validate_active_agent_profile_terms.py"
SPEC = importlib.util.spec_from_file_location("validate_active_agent_profile_terms", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ActiveAgentProfileTerminologyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_text(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_detects_locked_uppercase_legacy_forms(self) -> None:
        self.write_text(
            "SillyTavern_UI/terms.md",
            "TAR\nTAR-1\nAGENT-2\nAGENT-2-STORYTELLER\n",
        )
        result = validator.scan_repository(self.root)
        self.assertEqual(
            [(item.line, item.token) for item in result.findings],
            [(1, "TAR"), (2, "TAR-1"), (3, "AGENT-2"), (4, "AGENT-2-STORYTELLER")],
        )
        self.assertFalse(result.ok)

    def test_lowercase_internal_names_and_language_words_pass(self) -> None:
        self.write_text(
            "LOCAL_AGENTS/names.txt",
            "agent-0-eval\nagent-2_system_prompt.txt\nVi tar nästa steg.\nenglish agent\n",
        )
        result = validator.scan_repository(self.root)
        self.assertTrue(result.ok)
        self.assertEqual(result.findings, ())

    def test_every_locked_exclusion_is_ignored(self) -> None:
        excluded = (
            "docs/docs_plan/- old/legacy.md",
            "docs/docs_handoffs_to_ChatGPT/legacy.md",
            "SillyTavern_UI/_local_runtime/legacy.md",
            "SillyTavern_UI/.git/legacy.md",
            "SillyTavern_UI/.venv/legacy.md",
            "scripts/node_modules/pkg/legacy.md",
            "docs/docs_personal/legacy.md",
            "docs/docs_frameworks/legacy.md",
            "docs/docs_plan/[PLAN] - [Realize The Storyteller-Chat-Agent] (RTSCA) - [Claude's ideas].md",
        )
        for relative in excluded:
            self.assertTrue(validator.is_excluded(relative), relative)
            self.write_text(relative, "AGENT-9-STORYTELLER\n")
        self.write_text("scripts/active.md", "AGPR-2-STORYTELLER\n")
        result = validator.scan_repository(self.root)
        self.assertTrue(result.ok)
        self.assertEqual(result.files_scanned, 1)

    def test_findings_are_sorted_with_correct_lines_and_tokens(self) -> None:
        self.write_text("scripts/z.md", "clean\nAGENT-4-VOICE-MASTER\n")
        self.write_text("LOCAL_AGENTS/a.md", "TAR-2\nclean\nAGENT-2-STORYTELLER\n")
        result = validator.scan_repository(self.root)
        self.assertEqual(
            validator.format_failures(result),
            [
                "LEGACY LOCAL_AGENTS/a.md:1 TAR-2",
                "LEGACY LOCAL_AGENTS/a.md:3 AGENT-2-STORYTELLER",
                "LEGACY scripts/z.md:2 AGENT-4-VOICE-MASTER",
            ],
        )

    def test_clean_cli_returns_zero_and_single_compact_pass_line(self) -> None:
        self.write_text("scripts/clean.md", "AGPR is the active profile abbreviation.\n")
        self.write_text("[ CURRENT ARCHITECTURAL PROJECT STATE ].md", "Agent Profile\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = validator.main(["--root", str(self.root)])
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue(), "PASS active-agent-profile-terms files=2\n")

    def test_invalid_utf8_is_deterministic_error_and_exit_one(self) -> None:
        path = self.root / "scripts" / "bad.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"clean\n\xffbad\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = validator.main(["--root", str(self.root)])
        self.assertEqual(exit_code, 1)
        self.assertEqual(output.getvalue(), "UTF8 scripts/bad.md:2 byte=6\n")

    def test_binary_and_irrelevant_formats_are_ignored(self) -> None:
        path = self.root / "LOCAL_AGENTS" / "image.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\x89PNG\r\n\x1a\nAGENT-2\xff")
        result = validator.scan_repository(self.root)
        self.assertTrue(result.ok)
        self.assertEqual(result.files_scanned, 0)

    def test_root_architectural_state_is_scanned(self) -> None:
        self.write_text("[ CURRENT ARCHITECTURAL PROJECT STATE ].md", "AGENT-0-WORKER\n")
        result = validator.scan_repository(self.root)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].path, "[ CURRENT ARCHITECTURAL PROJECT STATE ].md")
        self.assertEqual(result.findings[0].token, "AGENT-0-WORKER")


if __name__ == "__main__":
    unittest.main()

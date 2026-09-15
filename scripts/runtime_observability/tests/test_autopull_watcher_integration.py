from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
WATCHER = ROOT / "scripts" / "github_autopull_chatgpts_repo_work" / "main_autopull_watcher.ps1"
INSTALLER = ROOT / "scripts" / "github_autopull_chatgpts_repo_work" / "install_main_autopull.ps1"


class AutoPullWatcherIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.watcher = WATCHER.read_text(encoding="utf-8")
        cls.installer = INSTALLER.read_text(encoding="utf-8")

    def test_codex_ff_only_safety_chain_is_preserved(self):
        for required in (
            '"fetch",',
            '"status", "--porcelain=v1", "--untracked-files=no"',
            '"merge-base", "--is-ancestor", $head.Output, $remote.Output',
            "Get-UntrackedCollisions",
            "SKIP_UNTRACKED_COLLISION",
            "SKIP_RACE_GUARD",
            '"merge", "--ff-only", "--quiet", "refs/remotes/origin/main"',
            "LOCAL_AHEAD",
            "DIVERGED",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.watcher)
        for forbidden_git_command in ("reset", "clean", "stash"):
            self.assertIsNone(
                re.search(rf'Invoke-Git\s+@\(\s*"{forbidden_git_command}"', self.watcher, flags=re.IGNORECASE)
            )

    def test_state_changes_publish_owner_capture_only_when_state_or_detail_changes(self):
        self.assertIn("if ($script:lastState -ne $State -or $script:lastDetail -ne $Detail)", self.watcher)
        self.assertIn("Publish-AutoPullState", self.watcher)
        self.assertIn("github_autopull_capture.py", self.watcher)
        self.assertNotIn('main-autopull.log"', self.watcher)
        self.assertNotIn("AppendAllText", self.watcher)

    def test_observability_is_best_effort_not_a_new_autopull_gate(self):
        self.assertIn("Observability is deliberately best-effort", self.watcher)
        self.assertIn("catch {", self.watcher)
        self.assertIn("Fail open for observability only", self.watcher)
        self.assertIn("if ($null -eq $pythonExe", self.watcher)
        self.assertIn('.venv\\Scripts\\python.exe', self.watcher)

    def test_installer_stops_redirecting_bootstrap_output_to_git_logs(self):
        self.assertNotIn("-RedirectStandardOutput", self.installer)
        self.assertNotIn("-RedirectStandardError", self.installer)
        self.assertIn('"main-autopull.log"', self.installer)
        self.assertIn("Remove-Item $legacyEvidencePaths", self.installer)
        self.assertIn('logs\\github_autopull', self.installer)


if __name__ == "__main__":
    unittest.main()

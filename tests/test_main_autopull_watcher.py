from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts/github_autopull_chatgpts_repo_work"
INSTALLER = SCRIPTS / "install_main_autopull.ps1"
WATCHER = SCRIPTS / "main_autopull_watcher.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


def git(cwd, *args):
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


class AutoPullSourceContractTest(unittest.TestCase):
    def test_installer_targets_colocated_watcher_and_current_uninstall_path(self):
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertIn('Join-Path $PSScriptRoot "main_autopull_watcher.ps1"', text)
        self.assertNotIn('"tools\\main_autopull_watcher.ps1"', text)
        self.assertIn("scripts\\github_autopull_chatgpts_repo_work\\install_main_autopull.ps1", text)

    def test_installer_uses_project_specific_startup_launcher(self):
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertIn('"SSIRA-LocalAgents-MainAutoPull.cmd"', text)
        # The ComfyUI startup launcher belongs to another repository and must not
        # be targeted by Local Agents install or uninstall behavior.
        executable_lines = [
            line for line in text.splitlines()
            if not line.lstrip().startswith("#")
        ]
        executable_text = "\n".join(executable_lines)
        self.assertNotIn('"SSIRA-ComfyUI-MainAutoPull.cmd"', executable_text)

    def test_watcher_remains_ff_only_and_has_explicit_collision_guard(self):
        text = WATCHER.read_text(encoding="utf-8")
        self.assertIn('"merge", "--ff-only"', text)
        self.assertIn("SKIP_UNTRACKED_COLLISION", text)
        for forbidden in ('"reset"', '"rebase"', '"clean"', '"stash"'):
            self.assertNotIn(forbidden, text)


@unittest.skipUnless(POWERSHELL, "PowerShell runtime required for watcher behavior tests")
class AutoPullBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.remote = base / "remote.git"
        self.seed = base / "seed"
        self.local = base / "local"
        self.writer = base / "writer"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        subprocess.run(["git", "init", str(self.seed)], check=True, capture_output=True)
        git(self.seed, "config", "user.name", "fixture")
        git(self.seed, "config", "user.email", "fixture@example.invalid")
        git(self.seed, "checkout", "-b", "main")
        (self.seed / "tracked.txt").write_text("base\n", encoding="utf-8")
        git(self.seed, "add", "tracked.txt")
        git(self.seed, "commit", "-m", "base")
        git(self.seed, "remote", "add", "origin", str(self.remote))
        git(self.seed, "push", "-u", "origin", "main")
        git(self.remote, "symbolic-ref", "HEAD", "refs/heads/main")
        subprocess.run(["git", "clone", "--branch", "main", str(self.remote), str(self.local)], check=True, capture_output=True)
        subprocess.run(["git", "clone", "--branch", "main", str(self.remote), str(self.writer)], check=True, capture_output=True)
        for repo in (self.local, self.writer):
            git(repo, "config", "user.name", "fixture")
            git(repo, "config", "user.email", "fixture@example.invalid")
        self.processes = []

    def tearDown(self):
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
        self.temp.cleanup()

    @property
    def log_path(self):
        return self.local / ".git/main-autopull.log"

    def start_watcher(self):
        process = subprocess.Popen([POWERSHELL, "-NoProfile", "-File", str(WATCHER),
                                    "-RepoRoot", str(self.local), "-IntervalSeconds", "1"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.processes.append(process)
        return process

    def wait_for(self, predicate, seconds=8):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(0.05)
        self.fail("condition was not observed within bounded watcher test time")

    def push_writer(self, name="remote.txt", text="remote\n"):
        (self.writer / name).write_text(text, encoding="utf-8")
        git(self.writer, "add", name)
        git(self.writer, "commit", "-m", "remote change")
        git(self.writer, "push", "origin", "main")

    def log_contains(self, text):
        return self.log_path.exists() and text in self.log_path.read_text(encoding="utf-8-sig")

    def test_safe_fast_forward(self):
        self.start_watcher()
        self.push_writer()
        expected = git(self.writer, "rev-parse", "HEAD")
        self.wait_for(lambda: git(self.local, "rev-parse", "HEAD") == expected)
        self.assertTrue((self.local / "remote.txt").is_file())

    def test_dirty_tracked_state_skips_worktree_update(self):
        before = git(self.local, "rev-parse", "HEAD")
        (self.local / "tracked.txt").write_text("dirty\n", encoding="utf-8")
        self.push_writer()
        self.start_watcher()
        self.wait_for(lambda: self.log_contains("STATE=SKIP_DIRTY_TRACKED"))
        self.assertEqual(before, git(self.local, "rev-parse", "HEAD"))
        self.assertEqual("dirty\n", (self.local / "tracked.txt").read_text(encoding="utf-8"))

    def test_divergence_is_reported_without_rewrite(self):
        (self.local / "local.txt").write_text("local\n", encoding="utf-8")
        git(self.local, "add", "local.txt")
        git(self.local, "commit", "-m", "local")
        local_head = git(self.local, "rev-parse", "HEAD")
        self.push_writer()
        self.start_watcher()
        self.wait_for(lambda: self.log_contains("STATE=DIVERGED"))
        self.assertEqual(local_head, git(self.local, "rev-parse", "HEAD"))

    def test_wrong_branch_is_skipped(self):
        git(self.local, "checkout", "-b", "topic")
        before = git(self.local, "rev-parse", "HEAD")
        self.push_writer()
        self.start_watcher()
        self.wait_for(lambda: self.log_contains("STATE=SKIP_BRANCH"))
        self.assertEqual("topic", git(self.local, "rev-parse", "--abbrev-ref", "HEAD"))
        self.assertEqual(before, git(self.local, "rev-parse", "HEAD"))

    def test_singleton_and_stop_signal(self):
        first = self.start_watcher()
        self.wait_for(lambda: self.log_path.exists())
        second = subprocess.run([POWERSHELL, "-NoProfile", "-File", str(WATCHER),
                                 "-RepoRoot", str(self.local), "-IntervalSeconds", "1"],
                                capture_output=True, timeout=3)
        self.assertEqual(0, second.returncode)
        stop = self.local / ".git/main-autopull.stop"
        stop.write_text("stop\n", encoding="ascii")
        first.wait(timeout=4)
        self.assertFalse(stop.exists())
        self.assertTrue(self.log_contains("STOP requested"))

    def test_colliding_untracked_file_is_preserved(self):
        before = git(self.local, "rev-parse", "HEAD")
        (self.local / "collision.txt").write_text("local untracked\n", encoding="utf-8")
        self.push_writer("collision.txt", "remote tracked\n")
        self.start_watcher()
        self.wait_for(lambda: self.log_contains("STATE=SKIP_UNTRACKED_COLLISION"))
        self.assertEqual(before, git(self.local, "rev-parse", "HEAD"))
        self.assertEqual("local untracked\n", (self.local / "collision.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

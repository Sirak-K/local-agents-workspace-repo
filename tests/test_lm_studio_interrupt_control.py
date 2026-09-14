"""Real stop invariants, bounded IPC and explicit live authentication checks."""
from __future__ import annotations

import os
from argparse import Namespace
import importlib.util
from pathlib import Path
import sys
import subprocess
import tempfile
import time
import unittest
from threading import Thread
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ROLE = ROOT / "LOCAL_AGENTS/AGENT-0-WORKER"
EVAL = ROLE / "agent-0-eval"
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "LM-Studio_connections/LM-Studio_for_codex"),
                str(ROLE / "agent-0-tools"), str(EVAL)]
from interruptible_prediction import SdkPredictionProcess, stop_verdict
from lm_studio_user_api_token import resolve_token
from worker_tool_process_control import WorkerToolProcessControl
import evaluation_paths as eval_paths

spec = importlib.util.spec_from_file_location("controlled_run", EVAL / "controlled_run.py")
controlled = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controlled)


class FakeSdk:
    """Control-contract fixture only; never a provider stop-verification claim."""
    result_reason = "userStopped"
    acknowledge = True

    def __init__(self, *_):
        self.started = False
        self.cancelled = False
        self.sent = False
        self.process = self

    def next_event(self, timeout=0.1):
        time.sleep(0.01)
        if not self.started:
            self.started = True
            return {"type": "prediction_started"}
        if self.cancelled and not self.sent:
            self.sent = True
            return {"type": "cancel_sent"}
        if self.cancelled and self.acknowledge:
            return {"type": "result", "content": "partial", "stats": {"stopReason": self.result_reason}}
        return None

    def cancel(self):
        self.cancelled = True

    def close(self):
        pass

    def poll(self):
        return 0


class RunControlContractTest(unittest.TestCase):
    def exercise(self, reason="userStopped", acknowledge=True):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            eval_root = root / "model_evaluations"
            eval_root.mkdir()
            eval_id = "EVAL_fixture"
            instruction = root / "instruction.txt"
            instruction.write_text("A clear instruction", encoding="utf-8")
            args = Namespace(eval_id=eval_id, input_file=str(instruction), system_prompt_file=None,
                             model="fixture", duration=10, stop_budget=1, max_tokens=10,
                             previous_run=None, change_reason=None, tool_stop_probe=False)
            outcome, errors = [], []

            class FixtureSdk(FakeSdk):
                result_reason = reason
            FixtureSdk.acknowledge = acknowledge

            def execute():
                try:
                    outcome.append(controlled.run(args))
                except BaseException as error:
                    errors.append(error)

            with patch.object(controlled, "ROOT", root), \
                    patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", eval_root), \
                    patch.object(controlled, "SdkPredictionProcess", FixtureSdk), \
                    patch.object(controlled, "resolve_token", return_value="fixture-secret"):
                thread = Thread(target=execute)
                thread.start()
                deadline = time.monotonic() + 3
                documents = []
                while not documents and time.monotonic() < deadline:
                    documents = list((eval_root / eval_id).glob("*/evidence.json")) if (eval_root / eval_id).exists() else []
                    time.sleep(0.01)
                self.assertTrue(documents)
                run_id = documents[0].parent.name
                self.assertTrue(controlled.request_stop(eval_id, run_id, "verified fixture defect"))
                self.assertFalse(controlled.request_stop(eval_id, run_id, "must not overwrite original reason"))
                thread.join(timeout=4)
                self.assertFalse(thread.is_alive())
                self.assertEqual(errors, [])
                self.assertEqual(outcome[0][1]["stop"]["reason"], "verified fixture defect")
                saved = controlled.read_json(documents[0], controlled.MAX_DOCUMENT_BYTES)
                self.assertEqual(eval_id, saved["eval_id"])
                self.assertNotIn("fixture-secret", documents[0].read_text(encoding="utf-8"))
                self.assertFalse(documents[0].read_bytes().startswith(bytes([239, 187, 191])))
                self.assertIn('\n  "run_id"', documents[0].read_text(encoding="utf-8"))
                self.assertFalse(controlled.request_stop(eval_id, run_id, "already finished"))
                return saved

    def test_separate_stop_works_before_first_token_and_preserves_partial_result(self):
        document = self.exercise()
        self.assertEqual(document["state"], "verified_cancel")
        self.assertEqual(document["result"]["content"], "partial")
        self.assertEqual(document["contract"]["model_tools"], [])

    def test_completion_race_is_not_reported_as_cancel_success(self):
        self.assertEqual(self.exercise("eosFound")["state"], "completed_race")

    def test_no_server_receipt_never_passes(self):
        self.assertEqual(self.exercise(acknowledge=False)["state"], "unverified")

    def test_scope_and_budget_guards(self):
        with self.assertRaises(ValueError):
            eval_paths.run_directory("../outside", "a" * 32)
        with self.assertRaises(ValueError):
            eval_paths.run_directory("EVAL_fixture", "../outside")
        for duration, stop, tokens in [(float("nan"), 1, 1), (1, 6, 1), (1, 1, 1025)]:
            with self.assertRaises(ValueError):
                controlled.validate_budgets(duration, stop, tokens)
        self.assertEqual(controlled.text_preview({"text_chunks": ["first", "second", "third"]}), ["first", "second"])

    def test_legitimate_prediction_is_not_cancelled(self):
        class CompletedSdk(FakeSdk):
            def next_event(self, timeout=0.1):
                if not self.started:
                    return super().next_event(timeout)
                return {"type": "result", "content": "OK", "stats": {"stopReason": "eosFound"}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            eval_root = root / "model_evaluations"
            eval_root.mkdir()
            instruction = root / "instruction.txt"
            instruction.write_text("Return OK", encoding="utf-8")
            args = Namespace(eval_id="EVAL_fixture", input_file=str(instruction), system_prompt_file=None,
                             model="fixture", duration=10, stop_budget=1, max_tokens=10,
                             previous_run=None, change_reason=None, tool_stop_probe=False)
            with patch.object(controlled, "ROOT", root), \
                    patch.object(eval_paths, "MODEL_EVALUATIONS_ROOT", eval_root), \
                    patch.object(controlled, "SdkPredictionProcess", CompletedSdk), \
                    patch.object(controlled, "resolve_token", return_value="fixture-secret"):
                _, document = controlled.run(args)
                self.assertEqual(document["state"], "completed")
                self.assertIsNone(document["stop"])
                self.assertFalse(document["verification"]["cancel_command_sent"])


class StopVerdictTest(unittest.TestCase):
    def test_timeout_and_client_exit_are_not_stop_proof(self):
        self.assertEqual(stop_verdict(None, True, True), "unverified")
        self.assertEqual(stop_verdict({"stats": {}}, True, True), "unverified")
        self.assertEqual(stop_verdict({"stats": {"stopReason": "unknown_provider_reason"}}, True, True), "unverified")

    def test_server_cancel_receipt_and_natural_completion_differ(self):
        self.assertEqual(stop_verdict({"stats": {"stopReason": "userStopped"}}, True, True), "verified_cancel")
        self.assertEqual(stop_verdict({"stats": {"stopReason": "eosFound"}}, True, True), "completed_race")
        self.assertEqual(stop_verdict({"stats": {"stopReason": "eosFound"}}, False, True), "completed")
        self.assertEqual(stop_verdict({"stats": {}}, False, True), "unverified")

    def test_no_prediction_is_not_a_generation_stop_probe(self):
        self.assertEqual(stop_verdict(None, True, False), "unverified")
        self.assertEqual(stop_verdict(None, True, False, not_started=True), "not_started")

    def test_sdk_auth_adapter_rejects_remote_origins_and_malformed_tokens(self):
        source = """
import assert from 'node:assert/strict';
import { authenticatedOptions } from './lm_studio_sdk_prediction.mjs';
const token = 'sk-lm-AbC12345:01234567890123456789';
assert.equal(authenticatedOptions(token,'ws://127.0.0.1:1234').clientIdentifier,'AbC12345');
for (const url of ['ws://example.com:1234','wss://127.0.0.1:1234','ws://user@localhost:1234','ws://localhost:1234/path']) {
  assert.throws(() => authenticatedOptions(token,url));
}
assert.throws(() => authenticatedOptions('bad-token','ws://127.0.0.1:1234'));
"""
        response = subprocess.run(["node", "--input-type=module", "-e", source],
                                  cwd=ROOT / "LM-Studio_connections/LM-Studio_for_codex",
                                  capture_output=True, timeout=5)
        self.assertEqual(response.returncode, 0, response.stderr[:1000])

    def test_real_sdk_chat_contract_freshness_no_system_and_explicit_system(self):
        source = """
import assert from 'node:assert/strict';
import { predictionChat } from './lm_studio_sdk_prediction.mjs';
const first = predictionChat('', 'independent task');
assert.equal(first.getLength(), 1);
assert.equal(first.at(0).getRole(), 'user');
assert.equal(first.at(0).getText(), 'independent task');
assert.equal(first.hasFiles(), false);
first.append('assistant', 'prior output');
const second = predictionChat('', 'new independent task');
assert.equal(second.getLength(), 1);
assert.equal(second.at(0).getText(), 'new independent task');
const explicit = predictionChat('explicit diagnostic system', 'task');
assert.equal(explicit.getLength(), 2);
assert.equal(explicit.at(0).getRole(), 'system');
assert.equal(explicit.at(0).getText(), 'explicit diagnostic system');
"""
        response = subprocess.run(["node", "--input-type=module", "-e", source],
                                  cwd=ROOT / "LM-Studio_connections/LM-Studio_for_codex",
                                  capture_output=True, timeout=5)
        self.assertEqual(response.returncode, 0, response.stderr[:1000])


@unittest.skipUnless(os.name == "nt", "Windows Job Objects required")
class WorkerProcessControlTest(unittest.TestCase):
    def test_owner_crash_kills_its_job(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            child = "import time; from pathlib import Path; time.sleep(1.5); Path('late-write.txt').write_text('bad')"
            source = ("import sys,os,time; from pathlib import Path; sys.path.insert(0," + repr(str(ROLE / "agent-0-tools")) + "); "
                      "from worker_tool_process_control import WorkerToolProcessControl; control=WorkerToolProcessControl(); "
                      "control.dispatch([sys.executable,'-c'," + repr(child) + "],Path('.')); os._exit(0)")
            owner = subprocess.Popen([sys.executable, "-c", source], cwd=directory,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                self.assertEqual(owner.wait(timeout=3), 0)
                time.sleep(1.6)
                self.assertFalse((directory / "late-write.txt").exists())
            finally:
                if owner.poll() is None:
                    owner.kill()
                    owner.wait(timeout=2)

    def test_real_parent_child_stop_and_no_late_write_or_new_dispatch(self):
        with tempfile.TemporaryDirectory() as temporary, WorkerToolProcessControl() as control:
            directory = Path(temporary)
            marker = directory / "late-write.txt"
            child_code = "import time; from pathlib import Path; time.sleep(1.5); Path('late-write.txt').write_text('bad')"
            parent_code = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c'," + repr(child_code) + "]); time.sleep(10)"
            control.dispatch([sys.executable, "-c", parent_code], directory)
            deadline = time.monotonic() + 3
            while control.accounting()["total_processes"] < 2 and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertGreaterEqual(control.accounting()["total_processes"], 2)
            result = control.stop()
            self.assertTrue(result["verified"])
            self.assertEqual(result["active_processes"], 0)
            with self.assertRaisesRegex(RuntimeError, "dispatch is closed"):
                control.dispatch([sys.executable, "-c", "pass"], directory)
            time.sleep(1.6)
            self.assertFalse(marker.exists())
            self.assertTrue(control.stop()["verified"])

    def test_legitimate_tool_completes_and_is_not_terminated_prematurely(self):
        with tempfile.TemporaryDirectory() as temporary, WorkerToolProcessControl() as control:
            directory = Path(temporary)
            control.dispatch([sys.executable, "-c", "from pathlib import Path; Path('done.txt').write_text('OK')"], directory)
            deadline = time.monotonic() + 3
            while control.accounting()["active_processes"] and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertEqual(control.accounting()["active_processes"], 0)
            self.assertEqual((directory / "done.txt").read_text(), "OK")


@unittest.skipUnless(os.environ.get("LM_STUDIO_AUTH_PROBE") == "1", "explicit live inventory probe only")
class LiveSdkAuthenticationTest(unittest.TestCase):
    def test_valid_token_inventory_and_invalid_token_rejection(self):
        for label, token in [("valid", resolve_token()), ("invalid", "sk-lm-00000000:00000000000000000000"), ("valid_after", resolve_token())]:
            with self.subTest(token=label):
                process = SdkPredictionProcess(token, {"inventory": True, "base_url": "ws://127.0.0.1:1234"})
                try:
                    deadline = time.monotonic() + 12
                    event = None
                    while time.monotonic() < deadline:
                        candidate = process.next_event()
                        if candidate and candidate["type"] in ("inventory", "error"):
                            event = candidate
                            break
                    self.assertIsNotNone(event)
                    self.assertEqual(event["type"], "error" if label == "invalid" else "inventory")
                finally:
                    process.close()


@unittest.skipUnless(os.environ.get("LM_STUDIO_GENERATION_PROBE") == "1" and os.environ.get("LM_STUDIO_MODEL_IDENTIFIER"),
                     "two short generation probes require explicit approval and a loaded identifier")
class LiveSdkGenerationTest(unittest.TestCase):
    """Retain real gate evidence. Never count these fixtures as an audition."""
    def setUp(self):
        from capture_model_lifecycle_events import fetch_models
        self.fetch_models = fetch_models
        self.identifier = os.environ["LM_STUDIO_MODEL_IDENTIFIER"]
        self.eval_id = os.environ.get("LM_STUDIO_EVAL_ID", "EVAL_live_interrupt_control")
        self.assertTrue(self.is_loaded(), "selected instance must be manually loaded")

    def is_loaded(self):
        payload = self.fetch_models("http://127.0.0.1:1234", resolve_token(), timeout_seconds=5)
        return any(instance.get("id") == self.identifier for model in payload["models"]
                   for instance in model.get("loaded_instances", []))

    def start_run(self, instruction, tool_probe=False):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "instruction.txt"
            source.write_text(instruction, encoding="utf-8")
            argv = [sys.executable, str(EVAL / "controlled_run.py"), "start",
                    "--eval-id", self.eval_id, "--model", self.identifier, "--input-file", str(source),
                    "--duration", "30", "--max-tokens", "1024"]
            if tool_probe:
                argv.append("--tool-stop-probe")
            response = subprocess.run(argv, capture_output=True, timeout=5, check=True)
            import json
            run_id = json.loads(response.stdout)["run_id"]
            path = eval_paths.run_directory(self.eval_id, run_id) / "evidence.json"
            self.assertTrue(path.exists())
        print("LIVE DIAGNOSTIC RUN", self.eval_id, run_id, flush=True)
        return run_id, path

    def wait_terminal(self, path, seconds=10):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            document = controlled.read_json(path, controlled.MAX_DOCUMENT_BYTES)
            if document["state"] in controlled.TERMINAL:
                return document
            time.sleep(0.05)
        self.fail("no terminal evidence within the bounded gate probe")

    def test_cancel_live_generation_and_owned_process_group(self):
        run_id, path = self.start_run("Write the integers from 1 to 5000 in ascending order, separated by spaces. Do not summarize or stop early.", True)
        deadline = time.monotonic() + 10
        try:
            fragments = []
            while time.monotonic() < deadline:
                document = controlled.read_json(path, controlled.MAX_DOCUMENT_BYTES)
                fragments = [e for e in document["events"] if e["data"].get("type") == "fragment"]
                if fragments:
                    break
                self.assertNotIn(document["state"], controlled.TERMINAL, "generation ended before observation")
                time.sleep(0.05)
            self.assertTrue(fragments, "must observe actual generated output before this stop probe")
            response = subprocess.run([sys.executable, str(EVAL / "controlled_run.py"), "stop",
                                       "--eval-id", self.eval_id, "--run-id", run_id,
                                       "--reason", "verify mandatory stop gate with disposable diagnostic fixture"],
                                      capture_output=True, timeout=5, check=True)
            self.assertIn(b"true", response.stdout)
            document = self.wait_terminal(path)
            self.assertEqual(document["state"], "verified_cancel")
            self.assertEqual(document["result"]["stats"]["stopReason"], "userStopped")
            self.assertTrue(document["verification"]["within_stop_budget"])
            self.assertEqual(document["verification"]["tools"]["active_processes"], 0)
            self.assertGreaterEqual(document["verification"]["tools"]["total_processes"], 2)
            self.assertFalse((path.parent / "late-tool-write.txt").exists())
            self.assertTrue(self.is_loaded(), "stop must preserve the loaded model and active server")
        finally:
            controlled.request_stop(self.eval_id, run_id, "diagnostic test cleanup if unfinished")

    def test_legitimate_live_generation_finishes_without_cancel(self):
        run_id, path = self.start_run("Return exactly OK and nothing else.")
        try:
            document = self.wait_terminal(path, 35)
            self.assertEqual(document["state"], "completed")
            self.assertEqual(document["result"]["content"].strip(), "OK")
            self.assertIsNone(document["stop"])
            self.assertFalse(document["verification"]["cancel_command_sent"])
            self.assertTrue(self.is_loaded())
        finally:
            controlled.request_stop(self.eval_id, run_id, "diagnostic test cleanup if unfinished")


if __name__ == "__main__":
    unittest.main()

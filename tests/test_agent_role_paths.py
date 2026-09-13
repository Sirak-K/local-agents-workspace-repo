from __future__ import annotations

import importlib
from pathlib import Path
import sys
import tempfile
import unittest


TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))


class AgentRolePathsTest(unittest.TestCase):
    def test_canonical_agent_roles_and_shared_surfaces_have_one_owner(self) -> None:
        try:
            path_module = importlib.import_module("agent_role_paths")
        except ModuleNotFoundError as exc:
            self.fail(f"central agent-role path owner is not implemented: {exc}")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            paths = path_module.AgentRolePaths(root)

            self.assertEqual(paths.project_bionic, root / "PROJECT_BIONIC")
            self.assertEqual(
                paths.agent_roles,
                root / "PROJECT_BIONIC/BIONIC_AGENTS",
            )
            self.assertEqual(
                paths.model_neutral_context,
                paths.agent_roles / "model-neutral-context",
            )
            self.assertEqual(
                paths.model_neutral_runtime_config,
                paths.agent_roles / "model-neutral-runtime-config",
            )
            self.assertEqual(
                paths.qwen_chat_agent,
                paths.agent_roles / "bionic_agent-1-Qwen3.5",
            )
            self.assertEqual(
                paths.qwen_chat_agent_context,
                paths.qwen_chat_agent / "agent-1-ctx",
            )
            self.assertEqual(
                paths.qwen_chat_agent_runtime,
                paths.qwen_chat_agent / "agent-1-runtime_config",
            )
            self.assertEqual(
                paths.qwen_chat_agent_skills,
                paths.qwen_chat_agent / "agent-1-skills",
            )
            self.assertEqual(
                paths.qwen_chat_agent_system_prompt,
                paths.qwen_chat_agent / "agent-1_system_prompt.txt",
            )
            self.assertEqual(
                paths.qwen_chat_agent_bionic_pg2_native_audit_config,
                paths.qwen_chat_agent_runtime
                / "agent_config_bionic_pg2_native_audit.json",
            )
            self.assertEqual(
                paths.qwen_chat_agent_pg2_filesystem_plugin_audit_config,
                paths.qwen_chat_agent_runtime
                / "agent_config_pg2_filesystem_plugin_audit.json",
            )
            self.assertEqual(
                paths.qwen_chat_agent_pg2_candidate_config,
                paths.qwen_chat_agent_pg2_filesystem_plugin_audit_config,
            )
            self.assertEqual(
                paths.lumimaid_story_agent,
                paths.agent_roles / "bionic_agent-2-Lumimaid",
            )
            self.assertEqual(
                paths.lumimaid_story_agent_context,
                paths.lumimaid_story_agent / "agent-2-ctx",
            )
            self.assertEqual(
                paths.lumimaid_story_agent_runtime,
                paths.lumimaid_story_agent / "agent-2-runtime_config",
            )

    def test_live_workspace_uses_only_canonical_agent_role_names(self) -> None:
        path_module = importlib.import_module("agent_role_paths")
        workspace_root = TOOLS_ROOT.parent
        paths = path_module.AgentRolePaths(workspace_root)

        self.assertTrue(paths.qwen_chat_agent.is_dir())
        self.assertTrue(paths.lumimaid_story_agent.is_dir())
        self.assertFalse((paths.agent_roles / "bionic_agent-1_Qwen3.5").exists())
        self.assertFalse((paths.agent_roles / "bionic_agent-2_Lumimaid").exists())

    def test_model_neutral_context_contains_no_model_or_specialist_binding(self) -> None:
        path_module = importlib.import_module("agent_role_paths")
        paths = path_module.AgentRolePaths(TOOLS_ROOT.parent)
        forbidden_terms = (
            "lumimaid",
            "qwen",
            "story creator",
            "saqc",
            "comfyui",
            "bionic_agent-1_",
            "bionic_agent-2_",
            "project_bionic/bionic_agent/",
        )

        for context_file in paths.model_neutral_context.glob("ctx_*.md"):
            content = context_file.read_text(encoding="utf-8").lower()
            for forbidden_term in forbidden_terms:
                with self.subTest(
                    context_file=context_file.name,
                    forbidden_term=forbidden_term,
                ):
                    self.assertNotIn(forbidden_term, content)


if __name__ == "__main__":
    unittest.main()

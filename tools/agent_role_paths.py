"""Construct canonical project-owned agent-role paths without filesystem I/O."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AgentRolePaths:
    """Canonical shared and role-specific agent paths rooted at the workspace."""

    workspace_root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "workspace_root", Path(self.workspace_root).resolve())

    @property
    def project_bionic(self) -> Path:
        return self.workspace_root / "PROJECT_BIONIC"

    @property
    def agent_roles(self) -> Path:
        return self.project_bionic / "BIONIC_AGENTS"

    @property
    def model_neutral_context(self) -> Path:
        return self.agent_roles / "model-neutral-context"

    @property
    def model_neutral_runtime_config(self) -> Path:
        return self.agent_roles / "model-neutral-runtime-config"

    @property
    def qwen_chat_agent(self) -> Path:
        return self.agent_roles / "bionic_agent-1-Qwen3.5"

    @property
    def qwen_chat_agent_context(self) -> Path:
        return self.qwen_chat_agent / "agent-1-ctx"

    @property
    def qwen_chat_agent_runtime(self) -> Path:
        return self.qwen_chat_agent / "agent-1-runtime_config"

    @property
    def qwen_chat_agent_skills(self) -> Path:
        return self.qwen_chat_agent / "agent-1-skills"

    @property
    def qwen_chat_agent_system_prompt(self) -> Path:
        return self.qwen_chat_agent / "agent-1_system_prompt.txt"

    @property
    def qwen_chat_agent_bionic_pg2_native_audit_config(self) -> Path:
        return (
            self.qwen_chat_agent_runtime
            / "agent_config_bionic_pg2_native_audit.json"
        )

    @property
    def qwen_chat_agent_pg2_filesystem_plugin_audit_config(self) -> Path:
        return (
            self.qwen_chat_agent_runtime
            / "agent_config_pg2_filesystem_plugin_audit.json"
        )

    @property
    def qwen_chat_agent_pg2_candidate_config(self) -> Path:
        """Compatibility name retained only for the isolated plugin audit harness."""
        return self.qwen_chat_agent_pg2_filesystem_plugin_audit_config

    @property
    def lumimaid_story_agent(self) -> Path:
        return self.agent_roles / "bionic_agent-2-Lumimaid"

    @property
    def lumimaid_story_agent_context(self) -> Path:
        return self.lumimaid_story_agent / "agent-2-ctx"

    @property
    def lumimaid_story_agent_runtime(self) -> Path:
        return self.lumimaid_story_agent / "agent-2-runtime_config"

    @property
    def lumimaid_story_agent_system_prompt(self) -> Path:
        return self.lumimaid_story_agent / "agent-2_system_prompt.txt"


__all__ = ["AgentRolePaths"]

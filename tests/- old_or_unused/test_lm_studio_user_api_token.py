from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


TOOLS_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = TOOLS_ROOT / "tools/lm_studio_user_api_token.py"
SPEC = importlib.util.spec_from_file_location("lm_studio_user_api_token", MODULE_PATH)
assert SPEC and SPEC.loader
token_loader = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = token_loader
SPEC.loader.exec_module(token_loader)


class LmStudioUserApiTokenTest(unittest.TestCase):
    def test_process_environment_has_priority(self) -> None:
        with patch.dict(os.environ, {"LM_API_TOKEN": "process-token"}):
            self.assertEqual(token_loader.resolve_token(), "process-token")

    @unittest.skipUnless(os.name == "nt", "Windows user environment is Windows-specific")
    def test_windows_user_environment_is_automatic_fallback(self) -> None:
        import winreg

        with patch.dict(os.environ, {}, clear=True), patch.object(
            winreg, "OpenKey"
        ), patch.object(
            winreg, "QueryValueEx", return_value=("persistent-token", winreg.REG_SZ)
        ):
            self.assertEqual(token_loader.resolve_token(), "persistent-token")


if __name__ == "__main__":
    unittest.main()

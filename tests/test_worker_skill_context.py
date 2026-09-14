"""Candidate skill source hashes and explicit/discovery exposure boundaries."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval"))
import worker_skill_context as skills


class WorkerSkillContextTest(unittest.TestCase):
    def test_explicit_source_and_discovery_metadata_are_different_declared_inputs(self):
        none = skills.expose_skills("none")
        self.assertEqual("", none["system_text"])
        explicit = skills.expose_skills("explicit", "workflow_title_preservation")
        self.assertEqual(1, len(explicit["skills"]))
        source = explicit["skills"][0]
        self.assertIn(source["content"], explicit["system_text"])
        self.assertEqual(source["sha256"], hashlib.sha256(source["content"].encode("utf-8")).hexdigest())
        discovery = skills.expose_skills("discovery")
        self.assertEqual(3, len(discovery["skills"]))
        self.assertNotIn(source["content"], discovery["system_text"])
        for mode, identifier in (("none", "workflow_title_preservation"), ("explicit", None),
                                 ("explicit", "missing"), ("discovery", "workflow_title_preservation")):
            with self.assertRaises(ValueError):
                skills.expose_skills(mode, identifier)

    def test_altered_skill_is_not_silently_exposed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copy2(skills.SKILLS / "skill_catalog.json", root / "skill_catalog.json")
            catalog = json.loads((root / "skill_catalog.json").read_text(encoding="utf-8"))
            for item in catalog["skills"]:
                (root / item["id"]).mkdir()
                shutil.copy2(skills.SKILLS / item["file"], root / item["file"])
            with (root / catalog["skills"][0]["file"]).open("ab") as handle:
                handle.write(b"changed")
            with patch.object(skills, "SKILLS", root), self.assertRaises(ValueError):
                skills.expose_skills("discovery")


if __name__ == "__main__":
    unittest.main()

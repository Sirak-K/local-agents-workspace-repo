import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_CASES = REPO_ROOT / "LOCAL_AGENTS" / "AGPR-3-IMAGE-MASTER" / "IMAGE-QUALIFICATION-CASES.json"
VOICE_CASES = REPO_ROOT / "LOCAL_AGENTS" / "AGPR-4-VOICE-MASTER" / "VOICE-QUALIFICATION-CASES.json"
ABSOLUTE_PATH = re.compile(r"^(?:[A-Za-z]:[\\/]|[\\/])")


def load_cases(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class QualificationCaseTests(unittest.TestCase):
    def test_case_files_are_qualification_only_and_have_unique_ids(self) -> None:
        for path in (IMAGE_CASES, VOICE_CASES):
            document = load_cases(path)
            self.assertIn("qualification-only", document["scope"])
            case_ids = [case["id"] for case in document["cases"]]
            self.assertEqual(len(case_ids), len(set(case_ids)))
            self.assertTrue(case_ids)

    def test_all_output_files_are_relative_and_profile_owned(self) -> None:
        for path, expected_prefix in (
            (IMAGE_CASES, "qualification_outputs/image/"),
            (VOICE_CASES, "qualification_outputs/voice/"),
        ):
            for case in load_cases(path)["cases"]:
                output_file = case["output_file"]
                self.assertFalse(ABSOLUTE_PATH.match(output_file))
                self.assertTrue(output_file.startswith(expected_prefix))

    def test_image_gate_is_one_base_plus_one_same_seed_revision(self) -> None:
        document = load_cases(IMAGE_CASES)
        self.assertEqual(document["settings"]["images_per_iteration"], 1)
        self.assertGreaterEqual(document["settings"]["seed"], 0)
        self.assertEqual([case["id"] for case in document["cases"]], [
            "base_composition",
            "single_attribute_revision",
        ])
        self.assertEqual(document["cases"][1]["base_case"], "base_composition")

    def test_voice_gate_covers_required_behaviors_with_one_reference(self) -> None:
        document = load_cases(VOICE_CASES)
        self.assertEqual(document["settings"]["voice_reference"], "female_primary")
        cases = {case["id"]: case for case in document["cases"]}
        self.assertEqual(cases["voice_repeat_a"]["spoken_text"], cases["voice_repeat_b"]["spoken_text"])
        self.assertIn("laughter", cases["natural_laughter"]["performance"])
        self.assertIn("scream", cases["high_intensity_scream"]["performance"])
        self.assertIn("exact transcript", cases["transcript_fidelity"]["performance"])


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "select_task.py"
CONFIG = json.loads((ROOT / "config" / "repositories.json").read_text(encoding="utf-8"))


class SelectorTests(unittest.TestCase):
    def run_script(self, *args: str) -> str:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return result.stdout

    def test_daily_selection_is_deterministic(self):
        first = self.run_script("--date", "2026-10-24")
        second = self.run_script("--date", "2026-10-24")
        self.assertEqual(first, second)
        self.assertIn("review-only", first)
        self.assertIn("pull request", first.lower())

    def test_selector_rotates_across_adjacent_days(self):
        first = self.run_script("--date", "2026-10-24")
        second = self.run_script("--date", "2026-10-25")
        self.assertNotEqual(first.split("**Target repository:** `", 1)[1].split("`", 1)[0],
                            second.split("**Target repository:** `", 1)[1].split("`", 1)[0])

    def test_biweekly_proposal_never_authorizes_repo_creation(self):
        proposal = self.run_script("--date", "2026-10-26", "--biweekly")
        self.assertIn("Approval required", proposal)
        self.assertIn("Do not create a repository", proposal)

    def test_config_has_safety_policy(self):
        policy = CONFIG["policy"]
        self.assertFalse(policy["allow_direct_push"])
        self.assertFalse(policy["allow_auto_merge"])
        self.assertFalse(policy["allow_create_repository"])


if __name__ == "__main__":
    unittest.main()

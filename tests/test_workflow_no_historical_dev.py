"""Safety regression: no historical DEV/FINAL scoring in main/PR CI.

This is a static workflow-text check only. NEVER executes a scorer or imports
actual task generators. Historical archived outcomes remain unchanged.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorkflowNoHistoricalHoldoutTests(unittest.TestCase):
    def test_research_ci_workflow_never_launches_dev_or_final(self):
        text = (ROOT / ".github/workflows/docs-check.yml").read_text()
        banned = [
            r"python\s+-m\s+packages[.]kernel[.]eval_cli\s+--phase\s+(?:dev|final)\b",
            r"python\s+-m\s+packages[.]exp0003a[.]pr3_cli\s+--mode\s+(?:dev|final)\b",
            r"python\s+-m\s+packages[.]exp0003a[.]freeze_cli\s+--mode\s+(?:dev|final)\b",
            r"EXP-0002B-DEV-smoke[.]json",
        ]
        for pattern in banned:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, text, flags=re.IGNORECASE))
        self.assertIn("python -m unittest discover -s tests -v", text)


if __name__ == "__main__":
    unittest.main()

"""CI-SAFE-V2 non-execution negative tests and immutable original-source gate."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts import check_research_ci_v2 as s


class SuccessorCIGuardTests(unittest.TestCase):
    def test_current_workflow_matches_reviewed_whitelist(self) -> None:
        s.validate_successor((s.ROOT / s.SUCCESSOR).read_bytes())

    def test_historic_method_and_both_source_locks_unchanged(self) -> None:
        receipt = s.validate_repo_files()
        self.assertEqual(receipt["status"], "static_source_integrity_pass")
        self.assertEqual(receipt["historic_pilot_source_count"], 9)
        self.assertEqual(receipt["historic_exp0003a_source_count"], 14)
        self.assertFalse(receipt["scoring_authorized"])
        self.assertFalse(receipt["legacy_workflow_disabled_verified"])
        self.assertFalse(receipt["successor_main_merge_authorized"])

    def test_main_push_old_dev_injection_rejected(self) -> None:
        dangerous = (
            "\n      - name: Historical DEV smoke (not permitted)\n"
            "        if: github.event_name == 'push'\n"
            "        run: python -m packages.kernel.eval_cli --phase dev\n"
        )
        with self.assertRaises(s.CISafetyError):
            s.validate_successor(
                (s.EXPECTED_SUCCESSOR + dangerous).encode("utf-8"))

    def test_final_upload_and_shell_block_rejected(self) -> None:
        for added in (
            "\n      - name: Upload FINAL original\n"
            "        uses: actions/upload-artifact@v4\n",
            "\n      - name: Arbitrary shell\n        run: |\n"
            "          echo not-a-safe-command\n",
            "\n  workflow_dispatch:\n",
        ):
            with self.subTest(added=added), self.assertRaises(s.CISafetyError):
                s.validate_successor(
                    (s.EXPECTED_SUCCESSOR + added).encode("utf-8"))

    def test_missing_workflow_and_symlink_rejected_before_source_import(self) -> None:
        with TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(s.CISafetyError):
                s.validate_repo_files(root)
            p = root / s.SUCCESSOR
            p.parent.mkdir(parents=True)
            p.symlink_to(s.ROOT / s.SUCCESSOR)
            with self.assertRaises(s.CISafetyError):
                s.validate_repo_files(root)

    def test_workflow_byte_mutations_fail_closed(self) -> None:
        original = s.EXPECTED_SUCCESSOR.encode("utf-8")
        for changed in (
            original + b"\n",
            original.replace(b"branches: [main]", b"branches: [main, dev]"),
            original.replace(b"python scripts/check_docs.py",
                             b"python -m packages.kernel.eval_cli --phase dev"),
            original.replace(b"pull_request:", b"workflow_dispatch:"),
        ):
            with self.subTest(mutated=changed[-40:]), self.assertRaises(
                s.CISafetyError
            ):
                s.validate_successor(changed)

    def test_empty_or_nonbytes_rejected(self) -> None:
        for invalid in (None, "", b"", bytearray()):
            with self.assertRaises(s.CISafetyError):
                s.validate_successor(invalid)


if __name__ == "__main__":
    unittest.main()

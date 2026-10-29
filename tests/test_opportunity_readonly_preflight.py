"""Synthetic-only tests of the owner-private pre-scoring preflight.

This suite NEVER accesses a genuine TRAIN64 private original or runs an
actual new TRAIN64 scorer, old DEV/FINAL, or history replay.
"""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import opportunity_readonly_preflight as m
from scripts import opportunity_one_shot_runner as runner
from scripts import opportunity_real_pair_engine as engine


class ReadonlyPreflightSyntheticTests(unittest.TestCase):
    def test_absent_ledger_only_checks_and_leaves_directory_unchanged(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / "owner"
            home.mkdir(mode=0o700)
            with runner._private_root(home) as fd:
                m._reject_existing_ledger(fd, runner.LEDGER_NAME)
            self.assertEqual(list(home.iterdir()), [])

    def test_ledger_present_forbids_preflight_without_mutation(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / "owner"
            home.mkdir(mode=0o700)
            ledger = home / runner.LEDGER_NAME
            ledger.mkdir(mode=0o700)
            with runner._private_root(home) as fd:
                with self.assertRaises(ValueError):
                    m._reject_existing_ledger(fd, runner.LEDGER_NAME)
            self.assertTrue(ledger.is_dir())
            self.assertEqual(list(ledger.iterdir()), [])

    def test_symlink_to_external_marker_is_still_detected_nofollow(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / "owner"
            home.mkdir(mode=0o700)
            (home / runner.LEDGER_NAME).symlink_to(
                Path(tmp) / "outside", target_is_directory=True)
            with runner._private_root(home) as fd:
                with self.assertRaises(ValueError):
                    m._reject_existing_ledger(fd, runner.LEDGER_NAME)
            self.assertTrue((home / runner.LEDGER_NAME).is_symlink())

    def test_hard_off_flags_cannot_allow_source_access(self):
        # No source/GPU/old historic TRAIN/DREAM evaluated in CI.
        with patch.object(runner, "_require_checkout",
                          side_effect=AssertionError("unexpected checkout")):
            with patch.object(engine, "SCORING_ACTIVATED", True):
                with self.assertRaises(ValueError):
                    m.verify_readonly(Path("/SYNTHETIC"), "0"*64, "a"*40)
            with patch.object(runner, "ONE_SHOT_ACTIVATED", True):
                with self.assertRaises(ValueError):
                    m.verify_readonly(Path("/SYNTHETIC"), "0"*64, "a"*40)

    def test_checkout_is_verified_before_source_import_or_private_read(self):
        with patch.object(runner, "_require_checkout",
                          side_effect=ValueError("invalid commit")), \
             patch.object(engine, "source_first_preflight",
                          side_effect=AssertionError("must not generate")):
            with self.assertRaises(ValueError):
                m.verify_readonly(Path("/SYNTHETIC"), "0"*64, "a"*40)

    def test_cli_catches_private_error_without_leaking_path(self):
        secret = "SYNTHETIC_SECRET_PATH_NOT_TO_LEAK"
        fake_args = ["--private-dir", "/"+secret,
                     "--original-sha256", "0"*64,
                     "--approved-main-commit", "a"*40]
        out,err=StringIO(),StringIO()
        with patch.object(m, "verify_readonly",
                          side_effect=ValueError(secret)), \
             redirect_stderr(err),redirect_stdout(out):
            self.assertEqual(m.main(fake_args),2)
        self.assertEqual(out.getvalue(),"")
        self.assertNotIn(secret,err.getvalue())
        self.assertIn("no new TRAIN64 scored",err.getvalue())


if __name__ == "__main__":
    unittest.main()

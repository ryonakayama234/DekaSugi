"""OPPORTUNITY-001 generator source lock: fail-closed, hash-only, no scoring."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.verify_opportunity_generator_lock import (
    LOCK_PATH, ROOT, REQUIRED_SOURCE_FILES,
    _git_blob_sha, validate_source_blobs, verify_generator_lock,
)


class OpportunityGeneratorLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    def test_exact_frozen_source_files_and_public_commitment(self):
        self.assertEqual(len(REQUIRED_SOURCE_FILES), 9)
        validate_source_blobs(self.lock, ROOT)
        self.assertEqual(self.lock["source_main_commit"],
                         "50bad2c7b31d21492e895a19ea107b82734e49fd")
        self.assertEqual(self.lock["public_manifest_sha256"],
                         "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85")
        for path, blob in self.lock["source_git_blobs"].items():
            self.assertEqual(_git_blob_sha(ROOT / path), blob)

    def test_no_scoring_authorization_and_full_policy_pinning(self):
        self.assertIs(self.lock["new_train_pilot_scoring_permitted"], False)
        self.assertIs(self.lock["old_dev_or_final_scoring_permitted"], False)
        self.assertEqual(set(self.lock["historic_policy_snapshot_sha256"]),
                         {"B1", "B2", "B3"})
        self.assertEqual(self.lock["historic_top_skill_body_sha256"],
                         "8fe1361cb5014f8503e4a57392e45f4fc7607e788fdd598f66668fbc11338eff")

    def test_hash_only_readonly_end_to_end_preflight(self):
        report = verify_generator_lock()
        self.assertEqual(report["status"],
                         "source_identity_verified_not_scoring_authorized")
        self.assertEqual(report["source_file_count"], 9)
        self.assertEqual(report["paired_trials_executed"], 0)
        self.assertIs(report["dev_or_final_evaluated"], False)

    def test_lock_tampering_fails_closed(self):
        modifications = [
            ("source_main_commit", "a" * 40),
            ("public_manifest_sha256", "b" * 64),
            ("third_audit_commitments_sha256", "b" * 64),
            ("new_train_pilot_scoring_permitted", True),
            ("old_dev_or_final_scoring_permitted", True),
            ("python_version", "3.13.1"),
        ]
        for key, bad in modifications:
            with self.subTest(key=key):
                tampered = deepcopy(self.lock)
                tampered[key] = bad
                with self.assertRaises(ValueError):
                    validate_source_blobs(tampered, ROOT)

    def test_hidden_field_and_policy_hash_tamper_fail(self):
        tampered = deepcopy(self.lock)
        tampered["private_audit"] = "must not be in lock"
        with self.assertRaisesRegex(ValueError, "shape"):
            validate_source_blobs(tampered, ROOT)
        tampered = deepcopy(self.lock)
        tampered["historic_policy_snapshot_sha256"]["B1"] = "bad"
        with self.assertRaises(ValueError):
            validate_source_blobs(tampered, ROOT)
        tampered = deepcopy(self.lock)
        tampered["source_git_blobs"].pop("packages/protocol/__init__.py")
        with self.assertRaises(ValueError):
            validate_source_blobs(tampered, ROOT)

    def test_true_byte_drift_detected_even_if_metadata_unchanged(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)
            for rel in sorted(REQUIRED_SOURCE_FILES):
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / rel).read_bytes())
            validate_source_blobs(self.lock, root)
            with (root / "packages/evaluation/opportunity_pilot.py").open("ab") as f:
                f.write(b"\n# unauthorized source drift\n")
            with self.assertRaisesRegex(ValueError, "Source byte drift"):
                validate_source_blobs(self.lock, root)

    def test_missing_file_and_symlink_fail(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)
            for rel in sorted(REQUIRED_SOURCE_FILES):
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / rel).read_bytes())
            (root / "packages/protocol/__init__.py").unlink()
            with self.assertRaisesRegex(ValueError, "Missing/symlinked"):
                validate_source_blobs(self.lock, root)


if __name__ == "__main__":
    unittest.main()

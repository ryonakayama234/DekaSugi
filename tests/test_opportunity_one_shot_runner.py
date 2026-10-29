"""Synthetic-only evidence for the inert OPPORTUNITY one-shot local runner.

NEVER generate true pilot tasks, reconstruct old DREAM, call actual audited_trial,
or import the historical DEV/FINAL implementation.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import opportunity_one_shot_runner as m


class OneShotPrivateSyntheticTests(unittest.TestCase):
    def test_all_production_scoring_hard_off_and_never_reads_original(self):
        self.assertFalse(m.ONE_SHOT_ACTIVATED)
        with patch.object(m, "_private_root", side_effect=AssertionError("must not read")):
            with self.assertRaises(ValueError):
                m.run_private_once(Path("/ignored/synthetic"), "0" * 64, "a" * 40)

    def test_both_flags_required_for_activation(self):
        for runner, engine in [(False, False), (False, True), (True, False)]:
            with patch.object(m, "ONE_SHOT_ACTIVATED", runner):
                with self.assertRaises(ValueError):
                    m._guard_activated(SimpleNamespace(SCORING_ACTIVATED=engine))
        with patch.object(m, "ONE_SHOT_ACTIVATED", True):
            m._guard_activated(SimpleNamespace(SCORING_ACTIVATED=True))

    def test_pinned_private_root_and_exclusive_original_read(self):
        with TemporaryDirectory() as tmp:
            private = Path(tmp) / "owner"
            private.mkdir(mode=0o700)
            raw = b"synthetic-only-blob"
            original = private / "original.bin"
            original.write_bytes(raw)
            original.chmod(0o600)
            expected = sha256(raw).hexdigest()
            with m._private_root(private) as fd:
                self.assertEqual(m._read_original(fd, expected), raw)
                with self.assertRaises(ValueError):
                    m._read_original(fd, "0" * 64)
            original.chmod(0o644)
            with m._private_root(private) as fd, self.assertRaises(ValueError):
                m._read_original(fd, expected)
            original.unlink()
            original.symlink_to(Path(tmp) / "fake-public-file")
            with m._private_root(private) as fd, self.assertRaises(ValueError):
                m._read_original(fd, expected)

    def test_once_reservation_survives_failure_and_forbids_rerun(self):
        with TemporaryDirectory() as tmp:
            private = Path(tmp) / "owner"
            private.mkdir(mode=0o700)
            with m._private_root(private) as fd:
                with self.assertRaisesRegex(RuntimeError, "SYNTHETIC"):
                    with m._reserve_once(fd, "a"*40, "f"*64) as ledger:
                        with self.assertRaises(FileExistsError):
                            m._write_exclusive(ledger, "STARTED.json", {"ok": False})
                        raise RuntimeError("SYNTHETIC")
                with self.assertRaises(FileExistsError):
                    with m._reserve_once(fd, "a"*40, "f"*64):
                        pass
            self.assertTrue((private / m.LEDGER_NAME / "STARTED.json").is_file())

    def test_arm_is_reserved_before_score_no_second_invocation(self):
        with TemporaryDirectory() as tmp:
            private=Path(tmp)/"owner"
            private.mkdir(mode=0o700)
            t=SimpleNamespace(task_id="t-"+"e"*64)
            calls=[]
            def synthetic_scorer(task, audit, registry, learned):
                calls.append(learned)
                return ({"search":{"task_id":task.task_id}}, 2, 0,
                        False, False, 0.1, 0.2, 0.3, 0.4)
            with m._private_root(private) as fd:
                with m._reserve_once(fd,"a"*40,"f"*64) as ledger:
                    m._record_arm_once(ledger,0,t,object(),object(),{},
                                       synthetic_scorer)
                    self.assertEqual(len(calls),1)
                    self.assertTrue((private/m.LEDGER_NAME/"trial-000-OFF.json").is_file())
                    with self.assertRaises(FileExistsError):
                        m._record_arm_once(ledger,0,t,object(),object(),{},
                                           synthetic_scorer)
                    self.assertEqual(len(calls),1)
                    def broken(*args):
                        raise RuntimeError("SYNTHETIC_FAILED")
                    with self.assertRaises(RuntimeError):
                        m._record_arm_once(ledger,1,t,object(),object(),{},
                                           broken)
                    self.assertTrue((private/m.LEDGER_NAME/"ARM_STARTED-001-OFF.json").is_file())
                    self.assertFalse((private/m.LEDGER_NAME/"trial-001-OFF.json").exists())
                    with self.assertRaises(FileExistsError):
                        m._record_arm_once(ledger,1,t,object(),object(),{},
                                           synthetic_scorer)
                    self.assertEqual(len(calls),1)

    def test_pinned_fd_survives_pathname_swap(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "owner"
            fake_public = root / "fake_public"
            original.mkdir(mode=0o700)
            fake_public.mkdir(mode=0o700)
            with m._private_root(original) as fd:
                original.rename(root / "moved")
                original.symlink_to(fake_public, target_is_directory=True)
                with m._reserve_once(fd, "a"*40, "f"*64) as ledger_fd:
                    m._write_exclusive(ledger_fd, "synthetic.json", {"safe": True})
            self.assertFalse((fake_public / m.LEDGER_NAME).exists())
            self.assertTrue((root / "moved" / m.LEDGER_NAME / "synthetic.json").exists())

    def test_private_source_metadata_and_third_audit_exact_match(self):
        cases = []
        originals = []
        decisions = []
        for i in range(64):
            tid = "t-" + f"{i:064x}"
            cases.append(SimpleNamespace(
                task=SimpleNamespace(task_id=tid), source_record_id=f"s-{i}",
                family="synthetic", seeds=(3*i, 3*i+1, 3*i+2),
                private_audit=SimpleNamespace(input=f"input-{i}",
                                               output=f"output-{i}")))
            originals.append({"task_id": tid, "source_record_id": f"s-{i}",
                              "family": "synthetic", "seeds": [3*i, 3*i+1, 3*i+2],
                              "third_audit": {"input": f"input-{i}",
                                              "output": f"output-{i}"}})
            decisions.append({"task_id": tid})
        m._original_binding(cases, originals, decisions)
        originals[0]["third_audit"]["output"] = "TAMPERED"
        with self.assertRaises(ValueError):
            m._original_binding(cases, originals, decisions)

    def test_redacted_pairs_accept_shape_and_block_sensitive_fields(self):
        pair = {
            "schema_version": "opportunity-paired-evidence-v1",
            "task_id": "t-"+"a"*64, "audit_commitment_sha256": "b"*64,
            "trials": {"OFF": {"primitive_calls": 5}, "ON": {"primitive_calls": 4}},
            "classification": "both_correct_on_cheaper",
            "unique_better_action": "ON", "policies": {"B1": {"action": "ON"}},
            "both_arms_audited": True, "best_of_two_correct": True}
        self.assertEqual(m._redacted_only(pair), pair)
        pair["trials"]["ON"]["third_audit"] = {"input": "SYNTHETIC"}
        with self.assertRaises(ValueError):
            m._redacted_only(pair)

    def test_bad_private_parent_permissions_fail(self):
        with TemporaryDirectory() as tmp:
            bad = Path(tmp)/"unsafe"
            bad.mkdir(mode=0o700)
            private = bad / "private"
            private.mkdir(mode=0o700)
            bad.chmod(0o777)
            with self.assertRaises(ValueError):
                with m._private_root(private):
                    pass


if __name__ == "__main__":
    unittest.main()

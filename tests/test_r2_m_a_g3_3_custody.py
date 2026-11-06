"""G3-3 synthetic-only custody fault injection; no science, no actual GitHub push."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest

from packages.r2_m_a.contracts import Slot, USE_POINTS, expected_slot_set
from packages.r2_m_a.evidence_ledger import (EvidenceLedger, ZERO, _write_once,
                                              canonical)
from packages.r2_m_a.evaluator_gate import (G4_ACTUAL_PATH_APPROVED,
    G5_ORDER_APPROVED, G6_EXECUTION_AND_SCORE_APPROVED,
    inspect_prescore_readiness, require_score_gate)
from packages.r2_m_a.g4_dossier import REQUIRED, generate_g4_dossier
from packages.r2_m_a.remote_custody import (CustodyBlocked, RemoteReceipt,
                                             GitHubRemoteCustody)

H = "a" * 64


class FakeRemote:
    """Fault-injectable *test* API. Never substitute for a real GitHub receipt."""
    def __init__(self):
        self.objects = {}
        self.n = 0
        self.fail_push = False
        self.fail_readback = False

    def commit_and_verify(self, source, content_sha256):
        if self.fail_push:
            raise CustodyBlocked("RUN_BLOCK: synthetic lost push")
        data = Path(source).read_bytes()
        assert sha256(data).hexdigest() == content_sha256
        self.n += 1
        commit = f"{self.n:040x}"
        receipt = RemoteReceipt(commit, "refs/heads/audit/r2ma/test-branch",
                                "audit/r2ma/run/" + Path(source).name,
                                content_sha256,
                                "https://github.com/ryonakayama234/DekaSugi")
        self.objects[commit] = data
        return receipt

    def verify_receipt(self, receipt, source):
        if self.fail_readback or self.objects.get(receipt.commit_sha) != Path(source).read_bytes():
            raise CustodyBlocked("RUN_BLOCK: synthetic remote readback mismatch")
        if sha256(self.objects[receipt.commit_sha]).hexdigest() != receipt.content_sha256:
            raise CustodyBlocked("RUN_BLOCK: synthetic digest mismatch")


class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        parent = Path(self.tmp.name) / "audit" / "r2ma"
        parent.mkdir(parents=True)
        self.root = parent / "run"
        self.ledger = EvidenceLedger.create(self.root, engineering_only=True)
        self.remote = FakeRemote()
        self.slot = Slot("0000", USE_POINTS[0], "F00")

    def tearDown(self):
        self.tmp.cleanup()

    def precommit(self, law="0000", remote=None):
        return self.ledger.precommit_q(law, history_sha256=H,
            legal_sha256="b"*64, deadline=20, committed_at=10,
            method_sha256="c"*64, policy_sha256="d"*64,
            remote=remote if remote is not None else self.remote)

    def q_ready(self, law="0000"):
        self.precommit(law)
        self.ledger.synthetic_answer_gate(
            law, remote=self.remote, answer=lambda: {"public_bit": 1}, now=11)
        self.ledger.lock_snapshot(law, snapshot_sha256="e"*64)

    def test_448_planned_not_448_executed_and_missing_visible(self):
        self.assertEqual(len(expected_slot_set()), 448)
        report = self.ledger.manifest()
        self.assertEqual(report["expected_slot_count"], 448)
        self.assertEqual(report["counts"], {"NOT_RUN": 448})
        self.assertFalse(report["eligible_for_future_score"])
        self.assertEqual(report["g5_order"], "NOT_FIXED")
        self.assertEqual(len(report["slots"]), 448)
        self.assertTrue(report["enumeration_not_execution_order"])
        self.q_ready()
        self.ledger.start_slot(self.slot, engineering_only=True)
        report = self.ledger.manifest()
        self.assertEqual(report["counts"], {"STARTED_MISSING": 1, "NOT_RUN": 447})
        self.assertFalse(report["eligible_for_future_score"])
        self.assertIn("started without terminal", str(report["slots"]))
        self.ledger.finish_slot(self.slot, status="RESOURCE_STOP",
                                missing_reason="CPU watchdog killed child")
        report = self.ledger.manifest()
        self.assertEqual(report["counts"], {"RESOURCE_STOP": 1, "NOT_RUN": 447})
        self.assertEqual(report["q_remote_verified_laws"], 1)

    def test_exclusive_run_and_prereg_slot_lock(self):
        with self.assertRaisesRegex(CustodyBlocked, "existing"):
            EvidenceLedger.create(self.root, engineering_only=True)
        with self.assertRaisesRegex(CustodyBlocked, "unauthorized"):
            EvidenceLedger.create(self.root.parent / "other", engineering_only=False)
        self.assertTrue((self.root / "expected-slots.json").exists())
        path = self.root / "expected-slots.json"
        with self.assertRaises(FileExistsError):
            path.open("xb")
        path.chmod(0o600)
        info = json.loads(path.read_bytes())
        info["slots"] = info["slots"][:-1]
        path.write_bytes(canonical(info))
        with self.assertRaisesRegex(CustodyBlocked, "slot set changed"):
            self.ledger.events()

    def test_q_remote_push_failure_blocks_answer_and_retry(self):
        called = []
        with self.assertRaisesRegex(CustodyBlocked, "unverified"):
            self.ledger.synthetic_answer_gate(
                "0000", remote=self.remote, answer=lambda: called.append(1), now=11)
        self.remote.fail_push = True
        with self.assertRaisesRegex(CustodyBlocked, "lost push"):
            self.precommit()
        self.assertEqual(called, [])
        self.assertEqual([e["kind"] for e in self.ledger.events()], ["Q_PRECOMMIT"])
        with self.assertRaisesRegex(CustodyBlocked, "duplicate"):
            self.precommit()

    def test_q_readback_loss_prevents_answer(self):
        self.precommit()
        self.remote.fail_readback = True
        called = []
        with self.assertRaisesRegex(CustodyBlocked, "readback"):
            self.ledger.synthetic_answer_gate(
                "0000", remote=self.remote, answer=lambda: called.append(1), now=11)
        self.assertEqual(called, [])
        self.assertFalse(any(e["kind"] == "Q_ANSWER" for e in self.ledger.events()))

    def test_q_chronology_one_shot_and_deadline(self):
        with self.assertRaisesRegex(CustodyBlocked, "early|before"):
            self.ledger.lock_snapshot("0000", snapshot_sha256=H)
        self.precommit()
        with self.assertRaisesRegex(CustodyBlocked, "expired"):
            self.ledger.synthetic_answer_gate("0000", remote=self.remote,
                                              answer=lambda: 1, now=21)
        self.assertEqual(self.ledger.synthetic_answer_gate(
            "0000", remote=self.remote, answer=lambda: {"public_bit": 0},
            now=20), {"public_bit": 0})
        with self.assertRaisesRegex(CustodyBlocked, "already used"):
            self.ledger.synthetic_answer_gate("0000", remote=self.remote,
                                              answer=lambda: 1, now=20)
        with self.assertRaisesRegex(CustodyBlocked, "duplicate"):
            self.ledger.lock_snapshot("0000", snapshot_sha256=H)
            self.ledger.lock_snapshot("0000", snapshot_sha256=H)
        self.assertEqual([e["kind"] for e in self.ledger.events()],
                         ["Q_PRECOMMIT", "Q_REMOTE", "Q_ANSWER", "SNAPSHOT_LOCK"])

    def test_q_invalid_input_rejected_before_remote_or_answer(self):
        with self.assertRaisesRegex(CustodyBlocked, "expired"):
            self.ledger.precommit_q("0000", history_sha256=H,
                legal_sha256=H, deadline=1, committed_at=2,
                method_sha256=H, policy_sha256=H, remote=self.remote)
        for law in ("11111", "../../oops", None):
            with self.assertRaisesRegex(CustodyBlocked, "unknown"):
                self.precommit(law)
        with self.assertRaisesRegex(CustodyBlocked, "SHA256"):
            self.ledger.precommit_q("0000", history_sha256="x",
                legal_sha256=H, deadline=20, committed_at=10,
                method_sha256=H, policy_sha256=H, remote=self.remote)
        self.assertEqual(self.ledger.events(), ())

    def test_duplicate_slot_start_finish_and_failures_are_immutable(self):
        self.q_ready()
        with self.assertRaisesRegex(CustodyBlocked, "unauthorized"):
            self.ledger.start_slot(self.slot, engineering_only=False)
        self.ledger.start_slot(self.slot, engineering_only=True)
        with self.assertRaisesRegex(CustodyBlocked, "duplicate"):
            self.ledger.start_slot(self.slot, engineering_only=True)
        with self.assertRaisesRegex(CustodyBlocked, "reason"):
            self.ledger.finish_slot(self.slot, status="INVALID")
        with self.assertRaisesRegex(CustodyBlocked, "trace needs"):
            self.ledger.finish_slot(self.slot, status="TRACE_PRESENT")
        self.ledger.finish_slot(self.slot, status="INVALID",
                                missing_reason="corrupt stdout")
        with self.assertRaisesRegex(CustodyBlocked, "duplicate"):
            self.ledger.finish_slot(self.slot, status="TRACE_PRESENT",
                                    trace_sha256=H, raw_receipt_sha256=H)
        self.assertEqual(self.ledger.manifest()["counts"],
                         {"INVALID": 1, "NOT_RUN": 447})

    def test_ordered_hash_chain_rejects_mutation_deletion_swap_truncation(self):
        self.q_ready()
        raw = self.ledger.journal.read_bytes()
        self.assertEqual(len(self.ledger.events()), 4)
        for mutated in (
            raw.replace(b"Q_REMOTE", b"Q_REPLACED"),
            b"".join(raw.splitlines(keepends=True)[1:]),
            b"".join([raw.splitlines(keepends=True)[1],
                      raw.splitlines(keepends=True)[0],
                      *raw.splitlines(keepends=True)[2:]]),
            raw[:-1],
            raw + b"\xff\n",
            raw + b'{"value":NaN}\n',
        ):
            with self.subTest(mutated=mutated[:22]):
                self.ledger.journal.write_bytes(mutated)
                with self.assertRaises(CustodyBlocked):
                    self.ledger.events()
        self.ledger.journal.write_bytes(raw)
        self.assertEqual(len(self.ledger.events()), 4)
        seqs = [e["seq"] for e in self.ledger.events()]
        self.assertEqual(seqs, list(range(1, 5)))
        self.assertEqual(self.ledger.events()[0]["prev_sha256"], ZERO)

    def test_remote_pre_score_has_missingness_and_never_opens_score(self):
        self.q_ready()
        self.ledger.start_slot(self.slot, engineering_only=True)
        self.ledger.finish_slot(self.slot, status="UNMEASURED",
                                missing_reason="wait4 absent")
        receipt = self.ledger.seal_prescore(self.remote)
        self.assertIs(type(receipt), RemoteReceipt)
        manifest = self.ledger.assert_prescore_remote(self.remote)
        self.assertEqual(manifest["counts"],
                         {"UNMEASURED": 1, "NOT_RUN": 447})
        with self.assertRaisesRegex(CustodyBlocked, "incomplete"):
            inspect_prescore_readiness(self.ledger, remote=self.remote)
        for kwargs in ({}, {"owner_approval": True},
                       {"owner_approval": {"g4": True, "g5": True, "g6": True}}):
            with self.assertRaisesRegex(CustodyBlocked, "not authorized"):
                require_score_gate(self.ledger, remote=self.remote, **kwargs)
        self.assertFalse(G4_ACTUAL_PATH_APPROVED)
        self.assertFalse(G5_ORDER_APPROVED)
        self.assertFalse(G6_EXECUTION_AND_SCORE_APPROVED)
        with self.assertRaisesRegex(CustodyBlocked, "freeze"):
            self.ledger.start_slot(Slot("0000", USE_POINTS[1], "F10"),
                                   engineering_only=True)
        with self.assertRaisesRegex(CustodyBlocked, "duplicate"):
            self.ledger.seal_prescore(self.remote)

    def test_pre_score_push_lost_is_stop_not_permission(self):
        self.q_ready()
        self.remote.fail_push = True
        with self.assertRaisesRegex(CustodyBlocked, "lost push"):
            self.ledger.seal_prescore(self.remote)
        self.assertEqual(self.ledger.events()[-1]["kind"], "PRE_SCORE_LOCAL")
        with self.assertRaisesRegex(CustodyBlocked, "absent"):
            self.ledger.assert_prescore_remote(self.remote)
        with self.assertRaisesRegex(CustodyBlocked, "freeze"):
            self.ledger.start_slot(self.slot, engineering_only=True)

    def test_pre_score_content_and_remote_integrity(self):
        self.q_ready()
        self.ledger.seal_prescore(self.remote)
        raw_path = self.root / "receipts" / "pre-score-manifest.json"
        with self.assertRaisesRegex(CustodyBlocked, "immutable artifact"):
            _write_once(raw_path, b"overwrite")
        self.remote.fail_readback = True
        with self.assertRaisesRegex(CustodyBlocked, "readback"):
            self.ledger.assert_prescore_remote(self.remote)
        self.remote.fail_readback = False
        self.remote.objects[next(reversed(self.remote.objects))] = b"forged remote"
        with self.assertRaisesRegex(CustodyBlocked, "readback"):
            self.ledger.assert_prescore_remote(self.remote)

    def test_prescore_journal_rewrite_and_q_loss_rejected(self):
        self.q_ready()
        self.ledger.seal_prescore(self.remote)
        self.assertEqual(self.ledger.assert_prescore_remote(self.remote)
                         ["counts"], {"NOT_RUN": 448})
        raw = self.ledger.journal.read_bytes()
        self.ledger.journal.write_bytes(raw.splitlines(keepends=True)[0])
        with self.assertRaises(CustodyBlocked):
            self.ledger.assert_prescore_remote(self.remote)
        self.ledger.journal.write_bytes(raw)
        self.remote.objects["0"*39 + "1"] = b"forged"
        with self.assertRaisesRegex(CustodyBlocked, "readback"):
            self.ledger.assert_prescore_remote(self.remote)

    def test_dossier_is_template_not_audit_and_exclusive(self):
        dest = Path(self.tmp.name) / "g4-scaffold"
        result = generate_g4_dossier(dest, target_head="f"*40,
                                     engineering_only=True)
        self.assertEqual(set(result), set(REQUIRED))
        for name in REQUIRED:
            raw = (dest / name).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), result[name])
            self.assertIn(b"NOT_AUDITED", raw)
        with self.assertRaisesRegex(CustodyBlocked, "already exists"):
            generate_g4_dossier(dest, target_head="f"*40, engineering_only=True)
        with self.assertRaisesRegex(CustodyBlocked, "exact prospective"):
            generate_g4_dossier(dest.parent / "bad", target_head="short",
                                engineering_only=True)
        self.assertFalse((dest.parent / "bad").exists())


if __name__ == "__main__":
    unittest.main()

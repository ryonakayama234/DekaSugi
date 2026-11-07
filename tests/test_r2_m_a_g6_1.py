"""G6-1 synthetic fault injection: no G6-2, real child, paid Q or scoring."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from packages.r2_m_a.contracts import PAID_Q001
from packages.r2_m_a.g6_order import (G5_BRANCH, G5_COMMIT, G5_SHA256,
                                      G6Blocked, canonical, sha, validate_g5)
from packages.r2_m_a.g6_orchestrator import (G6Orchestrator, make_event, replay,
                                             run_lock, restore_locked_snapshot)
from packages.r2_m_a.g6_measurement import authorize_g6
from packages.r2_m_eng.records import public_evidence_digest
from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource

# Test copy of exact sealed G5 bytes. Do not rewrite the remote G5 original.
SEALED = b'{"generated_by":"supervisor (mechanical computation from the frozen method)","law_order":["1100","1001","0111","0010","0110","1111","1110","0000","1000","1011","0001","1101","0011","0100","0101","1010"],"method":"hash-sort/1","prereg_id":"R2-M-A-20261105-EXHAUSTIVE16-ENGINEERING-PREREG","schema":"r2ma-g5-order/1","seed":"g5-seed-20261107-38aa706d0fe0178e879b311cec217ef7","target_head":"4e8a0c2d68ba431a8446720b314fd205babe2ac3","within_law_order":"manifest-enumeration"}'
TOKEN = "5" * 32


class FakeRemote:
    """Durable synthetic branch shared across independent restarted controllers."""
    def __init__(self):
        self.raw = []
        self.fail_kind = None
        self.ack_lost_after_publish = False

    def load(self):
        return tuple(self.raw)

    def append(self, kind, data, *, expected_tip, g5):
        state = replay(self.load(), g5)
        if state.tip != expected_tip:
            raise G6Blocked("RUN_BLOCK: stale CAS")
        event = make_event(len(self.raw) + 1, kind, data, state.tip)
        replay((*self.load(), canonical(event)), g5)
        if self.fail_kind == kind and not self.ack_lost_after_publish:
            raise G6Blocked("RUN_BLOCK: push result unknown")
        self.raw.append(canonical(event))
        if self.fail_kind == kind:
            raise G6Blocked("RUN_BLOCK: push acknowledged nowhere")
        return event


class G61Tests(unittest.TestCase):
    def setUp(self):
        self.g5 = validate_g5(SEALED, pinned_commit=G5_COMMIT,
                              remote_ref=G5_BRANCH, pinned_readback=True)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = FakeRemote()
        self.orch = self.fresh()

    def fresh(self):
        return G6Orchestrator(self.remote, self.g5, self.root)

    def _public_fixture(self):
        gateway = PublicGateway(SyntheticPrivateSource((1, 0, 1, 0)),
                                opened_at=5, expires_at=20)
        state = gateway.public_state(now=6)
        commitment = gateway.precommit(PAID_Q001,
                                      expected_legal_digest=state["legal_digest"],
                                      prediction=None, now=6)
        intent = {"history_sha256": public_evidence_digest(state["observations"]),
                  "legal_sha256": state["legal_digest"], "point": list(PAID_Q001),
                  "paid_budget_remaining": 1, "deadline": 20, "committed_at": 6,
                  "method_sha256": "a" * 64, "policy_sha256": "b" * 64,
                  "public_initial_count": 3, "commitment_sha256": commitment}
        return gateway, intent, commitment

    def ready_after_lock(self):
        gateway, intent, commitment = self._public_fixture()
        self.orch.precommit_synthetic("1100", intent)
        gateway.answer(PAID_Q001, precommit=commitment, now=7)
        self.orch.record_synthetic_q("1100", gateway.public_state(now=7)["observations"],
                                     gateway.public_journal(), 20)
        self.orch.snapshot_synthetic("1100", token=TOKEN)
        return self.fresh()

    def test_g5_order_immutable_expansion_448(self):
        self.assertEqual(len(SEALED), 473)
        self.assertEqual(sha(SEALED), G5_SHA256)
        self.assertEqual(len(self.g5.ordered), 448)
        self.assertNotEqual(self.g5.expanded_sha256, G5_SHA256)
        self.assertEqual([s.point for s in self.g5.ordered[:7]], [(0, 1, 1)] * 7)
        self.assertEqual([s.arm for s in self.g5.ordered[:7]],
                         sorted(s.arm for s in self.g5.ordered[:7]))
        self.assertEqual(self.g5.ordered[28].law_id, "1001")
        self.assertEqual([s.point for s in self.g5.ordered[7:14]], [(1, 0, 1)] * 7)
        self.assertEqual(run_lock(self.g5)["rss_bytes_cap"], 512_000_000)
        self.assertFalse(run_lock(self.g5)["retry"])

    def test_g5_tampered_order_pin_readback_or_bytes_blocks(self):
        obj = json.loads(SEALED)
        obj["law_order"][0], obj["law_order"][1] = obj["law_order"][1], obj["law_order"][0]
        wrong = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
        for raw, pin, readback in ((wrong, G5_COMMIT, True),
                                   (SEALED, "0" * 40, True),
                                   (SEALED, G5_COMMIT, False),
                                   (SEALED + b"\n", G5_COMMIT, True)):
            with self.subTest(raw=raw[:12], pin=pin, readback=readback):
                with self.assertRaisesRegex(G6Blocked, "RUN_BLOCK"):
                    validate_g5(raw, pinned_commit=pin, remote_ref=G5_BRANCH,
                                pinned_readback=readback)

    def test_remote_lock_and_reservation_are_write_once(self):
        self.orch.initialize()
        with self.assertRaisesRegex(G6Blocked, "run-lock"):
            self.fresh().initialize()
        fresh = self.ready_after_lock()
        count = []
        def spawn(req):
            count.append(req)
            self.assertTrue(req.snapshot_path.endswith("snapshot-" + TOKEN + ".json"))
            self.assertTrue(req.trace_path.endswith("trace-" + "6" * 32 + ".json"))
            self.assertNotIn("1100", req.snapshot_path)
            self.assertNotIn("F00", req.trace_path)
            return {"status": "UNMEASURED", "receipt_sha256": "c" * 64}
        fresh.run_synthetic_slot(0, trace_token="6" * 32, fake_spawn=spawn)
        with self.assertRaisesRegex(G6Blocked, "RUN_BLOCK"):
            self.fresh().run_synthetic_slot(0, trace_token="7" * 32, fake_spawn=spawn)
        self.assertEqual(len(count), 1)
        self.assertEqual(self.fresh().state().slot_status(0), "FINISHED")

    def test_push_unknown_prevents_spawn(self):
        self.orch.initialize()
        fresh = self.ready_after_lock()
        self.remote.fail_kind = "SLOT_RESERVED"
        attempted = []
        with self.assertRaisesRegex(G6Blocked, "RUN_BLOCK"):
            fresh.run_synthetic_slot(0, trace_token="6" * 32,
                                     fake_spawn=lambda r: attempted.append(r))
        self.assertFalse(attempted)
        self.remote.ack_lost_after_publish = True
        with self.assertRaisesRegex(G6Blocked, "RUN_BLOCK"):
            self.fresh().run_synthetic_slot(0, trace_token="7" * 32,
                                            fake_spawn=lambda r: attempted.append(r))
        self.assertFalse(attempted)

    def test_forced_exit_after_reservation_before_spawn(self):
        self.orch.initialize()
        fresh = self.ready_after_lock()
        self.remote.fail_kind = "SLOT_RESERVED"
        self.remote.ack_lost_after_publish = True
        attempted = []
        with self.assertRaises(G6Blocked):
            fresh.run_synthetic_slot(0, trace_token="6" * 32,
                                     fake_spawn=lambda r: attempted.append(r))
        self.assertFalse(attempted)
        self.remote.fail_kind = None
        with self.assertRaisesRegex(G6Blocked, "STARTED_MISSING"):
            self.fresh().resume()
        self.assertEqual(self.fresh().state().slot_status(0), "STARTED_MISSING")
        with self.assertRaises(G6Blocked):
            self.fresh().run_synthetic_slot(0, trace_token="8" * 32,
                                            fake_spawn=lambda r: attempted.append(r))
        self.assertFalse(attempted)

    def test_forced_exit_after_spawn_before_terminal(self):
        self.orch.initialize()
        fresh = self.ready_after_lock()
        count = []
        def killed_child(req):
            count.append(1)
            raise SystemExit("synthetic forced termination")
        with self.assertRaises(SystemExit):
            fresh.run_synthetic_slot(0, trace_token="6" * 32,
                                     fake_spawn=killed_child)
        with self.assertRaisesRegex(G6Blocked, "STARTED_MISSING"):
            self.fresh().resume()
        with self.assertRaises(G6Blocked):
            self.fresh().run_synthetic_slot(0, trace_token="7" * 32,
                                           fake_spawn=killed_child)
        self.assertEqual(len(count), 1)

    def test_paid_q_unknown_window_stops_entire_run_no_requery(self):
        self.orch.initialize()
        _, intent, _ = self._public_fixture()
        self.orch.precommit_synthetic("1100", intent)
        with self.assertRaisesRegex(G6Blocked, "STOPPED_Q_UNKNOWN"):
            self.fresh().resume()
        self.assertIn("STOPPED_Q_UNKNOWN", self.fresh().state().stages["1100"])
        with self.assertRaises(G6Blocked):
            self.fresh().record_synthetic_q("1100", (), (), 20)
        with self.assertRaises(G6Blocked):
            self.fresh().precommit_synthetic("1100", intent)

    def test_precommit_push_unknown_never_precommits_again(self):
        self.orch.initialize()
        _, intent, _ = self._public_fixture()
        self.remote.fail_kind = "Q_PRECOMMIT"
        with self.assertRaises(G6Blocked):
            self.orch.precommit_synthetic("1100", intent)
        self.remote.fail_kind = None
        with self.assertRaisesRegex(G6Blocked, "STOPPED_PRECOMMIT_UNKNOWN"):
            self.fresh().resume()
        with self.assertRaises(G6Blocked):
            self.fresh().precommit_synthetic("1100", intent)

    def test_snapshot_must_regenerate_from_pinned_public4(self):
        self.orch.initialize()
        self.ready_after_lock()
        state = self.fresh().state()
        answer = next(x["data"] for x in state.events if x["kind"] == "Q_ANSWER")
        lock = next(x["data"] for x in state.events if x["kind"] == "SNAPSHOT_LOCK")
        self.assertTrue(restore_locked_snapshot(answer, lock, self.root).is_file())
        path = self.root / ("snapshot-" + TOKEN + ".json")
        os.chmod(path, 0o600)  # deliberate adversarial chmod of immutable fixture
        path.write_bytes(b"tampered")
        with self.assertRaisesRegex(G6Blocked, "cached snapshot"):
            restore_locked_snapshot(answer, lock, self.root)

    def test_replay_rejects_reorder_duplicate_and_modified_chain(self):
        self.orch.initialize()
        fresh = self.ready_after_lock()
        state = fresh.state()
        event = make_event(len(state.events) + 1, "SLOT_RESERVED",
                           {"ordinal": 1, "slot": self.g5.ordered[1].as_dict(),
                            "journal_tip_before": state.tip,
                            "run_lock_sha256": sha(canonical(run_lock(self.g5)))},
                           state.tip)
        with self.assertRaisesRegex(G6Blocked, "RUN_BLOCK"):
            replay((*self.remote.load(), canonical(event)), self.g5)
        bad = bytearray(self.remote.raw[0])
        bad[-4] ^= 1
        with self.assertRaises(G6Blocked):
            replay((bytes(bad), *self.remote.load()[1:]), self.g5)

    def test_law_root_checkpoint_exactly_once_before_next_law(self):
        self.orch.initialize()
        controller = self.ready_after_lock()
        terminal = {"status": "UNMEASURED", "receipt_sha256": "c" * 64}
        # Exactly one completed law = four USE points times seven arms.
        for ordinal in range(28):
            controller.run_synthetic_slot(
                ordinal, trace_token=f"{ordinal + 100:032x}",
                fake_spawn=lambda request: terminal)
        _, intent, _ = self._public_fixture()
        with self.assertRaisesRegex(G6Blocked, "checkpoint"):
            controller.precommit_synthetic("1001", intent)
        controller.checkpoint_law("1100")
        with self.assertRaisesRegex(G6Blocked, "checkpoint"):
            controller.checkpoint_law("1100")
        controller.precommit_synthetic("1001", intent)
        self.assertIn("Q_PRECOMMIT", self.fresh().state().stages["1001"])

    def test_production_no_owner_GO_blocks_before_reservation(self):
        self.orch.initialize()
        fresh = self.ready_after_lock()
        before = fresh.state().tip
        with self.assertRaisesRegex(G6Blocked, "Owner GO"):
            fresh.run_production_slot(0, trace_token="6" * 32,
                                      owner_go=True, measurement_executor=lambda x: None)
        with self.assertRaisesRegex(G6Blocked, "Owner GO"):
            authorize_g6(self.g5, run_lock(self.g5), None)
        self.assertEqual(self.fresh().state().tip, before)


if __name__ == "__main__":
    unittest.main()

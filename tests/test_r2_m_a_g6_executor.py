"""G6 executor/scope fault injection. No GO, no remote append, no real study."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
import json
import os
import sys
import tempfile
import unittest

from packages.r2_m_a.contracts import ChildRequest, PAID_Q001, RSS_BYTES_CAP
from packages.r2_m_a.g6_order import (
    G5_BRANCH, G5_COMMIT, G6Blocked, canonical, sha, validate_g5,
)
from packages.r2_m_a.g6_orchestrator import (
    G6Orchestrator, GitRunJournal, RehearsalGitRunJournal,
    RUN_BRANCH, ROOT, make_event, replay, run_lock,
)
from packages.r2_m_a.g6_scope import (
    REHEARSAL_BRANCH, REHEARSAL_ROOT, RehearsalPermit, RehearsalGOReference,
    authorize_rehearsal_g6, rehearsal_run_lock,
)
from packages.r2_m_a.g6_measurement import (
    ProductionPermit, OwnerGOReference, MeasurementReceipt, authorize_g6,
)
from packages.r2_m_a.g6_q import (
    G6QStage, QArtifactFiles, FROZEN_PRODUCTION_METHOD, FROZEN_PRODUCTION_POLICY,
)
from packages.r2_m_eng.records import public_evidence_digest
from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource
from tests.test_r2_m_a_g6_1 import SEALED


class Backend:
    """Reversible in-memory test fixture; NEVER a remote science journal."""
    def __init__(self, scope):
        self.scope, self.raw = scope, []
        self.fail_kind = None

    def load(self):
        return tuple(self.raw)

    def append(self, kind, data, *, expected_tip, g5):
        state = replay(self.load(), g5, scope=self.scope)
        if state.tip != expected_tip:
            raise G6Blocked("RUN_BLOCK: CAS")
        entry = make_event(len(self.raw) + 1, kind, data, state.tip)
        replay((*self.load(), canonical(entry)), g5, scope=self.scope)
        if self.fail_kind == kind:
            raise G6Blocked("RUN_BLOCK: remote write uncertainty")
        self.raw.append(canonical(entry))
        return entry


def fake_supervisor(status="TRACE_PRESENT", *, engineering=False):
    return {
        "engineering_only": engineering,
        "status": status,
        "reason": None if status == "TRACE_PRESENT" else status,
        "exit_code": 0 if status == "TRACE_PRESENT" else 1,
        "reaped": True,
        "trace_sha256": "a" * 64 if status == "TRACE_PRESENT" else None,
        "stdout_sha256": "b" * 64,
        "stderr_sha256": "c" * 64,
        "raw_cost": {
            "process_total": {
                "monotonic_wall_seconds": .025,
                "wait4_cpu_seconds": None if status == "UNMEASURED" else .015,
                "wait4_peak_rss_bytes": (
                    RSS_BYTES_CAP if status == "BOUNDARY_REVIEW" else 1_024_000),
            },
            "cgroup": {"memory_peak_bytes": 1_200_000},
        },
    }


class G6ExecutorScopeTests(unittest.TestCase):
    def setUp(self):
        self.g5 = validate_g5(
            SEALED, pinned_commit=G5_COMMIT, remote_ref=G5_BRANCH,
            pinned_readback=True)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def orch(self, scope):
        # Exact journal runtime class with mock methods; no git/network calls.
        journal_class = (GitRunJournal if scope == "production"
                         else RehearsalGitRunJournal)
        remote = journal_class.__new__(journal_class)
        backend = Backend(scope)
        remote.load = backend.load
        remote.append = backend.append
        remote.pinned_g5 = lambda ref, commit, path: SEALED
        session = Path(tempfile.mkdtemp(prefix="scope-", dir=self.root))
        remote.root = session
        remote.ref = RUN_BRANCH if scope == "production" else REHEARSAL_BRANCH
        directory = (session if scope == "production"
                     else session / REHEARSAL_ROOT / "artifacts" / "fixture")
        directory.mkdir(parents=True, exist_ok=True)
        orch = G6Orchestrator(remote, self.g5, directory)
        permit = (ProductionPermit if scope == "production" else RehearsalPermit)(
            sha(canonical(orch.lock_data)), self.g5.expanded_sha256, 77)
        module = ("packages.r2_m_a.g6_orchestrator.authorize_g6"
                  if scope == "production"
                  else "packages.r2_m_a.g6_orchestrator.authorize_rehearsal_g6")
        return orch, backend, permit, module

    def initialize_with_fixture(self, orch, permit, auth_module):
        with patch(auth_module, return_value=permit):
            orch.initialize(owner_go=None)

    def ready(self, scope):
        orch, backend, permit, auth_module = self.orch(scope)
        self.initialize_with_fixture(orch, permit, auth_module)
        gateway = PublicGateway(SyntheticPrivateSource((1, 1, 0, 0)),
                                opened_at=5, expires_at=20)
        state = gateway.public_state(now=6)
        commitment = gateway.precommit(
            PAID_Q001, expected_legal_digest=state["legal_digest"],
            prediction=None, now=6)
        intent = {
            "history_sha256": public_evidence_digest(state["observations"]),
            "legal_sha256": state["legal_digest"], "point": list(PAID_Q001),
            "paid_budget_remaining": 1, "deadline": 20,
            "committed_at": 6, "method_sha256": "a" * 64,
            "policy_sha256": "b" * 64,
            "public_initial_count": 3, "commitment_sha256": commitment,
        }
        orch.precommit_synthetic("1100", intent)
        gateway.answer(PAID_Q001, precommit=commitment, now=7)
        orch.record_synthetic_q(
            "1100", gateway.public_state(now=7)["observations"],
            gateway.public_journal(), 20)
        orch.snapshot_synthetic("1100", token="d" * 32)
        return orch, backend, permit, auth_module

    def test_lock_schema_cross_scope_rejection_no_network(self):
        p, r = run_lock(self.g5), rehearsal_run_lock(self.g5)
        self.assertNotEqual(p["schema"], r["schema"])
        self.assertNotEqual(sha(canonical(p)), sha(canonical(r)))
        with self.assertRaisesRegex(G6Blocked, "run-lock"):
            authorize_g6(self.g5, r, OwnerGOReference("f" * 40, 1))
        with self.assertRaisesRegex(G6Blocked, "run-lock"):
            authorize_rehearsal_g6(
                self.g5, p, RehearsalGOReference("f" * 40, 1))
        with self.assertRaisesRegex(G6Blocked, "rehearsal Owner GO"):
            authorize_rehearsal_g6(self.g5, r, OwnerGOReference("f" * 40, 1))
        with self.assertRaisesRegex(G6Blocked, "Owner GO"):
            authorize_g6(self.g5, p, RehearsalGOReference("f" * 40, 1))

    def test_replay_lock_wrong_scope_is_blocked(self):
        orch, backend, permit, name = self.orch("rehearsal")
        self.initialize_with_fixture(orch, permit, name)
        with self.assertRaisesRegex(G6Blocked, "run-lock mismatch"):
            replay(backend.load(), self.g5, scope="production")
        with self.assertRaisesRegex(G6Blocked, "run-lock mismatch"):
            replay((canonical(make_event(
                1, "RUN_LOCK", run_lock(self.g5), "0" * 64)),),
                self.g5, scope="rehearsal")

    def test_remote_scope_ref_and_root_immutable_at_call_time(self):
        for cls, ref, root, scope in (
            (GitRunJournal, RUN_BRANCH, ROOT, "production"),
            (RehearsalGitRunJournal, REHEARSAL_BRANCH, REHEARSAL_ROOT,
             "rehearsal"),
        ):
            obj = cls.__new__(cls)
            obj.ref, obj.journal_root, obj.scope = ref, root, scope
            obj.git = lambda *args, ref=ref: ref
            obj._check_scope()
            obj.ref = REHEARSAL_BRANCH if scope == "production" else RUN_BRANCH
            with self.assertRaisesRegex(G6Blocked, "scope escaped"):
                obj._check_scope()
            obj.ref = ref
            obj.journal_root = ROOT if scope == "rehearsal" else REHEARSAL_ROOT
            with self.assertRaisesRegex(G6Blocked, "scope escaped"):
                obj._check_scope()

    def test_rehearsal_artifact_root_is_strict(self):
        orch, backend, permit, name = self.orch("rehearsal")
        with self.assertRaisesRegex(G6Blocked, "outside dedicated root"):
            G6Orchestrator(orch.remote, self.g5, self.root)

    def test_formal_terminal_states_and_receipt_digests(self):
        statuses = ("TRACE_PRESENT", "INVALID", "RESOURCE_STOP",
                    "RUN_BLOCK", "UNMEASURED", "BOUNDARY_REVIEW")
        for scope in ("production", "rehearsal"):
            for status in statuses:
                with self.subTest(scope=scope, status=status):
                    orch, backend, permit, name = self.ready(scope)
                    def run_supervisor(request, **kwargs):
                        self.assertEqual(kwargs["scope"], scope)
                        self.assertEqual(request.as_dict().keys(), {
                            "snapshot_path", "expected_sha256", "arm", "point",
                            "trace_path",
                        })
                        return fake_supervisor(status)
                    with patch(name, return_value=permit), patch(
                        "packages.r2_m_a.child_supervisor.supervise_formal_child",
                        side_effect=run_supervisor):
                        if scope == "production":
                            result = orch.run_production_slot(
                                0, trace_token="e" * 32, owner_go=None,
                                delegated_cgroup_root="/sys/fs/cgroup")
                        else:
                            result = orch.run_rehearsal_slot(
                                0, trace_token="e" * 32, owner_go=None,
                                delegated_cgroup_root="/sys/fs/cgroup")
                    self.assertEqual(result.finishes[0]["data"]["status"], status)
                    raw = (orch.artifact_dir / ("receipt-" + "e" * 32 + ".json")).read_bytes()
                    self.assertEqual(result.finishes[0]["data"]["receipt_sha256"], sha(raw))
                    self.assertEqual(json.loads(raw)["status"], status)
                    self.assertEqual(result.slot_status(0), "FINISHED")

    def test_post_reservation_crash_is_never_finished_or_respawned(self):
        for scope in ("production", "rehearsal"):
            orch, backend, permit, name = self.ready(scope)
            with patch(name, return_value=permit), patch(
                "packages.r2_m_a.child_supervisor.supervise_formal_child",
                side_effect=SystemExit("forced child crash")) as child:
                with self.assertRaises(SystemExit):
                    if scope == "production":
                        orch.run_production_slot(
                            0, trace_token="e" * 32, delegated_cgroup_root="/fake")
                    else:
                        orch.run_rehearsal_slot(
                            0, trace_token="e" * 32, delegated_cgroup_root="/fake")
            self.assertEqual(child.call_count, 1)
            self.assertEqual(orch.state().slot_status(0), "RESERVED")
            with self.assertRaisesRegex(G6Blocked, "STARTED_MISSING"):
                orch.resume()
            self.assertEqual(orch.state().slot_status(0), "STARTED_MISSING")
            self.assertNotIn(0, orch.state().finishes)

    def test_post_reservation_restore_fault_preserves_missing(self):
        orch, backend, permit, name = self.ready("production")
        # _reserve calls restore only after it has remotely sealed the slot.
        with patch(name, return_value=permit), patch(
            "packages.r2_m_a.g6_orchestrator.restore_locked_snapshot",
            side_effect=OSError("disk disappeared")):
            with self.assertRaises(OSError):
                orch.run_production_slot(
                    0, trace_token="f" * 32, delegated_cgroup_root="/fake")
        self.assertEqual(orch.state().slot_status(0), "RESERVED")
        with self.assertRaisesRegex(G6Blocked, "STARTED_MISSING"):
            orch.resume()

    def test_wrong_scope_permit_blocks_before_reservation(self):
        for scope in ("production", "rehearsal"):
            orch, backend, permit, name = self.ready(scope)
            wrong = (RehearsalPermit if scope == "production" else ProductionPermit)(
                permit.lock_sha256, self.g5.expanded_sha256, 77)
            with patch(name, return_value=wrong):
                with self.assertRaisesRegex(G6Blocked, "permit crossed scope"):
                    if scope == "production":
                        orch.run_production_slot(
                            0, trace_token="e" * 32, delegated_cgroup_root="/fake")
                    else:
                        orch.run_rehearsal_slot(
                            0, trace_token="e" * 32, delegated_cgroup_root="/fake")
            self.assertNotIn(0, orch.state().reservations)

    def test_injected_executor_or_missing_cgroup_blocks_before_reservation(self):
        orch, _, permit, name = self.ready("production")
        with patch(name, return_value=permit):
            with self.assertRaisesRegex(G6Blocked, "injected production executor"):
                orch.run_production_slot(
                    0, trace_token="e" * 32,
                    measurement_executor=lambda _: fake_supervisor())
            with self.assertRaisesRegex(G6Blocked, "delegated cgroup"):
                orch.run_production_slot(0, trace_token="e" * 32)
        self.assertFalse(orch.state().reservations)

    def test_no_production_digest_source_is_invented(self):
        self.assertIsNone(FROZEN_PRODUCTION_METHOD)
        self.assertIsNone(FROZEN_PRODUCTION_POLICY)
        orch, _, permit, name = self.orch("production")
        self.initialize_with_fixture(orch, permit, name)
        files = QArtifactFiles(Path(__file__), Path(__file__).resolve().parent /
                               "test_r2_m_a_g6_1.py")
        with self.assertRaisesRegex(G6Blocked, "unresolved"):
            G6QStage(orch).precommit(
                "1100", PublicGateway(
                    SyntheticPrivateSource((1, 1, 0, 0)), opened_at=5, expires_at=20),
                now=6, artifacts=files)
        self.assertEqual(len(orch.state().events), 1)

    def test_rehearsal_q_uses_real_gateway_precommit_and_public4(self):
        orch, _, permit, name = self.orch("rehearsal")
        self.initialize_with_fixture(orch, permit, name)
        files = QArtifactFiles(Path(__file__), Path(__file__).resolve().parent /
                               "test_r2_m_a_g6_1.py")
        gateway = PublicGateway(SyntheticPrivateSource((1, 1, 0, 0)),
                                opened_at=5, expires_at=20)
        q = G6QStage(orch)
        commitment = q.precommit("1100", gateway, now=6, artifacts=files)
        q.record_q("1100", gateway, commitment=commitment, now=7)
        path = q.snapshot("1100", token="d" * 32)
        self.assertTrue(path.is_file())
        self.assertEqual(len(orch.state().events), 5)


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "wait4"),
                     "requires Linux child process")
class G6FormalChildTests(unittest.TestCase):
    def test_formal_child_is_real_fresh_process_with_guard(self):
        from packages.r2_m_a.child_supervisor import (
            CgroupV2Lease, supervise_formal_child,
        )
        from packages.r2_m_a.public_pipeline import (
            SyntheticPrecommitReceipt, prepare_synthetic_snapshot,
        )
        from packages.r2_m_a.g6_order import validate_g5
        g5 = validate_g5(SEALED, pinned_commit=G5_COMMIT,
                         remote_ref=G5_BRANCH, pinned_readback=True)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gw = PublicGateway(SyntheticPrivateSource((1, 1, 0, 0)),
                               opened_at=5, expires_at=20)
            snapshot = prepare_synthetic_snapshot(
                gw, snapshot_path=root / "snapshot.json",
                precommit_at=6, answer_at=7,
                barrier=lambda intent: SyntheticPrecommitReceipt(intent.commitment),
                engineering_only=True)
            request = ChildRequest(
                snapshot.path, snapshot.sha256, "F00", (0, 1, 1),
                str((root / "opaque-trace.json").resolve()))
            class TestOnlyLease:
                initial_events = {"oom": 0, "oom_kill": 0}
                def attach(self, pid):
                    self.pid = pid
                def kill(self):
                    pass
                def cleanup(self):
                    pass
                def memory_observation(self):
                    return 200_000_000, {"oom": 0, "oom_kill": 0}
            with patch.object(CgroupV2Lease, "create", return_value=TestOnlyLease()), patch(
                "packages.r2_m_a.g6_measurement.authorize_g6",
                return_value=ProductionPermit("a" * 64, g5.expanded_sha256, 77)):
                raw = supervise_formal_child(
                    request, delegated_cgroup_root="/test-only",
                    g5=g5, lock=run_lock(g5), owner_go=None,
                    scope="production")
            self.assertEqual(raw["status"], "TRACE_PRESENT", raw)
            self.assertFalse(raw["engineering_only"])
            self.assertEqual(raw["exit_code"], 0)
            self.assertIsNotNone(raw["trace_sha256"])


if __name__ == "__main__":
    unittest.main()

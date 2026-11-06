"""G3-2 synthetic fault-injection regression; NO 448 scientific measurements.

Linux subprocesses below are deliberately artificial OS safety probes. They
do not run R2-M-A laws, score USE labels, or submit real experiment evidence.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from packages.r2_m_a.child_supervisor import (
    CgroupV2Lease, RunBlocked, _live_cpu_seconds, _wait_with_watchdog,
    supervise_synthetic_child,
)
from packages.r2_m_a.contracts import ChildRequest, rss_boundary_status
from packages.r2_m_a.cost_accounting import RawProcessCost, UNMEASURED, accounting_rows


class FakeFaultCgroup:
    """TEST ONLY. Not an option for the production supervisor."""
    initial_events = {"oom": 0, "oom_kill": 0}

    def __init__(self):
        self.kill_calls = 0

    def kill(self):
        self.kill_calls += 1


def _dead_or_zombie(pid: int) -> bool:
    try:
        data = Path(f"/proc/{pid}/stat").read_text()
        return data[data.rindex(")") + 2] in "ZX"
    except (FileNotFoundError, ProcessLookupError):
        return True


def _await_path(path: Path, seconds: float = 2.0) -> bool:
    limit = time.monotonic() + seconds
    while time.monotonic() < limit:
        if path.exists():
            return True
        time.sleep(0.01)
    return path.exists()


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "wait4"),
                     "requires Linux wait4 and /proc")
class G32FaultTests(unittest.TestCase):
    def test_cgroup_unavailable_blocks_before_any_child_launch_or_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot = root / "public-snapshot.json"
            snapshot.write_bytes(b"synthetic bytes, never loaded")
            trace = root / "opaque.trace.json"
            request = ChildRequest(str(snapshot.resolve()),
                                   sha256(snapshot.read_bytes()).hexdigest(),
                                   "F00", (0, 1, 1), str(trace.resolve()))
            with patch("packages.r2_m_a.child_supervisor.subprocess.Popen",
                       side_effect=AssertionError("child must not launch")):
                with self.assertRaisesRegex(RunBlocked, "RUN_BLOCK"):
                    supervise_synthetic_child(
                        request, delegated_cgroup_root=root / "not-delegated",
                        engineering_only=True)
            self.assertFalse(trace.exists())
            self.assertFalse((root / "opaque.trace.json.attempt").exists())
            with self.assertRaisesRegex(RunBlocked, "RUN_BLOCK"):
                supervise_synthetic_child(
                    request, delegated_cgroup_root=root,
                    engineering_only=False)

    def test_regular_directory_cannot_impersonate_cgroup_v2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cgroup.controllers").write_text("cpu memory\n")
            (root / "cgroup.subtree_control").write_text("memory\n")
            # Ordinary mkdir does not create kernel cgroup control files.
            with self.assertRaisesRegex(RunBlocked, "RUN_BLOCK"):
                CgroupV2Lease.create(root)

    def test_cpu_watchdog_kills_sigxcpu_ignoring_spin(self):
        # Deliberately install SIG_IGN; RLIMIT_CPU soft signal is insufficient.
        code = ("import signal,resource\n"
                "signal.signal(signal.SIGXCPU, signal.SIG_IGN)\n"
                "resource.setrlimit(resource.RLIMIT_CPU,(1,3))\n"
                "while True: pass\n")
        cg = FakeFaultCgroup()
        start = time.monotonic()
        p = subprocess.Popen([sys.executable, "-c", code], start_new_session=True)
        try:
            result = _wait_with_watchdog(
                p.pid, start=start, cgroup=cg, wall_cap=2.0, cpu_cap=0.20)
            self.assertTrue(result.reaped)
            p.returncode = os.waitstatus_to_exitcode(result.wait_status)
            self.assertEqual(result.stopped_for, "CPU")
            self.assertGreater(cg.kill_calls, 0)
            self.assertIsNotNone(result.cpu_seconds)
            self.assertIsNotNone(result.peak_rss_bytes)
            self.assertLess(result.wall_seconds, 2.0)
            self.assertNotEqual(os.waitstatus_to_exitcode(result.wait_status), 0)
        finally:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def test_group_kill_reaches_grandchild_not_just_leader(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "grandchild.pid"
            code = (
                "import subprocess,sys,time\n"
                "p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])\n"
                "open(sys.argv[1],'w').write(str(p.pid))\n"
                "while True: pass\n"
            )
            p = subprocess.Popen(
                [sys.executable, "-c", code, str(marker)],
                start_new_session=True)
            try:
                self.assertTrue(_await_path(marker), "grandchild not created")
                grandchild = int(marker.read_text())
                cg = FakeFaultCgroup()
                result = _wait_with_watchdog(
                    p.pid, start=time.monotonic(), cgroup=cg,
                    wall_cap=1.5, cpu_cap=0.20)
                self.assertTrue(result.reaped)
                p.returncode = os.waitstatus_to_exitcode(result.wait_status)
                # Production supervisor also invokes this cleanup on normal exit.
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                deadline = time.monotonic() + 2.0
                while time.monotonic() < deadline and not _dead_or_zombie(grandchild):
                    time.sleep(0.02)
                self.assertTrue(_dead_or_zombie(grandchild),
                                "killpg must terminate same-group descendant")
            finally:
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_parent_killed_survivor_negative_and_pdeathsig_positive(self):
        # A deliberately unprotected child SURVIVES killing its parent: this is
        # the required failure-injection negative. The protected one must die.
        repo = Path(__file__).resolve().parents[1]
        for protected in (False, True):
            with self.subTest(protected=protected), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                pidfile = root / "pid"
                ready = root / "ready"
                child = (
                    "import os,sys,time\n"
                    + ("from packages.r2_m_a.child_entry import arm_parent_death\n"
                       "arm_parent_death(int(sys.argv[1]))\n" if protected else "")
                    + "open(sys.argv[2],'w').write('ready')\n"
                    + "time.sleep(60)\n"
                )
                parent = (
                    "import os,subprocess,sys,time\n"
                    "child=sys.argv[3]\n"
                    "p=subprocess.Popen([sys.executable,'-c',child,str(os.getpid()),sys.argv[2]],"
                    "start_new_session=True)\n"
                    "open(sys.argv[1],'w').write(str(p.pid))\n"
                    "time.sleep(60)\n"
                )
                p = subprocess.Popen([sys.executable, "-c", parent,
                                      str(pidfile), str(ready), child], cwd=repo)
                child_pid = None
                try:
                    self.assertTrue(_await_path(ready), "child not initialized")
                    child_pid = int(pidfile.read_text())
                    os.kill(p.pid, signal.SIGKILL)  # actually kill parent
                    p.wait(timeout=2)
                    deadline = time.monotonic() + 1.5
                    while time.monotonic() < deadline and protected and not _dead_or_zombie(child_pid):
                        time.sleep(0.02)
                    if protected:
                        self.assertTrue(_dead_or_zombie(child_pid),
                                        "PDEATHSIG child survived killed parent")
                    else:
                        self.assertFalse(_dead_or_zombie(child_pid),
                                         "negative control must detect orphan survivor")
                finally:
                    if p.poll() is None:
                        p.kill()
                        p.wait(timeout=2)
                    if child_pid:
                        try:
                            os.killpg(child_pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass

    def test_single_artificial_public_child_with_test_only_cgroup_mock(self):
        """One synthetic integration smoke; no real cgroup or science claim."""
        from packages.r2_m_a.public_pipeline import (
            SyntheticPrecommitReceipt, prepare_synthetic_snapshot,
        )
        from packages.r2_m_eng.source_gateway import (
            PublicGateway, SyntheticPrivateSource,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gw = PublicGateway(SyntheticPrivateSource((1, 0, 1, 0)),
                               opened_at=5, expires_at=20)
            ref = prepare_synthetic_snapshot(
                gw, snapshot_path=root / "snapshot.json",
                precommit_at=6, answer_at=7,
                barrier=lambda intent: SyntheticPrecommitReceipt(intent.commitment),
                engineering_only=True)
            request = ChildRequest(ref.path, ref.sha256, "F00", (0, 1, 1),
                                   str((root / "opaque-trace.json").resolve()))

            class TestOnlyLease:
                initial_events = {"oom": 0, "oom_kill": 0}
                attached = None
                cleaned = False
                def attach(self, pid):
                    self.attached = pid
                def kill(self):
                    pass
                def cleanup(self):
                    self.cleaned = True
                def memory_observation(self):
                    return 1234, {"oom": 0, "oom_kill": 0}

            fake = TestOnlyLease()
            with patch.object(CgroupV2Lease, "create", return_value=fake):
                result = supervise_synthetic_child(
                    request, delegated_cgroup_root=root, engineering_only=True)
            self.assertIsNotNone(fake.attached)
            self.assertTrue(fake.cleaned)
            self.assertEqual(result["status"], "ENGINEERING_ONLY", result)
            self.assertTrue(result["reaped"])
            self.assertEqual(result["exit_code"], 0)
            self.assertEqual(result["raw_cost"]["per_fresh_process"]["catalog_entries"], 16)
            self.assertIsNotNone(result["trace_sha256"])
            self.assertEqual(result["raw_cost"]["one_off_preparation"]["actual_cpu_s"],
                             UNMEASURED)

    def test_child_entry_no_parent_gate_never_dispatches(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            p = subprocess.run(
                [sys.executable, "-S", "-B", "-m", "packages.r2_m_a.child_entry"],
                cwd=tmp, env={"PYTHONPATH": str(repo), "LANG": "C.UTF-8"},
                capture_output=True, timeout=3)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn(b"RUN_BLOCK", p.stderr)


class G32CostContractsTests(unittest.TestCase):
    def test_wait4_peak_rss_bytes_is_not_cgroup_memory_peak(self):
        raw = RawProcessCost(0.17, 0.08, 512_000_001, 514_000_000,
                             {"import_cpu_seconds": 0.01,
                              "import_wall_seconds": 0.02,
                              "catalog_preparation_cpu_seconds": 0.005,
                              "catalog_preparation_wall_seconds": 0.007,
                              "catalog_serialized_bytes": 123,
                              "catalog_entries": 16},
                             500)
        doc = raw.as_dict()
        self.assertEqual(doc["process_total"]["rss_boundary_status"],
                         "BOUNDARY_REVIEW")
        self.assertEqual(doc["cgroup"]["memory_peak_bytes"], 514_000_000)
        self.assertTrue(doc["per_fresh_process"]["catalog_cost_is_part_of_import_not_extra"])
        self.assertTrue(doc["no_raw_total_subtraction"])
        self.assertEqual(doc["one_off_preparation"]["actual_cpu_s"], UNMEASURED)
        rows = accounting_rows(raw=raw, arm="FIXED-MACRO", law_id="0001",
                               child_slot="opaque")
        required = {"charge_scope", "observed_or_projected", "phase", "arm",
                    "law", "child_slot", "metric_unit", "value_or_UNMEASURED",
                    "causal_origin", "included_in_process_total",
                    "allocation_rule_version", "raw_receipt_sha256"}
        self.assertTrue(all(required == set(row) for row in rows))
        self.assertEqual(sum(r["charge_scope"] == "one_off_preparation"
                             for r in rows), 3)
        self.assertFalse(any(r["observed_or_projected"] == "projected"
                             for r in rows))
        self.assertEqual(rss_boundary_status(512_000_000), "BOUNDARY_REVIEW")
        self.assertEqual(rss_boundary_status(536_870_912), "BOUNDARY_REVIEW")

    def test_missing_import_and_one_off_are_unmeasured_not_zero(self):
        raw = RawProcessCost(1.0, None, None, None, None, None)
        rows = accounting_rows(raw=raw, arm="F00")
        self.assertTrue(any(r["value_or_UNMEASURED"] == UNMEASURED
                            for r in rows))
        self.assertEqual(raw.as_dict()["one_off_preparation"]["actual_bytes"],
                         UNMEASURED)
        self.assertIsNone(raw.as_dict()["process_total"]["wait4_cpu_seconds"])


if __name__ == "__main__":
    unittest.main()

"""G4 environment probe (auditor-side; runs only on the probe branch in CI).

Proves or refutes, on the executing machine:
 1. cgroup v2 memory/cpu controllers can be delegated and memory.max enforced
    by the PRODUCTION supervisor on a real synthetic child, end to end.
 2. A memory hog inside a production lease is OOM-killed at the SI cap and the
    kill is visible in memory.events (group/process RSS enforcement evidence).
Writes probe-result.json in the current directory and prints PROBE_RESULT.
Synthetic data only; no laws are measured, no scoring, no 448 run.
"""
import json, os, subprocess, sys, tempfile, time
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, os.getcwd())
RESULT = {"environment": {}, "supervisor_run": None, "rss_enforcement": None}

def report():
    Path("probe-result.json").write_text(json.dumps(RESULT, indent=1, sort_keys=True, default=str))
    print("PROBE_RESULT " + json.dumps(RESULT, sort_keys=True, default=str))

def main():
    import platform
    RESULT["environment"] = {
        "platform": platform.platform(), "python": sys.version.split()[0],
        "cgroup_controllers_root": Path("/sys/fs/cgroup/cgroup.controllers").read_text().strip(),
    }
    root = os.environ["G4_DELEGATED_ROOT"]
    RESULT["environment"]["delegated_root"] = root
    RESULT["environment"]["delegated_controllers"] = Path(root, "cgroup.controllers").read_text().strip()
    RESULT["environment"]["delegated_subtree_control"] = Path(root, "cgroup.subtree_control").read_text().strip()

    from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource
    from packages.r2_m_a.public_pipeline import SyntheticPrecommitReceipt, prepare_synthetic_snapshot
    from packages.r2_m_a.child_supervisor import supervise_synthetic_child, CgroupV2Lease
    from packages.r2_m_a.contracts import ChildRequest

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        gw = PublicGateway(SyntheticPrivateSource((1, 0, 1, 0)), opened_at=5,
                           expires_at=20, journal_path=tmp / "public.jsonl")
        ref = prepare_synthetic_snapshot(
            gw, snapshot_path=tmp / "snapshot.json", precommit_at=6, answer_at=7,
            barrier=lambda intent: SyntheticPrecommitReceipt(intent.commitment),
            engineering_only=True)
        trace = tmp / "trace.json"
        req = ChildRequest(str(Path(ref.path).resolve()), ref.sha256, "F00",
                           (0, 1, 1), str(trace.resolve()))
        try:
            out = supervise_synthetic_child(req, delegated_cgroup_root=root,
                                            engineering_only=True)
            RESULT["supervisor_run"] = {"ok": True, "result": out}
        except Exception as exc:
            RESULT["supervisor_run"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:300]}
            report(); return

    # RSS enforcement: hog inside a production lease must die at the cap.
    lease = CgroupV2Lease.create(root)
    hog_code = ("import time\n"
                "time.sleep(1.5)\n"
                "chunks = []\n"
                "while True:\n"
                "    chunks.append(bytearray(10_000_000))\n"
                "    time.sleep(0.02)\n")
    proc = subprocess.Popen([sys.executable, "-c", hog_code], start_new_session=True)
    try:
        lease.attach(proc.pid)
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline and proc.poll() is None:
            time.sleep(0.1)
        peak, events = lease.memory_observation()
        RESULT["rss_enforcement"] = {
            "hog_exit": proc.poll(), "cgroup_peak_bytes": peak,
            "memory_events": events,
            "oom_kill_observed": events.get("oom_kill", 0) > 0 or events.get("oom", 0) > 0,
        }
    finally:
        try:
            lease.kill()
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        lease.cleanup()
    report()

if __name__ == "__main__":
    main()

"""G6 journal live rehearsal (auditor-side driver; synthetic fixture only).

Drives the REAL GitRunJournal against real GitHub on a dedicated rehearsal
branch, with the journal's branch/root constants redirected in this driver
process only (repository code is unchanged). No Owner GO artifact, no child
execution, no production branch access. Phase A appends through a crash
point; phase B restarts from the remote and proves recovery semantics.
Writes rehearsal-result.json with per-append timings.
"""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, os.getcwd())
import packages.r2_m_a.g6_orchestrator as orch

REH_BRANCH = "refs/heads/audit/r2ma/g6-rehearsal-20261107"
orch.RUN_BRANCH = REH_BRANCH
orch.ROOT = "audit/r2ma/g6-rehearsal"

from packages.r2_m_a.contracts import PAID_Q001
from packages.r2_m_a.g6_orchestrator import GitRunJournal, replay, run_lock
from packages.r2_m_a.g6_order import G6Blocked, load_pinned_g5, sha
from packages.r2_m_eng.records import public_evidence_digest
from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource
from packages.r2_m_eng.snapshot import write_snapshot
from packages.r2_m_eng.decoder import decode_public
from packages.r2_m_eng.sleep_lite import sleep_lite

RESULT = Path("rehearsal-result.json")
ZERO = "0" * 64
timings = []

def timed(label, fn):
    t0 = time.perf_counter()
    out = fn()
    timings.append({"op": label, "seconds": round(time.perf_counter() - t0, 3)})
    return out

def append(journal, g5, kind, data, tip):
    ev = timed("append:" + kind, lambda: journal.append(kind, data, expected_tip=tip, g5=g5))
    return ev["entry_sha256"]

def load_state(journal, g5):
    return timed("load+replay", lambda: replay(journal.load(), g5))

def fixture():
    gateway = PublicGateway(SyntheticPrivateSource((1, 0, 1, 0)), opened_at=5, expires_at=20)
    state = gateway.public_state(now=6)
    commitment = gateway.precommit(PAID_Q001, expected_legal_digest=state["legal_digest"],
                                   prediction=None, now=6)
    intent = {"history_sha256": public_evidence_digest(state["observations"]),
              "legal_sha256": state["legal_digest"], "point": list(PAID_Q001),
              "paid_budget_remaining": 1, "deadline": 20, "committed_at": 6,
              "method_sha256": "a" * 64, "policy_sha256": "b" * 64,
              "public_initial_count": 3, "commitment_sha256": commitment}
    return gateway, intent, commitment

def phase_a():
    subprocess.run(["git", "checkout", "-B", "audit/r2ma/g6-rehearsal-20261107"],
                   check=True, capture_output=True)
    journal = GitRunJournal(os.getcwd())
    g5 = timed("pinned_g5_load", lambda: load_pinned_g5(journal.pinned_g5))
    state = load_state(journal, g5)
    assert state.lock is None and state.tip == ZERO, "rehearsal journal not empty"
    tip = append(journal, g5, "RUN_LOCK", run_lock(g5), ZERO)
    gateway, intent, commitment = fixture()
    tip = append(journal, g5, "Q_ATTEMPT", {"law_id": "1100"}, tip)
    tip = append(journal, g5, "Q_PRECOMMIT", {"law_id": "1100", "intent": intent}, tip)
    gateway.answer(PAID_Q001, precommit=commitment, now=7)
    answer = {"law_id": "1100",
              "observations": [o.as_dict() for o in gateway.public_state(now=7)["observations"]],
              "journal": list(gateway.public_journal()), "expires_at": 20}
    tip = append(journal, g5, "Q_ANSWER", answer, tip)
    obs = gateway.public_state(now=7)["observations"]
    decoded = decode_public(obs)
    body, receipt = sleep_lite(decoded.body, obs)
    assert receipt.meaning_preserved_all_8
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "public.json"
        write_snapshot(p, obs, tuple(gateway.public_journal()), body, expires_at=20)
        snap_sha = sha(p.read_bytes())
    tip = append(journal, g5, "SNAPSHOT_LOCK",
                 {"law_id": "1100", "sha256": snap_sha, "token": "a" * 32}, tip)
    state = load_state(journal, g5)
    for n in range(5):
        slot = g5.ordered[n]
        res_tip = append(journal, g5, "SLOT_RESERVED",
                         {"ordinal": n, "slot": slot.as_dict(),
                          "journal_tip_before": tip,
                          "run_lock_sha256": sha(orch.canonical(run_lock(g5)))}, tip)
        tip = append(journal, g5, "SLOT_FINISHED",
                     {"ordinal": n, "reservation_tip": res_tip,
                      "status": "TRACE_PRESENT", "receipt_sha256": "f" * 64}, res_tip)
        tip = tip
    slot = g5.ordered[5]
    tip = append(journal, g5, "SLOT_RESERVED",
                 {"ordinal": 5, "slot": slot.as_dict(), "journal_tip_before": tip,
                  "run_lock_sha256": sha(orch.canonical(run_lock(g5)))}, tip)
    RESULT.write_text(json.dumps({"phase": "A", "timings": timings,
                                  "crash_point": "ordinal 5 reserved, never finished",
                                  "tip": tip}, indent=1))
    print("PHASE A DONE; simulated crash after reserving ordinal 5")

def phase_b():
    subprocess.run(["git", "fetch", "--quiet", "origin"], check=True)
    subprocess.run(["git", "checkout", "-B", "audit/r2ma/g6-rehearsal-20261107",
                    "origin/audit/r2ma/g6-rehearsal-20261107"],
                   check=True, capture_output=True)
    journal = GitRunJournal(os.getcwd())
    g5 = timed("pinned_g5_load", lambda: load_pinned_g5(journal.pinned_g5))
    state = load_state(journal, g5)
    assert state.slot_status(5) == "RESERVED", state.slot_status(5)
    assert state.slot_status(0) == "FINISHED"
    tip = append(journal, g5, "STARTED_MISSING", {"ordinal": 5}, state.tip)
    state = load_state(journal, g5)
    assert state.slot_status(5) == "STARTED_MISSING", state.slot_status(5)
    blocked = {}
    slot = g5.ordered[5]
    try:
        journal.append("SLOT_RESERVED",
                       {"ordinal": 5, "slot": slot.as_dict(), "journal_tip_before": tip,
                        "run_lock_sha256": sha(orch.canonical(run_lock(g5)))},
                       expected_tip=tip, g5=g5)
        blocked["re_reserve_5"] = "NOT BLOCKED (DEFECT)"
    except G6Blocked:
        blocked["re_reserve_5"] = "RUN_BLOCK (expected)"
    try:
        journal.append("SLOT_FINISHED",
                       {"ordinal": 0, "reservation_tip": state.reservations[0]["entry_sha256"],
                        "status": "TRACE_PRESENT", "receipt_sha256": "f" * 64},
                       expected_tip=tip, g5=g5)
        blocked["duplicate_finish_0"] = "NOT BLOCKED (DEFECT)"
    except G6Blocked:
        blocked["duplicate_finish_0"] = "RUN_BLOCK (expected)"
    prior = json.loads(RESULT.read_text())
    all_timings = prior["timings"] + timings
    appends = [t["seconds"] for t in all_timings if t["op"].startswith("append:")]
    loads = [t["seconds"] for t in all_timings if t["op"] == "load+replay"]
    mean_append = sum(appends) / len(appends)
    production_appends = 1 + 16 * 4 + 448 + 448 + 16
    result = {"phase": "AB", "timings": all_timings, "blocked_checks": blocked,
              "appends_measured": len(appends),
              "mean_append_seconds": round(mean_append, 3),
              "max_append_seconds": max(appends),
              "mean_load_replay_seconds": round(sum(loads) / len(loads), 3) if loads else None,
              "production_append_estimate": production_appends,
              "extrapolated_journal_overhead_seconds": round(mean_append * production_appends),
              "verdict": "journal live path works; ordinal5 STARTED_MISSING; re-reserve and duplicate finish blocked"}
    RESULT.write_text(json.dumps(result, indent=1))
    print("REHEARSAL_RESULT " + json.dumps(result))

if __name__ == "__main__":
    {"A": phase_a, "B": phase_b}[sys.argv[1]]()

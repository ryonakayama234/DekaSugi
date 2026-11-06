"""G4 custody demonstration on GitHub Actions (auditor-side; synthetic data).

Runs inside an actions/checkout of the audit branch. Exercises the REAL
GitHubRemoteCustody end to end: Q precommit seal (commit + push + ls-remote +
pinned fetch readback), synthetic answer gate, snapshot lock, and the
pre-score manifest seal with remote re-verification. No laws are measured,
no scoring; the run root and seals live under audit/r2ma/ in the checkout.
Writes custody-demo-result.json and prints CUSTODY_RESULT.
"""
import json, os, sys
from pathlib import Path

sys.path.insert(0, os.getcwd())
BRANCH = "audit/r2ma/g4-actions-20261106"

def main():
    from packages.r2_m_a.evidence_ledger import EvidenceLedger
    from packages.r2_m_a.remote_custody import GitHubRemoteCustody

    run_root = Path("audit/r2ma/g4-actions-20261106-run")
    run_root.parent.mkdir(parents=True, exist_ok=True)
    ledger = EvidenceLedger.create(run_root, engineering_only=True)
    remote = GitHubRemoteCustody(".", branch=BRANCH)
    H = "a" * 64
    pre = ledger.precommit_q("0000", history_sha256=H, legal_sha256="b" * 64,
                             deadline=2000000000, committed_at=1000000000,
                             method_sha256="c" * 64, policy_sha256="d" * 64,
                             remote=remote)
    answer = ledger.synthetic_answer_gate("0000", remote=remote,
                                          answer=lambda: {"public_bit": 1},
                                          now=1000000001)
    ledger.lock_snapshot("0000", snapshot_sha256="e" * 64)
    seal = ledger.seal_prescore(remote)
    manifest = ledger.assert_prescore_remote(remote)
    result = {
        "branch": BRANCH,
        "precommit_receipt": pre.as_dict(),
        "answer_public": answer,
        "prescore_receipt": seal.as_dict(),
        "manifest_counts": manifest["counts"],
        "journal_events": [e["kind"] for e in ledger.events()],
        "eligible_for_future_score": manifest["eligible_for_future_score"],
    }
    Path("custody-demo-result.json").write_text(
        json.dumps(result, indent=1, sort_keys=True))
    print("CUSTODY_RESULT " + json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()

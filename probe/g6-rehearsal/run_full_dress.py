"""G6-2 full-dress rehearsal driver (auditor-side; rehearsal scope only).

Resolves the rehearsal Owner GO from its dedicated remote branch, then runs
G6Driver.start(max_laws=1) against the real RehearsalGitRunJournal: real Q
(synthetic gateway), real formal children, real receipts, remote-first
journal. Production branch, production lock and production GO are never
touched. Prints a JSON outcome line for the workflow log.
"""
import json, os, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, os.getcwd())
GO_BRANCH = "audit/r2ma/g6-rehearsal-go-20261107"
GO_PATH = "audit/r2ma/g6-rehearsal-owner-go.json"

def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()

def main():
    checkout = os.getcwd()
    git("config", "--global", "--add", "safe.directory", checkout)
    git("checkout", "-B", "audit/r2ma/g6-rehearsal-20261107")
    # Resolve the rehearsal GO reference from the remote artifact itself.
    go_sha = git("ls-remote", "origin", f"refs/heads/{GO_BRANCH}").split()[0]
    git("fetch", "--quiet", "origin", GO_BRANCH)
    artifact = json.loads(git("show", f"{go_sha}:{GO_PATH}"))
    comment_id = artifact["comment_id"]
    print(f"rehearsal GO: commit={go_sha} comment_id={comment_id}", flush=True)

    from packages.r2_m_a.g6_order import load_pinned_g5
    from packages.r2_m_a.g6_orchestrator import G6Orchestrator, RehearsalGitRunJournal
    from packages.r2_m_a.g6_scope import RehearsalGOReference
    from packages.r2_m_a.g6_q import QArtifactFiles
    from packages.r2_m_a.g6_driver import G6Driver

    journal = RehearsalGitRunJournal(checkout)
    g5 = load_pinned_g5(journal.pinned_g5)
    artifact_dir = Path(checkout) / "audit/r2ma/g6-rehearsal/artifacts/full-dress-1"
    fixture_dir = artifact_dir / "q-fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    method = fixture_dir / "rehearsal-method.txt"
    policy = fixture_dir / "rehearsal-policy.txt"
    method.write_text("G6-2 rehearsal fixture METHOD (not a frozen production method)\n")
    policy.write_text("G6-2 rehearsal fixture POLICY (not a frozen production policy)\n")
    orch = G6Orchestrator(journal, g5, artifact_dir)
    driver = G6Driver(
        orch,
        owner_go=RehearsalGOReference(commit_sha=go_sha, comment_id=comment_id),
        delegated_cgroup_root="/sys/fs/cgroup",
        q_artifacts=QArtifactFiles(method_path=method, policy_path=policy))
    t0 = time.time()
    outcome = driver.start(max_laws=1)
    result = {"laws_checkpointed": outcome.laws_checkpointed,
              "slots_finished": outcome.slots_finished,
              "first_law_cost_report": outcome.first_law_cost_report,
              "status": outcome.status,
              "wall_seconds_total": round(time.time() - t0, 1)}
    print("FULL_DRESS_RESULT " + json.dumps(result), flush=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Auditor driver: G6-3 PRODUCTION run, all 16 laws (448 slots).

Runs on GitHub Actions (root, real cgroup delegation) on the production run
branch. Authorization comes only from the production Owner GO artifact and
comment; this script merely resolves their remote identifiers.
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from packages.r2_m_a.g6_order import validate_g5  # noqa: E402
from packages.r2_m_a.g6_orchestrator import G6Orchestrator, GitRunJournal  # noqa: E402
from packages.r2_m_a.g6_driver import G6Driver  # noqa: E402
from packages.r2_m_a.g6_q import QArtifactFiles  # noqa: E402
from packages.r2_m_a.g6_measurement import OwnerGOReference  # noqa: E402
from packages.r2_m_a.g6_production_gateway import production_gateway_factory  # noqa: E402

API = "https://api.github.com/repos/ryonakayama234/DekaSugi"


def api(path: str) -> dict:
    import os
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
        "User-Agent": "r2ma-g6-production-driver"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main() -> int:
    g5_bytes = subprocess.run(
        ["git", "show",
         "bb2e27a20657fefa5426d970c3275b8d95a846dc:audit/r2ma/g5-order-manifest.json"],
        cwd=REPO_ROOT, capture_output=True, check=True).stdout
    g5 = validate_g5(
        g5_bytes, pinned_commit="bb2e27a20657fefa5426d970c3275b8d95a846dc",
        remote_ref="refs/heads/audit/r2ma/g5-order-20261107", pinned_readback=True)
    ref = api("/git/ref/heads/audit/r2ma/g6-owner-go-20261107")
    go_commit = ref["object"]["sha"]
    obj = api("/contents/audit/r2ma/g6-owner-go.json?ref=" + go_commit)
    artifact = json.loads(base64.b64decode(obj["content"]))
    owner_go = OwnerGOReference(commit_sha=go_commit,
                                comment_id=int(artifact["comment_id"]))
    journal = GitRunJournal(REPO_ROOT)
    artifact_dir = REPO_ROOT / "audit/r2ma/g6/artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    orch = G6Orchestrator(journal, g5, artifact_dir)
    q_artifacts = QArtifactFiles(
        REPO_ROOT / "packages/r2_m_eng/source_gateway.py",
        REPO_ROOT / "docs/research/R2-M-A-20261105-exhaustive16-engineering-prereg-draft.md")
    driver = G6Driver(
        orch, owner_go=owner_go,
        delegated_cgroup_root="/sys/fs/cgroup",
        q_artifacts=q_artifacts,
        gateway_factory=production_gateway_factory)
    outcome = driver.start(max_laws=16)
    print("outcome:", outcome)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""G6-2 rehearsal scope: distinct lock, Owner decision and remote journal namespace.

No GO artifact is generated here. A rehearsal permit is not a production permit.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import json

from .g6_order import G5_COMMIT, G5_SHA256, G6Blocked, SealedG5, canonical, sha
from .g6_measurement import OWNER_ID, SHA40, _fetch_json

REHEARSAL_BRANCH = "refs/heads/audit/r2ma/g6-rehearsal-20261107"
REHEARSAL_ROOT = "audit/r2ma/g6-rehearsal"
REHEARSAL_LOCK_SCHEMA = "r2ma-g6-rehearsal-run-lock/1"
REHEARSAL_GO_REF = "refs/heads/audit/r2ma/g6-rehearsal-go-20261107"
REHEARSAL_GO_PATH = "audit/r2ma/g6-rehearsal-owner-go.json"
REHEARSAL_GO_SCHEMA = "r2ma-g6-rehearsal-owner-go/1"
REHEARSAL_GO_DECISION = "G6-2_REHEARSAL_OWNER_GO"


def rehearsal_run_lock(g5: SealedG5) -> dict:
    from .g6_orchestrator import run_lock
    lock = run_lock(g5).copy()
    lock["schema"] = REHEARSAL_LOCK_SCHEMA
    lock["rehearsal_only"] = True
    return lock


@dataclass(frozen=True)
class RehearsalGOReference:
    commit_sha: str
    comment_id: int


@dataclass(frozen=True)
class RehearsalPermit:
    lock_sha256: str
    expanded_sha256: str
    owner_comment_id: int
    scope: str = "rehearsal"


def authorize_rehearsal_g6(g5: SealedG5, lock: dict,
                            approval: object) -> RehearsalPermit:
    """Independent, pinned owner-authenticated GO. Never accepts production GO."""
    if (type(g5) is not SealedG5 or g5.pinned_commit != G5_COMMIT
            or g5.raw_sha256 != G5_SHA256
            or lock != rehearsal_run_lock(g5)):
        raise G6Blocked("RUN_BLOCK: rehearsal G5/run-lock mismatch")
    if (type(approval) is not RehearsalGOReference
            or type(approval.commit_sha) is not str
            or not SHA40.fullmatch(approval.commit_sha)
            or type(approval.comment_id) is not int
            or approval.comment_id <= 0):
        raise G6Blocked("RUN_BLOCK: rehearsal Owner GO absent")
    base = "https://api.github.com/repos/ryonakayama234/DekaSugi"
    ref = _fetch_json(base + "/git/ref/heads/audit/r2ma/g6-rehearsal-go-20261107")
    if ref.get("object", {}).get("sha") != approval.commit_sha:
        raise G6Blocked("RUN_BLOCK: rehearsal GO ref pin mismatch")
    obj = _fetch_json(base + "/contents/" + REHEARSAL_GO_PATH + "?ref="
                      + approval.commit_sha)
    try:
        raw = base64.b64decode(obj["content"], validate=False)
        artifact = json.loads(raw)
    except (ValueError, TypeError, KeyError) as exc:
        raise G6Blocked("RUN_BLOCK: rehearsal GO bytes unavailable") from exc
    expected = {
        "schema": REHEARSAL_GO_SCHEMA, "decision": REHEARSAL_GO_DECISION,
        "run_lock_sha256": sha(canonical(lock)),
        "g5_expanded_sha256": g5.expanded_sha256,
        "branch": REHEARSAL_BRANCH, "journal_root": REHEARSAL_ROOT,
        "issue": 146, "comment_id": approval.comment_id,
    }
    if artifact != expected or raw != canonical(expected) or not obj.get("sha"):
        raise G6Blocked("RUN_BLOCK: rehearsal GO artifact mismatch")
    comment = _fetch_json(base + f"/issues/comments/{approval.comment_id}")
    body = comment.get("body")
    if (comment.get("id") != approval.comment_id
            or comment.get("user", {}).get("id") != OWNER_ID
            or type(body) is not str
            or "G6-2 Rehearsal GO" not in body
            or expected["run_lock_sha256"] not in body
            or comment.get("issue_url") != base + "/issues/146"):
        raise G6Blocked("RUN_BLOCK: rehearsal GO not authenticated")
    return RehearsalPermit(expected["run_lock_sha256"],
                           g5.expanded_sha256, approval.comment_id)

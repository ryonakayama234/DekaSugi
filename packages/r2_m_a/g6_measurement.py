"""G6-1 prospective authorization and non-scoring measurement receipt.

No activation artifact or executor is provided in G6-1. Existing G3 safety
guards remain unchanged and G6-4 scoring has a separate Owner gate.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import base64
import json
import math
import os
import re
from urllib.request import Request, urlopen

from .contracts import (ChildRequest, Slot, WALL_SECONDS_CAP,
                        PROCESS_CPU_SECONDS_CAP, RSS_BYTES_CAP)
from .g6_order import G6Blocked, SealedG5, G5_SHA256, G5_COMMIT, canonical, sha

OWNER_ID = 216265384
OWNER_GO_REF = "refs/heads/audit/r2ma/g6-owner-go-20261107"
GO_PATH = "audit/r2ma/g6-owner-go.json"
GO_SCHEMA = "r2ma-g6-owner-go/1"
RECEIPT_SCHEMA = "r2ma-g6-measurement/1"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class OwnerGOReference:
    """Untrusted reference: constructing this never grants permission."""
    commit_sha: str
    comment_id: int


@dataclass(frozen=True)
class ProductionPermit:
    lock_sha256: str
    expanded_sha256: str
    owner_comment_id: int


def _fetch_json(url: str) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "r2ma-g6-authorization"}
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urlopen(Request(url, headers=headers), timeout=15) as response:
            raw = response.read(65_537)
        if len(raw) > 65_536:
            raise ValueError("oversize")
        result = json.loads(raw)
        if type(result) is not dict:
            raise ValueError("not object")
        return result
    except Exception as exc:
        raise G6Blocked("RUN_BLOCK: Owner GO remote verification unavailable") from exc


def authorize_g6(g5: SealedG5, lock: dict,
                 owner_go: object) -> ProductionPermit:
    """Require independent G5, exact run-lock and authentic remote Owner GO.

    The GO artifact is pinned to a remote commit AND authenticated against an
    Owner-authored decision comment on #146. Caller booleans cannot authorize.
    """
    from .g6_orchestrator import run_lock
    if (type(g5) is not SealedG5 or g5.pinned_commit != G5_COMMIT
            or g5.raw_sha256 != G5_SHA256 or lock != run_lock(g5)):
        raise G6Blocked("RUN_BLOCK: G5/ G6 run-lock mismatch")
    if (type(owner_go) is not OwnerGOReference
            or type(owner_go.comment_id) is not int
            or owner_go.comment_id <= 0
            or type(owner_go.commit_sha) is not str
            or not SHA40.fullmatch(owner_go.commit_sha)):
        raise G6Blocked("RUN_BLOCK: G6-3 Owner GO artifact absent")
    repo = "ryonakayama234/DekaSugi"
    base = f"https://api.github.com/repos/{repo}"
    ref = _fetch_json(base + "/git/ref/heads/audit/r2ma/g6-owner-go-20261107")
    if ref.get("object", {}).get("sha") != owner_go.commit_sha:
        raise G6Blocked("RUN_BLOCK: Owner GO ref pin changed")
    obj = _fetch_json(base + "/contents/" + GO_PATH + "?ref=" + owner_go.commit_sha)
    try:
        raw = base64.b64decode(obj["content"], validate=False)
        artifact = json.loads(raw)
    except (ValueError, TypeError, KeyError) as exc:
        raise G6Blocked("RUN_BLOCK: Owner GO artifact unavailable") from exc
    expected = {"schema": GO_SCHEMA, "decision": "G6-3_OWNER_GO",
                "run_lock_sha256": sha(canonical(lock)),
                "g5_expanded_sha256": g5.expanded_sha256,
                "issue": 146, "comment_id": owner_go.comment_id}
    if artifact != expected or raw != canonical(expected) or not obj.get("sha"):
        raise G6Blocked("RUN_BLOCK: G6 Owner GO artifact mismatch")
    comment = _fetch_json(base + f"/issues/comments/{owner_go.comment_id}")
    body = comment.get("body")
    if (comment.get("id") != owner_go.comment_id
            or comment.get("user", {}).get("id") != OWNER_ID
            or type(body) is not str or "G6-3 Owner GO" not in body
            or expected["run_lock_sha256"] not in body
            or comment.get("issue_url") != base + "/issues/146"):
        raise G6Blocked("RUN_BLOCK: Owner GO not authenticated")
    return ProductionPermit(expected["run_lock_sha256"],
                            g5.expanded_sha256, owner_go.comment_id)


@dataclass(frozen=True)
class MeasurementReceipt:
    """G6 production receipt; G3 ENGINEERING_ONLY data cannot impersonate it."""
    slot: dict
    request_sha256: str
    run_lock_sha256: str
    status: str
    trace_sha256: str | None
    stdout_sha256: str | None
    stderr_sha256: str | None
    wall_seconds: float
    cpu_seconds: float
    peak_rss_bytes: int
    cgroup_peak_bytes: int
    exit_code: int | None
    reaped: bool
    stop_reason: str | None
    environment: dict
    schema: str = RECEIPT_SCHEMA

    @property
    def digest(self) -> str:
        return sha(canonical(asdict(self)))

    def verify(self, slot: Slot, request: ChildRequest, permit: ProductionPermit) -> None:
        if (type(slot) is not Slot or type(request) is not ChildRequest
                or type(permit) is not ProductionPermit
                or self.schema != RECEIPT_SCHEMA
                or self.slot != slot.as_dict()
                or self.request_sha256 != sha(canonical(request.as_dict()))
                or self.run_lock_sha256 != permit.lock_sha256):
            raise G6Blocked("RUN_BLOCK: malformed measurement receipt")
        for digest in (self.trace_sha256, self.stdout_sha256, self.stderr_sha256):
            if digest is not None and (type(digest) is not str
                                       or not SHA64.fullmatch(digest)):
                raise G6Blocked("RUN_BLOCK: invalid trace/output SHA")
        if (type(self.wall_seconds) not in (int, float)
                or type(self.cpu_seconds) not in (int, float)
                or not math.isfinite(self.wall_seconds)
                or not math.isfinite(self.cpu_seconds)
                or self.wall_seconds < 0 or self.cpu_seconds < 0
                or type(self.peak_rss_bytes) is not int
                or self.peak_rss_bytes < 0
                or type(self.cgroup_peak_bytes) is not int
                or self.cgroup_peak_bytes < 0
                or type(self.reaped) is not bool
                or type(self.environment) is not dict
                or not {"runner_os", "python", "cgroup_v2"} <= set(self.environment)):
            raise G6Blocked("RUN_BLOCK: invalid raw metrology")
        if self.status not in {"TRACE_PRESENT", "INVALID", "RESOURCE_STOP",
                               "RUN_BLOCK", "UNMEASURED", "BOUNDARY_REVIEW"}:
            raise G6Blocked("RUN_BLOCK: illegal measurement status")
        if self.status == "TRACE_PRESENT":
            if (not self.reaped or self.exit_code != 0
                    or self.trace_sha256 is None or self.stop_reason is not None
                    or self.peak_rss_bytes >= RSS_BYTES_CAP
                    or self.cgroup_peak_bytes >= RSS_BYTES_CAP
                    or self.wall_seconds > WALL_SECONDS_CAP
                    or self.cpu_seconds > PROCESS_CPU_SECONDS_CAP):
                raise G6Blocked("RUN_BLOCK: false clean measurement")
        elif not self.stop_reason:
            raise G6Blocked("RUN_BLOCK: incomplete failure reason")
        if (self.peak_rss_bytes >= RSS_BYTES_CAP
                or self.cgroup_peak_bytes >= RSS_BYTES_CAP):
            if self.status not in {"RESOURCE_STOP", "BOUNDARY_REVIEW", "RUN_BLOCK"}:
                raise G6Blocked("RUN_BLOCK: RSS cap breach hidden")

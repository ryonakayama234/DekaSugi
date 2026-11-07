"""Explicit G6 START/RESUME driver; law-boundary STOP and cost-only interim.

No GO artifact issuance, hidden re-authorization bypass, scoring or remote
execution on import. Callers must provide a real authorized journal and cgroup.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import time
from typing import Callable

from .contracts import ARMS
from .g6_order import G6Blocked, canonical, sha
from .g6_orchestrator import (
    G6Orchestrator, GitRunJournal, RehearsalGitRunJournal,
)
from .g6_q import G6QStage, QArtifactFiles

LAW_SIZE = 4 * len(ARMS)


@dataclass(frozen=True)
class DriverOutcome:
    laws_checkpointed: int
    slots_finished: int
    first_law_cost_report: str | None
    status: str = "BOUNDARY_PAUSE"


def synthetic_rehearsal_gateway(law: str, at: int):
    """Known-law synthetic source, NOT independent scientific source/truth."""
    from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource
    if type(law) is not str or len(law) != 4 or set(law) - {"0", "1"}:
        raise G6Blocked("RUN_BLOCK: malformed rehearsal fixture law")
    return PublicGateway(
        SyntheticPrivateSource(tuple(int(ch) for ch in law)),
        opened_at=at, expires_at=at + 900)


class G6Driver:
    def __init__(self, orchestrator: G6Orchestrator, *,
                 owner_go: object, delegated_cgroup_root: str | Path,
                 q_artifacts: QArtifactFiles,
                 gateway_factory: Callable | None = None):
        if (type(orchestrator) is not G6Orchestrator
                or type(orchestrator.remote) not in (
                    GitRunJournal, RehearsalGitRunJournal)
                or delegated_cgroup_root is None
                or type(q_artifacts) is not QArtifactFiles):
            raise G6Blocked("RUN_BLOCK: explicit formal driver configuration required")
        if orchestrator.scope == "production" and gateway_factory is None:
            raise G6Blocked("RUN_BLOCK: production source gateway must be explicit")
        self.orch = orchestrator
        self.owner_go = owner_go
        self.cgroup = delegated_cgroup_root
        self.q_artifacts = q_artifacts
        self.gateway_factory = gateway_factory or synthetic_rehearsal_gateway
        self.first_costs = []

    def start(self, *, max_laws: int = 16) -> DriverOutcome:
        """START only with a missing run-lock; seal it after fresh Owner GO."""
        self.orch.initialize(owner_go=self.owner_go)
        return self._drive(max_laws)

    def resume(self, *, max_laws: int = 16) -> DriverOutcome:
        """RESUME only from pinned remote run-lock with fresh Owner GO."""
        self.orch.resume_authorized(owner_go=self.owner_go)
        return self._drive(max_laws)

    def _receipt_cost(self, ordinal: int, token: str) -> dict:
        path = self.orch.artifact_dir / ("receipt-" + token + ".json")
        raw = path.read_bytes()
        state = self.orch.state()
        if sha(raw) != state.finishes[ordinal]["data"]["receipt_sha256"]:
            raise G6Blocked("RUN_BLOCK: cost receipt not tied to remote finish")
        try:
            obj = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise G6Blocked("RUN_BLOCK: cost receipt unavailable") from exc
        if canonical(obj) != raw:
            raise G6Blocked("RUN_BLOCK: noncanonical cost receipt")
        return {k: obj[k] for k in (
            "wall_seconds", "cpu_seconds", "peak_rss_bytes", "cgroup_peak_bytes")}

    def _first_law_report(self) -> str:
        """Raw cost only; no answers, predictions, routes or score keys."""
        folder = self.orch.artifact_dir
        path = folder / "first-law-cost-only.json"
        values = self.first_costs
        def measured(key):
            present = [row[key] for row in values if row[key] is not None]
            return {
                "observed": len(present), "unmeasured": LAW_SIZE-len(present),
                "sum": sum(present) if len(present) == LAW_SIZE
                       and key in ("wall_seconds", "cpu_seconds") else None,
                "max": max(present) if present else None,
            }
        doc = {"schema": "r2ma-g6-first-law-cost/1", "scope": self.orch.scope,
               "expected_slots": LAW_SIZE, "observed_receipts": len(values),
               "wall_seconds": measured("wall_seconds"),
               "cpu_seconds": measured("cpu_seconds"),
               "peak_rss_bytes": measured("peak_rss_bytes"),
               "cgroup_peak_bytes": measured("cgroup_peak_bytes"),
               "projection": "NOT_EVALUATED", "no_scoring": True}
        body = canonical(doc)
        # A restarted runner cannot silently overwrite an earlier cost report.
        if path.exists():
            if path.is_symlink() or path.read_bytes() != body:
                raise G6Blocked("RUN_BLOCK: first-law cost report changed")
        else:
            try:
                fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o400)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(body)
                    stream.flush()
                    os.fsync(stream.fileno())
            except OSError as exc:
                raise G6Blocked("RUN_BLOCK: first-law cost report could not be sealed") from exc
        return str(path)

    def _drive(self, max_laws: int) -> DriverOutcome:
        if type(max_laws) is not int or not 1 <= max_laws <= 16:
            raise G6Blocked("RUN_BLOCK: invalid law boundary")
        laws = tuple(dict.fromkeys(s.law_id for s in self.orch.g5.ordered))
        first_report = None
        for law_no, law in enumerate(laws[:max_laws]):
            # Never bypass STOPPED_* or STARTED_MISSING. An interruption at Q
            # or slot boundary is Owner-decision territory, not a retry.
            state = self.orch.resume()
            if state.missing or state.stopped:
                raise G6Blocked("RUN_BLOCK: Owner decision at law boundary")
            if "LAW_CHECKPOINT" in {e["kind"] for e in state.events
                                   if e["data"].get("law_id") == law}:
                continue
            phases = state.stages.get(law, set())
            q = G6QStage(self.orch)
            if not phases:
                now = int(time.time())
                gateway = self.gateway_factory(law, now)
                commitment = q.precommit(
                    law, gateway, now=now, artifacts=self.q_artifacts)
                q.record_q(law, gateway, commitment=commitment, now=now + 1)
                q.snapshot(law, token=secrets.token_hex(16))
            elif "Q_ANSWER" in phases and "SNAPSHOT_LOCK" not in phases:
                q.snapshot(law, token=secrets.token_hex(16))
            elif "SNAPSHOT_LOCK" not in phases:
                raise G6Blocked("RUN_BLOCK: interrupted Q requires Owner decision")
            for ordinal in range(law_no * LAW_SIZE, (law_no + 1) * LAW_SIZE):
                state = self.orch.state()
                if ordinal in state.finishes:
                    continue
                if ordinal in state.reservations:
                    raise G6Blocked("RUN_BLOCK: STARTED_MISSING Owner decision")
                token = secrets.token_hex(16)
                if self.orch.scope == "production":
                    self.orch.run_production_slot(
                        ordinal, trace_token=token, owner_go=self.owner_go,
                        delegated_cgroup_root=self.cgroup)
                else:
                    self.orch.run_rehearsal_slot(
                        ordinal, trace_token=token, owner_go=self.owner_go,
                        delegated_cgroup_root=self.cgroup)
                if law_no == 0:
                    self.first_costs.append(self._receipt_cost(ordinal, token))
            self.orch.checkpoint_law(law)
            if law_no == 0:
                first_report = self._first_law_report()
        state = self.orch.state()
        checkpoint_count = sum(e["kind"] == "LAW_CHECKPOINT" for e in state.events)
        return DriverOutcome(checkpoint_count, len(state.finishes), first_report,
                             "ALL_LAWS_COMPLETE" if checkpoint_count == 16
                             else "BOUNDARY_PAUSE")

"""G6 Q001 formal precommit -> paid response -> immutable public Snapshot.

The production digest anchors are deliberately absent until the Owner identifies
the frozen METHOD and POLICY byte artifacts. Rehearsal digests are explicitly
fixture-only and cannot satisfy production Q authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from packages.r2_m_eng.records import (
    PUBLIC_POINTS, PublicObservation, digest, public_evidence_digest,
    validate_public_history,
)
from .g6_order import G6Blocked

# NO production hash is guessed from version labels or a nearby source file.
FROZEN_PRODUCTION_METHOD: tuple[str, str] | None = None
FROZEN_PRODUCTION_POLICY: tuple[str, str] | None = None


@dataclass(frozen=True)
class QArtifactFiles:
    """Two concrete byte artifacts; in production each must match a frozen pin."""
    method_path: Path
    policy_path: Path

    def digests(self, *, scope: str) -> tuple[str, str]:
        if scope == "production":
            if FROZEN_PRODUCTION_METHOD is None or FROZEN_PRODUCTION_POLICY is None:
                raise G6Blocked("RUN_BLOCK: frozen method/policy digest originals unresolved")
            anchors = (FROZEN_PRODUCTION_METHOD, FROZEN_PRODUCTION_POLICY)
        elif scope == "rehearsal":
            anchors = (None, None)  # synthetic fixture, not an Owner-frozen method
        else:
            raise G6Blocked("RUN_BLOCK: unknown Q scope")
        values = []
        for path, pin in zip((self.method_path, self.policy_path), anchors):
            source = Path(path)
            if source.is_symlink() or not source.is_file():
                raise G6Blocked("RUN_BLOCK: Q artifact missing or symlinked")
            if scope == "production" and (str(source.resolve()) != pin[0]
                                           or len(pin[1]) != 64):
                raise G6Blocked("RUN_BLOCK: frozen Q artifact path/pin mismatch")
            value = sha256(source.read_bytes()).hexdigest()
            if scope == "production" and value != pin[1]:
                raise G6Blocked("RUN_BLOCK: frozen Q artifact bytes changed")
            values.append(value)
        if values[0] == values[1]:
            raise G6Blocked("RUN_BLOCK: Q method and policy must be independent")
        return tuple(values)


class G6QStage:
    """One irreversible Q attempt per law. No resume/requery inside the Q window."""

    def __init__(self, orchestrator):
        self.orch = orchestrator

    def _require_formal(self) -> None:
        from .g6_orchestrator import GitRunJournal, RehearsalGitRunJournal
        expected = (GitRunJournal if self.orch.scope == "production"
                    else RehearsalGitRunJournal)
        if type(self.orch.remote) is not expected or self.orch._production_permit is None:
            raise G6Blocked("RUN_BLOCK: formal Q scope not authenticated")

    def precommit(self, law: str, gateway, *, now: int,
                  artifacts: QArtifactFiles) -> str:
        self._require_formal()
        # Validate ALL unknown provenance before the one-shot Q_ATTEMPT.
        method_sha, policy_sha = artifacts.digests(scope=self.orch.scope)
        self.orch.resume()
        state = self.orch.state()
        if law not in {slot.law_id for slot in self.orch.g5.ordered} or law in state.stages:
            raise G6Blocked("RUN_BLOCK: duplicate or wrong-law Q attempt")
        public = gateway.public_state(now=now)
        history = public["observations"]
        validate_public_history(history)
        if (len(history) != 3 or public["legal_actions"] != (PUBLIC_POINTS[3],)
                or public["paid_budget_remaining"] != 1
                or type(public["expires_at"]) is not int or now > public["expires_at"]):
            raise G6Blocked("RUN_BLOCK: illegal Q gateway state")
        history_sha = public_evidence_digest(history)
        legal_sha = public["legal_digest"]
        commitment = digest({
            "kind": "Q001-precommit", "seq": 3, "point": PUBLIC_POINTS[3],
            "legal_digest": legal_sha, "prediction": None,
            "history_digest": history_sha, "event_at": now,
        })
        intent = {
            "history_sha256": history_sha, "legal_sha256": legal_sha,
            "point": list(PUBLIC_POINTS[3]), "paid_budget_remaining": 1,
            "deadline": public["expires_at"], "committed_at": now,
            "method_sha256": method_sha, "policy_sha256": policy_sha,
            "public_initial_count": 3, "commitment_sha256": commitment,
        }
        self.orch._append("Q_ATTEMPT", {"law_id": law})
        # The marker survives any exception; never create a second attempt.
        actual = gateway.precommit(
            PUBLIC_POINTS[3], expected_legal_digest=legal_sha,
            prediction=None, now=now)
        if actual != commitment:
            raise G6Blocked("RUN_BLOCK: gateway Q commitment mismatch")
        self.orch._append("Q_PRECOMMIT", {"law_id": law, "intent": intent})
        return commitment

    def record_q(self, law: str, gateway, *, commitment: str,
                 now: int) -> None:
        self._require_formal()
        state = self.orch.state()  # Never call resume across an active Q window.
        phase = state.stages.get(law, set())
        if "Q_PRECOMMIT" not in phase or "Q_ANSWER" in phase or law in state.stopped:
            raise G6Blocked("RUN_BLOCK: Q must be precommitted exactly once")
        intent = next(e["data"]["intent"] for e in state.events
                      if e["kind"] == "Q_PRECOMMIT" and e["data"]["law_id"] == law)
        if commitment != intent["commitment_sha256"]:
            raise G6Blocked("RUN_BLOCK: paid Q commitment drift")
        gateway.answer(PUBLIC_POINTS[3], precommit=commitment, now=now)
        observed = gateway.public_state(now=now)["observations"]
        validate_public_history(observed, complete=True)
        self.orch.record_synthetic_q(
            law, observed, gateway.public_journal(),
            intent["deadline"])

    def snapshot(self, law: str, *, token: str) -> Path:
        self._require_formal()
        # Snapshot regeneration and digest locking are identical in both scopes.
        return self.orch.snapshot_synthetic(law, token=token)

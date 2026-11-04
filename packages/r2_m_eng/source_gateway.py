"""Evaluator-side synthetic F_aff source and one-way public inquiry gateway.

The private source lives ONLY here. Importing this module is forbidden in
records/decoder/validator/sleep_lite. This is a module boundary, NOT a
malicious same-process isolation guarantee. No real sealed source is accepted.
"""
from __future__ import annotations

from .records import (
    FAMILY_VERSION, PUBLIC_POINTS, PublicObservation, PublicStep,
    check_bit, check_point, check_sha, digest, public_evidence_digest,
)

Q001 = (0, 0, 1)


class SyntheticPrivateSource:
    """A known-law test fixture held by the evaluator-side gateway only."""

    __slots__ = ("_coefficients",)

    def __init__(self, coefficients: tuple[int, int, int, int]):
        if type(coefficients) is not tuple or len(coefficients) != 4:
            raise ValueError("INVALID: artificial 4 coefficient tuple required")
        self._coefficients = tuple(check_bit(bit) for bit in coefficients)

    def _answer(self, point: tuple[int, int, int]) -> int:
        x, y, z = check_point(point)
        a, b, c, d = self._coefficients
        return (a & x) ^ (b & y) ^ (c & z) ^ d


class PublicGateway:
    """Release P initially; one paid Q001 only after an immutable precommit.

    The in-memory journal is append-only from the public API perspective.
    Durable fsync and evaluator custody are intentionally deferred to stage 2/3.
    """
    __slots__ = ("__source", "_expires_at", "_observations", "_events",
                 "_pending", "_budget", "_invalid", "_last_tick")

    def __init__(self, source: SyntheticPrivateSource, *, opened_at: int = 0,
                 expires_at: int = 100):
        if type(source) is not SyntheticPrivateSource:
            raise ValueError("INVALID: synthetic evaluator source required")
        if (type(opened_at) is not int or type(expires_at) is not int or
                opened_at < 0 or expires_at < opened_at):
            raise ValueError("INVALID: deadline")
        self.__source = source
        self._expires_at = expires_at
        self._budget = 1
        self._pending: tuple[tuple[int, int, int], str, int] | None = None
        self._invalid = False
        self._last_tick = opened_at
        legal, legal_hash = self._legality(opened_at)
        self._observations = []
        self._events = []
        for i, point in enumerate(PUBLIC_POINTS[:3]):
            answer = source._answer(point)
            row = PublicObservation(i, point, answer, 0, legal_hash, None, opened_at)
            self._observations.append(row)
            self._events.append(PublicStep("initial", i, point, legal, legal_hash,
                                           opened_at, answer=answer))

    def _legality(self, now: int) -> tuple[tuple[tuple[int, int, int], ...], str]:
        legal = (Q001,) if self._budget and now <= self._expires_at else ()
        return legal, digest({"family": FAMILY_VERSION,
                              "legal_actions": [list(p) for p in legal],
                              "paid_budget_remaining": self._budget,
                              "expires_at": self._expires_at})

    def _tick(self, now: int) -> None:
        if self._invalid:
            raise ValueError("INVALID: quarantined gateway")
        if type(now) is not int or now < self._last_tick:
            self._invalid = True
            raise ValueError("INVALID: nonmonotonic event time")
        self._last_tick = now

    def public_state(self, *, now: int = 0) -> dict[str, object]:
        self._tick(now)
        legal, legal_hash = self._legality(now)
        return {"observations": tuple(self._observations),
                "legal_actions": legal,
                "legal_digest": legal_hash,
                "paid_budget_remaining": self._budget,
                "expires_at": self._expires_at}

    def public_journal(self) -> tuple[dict[str, object], ...]:
        if self._invalid:
            raise ValueError("INVALID: quarantined gateway")
        return tuple(row.as_dict() for row in self._events)

    def precommit(self, point: tuple[int, int, int], *,
                  expected_legal_digest: str, prediction: int | None,
                  now: int) -> str:
        self._tick(now)
        try:
            check_point(point)
            check_sha(expected_legal_digest)
            if prediction is not None:
                check_bit(prediction)
            legal, legal_hash = self._legality(now)
            if now > self._expires_at:
                raise ValueError("UNIDENTIFIABLE: Q001 expired")
            if (point != Q001 or self._budget != 1 or self._pending is not None
                    or point not in legal or expected_legal_digest != legal_hash):
                raise ValueError("INVALID: illegal or tampered precommit")
        except ValueError as exc:
            if "UNIDENTIFIABLE" not in str(exc):
                self._invalid = True
            raise
        commitment = digest({"kind": "Q001-precommit", "seq": 3, "point": point,
                             "legal_digest": legal_hash, "prediction": prediction,
                             "history_digest": public_evidence_digest(
                                 tuple(self._observations)),
                             "event_at": now})
        self._pending = (point, commitment, now)
        self._events.append(PublicStep("precommit", 3, point, legal, legal_hash, now,
                                       precommit=commitment, prediction=prediction))
        return commitment

    def answer(self, point: tuple[int, int, int], *,
               precommit: str, now: int) -> PublicObservation:
        self._tick(now)
        try:
            check_point(point)
            check_sha(precommit)
            if (self._pending is None or self._pending[:2] != (point, precommit)
                    or self._budget != 1 or now > self._expires_at):
                raise ValueError("INVALID: response without valid timely precommit")
        except ValueError:
            self._invalid = True
            raise
        legal, legal_hash = self._legality(now)
        # This is the ONLY private-source read after public initial P.
        row = PublicObservation(3, point, self.__source._answer(point), 1,
                                legal_hash, precommit, now)
        self._observations.append(row)
        self._events.append(PublicStep("answer", 3, point, legal, legal_hash, now,
                                       answer=row.answer, paid_cost=1,
                                       precommit=precommit))
        self._pending = None
        self._budget = 0
        return row

"""Private finite source and public-only query gateway for the FOUR approved fixtures.

The source object is held by the orchestrator, never passed to synthesis,
validator or fresh-use process. This Python role boundary is not a malicious
same-process sandbox; the engineering claim is restricted accordingly.
"""
from __future__ import annotations

from .core import Observation, DOMAIN, check_point, digest, h0_predict, scan_h0

INITIAL = {
    "N": (),
    "S": (),
    "R": ((0, 0), (0, 1), (1, 0)),
    "E": ((0, 0), (1, 0)),
}
LEGAL = {"N": ((0, 0), (0, 1), (1, 0)),
         "S": ((0, 0),), "R": ((1, 1),), "E": ()}
BUDGET = {"N": 1, "S": 1, "R": 1, "E": 0}
VARIANTS = {"N": ("A", "B"), "S": ("A", "B"),
            "R": ("A", "B"), "E": ("A",)}


class PrivateSource:
    """Evaluator/source-side only; never serialize this object or its law."""
    def __init__(self, case: str, variant: str):
        if case not in VARIANTS or variant not in VARIANTS[case]:
            raise ValueError("unknown approved finite fixture")
        self.case = case
        self.variant = variant

    def answer(self, point: tuple[int, int]) -> int:
        x, z = check_point(point)
        if self.case == "N":
            return x if self.variant == "A" else (x & (1 - z))
        if self.case == "S":
            return x if self.variant == "A" else 1 - x
        if self.case == "R":
            return x ^ z if self.variant == "A" else x | z
        return x


class PublicGateway:
    """Answer paid requests only after prediction commit, enforcing legal Q."""
    def __init__(self, world: PrivateSource):
        if type(world) is not PrivateSource:
            raise ValueError("source required")
        self._source = world
        self._legal = LEGAL[world.case]
        self._budget = BUDGET[world.case]
        self._pending: tuple[tuple[int, int], str] | None = None
        self._invalid = False
        legal_digest = digest({"legal": self._legal, "budget": self._budget})
        self._records = [Observation(i, point, world.answer(point), 0,
                                     legal_digest, None)
                         for i, point in enumerate(INITIAL[world.case])]

    def public(self) -> tuple[tuple[Observation, ...], tuple[tuple[int, int], ...], int]:
        return tuple(self._records), tuple(p for p in self._legal if
                                          p not in {o.point for o in self._records}), self._budget

    def precommit(self, point: tuple[int, int], prediction: int | None) -> str:
        if self._invalid:
            raise ValueError("INVALID session")
        check_point(point)
        if prediction is not None and (type(prediction) is not int or prediction not in (0, 1)):
            self._invalid = True
            raise ValueError("invalid prediction commit")
        if self._pending is not None or point not in self.public()[1] or self._budget <= 0:
            self._invalid = True
            raise ValueError("INVALID illegal or unbudgeted precommit")
        commitment = digest({"seq": len(self._records), "point": point,
                             "prediction": prediction, "kind": "pre-observation"})
        self._pending = (point, commitment)
        return commitment

    def ask(self, point: tuple[int, int], precommit: str) -> Observation:
        if (self._invalid or self._pending != (point, precommit) or
            point not in self.public()[1] or self._budget <= 0):
            self._invalid = True
            raise ValueError("INVALID query without valid precommit")
        # The private source is accessed only AFTER an immutable commitment exists.
        current_legal, remaining = self.public()[1:]
        legal_digest = digest({"legal": current_legal, "budget": remaining})
        obs = Observation(len(self._records), point, self._source.answer(point),
                          1, legal_digest, precommit)
        self._records.append(obs)
        self._budget -= 1
        self._pending = None
        return obs


def finite_certificate(case: str) -> dict[str, object]:
    """Source-side mathematical witnesses, NEVER training labels or scientific scores."""
    if case not in VARIANTS:
        raise ValueError("not a reviewed N/S/R/E case")
    worlds = tuple(PrivateSource(case, v) for v in VARIANTS[case])
    if case == "N":
        assert all(worlds[0].answer(p) == worlds[1].answer(p) for p in LEGAL[case])
        assert worlds[0].answer((1, 1)) != worlds[1].answer((1, 1))
        return {"status": "UNIDENTIFIABLE", "proof": "all legal Q indistinguishable"}
    if case == "S":
        assert worlds[0].answer((0, 0)) != worlds[1].answer((0, 0))
        assert all(any(all(h0_predict(h, p) == w.answer(p) for p in DOMAIN)
                       for h in ("x", "!x")) for w in worlds)
        return {"status": "SUFFICIENT_H0", "proof": "one Q separates two H0 laws"}
    if case == "R":
        assert all(worlds[0].answer(p) == worlds[1].answer(p)
                   for p in INITIAL["R"])
        assert worlds[0].answer((1, 1)) != worlds[1].answer((1, 1))
        errors = {v: min(sum(h0_predict(h, p) != w.answer(p) for p in DOMAIN)
                         for h in ("0", "1", "x", "!x", "z", "!z"))
                  for v, w in zip(VARIANTS["R"], worlds)}
        assert errors == {"A": 2, "B": 1}
        return {"status": "MISMATCH_CANDIDATE",
                "proof": "six H0 objects fail public prefix; Q(1,1) separates",
                "object_error_min": errors}
    history = PublicGateway(worlds[0]).public()[0]
    assert scan_h0(history, 5).status == "SEARCH_INCOMPLETE"
    assert scan_h0(history, 6).consistent == ("x",)
    return {"status": "SEARCH_INCOMPLETE", "proof": "x is sixth in H0 enumeration"}

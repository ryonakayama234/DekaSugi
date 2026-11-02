"""EXP-REP-005 G0: orthogonal representation and identification diagnostics.

Artificial method-only preflight. The source hypothesis set is evaluator-private.
No learner, authenticated oracle, paid TRAIN, Snapshot, score or FINAL.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
import importlib.util
import sys

WITNESS_PATH = Path(__file__).with_name("g0_witness.py")
_SPEC = importlib.util.spec_from_file_location("rep005_g0_inherited_witness", WITNESS_PATH)
assert _SPEC is not None and _SPEC.loader is not None
w = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = w
_SPEC.loader.exec_module(w)


class Representation(str, Enum):
    H0 = "H0_SUFFICIENT"
    HPLUS = "HPLUS_ONLY"
    OUTSIDE = "OUTSIDE_HPLUS"
    STOCHASTIC = "STOCHASTIC_OR_INVALID"
    UNCERTIFIED = "NOT_CERTIFIED"


class Identification(str, Enum):
    IDENTIFIABLE = "IDENTIFIABLE_WITHIN_BUDGET"
    UNIDENTIFIABLE = "NO_UNIFORM_IDENTIFICATION_WITHIN_BUDGET"
    UNCERTIFIED = "NOT_CERTIFIED"


@dataclass(frozen=True)
class Classification:
    representation: Representation
    identification: Identification
    certified: bool

    def __post_init__(self):
        if (type(self.certified) is not bool or
            type(self.representation) is not Representation or
            type(self.identification) is not Identification):
            raise ValueError("uncanonical diagnosis")
        if self.certified and (self.representation is Representation.UNCERTIFIED or
                               self.identification is Identification.UNCERTIFIED):
            raise ValueError("cannot certify incomplete diagnosis")


def classify_representation(*, h0_complete_fit: bool, hplus_complete_fit: bool,
                            stochastic_or_invalid: bool = False,
                            exhaustive: bool = True) -> Representation:
    """Classification logic; input truth must be independently established.

    Public-trace consistency alone does NOT prove exhaustive=True.
    H0 is a subset of Hplus. OUTSIDE and STOCHASTIC can be correct negative
    controls, rather than reasons to fail the diagnostic gate.
    """
    if any(type(x) is not bool for x in (h0_complete_fit, hplus_complete_fit,
                                         stochastic_or_invalid, exhaustive)):
        raise ValueError("exact booleans required")
    if not exhaustive:
        return Representation.UNCERTIFIED
    if stochastic_or_invalid:
        if h0_complete_fit or hplus_complete_fit:
            raise ValueError("stochastic evidence needs a distinct contract")
        return Representation.STOCHASTIC
    if h0_complete_fit and not hplus_complete_fit:
        raise ValueError("H0 must be contained in Hplus")
    if h0_complete_fit:
        return Representation.H0
    if hplus_complete_fit:
        return Representation.HPLUS
    return Representation.OUTSIDE


def primary_cell(classification: Classification) -> str | None:
    """Orthogonal 2x2 descriptive cells. OOD safety cases remain separate."""
    if (not classification.certified or
        classification.representation not in (Representation.H0, Representation.HPLUS) or
        classification.identification is Identification.UNCERTIFIED):
        return None
    return classification.representation.value + "__" + classification.identification.value


def g2_diagnostic_gate(cases: tuple[Classification, ...]) -> bool:
    """Gate logic only, not source-authenticated scientific certification.

    N_grammar and N_noise must be correctly classified, NOT fit by Hplus.
    An actual evaluator must check membership claims against independent truth.
    """
    return type(cases) is tuple and bool(cases) and all(
        type(case) is Classification and case.certified for case in cases)


@dataclass(frozen=True)
class IdentificationReceipt:
    status: Identification
    nodes: int
    horizon: int
    hypothesis_count: int
    complete: bool


def identify_finite_class(worlds: tuple[w.PrivateFixture, ...],
                          max_actions: int = 8,
                          max_nodes: int = 50000) -> IdentificationReceipt:
    """Worst-case adaptive decision tree over a DECLARED closed deterministic class.

    All worlds share initial visible state 0. Policy sees ONLY actions/outcomes;
    each of the 12 actions costs one, there are no resets, and every possible
    outcome branch must reduce the candidate class to a single world index.
    The evaluator owns the private list of worlds; no trained learner gets it.
    The result is scoped to max lag <=2 and the supplied finite candidate set.
    """
    if (type(worlds) is not tuple or not worlds or
        any(type(x) is not w.PrivateFixture or x.lag > 2 for x in worlds) or
        type(max_actions) is not int or not 0 <= max_actions <= 8 or
        type(max_nodes) is not int or max_nodes < 1):
        raise ValueError("invalid finite identification scope")
    explored = 0

    class SearchLimit(Exception):
        pass

    @lru_cache(maxsize=None)
    def solve(indices: tuple[int, ...], state: int, history: tuple[w.Action, ...],
              remaining: int) -> bool:
        nonlocal explored
        explored += 1
        if explored > max_nodes:
            raise SearchLimit
        if len(indices) == 1:
            return True
        if remaining == 0:
            return False
        for action in w.all_actions():
            buckets: dict[int, list[int]] = {}
            for idx in indices:
                outcome = w.next_state(worlds[idx], state, history, action)
                buckets.setdefault(outcome, []).append(idx)
            updated_history = (*history, action)[-2:]
            if all(solve(tuple(bucket), outcome, updated_history, remaining - 1)
                   for outcome, bucket in buckets.items()):
                return True
        return False

    try:
        identified = solve(tuple(range(len(worlds))), 0, (), max_actions)
    except SearchLimit:
        return IdentificationReceipt(Identification.UNCERTIFIED, explored,
                                     max_actions, len(worlds), False)
    return IdentificationReceipt(
        Identification.IDENTIFIABLE if identified else Identification.UNIDENTIFIABLE,
        explored, max_actions, len(worlds), True)


def preflight() -> dict[str, object]:
    """Only a bounded-scope negative family feasibility result, not G0b PASS."""
    orbit = w.fixture_role_orbit_upper_bound()
    yes = identify_finite_class((w.PrivateFixture(mode="always"),
                                 w.PrivateFixture(mode="never")), max_actions=1)
    no = identify_finite_class((w.PrivateFixture(source=0,target=1,mode="never"),
                                w.PrivateFixture(source=1,target=0,mode="never")))
    return {
        "schema": "rep005-g0-orthogonal-method/1",
        "status": "ENGINEERING_PRECHECK_NOT_SCIENTIFIC_G0B",
        "inherited_witness_length": w.audit()["shortest_charged_actions"],
        "pilot_structural_orbit_UPPER_BOUND": orbit,
        "pilot_can_supply_80_independent_families": orbit["total"] >= 80,
        "identified_pair": yes.status.value,
        "nonidentified_pair": no.status.value,
        "h0_hplus_truth_membership_full_certification": False,
        "80_independent_families_certified": False,
        "learning_performed": False,
        "scoring_performed": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(preflight(), sort_keys=True, allow_nan=False))

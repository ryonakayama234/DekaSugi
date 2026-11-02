"""EXP-REP-005 G0 ONLY: public-witness feasibility checker.

This is NOT the learner, G1/G2 certification, evaluator or a scored experiment.
The fixture's private world law is used to create controlled public transcripts,
never as an input to public-only inference. No historical data is imported.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product


@dataclass(frozen=True)
class Action:
    kind: str
    object_id: int
    value: int | None = None

    def __post_init__(self):
        if self.kind not in ("set", "pulse"):
            raise ValueError("invalid kind")
        if type(self.object_id) is not int or self.object_id not in range(4):
            raise ValueError("invalid object")
        if (self.kind == "set" and
                (type(self.value) is not int or self.value not in (0, 1))):
            raise ValueError("invalid set value")
        if self.kind == "pulse" and self.value is not None:
            raise ValueError("pulse has no value")


@dataclass(frozen=True)
class PublicEvent:
    ordinal: int
    state_before: int
    action: Action
    state_after: int
    paid_cost: int


@dataclass(frozen=True)
class PrivateFixture:
    source: int = 0
    target: int = 1
    guard: int = 0
    guard_value: int = 0
    lag: int = 1
    mode: str = "guard"

    def __post_init__(self):
        if any(type(x) is not int or x not in range(4)
               for x in (self.source, self.target, self.guard)):
            raise ValueError("invalid roles")
        if self.source == self.target or self.guard_value not in (0, 1):
            raise ValueError("invalid source/target/guard")
        if type(self.lag) is not int or self.lag < 1:
            raise ValueError("invalid lag")
        if self.mode not in ("guard", "always", "never"):
            raise ValueError("invalid mode")


def all_actions() -> tuple[Action, ...]:
    return tuple(Action("set", i, v) for i in range(4) for v in (0, 1)) + tuple(
        Action("pulse", i) for i in range(4)
    )


def next_state(spec: PrivateFixture, state: int,
               previous: tuple[Action, ...], action: Action) -> int:
    """Private source law, called by the trusted fixture only."""
    if type(state) is not int or state not in range(16):
        raise ValueError("invalid visible state")
    if action.kind == "set":
        mask = 1 << action.object_id
        return (state | mask) if action.value else (state & ~mask)
    if action.object_id != spec.source or spec.mode == "never":
        return state
    if spec.mode == "always":
        return state ^ (1 << spec.target)
    enabled = len(previous) >= spec.lag and previous[-spec.lag] == Action(
        "set", spec.guard, spec.guard_value
    )
    return (state ^ (1 << spec.target)) if enabled else state


def public_trace(spec: PrivateFixture,
                 actions: tuple[Action, ...]) -> tuple[PublicEvent, ...]:
    """One paid action per event, no free environment reset."""
    state = 0
    previous: tuple[Action, ...] = ()
    events: list[PublicEvent] = []
    for i, action in enumerate(actions):
        future = next_state(spec, state, previous, action)
        events.append(PublicEvent(i, state, action, future, 1))
        previous += (action,)
        state = future
    return tuple(events)


def validate_public(events: tuple[PublicEvent, ...]) -> None:
    state = 0
    for i, event in enumerate(events):
        if type(event) is not PublicEvent or type(event.action) is not Action:
            raise ValueError("uncanonical event")
        if (type(event.ordinal) is not int or event.ordinal != i or
                type(event.paid_cost) is not int or event.paid_cost != 1 or
                type(event.state_before) is not int or
                type(event.state_after) is not int or
                event.state_before not in range(16) or
                event.state_after not in range(16) or
                event.state_before != state):
            raise ValueError("invalid paid chronology")
        state = event.state_after


def memoryless_conflict(events: tuple[PublicEvent, ...]) -> (
        tuple[int, int] | None):
    """Proof against ALL deterministic f(visible state, action), not just H0 catalogue."""
    validate_public(events)
    seen: dict[tuple[int, Action], tuple[int, int]] = {}
    for event in events:
        key = (event.state_before, event.action)
        old = seen.get(key)
        if old is not None and old[0] != event.state_after:
            return (old[1], event.ordinal)
        seen[key] = (event.state_after, event.ordinal)
    return None


def _candidate_predict(source: int, target: int, guard: int, value: int,
                       lag: int, mode: str, state: int,
                       prev: tuple[Action, ...], action: Action) -> int:
    if action.kind == "set":
        mask = 1 << action.object_id
        return (state | mask) if action.value else (state & ~mask)
    if action.object_id != source or mode == "never":
        return state
    if mode == "always":
        return state ^ (1 << target)
    active = len(prev) >= lag and prev[-lag] == Action("set", guard, value)
    return state ^ (1 << target) if active else state


def public_consistent_hplus(events: tuple[PublicEvent, ...],
                            max_lag: int = 2) -> int:
    """Count typed grammar matches using PUBLIC data only.

    Enumerates 4x3 legal source/target role bindings, 4 guard bindings,
    2 public values and allowed lags. Never accepts a hidden fixture object.
    This is evidence of expressibility, NOT learner invention.
    """
    validate_public(events)
    count = 0
    for source in range(4):
        for target in range(4):
            if source == target:
                continue
            for mode, guard, value, lag in (
                [("always", 0, 0, 1), ("never", 0, 0, 1)] +
                [("guard", g, v, k) for g in range(4)
                 for v in (0, 1) for k in range(1, max_lag + 1)]
            ):
                history: tuple[Action, ...] = ()
                for e in events:
                    predicted = _candidate_predict(source, target, guard, value, lag,
                                                   mode, e.state_before, history,
                                                   e.action)
                    if predicted != e.state_after:
                        break
                    history += (e.action,)
                else:
                    count += 1
    return count


def find_minimum_witness(spec: PrivateFixture,
                         max_actions: int = 3) -> tuple[Action, ...] | None:
    """Brute-force finite action search for a deterministic H0 contradiction."""
    alphabet = all_actions()
    for size in range(1, max_actions + 1):
        for sequence in product(alphabet, repeat=size):
            if memoryless_conflict(public_trace(spec, sequence)) is not None:
                return sequence
    return None


def permuted(spec: PrivateFixture, order: tuple[int, ...]) -> PrivateFixture:
    if tuple(sorted(order)) != (0, 1, 2, 3):
        raise ValueError("not a permutation")
    return PrivateFixture(
        source=order[spec.source], target=order[spec.target],
        guard=order[spec.guard], guard_value=spec.guard_value,
        lag=spec.lag, mode=spec.mode,
    )


def permute_actions(actions: tuple[Action, ...],
                    order: tuple[int, ...]) -> tuple[Action, ...]:
    return tuple(Action(a.kind, order[a.object_id], a.value) for a in actions)


def audit() -> dict[str, object]:
    spec = PrivateFixture()
    witness = find_minimum_witness(spec)
    if witness is None:
        raise AssertionError("no witness within 3 paid actions")
    result = public_trace(spec, witness)
    witnesses = sum(
        memoryless_conflict(public_trace(permuted(spec, p),
                                        permute_actions(witness, p))) is not None and
        public_consistent_hplus(public_trace(permuted(spec, p),
                                             permute_actions(witness, p))) > 0
        for p in permutations(range(4))
    )
    if witnesses != 24:
        raise AssertionError("role invariance failed")
    return {
        "schema": "rep005-g0-feasibility/1",
        "status": "method_feasibility_only_not_certified",
        "shortest_charged_actions": len(witness),
        "shortest_witness": [repr(a) for a in witness],
        "h0_universal_memoryless_conflict": memoryless_conflict(result) is not None,
        "hplus_consistent_public_models": public_consistent_hplus(result),
        "role_permutations_checked": witnesses,
        "learning_performed": False,
        "scoring_performed": False,
        "distinct_structural_families_verified": False,
    }

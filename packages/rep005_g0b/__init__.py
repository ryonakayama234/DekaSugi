"""EXP-REP-005 G0b-A: source-only finite causal-world engineering laboratory.

No learner, historical evaluator or scored dataset is imported. This is an
invented fixture certifier, NOT a scientific sample or a trained model.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, permutations, product
from functools import lru_cache
import json

SCHEMA = "rep005-g0b-pilot/1"
OBJECTS = range(4)
FULL_CELLS = 16 * 157 * 12
DEFAULT_MAX_NODES = 250_000


def digest(x: object) -> str:
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class Action:
    kind: str
    obj: int
    value: int = -1

    def __post_init__(self) -> None:
        if (type(self.kind) is not str or self.kind not in ("set", "pulse")
            or type(self.obj) is not int or self.obj not in OBJECTS
            or type(self.value) is not int
            or (self.kind == "pulse" and self.value != -1)
            or (self.kind == "set" and self.value not in (0, 1))):
            raise ValueError("invalid public action")

    def key(self) -> tuple:
        return (self.kind, self.obj, self.value)


ACTIONS = tuple(Action("set", i, v) for i in OBJECTS for v in (0, 1)) + tuple(Action("pulse", i) for i in OBJECTS)
HISTORIES = ((),) + tuple((a,) for a in ACTIONS) + tuple(product(ACTIONS, repeat=2))


@dataclass(frozen=True, slots=True)
class Literal:
    kind: str
    obj: int
    value: int = -1
    lag: int = 0

    def __post_init__(self) -> None:
        if (type(self.kind) is not str or self.kind not in ("bit", "prev_set", "prev_pulse")
            or type(self.obj) is not int or self.obj not in OBJECTS
            or type(self.value) is not int or type(self.lag) is not int
            or (self.kind == "bit" and (self.lag != 0 or self.value not in (0, 1)))
            or (self.kind == "prev_set" and (self.lag not in (1, 2) or self.value not in (0, 1)))
            or (self.kind == "prev_pulse" and (self.lag not in (1, 2) or self.value != -1))):
            raise ValueError("invalid typed literal")

    def key(self) -> tuple:
        return (self.kind, self.obj, self.value, self.lag)


@dataclass(frozen=True, slots=True)
class Edge:
    source: int
    target: int
    lag: int = 0
    guard: tuple[Literal, ...] = ()

    def __post_init__(self) -> None:
        if (type(self.source) is not int or self.source not in OBJECTS
            or type(self.target) is not int or self.target not in OBJECTS
            or self.source == self.target or type(self.lag) is not int
            or self.lag not in (0, 1, 2) or type(self.guard) is not tuple
            or len(self.guard) > 2 or any(type(g) is not Literal for g in self.guard)
            or tuple(sorted(self.guard, key=lambda x: x.key())) != self.guard
            or len(set(self.guard)) != len(self.guard)):
            raise ValueError("noncanonical typed edge")
        for a, b in combinations(self.guard, 2):
            if a.kind == b.kind == "bit" and a.obj == b.obj and a.value != b.value:
                raise ValueError("contradictory bit guard")
            if a.kind.startswith("prev") and b.kind.startswith("prev") and a.lag == b.lag and a != b:
                raise ValueError("contradictory past-action guard")

    def key(self) -> tuple:
        return (self.source, self.target, self.lag, tuple(g.key() for g in self.guard))


@dataclass(frozen=True, slots=True)
class Law:
    edges: tuple[Edge, ...]

    def __post_init__(self) -> None:
        if (type(self.edges) is not tuple or len(self.edges) > 2
            or any(type(e) is not Edge for e in self.edges)
            or self.edges != tuple(sorted(self.edges, key=lambda x: x.key()))
            or len(set(self.edges)) != len(self.edges)):
            raise ValueError("noncanonical typed law")

    def key(self) -> tuple:
        return tuple(e.key() for e in self.edges)


def law(*edges: Edge) -> Law:
    return Law(tuple(sorted(edges, key=lambda x: x.key())))


def check_public(state: int, history: tuple[Action, ...], action: Action | None = None) -> None:
    if (type(state) is not int or not 0 <= state < 16
        or type(history) is not tuple or len(history) > 2
        or any(type(a) is not Action for a in history)
        or (action is not None and type(action) is not Action)):
        raise ValueError("invalid public state/history")


def literal_holds(g: Literal, state: int, history: tuple[Action, ...]) -> bool:
    if g.kind == "bit":
        return ((state >> g.obj) & 1) == g.value
    if len(history) < g.lag:
        return False
    a = history[-g.lag]
    return a.obj == g.obj and (
        (g.kind == "prev_pulse" and a.kind == "pulse")
        or (g.kind == "prev_set" and a.kind == "set" and a.value == g.value))


def transition(model: Law, state: int, history: tuple[Action, ...], action: Action) -> tuple[int, tuple[Action, ...]]:
    if type(model) is not Law:
        raise ValueError("untrusted law type")
    check_public(state, history, action)
    base = state
    if action.kind == "set":
        base = (base & ~(1 << action.obj)) | (action.value << action.obj)
    mask = 0
    for e in model.edges:
        trigger = action if e.lag == 0 else (history[-e.lag] if len(history) >= e.lag else None)
        if trigger == Action("pulse", e.source) and all(literal_holds(g, state, history) for g in e.guard):
            mask ^= 1 << e.target
    return base ^ mask, (history + (action,))[-2:]


def full_signature(model: Law) -> bytes:
    """30,144 complete typed-domain outputs: NOT the reachable public domain."""
    result = bytearray()
    for state in range(16):
        for hist in HISTORIES:
            for a in ACTIONS:
                result.append(transition(model, state, hist, a)[0])
    if len(result) != FULL_CELLS:
        raise AssertionError("signature domain incomplete")
    return bytes(result)


def permute_action(a: Action, p: tuple[int, ...]) -> Action:
    return Action(a.kind, p[a.obj], a.value)


def permute_law(model: Law, p: tuple[int, ...]) -> Law:
    if type(p) is not tuple or sorted(p) != list(OBJECTS):
        raise ValueError("not a 4-object permutation")
    return law(*(Edge(p[e.source], p[e.target], e.lag, tuple(sorted(
        (Literal(g.kind, p[g.obj], g.value, g.lag) for g in e.guard), key=lambda x: x.key())))
        for e in model.edges))


def permute_state(state: int, p: tuple[int, ...]) -> int:
    if type(state) is not int or not 0 <= state < 16 or type(p) is not tuple or sorted(p) != list(OBJECTS):
        raise ValueError("invalid permutation")
    return sum(((state >> i) & 1) << p[i] for i in OBJECTS)


def role_key(model: Law) -> tuple:
    """Syntactic typed mechanism role orbit; distinct from semantic-equivalence proof."""
    return min(permute_law(model, p).key() for p in permutations(OBJECTS))


def reachable_domain(model: Law, depth: int = 8) -> dict[tuple, int]:
    if type(depth) is not int or not 0 <= depth <= 8:
        raise ValueError("depth outside preregistered pilot")
    seen = {(0, ())}
    fringe = deque([(0, (), 0)])
    evidence: dict[tuple, int] = {}
    while fringe:
        state, hist, d = fringe.popleft()
        if d == depth:
            continue
        for a in ACTIONS:
            new_state, new_hist = transition(model, state, hist, a)
            key = (state, tuple(x.key() for x in hist), a.key())
            evidence[key] = new_state
            dest = (new_state, new_hist)
            if dest not in seen:
                seen.add(dest)
                fringe.append((new_state, new_hist, d + 1))
    return evidence


def memoryless_contradiction(model: Law, max_depth: int = 3) -> dict | None:
    """Two REAL reset-from-0 public prefixes, same (state,action), unequal successor."""
    if type(max_depth) is not int or not 0 <= max_depth <= 8:
        raise ValueError("bad witness depth")
    fringe = deque([(0, (), ())])
    seen = {(0, ())}
    observed: dict[tuple[int, Action], tuple[int, tuple[Action, ...]]] = {}
    while fringe:
        state, hist, prefix = fringe.popleft()
        if len(prefix) >= max_depth:
            continue
        for a in ACTIONS:
            nxt, new_hist = transition(model, state, hist, a)
            k = (state, a)
            if k in observed and observed[k][0] != nxt:
                other, first_prefix = observed[k]
                return {"state": state, "action": a.key(),
                        "prefix_a": tuple(x.key() for x in first_prefix),
                        "prefix_b": tuple(x.key() for x in prefix),
                        "successor_a": other, "successor_b": nxt}
            observed.setdefault(k, (nxt, prefix))
            dest = (nxt, new_hist)
            if dest not in seen:
                seen.add(dest)
                fringe.append((nxt, new_hist, prefix + (a,)))
    return None


class ProofLimit(Exception):
    pass


def _candidate_set(models: tuple[Law, ...]) -> tuple[str, ...]:
    if type(models) is not tuple or not models or any(type(w) is not Law for w in models):
        raise ValueError("bad finite hypothesis class")
    signatures = [full_signature(w) for w in models]
    if len(set(signatures)) != len(models):
        raise ValueError("semantic alias in closed hypothesis class")
    return tuple(sha256(sig).hexdigest() for sig in signatures)


def adaptive_identification(models: tuple[Law, ...], budget: int = 8,
                            max_nodes: int = DEFAULT_MAX_NODES) -> dict:
    """Complete worst-case adaptive decision-tree search; NOT_CERTIFIED on node limit.

    A node includes the shared *observed* state, common public action history,
    remaining semantic candidate indices and remaining paid budget.
    """
    ids = _candidate_set(models)
    if type(budget) is not int or not 0 <= budget <= 8 or type(max_nodes) is not int or max_nodes < 0:
        raise ValueError("invalid proof bound")
    nodes = 0
    memo: dict[tuple, tuple[bool, tuple | None]] = {}

    def solve(remaining: tuple[int, ...], state: int, hist: tuple[Action, ...], left: int):
        nonlocal nodes
        k = (remaining, state, hist, left)
        if k in memo:
            return memo[k]
        nodes += 1
        if nodes > max_nodes:
            raise ProofLimit
        if len(remaining) <= 1:
            memo[k] = (True, None)
            return memo[k]
        if left == 0:
            memo[k] = (False, None)
            return memo[k]
        for a in ACTIONS:
            groups: dict[int, list[int]] = {}
            for i in remaining:
                new_state, _ = transition(models[i], state, hist, a)
                groups.setdefault(new_state, []).append(i)
            children = []
            works = True
            for obs, grp in sorted(groups.items()):
                nxt_hist = (hist + (a,))[-2:]
                ok, child = solve(tuple(grp), obs, nxt_hist, left - 1)
                if not ok:
                    works = False
                    break
                children.append((obs, child))
            if works:
                memo[k] = (True, (a.key(), tuple(children)))
                return memo[k]
        memo[k] = (False, None)
        return memo[k]

    try:
        ok, tree = solve(tuple(range(len(models))), 0, (), budget)
        status = "ID" if ok else "UNID"
    except ProofLimit:
        tree, status = None, "NOT_CERTIFIED"
    return {"schema": SCHEMA, "status": status, "candidate_digest": digest(ids),
            "budget": budget, "nodes": nodes, "max_nodes": max_nodes,
            "witness_tree": tree if status == "ID" else None}


def action_opportunity(models: tuple[Law, ...], budget: int = 1,
                       baseline: Action = ACTIONS[0], max_nodes: int = DEFAULT_MAX_NODES) -> dict:
    """Source-only exact optimal vs fixed-action identification utility.

    Uniform prior, terminal MAP hypothesis accuracy = #nonempty leaves / N.
    The returned full tree is a FEASIBLE policy witness; not a relaxed upper bound.
    """
    ids = _candidate_set(models)
    if (type(budget) is not int or not 0 <= budget <= 8
        or type(max_nodes) is not int or max_nodes < 0 or type(baseline) is not Action):
        raise ValueError("invalid opportunity input")
    nodes = 0
    memo: dict[tuple, tuple[int, tuple | None]] = {}

    def split(remaining: tuple[int, ...], state: int, hist: tuple[Action, ...], a: Action):
        groups: dict[int, tuple[int, ...]] = {}
        found: dict[int, list[int]] = {}
        for i in remaining:
            obs, _ = transition(models[i], state, hist, a)
            found.setdefault(obs, []).append(i)
        return {k: tuple(v) for k, v in found.items()}

    def best(remaining: tuple[int, ...], state: int, hist: tuple[Action, ...], left: int):
        nonlocal nodes
        k = (remaining, state, hist, left)
        if k in memo:
            return memo[k]
        nodes += 1
        if nodes > max_nodes:
            raise ProofLimit
        if len(remaining) == 1 or left == 0:
            memo[k] = (1, None)
            return memo[k]
        current = (0, None)
        for a in ACTIONS:
            groups = split(remaining, state, hist, a)
            children = []
            total = 0
            for obs, grp in sorted(groups.items()):
                leaves, child = best(grp, obs, (hist + (a,))[-2:], left - 1)
                total += leaves
                children.append((obs, child))
            if total > current[0]:
                current = (total, (a.key(), tuple(children)))
            if total == len(remaining):
                break  # no legal policy can exceed one identified leaf per candidate
        memo[k] = current
        return current

    def fixed(remaining: tuple[int, ...], state: int, hist: tuple[Action, ...], left: int):
        if len(remaining) <= 1 or left == 0:
            return 1
        return sum(fixed(grp, obs, (hist + (baseline,))[-2:], left - 1)
                   for obs, grp in split(remaining, state, hist, baseline).items())

    try:
        leaves, tree = best(tuple(range(len(models))), 0, (), budget)
        fixed_leaves = fixed(tuple(range(len(models))), 0, (), budget)
        status = "POSITIVE" if leaves > fixed_leaves else "NO_OPPORTUNITY"
        return {"schema": SCHEMA, "status": status, "candidate_digest": digest(ids),
                "budget": budget, "nodes": nodes, "max_nodes": max_nodes,
                "baseline_action": baseline.key(), "optimal_value": leaves / len(models),
                "baseline_value": fixed_leaves / len(models),
                "feasible_policy_tree": tree, "prior": "uniform",
                "utility": "terminal-MAP-identification-accuracy"}
    except ProofLimit:
        return {"schema": SCHEMA, "status": "NOT_CERTIFIED",
                "candidate_digest": digest(ids), "budget": budget, "nodes": nodes,
                "max_nodes": max_nodes, "baseline_action": baseline.key()}


def witness_pilot_worlds() -> tuple[tuple[str, Law], ...]:
    """Small disclosed source-only fixture, NOT an exhaustive full grammar census."""
    bit = lambda i, v: (Literal("bit", i, v),)
    return (
        ("null", law()),
        ("direct", law(Edge(0, 1))),
        ("lag1", law(Edge(0, 1, 1))),
        ("lag2", law(Edge(0, 1, 2))),
        ("guard", law(Edge(0, 1, 0, bit(2, 1)))),
        ("two_edges", law(Edge(0, 1), Edge(1, 2))),
        ("cancel", law(Edge(0, 1), Edge(0, 1, 0, bit(2, 1)))),
        ("history_guard", law(Edge(0, 1, 0, (Literal("prev_pulse", 2, -1, 1),)))),
    )


def pilot_census() -> dict:
    """Attained CERTIFIED fixture counts; DO NOT extrapolate to full Hplus_G."""
    fixtures = witness_pilot_worlds()
    total_semantics: dict[bytes, list[str]] = {}
    structural: dict[tuple, list[str]] = {}
    rows = []
    for tag, model in fixtures:
        sig = full_signature(model)
        total_semantics.setdefault(sig, []).append(tag)
        structural.setdefault(role_key(model), []).append(tag)
        reach = reachable_domain(model, 8)
        rows.append({"fixture": tag, "total_digest": sha256(sig).hexdigest(),
                     "reachable_cells": len(reach),
                     "reachable_digest": digest(sorted((str(k), v) for k, v in reach.items())),
                     "memoryless_contradiction": memoryless_contradiction(model) is not None,
                     "constructed_H0_G": all(e.lag == 0 and all(g.kind == "bit" for g in e.guard)
                                            for e in model.edges)})
    pair = (fixtures[0][1], fixtures[1][1])
    proof_id = adaptive_identification(pair, 8)
    proof_op = action_opportunity(pair, 1)
    return {"schema": SCHEMA, "status": "G0B_STOP_FULL_GRAMMAR_NOT_ENUMERATED",
            "fixture_instances": len(fixtures),
            "distinct_full_semantics": len(total_semantics),
            "typed_role_orbits": len(structural),
            "observational_reachable_scope": "depth<=8 from all-zero initial",
            "full_cells_per_law": FULL_CELLS,
            "rows": rows, "sample_identification": proof_id,
            "sample_action_opportunity": proof_op,
            "independent_family_count": "NOT_CERTIFIED",
            "H0_G_Hplus_G_full_membership": "NOT_CERTIFIED",
            "M2_M3_cohorts": "NOT_CONSTRUCTED",
            "statistical_power": "NOT_ESTIMATED",
            "science_train_score": "NOT_RUN"}


def main() -> None:
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Synthetic-source-only G0b-A engineering feasibility")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = pilot_census()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("rows", "sample_identification", "sample_action_opportunity")},
                     sort_keys=True))


if __name__ == "__main__":
    main()

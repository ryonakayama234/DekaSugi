"""REP005 V4-C1: finite PRIVATE constructive causal source and source-only certificates.

This module is private to the laboratory evaluator. Do not import it in a learner.
No full historical Hplus_G census or independently powered study is implied.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import permutations, product
from time import monotonic
from typing import Literal
import hashlib

N = 5
BUDGET = 8
ACTIONS = tuple([("set", i, b) for i in range(N) for b in (0, 1)] +
                [("pulse", i, -1) for i in range(N)])
ACTION_INDEX = {action: k for k, action in enumerate(ACTIONS)}
HISTORIES = ((),) + tuple((a,) for a in ACTIONS) + tuple(product(ACTIONS, repeat=2))
HIST_INDEX = {h: i for i, h in enumerate(HISTORIES)}
DOMAIN_CELLS = (1 << N) * len(HISTORIES) * len(ACTIONS)
assert DOMAIN_CELLS == 115_680
Action = tuple[str, int, int]
History = tuple[Action, ...]


@dataclass(frozen=True)
class Atom:
    kind: Literal["bit", "pulse", "set"]
    role: int
    value: int = -1
    lag: int = 0

    def __post_init__(self):
        if type(self.role) is not int or not 0 <= self.role < N:
            raise ValueError("invalid atom role")
        if self.kind == "bit":
            if type(self.value) is not int or self.value not in (0, 1) or self.lag != 0:
                raise ValueError("invalid current-bit atom")
        elif self.kind in ("pulse", "set"):
            if self.lag not in (1, 2):
                raise ValueError("invalid public history lag")
            if (self.kind == "pulse" and self.value != -1) or (
                self.kind == "set" and self.value not in (0, 1)
            ):
                raise ValueError("invalid previous-action atom")
        else:
            raise ValueError("unrecognized atom")


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    lag: int = 0
    guard: tuple[Atom, ...] = ()

    def __post_init__(self):
        if type(self.source) is not int or type(self.target) is not int:
            raise ValueError("roles must be int")
        if not (0 <= self.source < N and 0 <= self.target < N) or self.source == self.target:
            raise ValueError("edge endpoints")
        if type(self.lag) is not int or self.lag not in (0, 1, 2):
            raise ValueError("trigger lag")
        if len(self.guard) > 2 or len(set(self.guard)) != len(self.guard):
            raise ValueError("duplicate or oversized guard")
        if tuple(sorted(self.guard, key=repr)) != self.guard:
            raise ValueError("guard not canonical")
        if any(a.kind == "bit" and b.kind == "bit"
               and a.role == b.role and a.value != b.value
               for a in self.guard for b in self.guard):
            raise ValueError("contradictory bit guard")
        if any(a.kind != "bit" and b.kind != "bit" and a.lag == b.lag and a != b
               for a in self.guard for b in self.guard):
            raise ValueError("mutually exclusive previous action")


def guarded(*atoms: Atom) -> tuple[Atom, ...]:
    return tuple(sorted(atoms, key=repr))


@dataclass(frozen=True)
class Law:
    edges: tuple[Edge, ...] = ()

    def __post_init__(self):
        if len(self.edges) > 2 or len(self.edges) != len(set(self.edges)):
            raise ValueError("law needs 0..2 distinct edges")
        if tuple(sorted(self.edges, key=repr)) != self.edges:
            raise ValueError("edge list must be canonical")


def law(*edges: Edge) -> Law:
    return Law(tuple(sorted(edges, key=repr)))


@dataclass(frozen=True)
class ConstructiveCandidate:
    source_root: str
    constructor: str
    parents: tuple[str, ...]
    model: Law


@dataclass(frozen=True)
class PublicStep:
    before: int
    history: History
    action: Action
    after: int
    paid_cost: int = 1


def validate_action(a: Action) -> None:
    if type(a) is not tuple or len(a) != 3 or a not in ACTION_INDEX:
        raise ValueError("not a typed legal action")
    if type(a[1]) is not int or type(a[2]) is not int:
        raise ValueError("not a typed int action")


def validate_public_step(step: PublicStep) -> None:
    if type(step) is not PublicStep:
        raise ValueError("wrong public step type")
    if type(step.before) is not int or type(step.after) is not int:
        raise ValueError("invalid bit state type")
    if not (0 <= step.before < (1 << N) and 0 <= step.after < (1 << N)):
        raise ValueError("out-of-range visible state")
    if type(step.history) is not tuple or step.history not in HIST_INDEX:
        raise ValueError("not a public action history")
    validate_action(step.action)
    if type(step.paid_cost) is not int or step.paid_cost != 1:
        raise ValueError("wrong paid cost")


def _matches(a: Atom, x: int, hist: History) -> bool:
    if a.kind == "bit":
        return ((x >> a.role) & 1) == a.value
    if len(hist) < a.lag:
        return False
    past = hist[-a.lag]
    return past == (a.kind, a.role, a.value)


def _trigger(edge: Edge, hist: History, action: Action) -> bool:
    if edge.lag == 0:
        return action == ("pulse", edge.source, -1)
    return len(hist) >= edge.lag and hist[-edge.lag] == ("pulse", edge.source, -1)


def step(model: Law, x: int, hist: History, action: Action) -> tuple[int, History]:
    validate_action(action)
    if type(x) is not int or not 0 <= x < (1 << N) or hist not in HIST_INDEX:
        raise ValueError("invalid state/history")
    base = x
    if action[0] == "set":
        base = (x & ~(1 << action[1])) | (action[2] << action[1])
    parity_mask = 0
    for e in model.edges:
        if _trigger(e, hist, action) and all(_matches(g, x, hist) for g in e.guard):
            parity_mask ^= (1 << e.target)
    return base ^ parity_mask, (hist + (action,))[-2:]


def full_signature(model: Law) -> bytes:
    """Authoritative complete typed-domain semantics, not just reachable prefixes."""
    out = bytearray(DOMAIN_CELLS)
    p = 0
    for x in range(1 << N):
        for hist in HISTORIES:
            for a in ACTIONS:
                out[p] = step(model, x, hist, a)[0]
                p += 1
    return bytes(out)


def rename_action(a: Action, p: tuple[int, ...]) -> Action:
    return a[0], p[a[1]], a[2]


def rename_bitmask(x: int, p: tuple[int, ...]) -> int:
    return sum((((x >> i) & 1) << p[i]) for i in range(N))


def permute_signature(sig: bytes, p: tuple[int, ...]) -> bytes:
    """Exact conjugation under public simultaneous role permutation."""
    if len(sig) != DOMAIN_CELLS or sorted(p) != list(range(N)):
        raise ValueError("bad permutation or signature")
    xs = tuple(rename_bitmask(x, p) for x in range(1 << N))
    hs = tuple(HIST_INDEX[tuple(rename_action(a, p) for a in h)] for h in HISTORIES)
    acts = tuple(ACTION_INDEX[rename_action(a, p)] for a in ACTIONS)
    result = bytearray(DOMAIN_CELLS)
    width = len(ACTIONS)
    hsize = len(HISTORIES)
    for x, nx in enumerate(xs):
        old_block, new_block = x * hsize * width, nx * hsize * width
        for hi, nhi in enumerate(hs):
            from_base, to_base = old_block + hi * width, new_block + nhi * width
            for ai, nai in enumerate(acts):
                result[to_base + nai] = xs[sig[from_base + ai]]
    return bytes(result)


def canonical_semantic_orbit(sig: bytes) -> bytes:
    """Enumerate ALL 120 renamings; exact canonical bytes, digest only for display."""
    return min(permute_signature(sig, p) for p in permutations(range(N)))


def _source_motifs() -> tuple[ConstructiveCandidate, ...]:
    """Predeclared, disclosed constructor roots; not an independent-world population."""
    constructors = (
        ("null", law()),
        ("direct", law(Edge(0, 1))),
        ("lag1", law(Edge(0, 1, 1))),
        ("lag2", law(Edge(0, 1, 2))),
        ("current_bit_gate", law(Edge(0, 1, 0, guarded(Atom("bit", 2, 1))))),
        ("past_pulse_gate", law(Edge(0, 1, 0, guarded(Atom("pulse", 2, -1, 1))))),
        ("and_gate", law(Edge(0, 1, 0, guarded(Atom("bit", 2, 1),
                                                   Atom("pulse", 3, -1, 1))))),
        ("chain", law(Edge(0, 1, 0), Edge(1, 2, 1))),
        ("fanout", law(Edge(0, 1, 0), Edge(0, 2, 0))),
        ("convergent", law(Edge(0, 2, 0), Edge(1, 2, 0))),
        ("inhibitory", law(Edge(0, 1, 0, guarded(Atom("bit", 2, 0))))),
        ("feedback", law(Edge(0, 1, 0), Edge(1, 0, 1))),
    )
    return tuple(ConstructiveCandidate("C1/" + name, name, (), m)
                 for name, m in constructors)


def certificate_catalog(max_candidates: int = 12) -> dict:
    """Exact finite pilot source census; NO inference about 100M historical laws."""
    if type(max_candidates) is not int or not 0 < max_candidates <= 12:
        raise ValueError("bounded source pilot only")
    seen: dict[bytes, str] = {}
    records = []
    started = monotonic()
    for source in _source_motifs()[:max_candidates]:
        sig = full_signature(source.model)
        orbit = canonical_semantic_orbit(sig)
        representative = seen.get(orbit)
        if representative is None:
            seen[orbit] = source.source_root
        records.append({
            "constructor": source.constructor,
            "source_root": source.source_root,
            "parent_roots": list(source.parents),
            "full_signature_sha256": hashlib.sha256(sig).hexdigest(),
            "role_orbit_sha256": hashlib.sha256(orbit).hexdigest(),
            "exact_orbit_alias_of": representative,
            "full_signature_cells": len(sig),
            "role_permutations": 120,
        })
    return {
        "grammar": "Constructive-C1-draft-source-pilot",
        "raw_named_constructor_count": len(records),
        "nonalias_exact_semantic_orbits": len(seen),
        "source_roots_proposed_not_independent_certified": len(records),
        "verified_closed_full_Hplus_G": False,
        "historic_full_Hplus_G_status": "NOT_CERTIFIED",
        "elapsed_wall_seconds": round(monotonic() - started, 3),
        "records": records,
    }


def legal_closed_class_id(
    models: tuple[Law, ...], budget: int, *,
    max_nodes: int = 250_000, deadline_seconds: float = 120,
) -> dict:
    """Complete worst-case public adaptive decision tree for declared C, or NOT_CERTIFIED.

    Exact UNID is relative only to this declared C, the common initial state and B.
    """
    if type(budget) is not int or not 0 <= budget <= BUDGET:
        raise ValueError("invalid budget")
    if len(models) == 0 or len(models) > 64:
        return {"status": "NOT_CERTIFIED", "reason": "CLASS_SIZE_CAP", "nodes": 0}
    if len(set(full_signature(m) for m in models)) != len(models):
        return {"status": "NOT_CERTIFIED", "reason": "SEMANTIC_DUPLICATES", "nodes": 0}
    started = monotonic()
    visited = 0
    cache = {}

    class ResourceStop(Exception):
        pass

    def recurse(ixs: tuple[int, ...], state: int, hist: History, b: int):
        nonlocal visited
        key = ixs, state, hist, b
        if key in cache:
            return cache[key]
        visited += 1
        if visited > max_nodes or monotonic() - started > deadline_seconds:
            raise ResourceStop
        if len(ixs) == 1:
            return {"model": ixs[0]}
        if b == 0:
            cache[key] = None
            return None
        for a in ACTIONS:
            groups: dict[int, list[int]] = {}
            for j in ixs:
                sx, _ = step(models[j], state, hist, a)
                groups.setdefault(sx, []).append(j)
            branches = {}
            ok = True
            for outcome, group in groups.items():
                subtree = recurse(tuple(group), outcome, (hist + (a,))[-2:], b - 1)
                if subtree is None:
                    ok = False
                    break
                branches[str(outcome)] = subtree
            if ok:
                tree = {"action": list(a), "branches": branches}
                cache[key] = tree
                return tree
        cache[key] = None
        return None

    try:
        tree = recurse(tuple(range(len(models))), 0, (), budget)
    except ResourceStop:
        return {"status": "NOT_CERTIFIED", "reason": "PROOF_RESOURCE_CAP", "nodes": visited}
    return {"status": "ID" if tree is not None else "UNID",
            "budget": budget, "nodes": visited, "witness_tree": tree}


def memorylessness_witness(model: Law) -> dict | None:
    """Find an actual single-world legal same-(visible state, action) contradiction."""
    from collections import deque
    queue = deque([(0, (), ())])
    visited = {(0, ())}
    matched: dict[tuple[int, Action], tuple[int, tuple[Action, ...]]] = {}
    while queue:
        x, hist, prefix = queue.popleft()
        for a in ACTIONS:
            nxt, nh = step(model, x, hist, a)
            key = (x, a)
            previous = matched.get(key)
            if previous is not None and previous[0] != nxt:
                return {
                    "before": x, "action": list(a),
                    "first_after": previous[0], "second_after": nxt,
                    "first_prefix": [list(v) for v in previous[1]],
                    "second_prefix": [list(v) for v in prefix],
                    "scope": "one stationary source world; legal public prefixes",
                }
            matched.setdefault(key, (nxt, prefix))
            if len(prefix) + 1 < BUDGET and (nxt, nh) not in visited:
                visited.add((nxt, nh))
                queue.append((nxt, nh, prefix + (a,)))
    return None


def feasible_fixed_opportunity(a: Law, b: Law, adaptive_action: Action,
                               baseline_action: Action) -> dict:
    """One paid question, equiprobable closed two-world class, terminal MAP."""
    validate_action(adaptive_action)
    validate_action(baseline_action)
    def terminal_accuracy(action: Action) -> float:
        observations = {step(m, 0, (), action)[0] for m in (a, b)}
        return 1.0 if len(observations) == 2 else 0.5
    adaptive = terminal_accuracy(adaptive_action)
    fixed = terminal_accuracy(baseline_action)
    return {"horizon": 1, "prior": [0.5, 0.5],
            "legal_feasible_action": list(adaptive_action),
            "nonadaptive_fixed_action": list(baseline_action),
            "terminal_MAP_feasible": adaptive,
            "terminal_MAP_fixed": fixed,
            "gap": adaptive - fixed,
            "status": "POSITIVE" if adaptive > fixed else "ZERO"}


class PrivateWorld:
    """Source-owned in-memory pilot. Never hand object or its Law to the learner."""

    def __init__(self, model: Law):
        if type(model) is not Law:
            raise ValueError("private Law type")
        self._model = model
        self.x = 0
        self.hist: History = ()
        self.paid = 0

    def observe_paid(self, action: Action) -> PublicStep:
        validate_action(action)
        if self.paid >= BUDGET:
            raise ValueError("no free step beyond paid budget")
        before, hist = self.x, self.hist
        self.x, self.hist = step(self._model, before, hist, action)
        self.paid += 1
        item = PublicStep(before, hist, action, self.x, 1)
        validate_public_step(item)
        return item


def verify_public_chronology(trace: tuple[PublicStep, ...]) -> None:
    if len(trace) > BUDGET:
        raise ValueError("episode over budget")
    x, hist = 0, ()
    for record in trace:
        validate_public_step(record)
        if record.before != x or record.history != hist:
            raise ValueError("forged public chronology")
        x, hist = record.after, (hist + (record.action,))[-2:]

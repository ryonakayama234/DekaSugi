"""G0C source-only finite causal laboratory; never import into a learner.

Declared universe: five visible Boolean variables, 15 typed actions, and
at most two previous actions. Certification claims are finite and scoped.
This is source engineering, not learned intelligence or independent science.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import permutations, product
from hashlib import sha256
from time import monotonic

N = 5
ACTIONS = tuple(("set", i, v) for i in range(N) for v in (0, 1)) + tuple(
    ("pulse", i, -1) for i in range(N))
HISTORIES = ((),) + tuple((a,) for a in ACTIONS) + tuple(product(ACTIONS, repeat=2))
DOMAIN_CELLS = (1 << N) * len(HISTORIES) * len(ACTIONS)
assert DOMAIN_CELLS == 115_680


@dataclass(frozen=True)
class Atom:
    kind: str
    role: int
    value: int = -1
    lag: int = 0

    def __post_init__(self):
        if type(self.role) is not int or not 0 <= self.role < N:
            raise ValueError("atom role")
        if self.kind == "bit":
            if type(self.value) is not int or self.value not in (0, 1) or self.lag != 0:
                raise ValueError("bit atom")
        elif self.kind in ("pulse", "set"):
            if type(self.lag) is not int or self.lag not in (1, 2):
                raise ValueError("history atom lag")
            if self.value not in ((-1,) if self.kind == "pulse" else (0, 1)):
                raise ValueError("history atom value")
        else:
            raise ValueError("unknown atom")


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    lag: int = 0
    guard: tuple[Atom, ...] = ()

    def __post_init__(self):
        if any(type(v) is not int or not 0 <= v < N for v in (self.source, self.target)):
            raise ValueError("edge endpoint")
        if self.source == self.target or type(self.lag) is not int or self.lag not in (0, 1, 2):
            raise ValueError("edge lag or self-loop")
        if type(self.guard) is not tuple or len(self.guard) > 2 or len(set(self.guard)) != len(self.guard):
            raise ValueError("invalid guard")
        if tuple(sorted(self.guard, key=repr)) != self.guard:
            raise ValueError("uncanonical guard")
        for a in self.guard:
            if type(a) is not Atom:
                raise ValueError("wrong guard type")
        if any(a.kind == b.kind == "bit" and a.role == b.role and a.value != b.value
               for a in self.guard for b in self.guard):
            raise ValueError("contradictory current-bit guard")
        if any(a.kind != "bit" and b.kind != "bit" and a.lag == b.lag and a != b
               for a in self.guard for b in self.guard):
            raise ValueError("incompatible same-lag public actions")


@dataclass(frozen=True)
class Law:
    edges: tuple[Edge, ...] = ()

    def __post_init__(self):
        if type(self.edges) is not tuple or any(type(e) is not Edge for e in self.edges) or len(self.edges) > 2 or len(set(self.edges)) != len(self.edges):
            raise ValueError("law edge count/duplicates")
        if tuple(sorted(self.edges, key=repr)) != self.edges:
            raise ValueError("uncanonical law")


def law(*edges: Edge) -> Law:
    return Law(tuple(sorted(edges, key=repr)))


def guards(*atoms: Atom) -> tuple[Atom, ...]:
    return tuple(sorted(atoms, key=repr))


def validate_action(a: tuple) -> None:
    if type(a) is not tuple or len(a) != 3 or any(type(x) is not int for x in a[1:]) or a not in ACTIONS:
        raise ValueError("invalid typed action")


def transition(model: Law, state: int, history: tuple, action: tuple) -> tuple[int, tuple]:
    if type(model) is not Law or type(state) is not int or state not in range(1 << N):
        raise ValueError("invalid law/state")
    if type(history) is not tuple or len(history) > 2:
        raise ValueError("invalid history")
    for h in history:
        validate_action(h)
    validate_action(action)
    return _transition(model, state, history, action)


def _transition(model: Law, state: int, history: tuple, action: tuple) -> tuple[int, tuple]:
    base = (state & ~(1 << action[1])) | (action[2] << action[1]) if action[0] == "set" else state
    mask = 0
    for e in model.edges:
        current = action if e.lag == 0 else history[-e.lag] if len(history) >= e.lag else None
        if current != ("pulse", e.source, -1):
            continue
        match = True
        for a in e.guard:
            if a.kind == "bit":
                good = ((state >> a.role) & 1) == a.value
            else:
                good = len(history) >= a.lag and history[-a.lag] == (a.kind, a.role, a.value)
            if not good:
                match = False
                break
        if match:
            mask ^= 1 << e.target
    return base ^ mask, (history + (action,))[-2:]


def signature(model: Law, *, deadline_at: float | None = None) -> bytes:
    """Every typed input (including unreachable entries), one byte/output."""
    if deadline_at is not None and (type(deadline_at) not in (int, float) or not 0 <= deadline_at < float("inf")):
        raise ValueError("invalid absolute deadline")
    out = bytearray(DOMAIN_CELLS)
    n = 0
    for x in range(1 << N):
        for h in HISTORIES:
            if deadline_at is not None and monotonic() >= deadline_at:
                raise TimeoutError("full signature deadline")
            for a in ACTIONS:
                out[n] = _transition(model, x, h, a)[0]
                n += 1
    return bytes(out)


def permute_law(model: Law, perm: tuple[int, ...]) -> Law:
    if type(perm) is not tuple or len(perm) != N or sorted(perm) != list(range(N)):
        raise ValueError("permutation")
    return law(*(Edge(perm[e.source], perm[e.target], e.lag,
                      guards(*(Atom(g.kind, perm[g.role], g.value, g.lag) for g in e.guard)))
                 for e in model.edges))


def full_semantic_orbit_equivalence(left: Law, right: Law,
                                    *, deadline_seconds: float = 120) -> dict:
    """Exact all-120 role equality: mismatch witness per permutation or full equality.

    Never use a sample fingerprint as proof. For nonalias, one mismatch for
    each permutation proves none is equal. For alias, all 115680 matching cells
    under one permutation prove equality.
    """
    if type(deadline_seconds) not in (int, float) or not 0 < deadline_seconds <= 3600:
        return {"status": "NOT_CERTIFIED", "reason": "PROOF_RESOURCE_CAP"}
    deadline = monotonic() + deadline_seconds
    try:
        reference = signature(left, deadline_at=deadline)
        witnesses = []
        for perm in permutations(range(N)):
            if monotonic() >= deadline:
                raise TimeoutError("orbit time limit")
            renamed = permute_law(right, tuple(perm))
            i = 0
            first = None
            for x in range(1 << N):
                for h in HISTORIES:
                    if monotonic() >= deadline:
                        raise TimeoutError("orbit time limit")
                    for a in ACTIONS:
                        if _transition(renamed, x, h, a)[0] != reference[i]:
                            first = (x, h, a)
                            break
                        i += 1
                    if first is not None:
                        break
                if first is not None:
                    break
            if first is None:
                if monotonic() >= deadline:
                    raise TimeoutError("orbit time limit")
                return {"status": "ALIAS", "permutation": list(perm),
                        "checked_permutations": len(witnesses) + 1,
                        "full_cells_on_matching_permutation": DOMAIN_CELLS}
            witnesses.append(first)
        if monotonic() >= deadline:
            raise TimeoutError("orbit time limit")
        return {"status": "NONALIAS", "checked_permutations": 120,
                "mismatch_witnesses": len(witnesses)}
    except TimeoutError:
        return {"status": "NOT_CERTIFIED", "reason": "PROOF_RESOURCE_CAP"}


PRODUCTIONS = (
    "direct", "lag1", "lag2", "guard_bit", "guard_pulse", "and_guard",
    "chain", "fork", "join", "feedback", "split_guard_alias", "guarded_pair",
)


def compose(production: str, roles: tuple[int, int, int]) -> Law:
    if production not in PRODUCTIONS or type(roles) is not tuple or len(roles) != 3 or any(
        type(i) is not int or not 0 <= i < N for i in roles
    ) or len(set(roles)) != 3:
        raise ValueError("production/roles")
    s, t, c = roles
    if production == "direct": return law(Edge(s, t))
    if production == "lag1": return law(Edge(s, t, 1))
    if production == "lag2": return law(Edge(s, t, 2))
    if production == "guard_bit": return law(Edge(s, t, 0, guards(Atom("bit", c, 1))))
    if production == "guard_pulse": return law(Edge(s, t, 0, guards(Atom("pulse", c, -1, 1))))
    if production == "and_guard": return law(Edge(s, t, 0, guards(Atom("bit", c, 1), Atom("pulse", c, -1, 1))))
    if production == "chain": return law(Edge(s, t), Edge(t, c, 1))
    if production == "fork": return law(Edge(s, t), Edge(s, c))
    if production == "join": return law(Edge(s, c), Edge(t, c))
    if production == "feedback": return law(Edge(s, t), Edge(t, s, 1))
    if production == "split_guard_alias": return law(
        Edge(s, t, 0, guards(Atom("bit", c, 0))),
        Edge(s, t, 0, guards(Atom("bit", c, 1))))
    return law(Edge(s, t, 0, guards(Atom("bit", c, 1))), Edge(s, t, 1))


def generate(max_proposals: int = 48):
    """Deterministic interleaved grammar, counting aliases as proposals."""
    if type(max_proposals) is not int or not 1 <= max_proposals <= 720:
        raise ValueError("max_proposals")
    count = 0
    for roles in permutations(range(N), 3):
        for production in PRODUCTIONS:
            if count >= max_proposals:
                return
            count += 1
            yield {"proposal_id": f"g0c-{count:04d}",
                   "source_root": f"production/{production}", "parents": [],
                   "role_binding": list(roles), "model": compose(production, tuple(roles))}


def census(max_proposals: int = 48, *, deadline_seconds: float = 120) -> dict:
    """Exact full-domain signatures and pairwise role-equivalence of a cohort.

    Does NOT prove independence of generated samples or a full Hplus census.
    """
    if type(deadline_seconds) not in (int, float) or not 0 < deadline_seconds <= 3600:
        return {"status": "NOT_CERTIFIED", "reason": "PROOF_RESOURCE_CAP"}
    deadline = monotonic() + deadline_seconds
    reps, records = [], []
    try:
        for item in generate(max_proposals):
            model = item["model"]
            sig = signature(model, deadline_at=deadline)
            alias = None
            for rep in reps:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    raise TimeoutError("census deadline")
                cert = full_semantic_orbit_equivalence(rep["model"], model,
                                                        deadline_seconds=remaining)
                if cert["status"] == "NOT_CERTIFIED":
                    raise TimeoutError("pairwise orbit deadline")
                if cert["status"] == "ALIAS":
                    alias = rep["proposal_id"]
                    break
            if alias is None:
                reps.append({"proposal_id": item["proposal_id"], "model": model})
            records.append({"proposal_id": item["proposal_id"],
                            "source_root": item["source_root"], "parents": item["parents"],
                            "role_binding": item["role_binding"],
                            "semantic_sha256": sha256(sig).hexdigest(),
                            "orbit_alias_of": alias})
        if monotonic() >= deadline:
            raise TimeoutError("census deadline")
    except TimeoutError:
        return {"status": "NOT_CERTIFIED", "reason": "PROOF_RESOURCE_CAP",
                "examined_proposals": len(records), "partial_records": records}
    return {"status": "CERTIFIED_CLOSED_COHORT", "source_grammar": "G0C-V5-1",
            "proposals": len(records), "nonalias_role_orbits": len(reps),
            "unique_production_roots_not_independent_families":
                len({r["source_root"] for r in records}),
            "full_signature_cells_per_law": DOMAIN_CELLS,
            "role_permutations_upper_bound_per_pair": 120,
            "independent_scientific_family_count": None,
            "records": records, "representatives": [r["proposal_id"] for r in reps]}

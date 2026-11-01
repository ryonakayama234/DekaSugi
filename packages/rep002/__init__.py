"""EXP-REP-002: disclosed direct-relation preflight, not formal transfer scoring.
A deliberately small, bounded engineering calibration. No sealed sources or credentials.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
from time import process_time_ns

SCHEMA = "rep002-disclosed-direct-preflight/1"
ROLES = ("hub", "x", "y", "z", "q")
HORIZONS = (0, 2, 4, 8)
STRATA = ("RENAMED", "COMPOSITION", "NOVEL", "DISTRACTOR")
ARMS = ("LQ", "LA", "LR", "FA")
MAX_EXPANDED_NODES = 4096


def digest(x: object) -> str:
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def step(state: tuple[bool, ...], source: int,
         edges: tuple[tuple[int, int], ...]) -> tuple[bool, ...]:
    if type(state) is not tuple or len(state) != 5 or any(type(v) is not bool for v in state):
        raise ValueError("Invalid state")
    if type(source) is not int or not 0 <= source < 5:
        raise ValueError("Invalid pulse source")
    if type(edges) is not tuple or len(edges) > 4:
        raise ValueError("Invalid relation class")
    changed = {source}
    for e in edges:
        if type(e) is not tuple or len(e) != 2 or any(type(i) is not int or not 0 <= i < 5 for i in e) or e[0] == e[1]:
            raise ValueError("Invalid relation edge")
        if e[0] == source:
            if e[1] in changed:
                changed.remove(e[1])
            else:
                changed.add(e[1])
    return tuple((not v) if i in changed else v for i, v in enumerate(state))


def structure_signature(edges: tuple[tuple[int, int], ...]) -> str:
    """Canonical directed graph identifier under every object renaming."""
    return min(digest(sorted((p[a], p[b]) for a, b in edges))
               for p in permutations(range(5)))


def behavior_signature(edges: tuple[tuple[int, int], ...]) -> str:
    """Full finite-domain pulse behavior, canonical under object renaming."""
    rows = []
    for p in permutations(range(5)):
        mapping = tuple(sorted((p[a], p[b]) for a, b in edges))
        table = []
        for bits in product((False, True), repeat=5):
            for src in range(5):
                table.append(step(bits, src, mapping))
        rows.append(digest(table))
    return min(rows)


@dataclass(frozen=True)
class World:
    name: str
    object_ids: tuple[str, ...]
    public_roles: tuple[str, ...]
    hidden_edges: tuple[tuple[int, int], ...]


def world(index: int, stratum: str) -> World:
    if type(index) is not int or index < 0 or stratum not in ("TRAIN",) + STRATA:
        raise ValueError("Invalid world request")
    # TRAIN: three distinct 3-edge structures sharing a fork motif. Each
    # has different object-name permutations, but only distinct graph topologies
    # count toward motif support.
    train = (
        ((0, 1), (0, 2), (3, 4)),  # fork + disconnected edge
        ((0, 1), (0, 2), (2, 3)),  # fork + chain
        ((0, 1), (0, 2), (0, 3)),  # 3-star
    )
    composition = (
        ((0, 1), (0, 2), (0, 3), (3, 4)),
        ((0, 1), (0, 2), (0, 4), (2, 3)),
        ((0, 1), (0, 2), (0, 3), (4, 2)),
    )
    novel = (
        ((0, 1), (1, 2), (2, 3), (3, 4)),
        ((0, 1), (1, 2), (0, 3), (3, 4)),
        ((4, 0), (0, 1), (1, 2), (2, 3)),
    )
    distractor = (
        ((0, 1), (0, 2), (3, 4), (4, 1)),
        ((0, 1), (0, 2), (3, 4), (2, 4)),
        ((0, 1), (0, 2), (1, 4), (3, 2)),
    )
    choices = {"TRAIN": train, "RENAMED": train,
               "COMPOSITION": composition, "NOVEL": novel,
               "DISTRACTOR": distractor}[stratum]
    edges = choices[index % len(choices)]
    # Deterministic 5-node permutation, independent of global random state.
    import random
    p = list(range(5))
    random.Random(8243 + index * 127 + sum(map(ord, stratum))).shuffle(p)
    return World(stratum + "-" + str(index), tuple("o" + str(i) for i in range(5)),
                 tuple(ROLES[p.index(i)] for i in range(5)),
                 tuple(sorted((p[a], p[b]) for a, b in edges)))


class Session:
    """Same-process disclosed host, NOT an independent private evaluator."""
    def __init__(self, w: World):
        self._edges = w.hidden_edges
        self.roles = w.public_roles
        self.state = (False,) * 5
        self.actions = 0
        self.trace: list[dict[str, object]] = []

    def pulse(self, source: int) -> dict[str, object]:
        if type(source) is not int or source not in range(5):
            raise ValueError("Invalid pulse")
        before = self.state
        after = step(before, source, self._edges)
        self.state = after
        self.actions += 1
        record = {"kind": "pulse", "source": source,
                  "before": before, "after": after, "cost": 1}
        self.trace.append(record)
        return record


def reveal_outgoing(public_record: dict[str, object]) -> tuple[int, ...]:
    before = public_record["before"]
    after = public_record["after"]
    src = public_record["source"]
    if type(src) is not int or type(before) is not tuple or type(after) is not tuple:
        raise ValueError("Invalid public record")
    if len(before) != 5 or len(after) != 5 or any(type(x) is not bool for x in before + after):
        raise ValueError("Invalid public states")
    if (before[src] == after[src]) or public_record["cost"] != 1:
        raise ValueError("Contradictory public pulse")
    return tuple(i for i in range(5) if i != src and before[i] != after[i])


def train(n: int) -> dict[str, object]:
    if type(n) is not int or n not in (0, 3, 8, 16, 32, 64):
        raise ValueError("Invalid training curve count")
    observed: dict[str, list[set[tuple[str, str]]]] = {}
    receipts: list[str] = []
    topology: set[str] = set()
    total_actions = 0
    for i in range(n):
        w = world(i, "TRAIN")
        session = Session(w)
        typed_edges = set()
        for src in range(5):
            obs = session.pulse(src)
            for tgt in reveal_outgoing(obs):
                typed_edges.add((w.public_roles[src], w.public_roles[tgt]))
        topology.add(structure_signature(w.hidden_edges))
        observed.setdefault(structure_signature(w.hidden_edges), []).append(typed_edges)
        receipts.append(digest(session.trace))
        total_actions += session.actions
    # Each structure counts once; repeated renamed objects do not increase
    # independent topology support.
    per_structure = [set.intersection(*v) for v in observed.values()]
    common = set.intersection(*per_structure) if per_structure else set()
    motif = tuple(sorted(e for e in common if e[0] == "hub"))
    if len(topology) < 3 or len(motif) < 2:
        motif = ()
    payload = {"schema": SCHEMA, "train_count": n, "distinct_structures": len(topology),
               "motif": motif, "training_receipts_hash": digest(receipts),
               "metered_train_actions": total_actions, "grammar": "direct-xor/4"}
    return {**payload, "digest": digest(payload)}


def validate(snapshot: dict[str, object]) -> None:
    if type(snapshot) is not dict or set(snapshot) != {"schema", "train_count",
        "distinct_structures", "motif", "training_receipts_hash",
        "metered_train_actions", "grammar", "digest"}:
        raise ValueError("Invalid snapshot envelope")
    if snapshot["schema"] != SCHEMA or snapshot["grammar"] != "direct-xor/4":
        raise ValueError("Unsupported snapshot schema")
    if any(type(snapshot[k]) is not int for k in
           ("train_count", "distinct_structures", "metered_train_actions")):
        raise ValueError("Invalid snapshot numbers")
    if type(snapshot["motif"]) is not tuple or any(
        type(pair) is not tuple or len(pair) != 2 or
        any(type(role) is not str or role not in ROLES for role in pair)
        for pair in snapshot["motif"]
    ):
        raise ValueError("Invalid motif")
    if type(snapshot["training_receipts_hash"]) is not str or type(snapshot["digest"]) is not str:
        raise ValueError("Invalid digests")
    if snapshot["digest"] != digest({k: v for k, v in snapshot.items() if k != "digest"}):
        raise ValueError("Snapshot digest mismatch")


def save(snapshot: dict[str, object], path: Path) -> None:
    validate(snapshot)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, sort_keys=True, indent=2) + "\n", encoding="utf8")


def load(path: Path) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf8"))
    if type(raw) is not dict or type(raw.get("motif")) is not list:
        raise ValueError("Invalid serialized snapshot")
    raw["motif"] = tuple(tuple(pair) for pair in raw["motif"])
    validate(raw)
    return raw


def committed_edges(snapshot: dict[str, object], roles: tuple[str, ...],
                    observed: dict[int, tuple[int, ...]], arm: str) -> tuple[tuple[int, int], ...]:
    edges = set()
    if arm != "LR":
        for src_role, tgt_role in snapshot["motif"]:
            edges.add((roles.index(src_role), roles.index(tgt_role)))
    for src, targets in observed.items():
        edges = {e for e in edges if e[0] != src}
        edges.update((src, tgt) for tgt in targets)
    return tuple(sorted(edges))


def choose(roles: tuple[str, ...], known: frozenset[int],
           snapshot: dict[str, object], arm: str, meter: dict[str, int]) -> int | None:
    unknown = [i for i in range(5) if i not in known]
    if not unknown:
        return None
    # Count expanded primitive operations for proposals even if not executed.
    meter["expanded_nodes"] += len(unknown)
    if meter["expanded_nodes"] > MAX_EXPANDED_NODES:
        return None
    if arm in ("LQ", "FA"):
        # FA is a deliberately strong fixed public-role heuristic: it can
        # copy a hub-first rule without learning a transferable concept.
        if arm == "FA" or snapshot["motif"]:
            hubs = [i for i in unknown if roles[i] == "hub"]
            if hubs:
                return hubs[0]
    return unknown[0]


def use(snapshot: dict[str, object], w: World, arm: str,
        budget: int) -> dict[str, object]:
    validate(snapshot)
    if arm not in ARMS or type(budget) is not int or budget not in HORIZONS:
        raise ValueError("Invalid use arguments")
    s = Session(w)
    observations: dict[int, tuple[int, ...]] = {}
    meter = {"expanded_nodes": 0}
    for _ in range(budget):
        selected = choose(s.roles, frozenset(observations), snapshot, arm, meter)
        if selected is None:
            break
        evidence = s.pulse(selected)
        observations[selected] = reveal_outgoing(evidence)
    model = committed_edges(snapshot, s.roles, observations, arm)
    meter["expanded_nodes"] += len(model)
    if meter["expanded_nodes"] > MAX_EXPANDED_NODES:
        return {"status": "ABSTAIN", "edges": (), "actions": s.actions,
                "meter": meter, "trace_hash": digest(s.trace)}
    return {"status": "COMMITTED", "edges": model, "actions": s.actions,
            "meter": meter, "trace_hash": digest(s.trace)}


def audit(w: World, model: tuple[tuple[int, int], ...], status: str) -> int:
    if status != "COMMITTED":
        return 0
    import random
    rng = random.Random(9001 + sum(ord(x) for x in w.name))
    correct = 0
    for _ in range(32):
        state = tuple(bool(rng.randrange(2)) for _ in range(5))
        action = rng.randrange(5)
        correct += step(state, action, model) == step(state, action, w.hidden_edges)
    return correct


def evaluate() -> dict[str, object]:
    t0 = process_time_ns()
    snapshots = {str(n): train(n) for n in (0, 3, 8, 16, 32, 64)}
    snapshot = snapshots["64"]
    validate(snapshot)
    rows = []
    for stratum in STRATA:
        for index in range(12):
            w = world(index + 300, stratum)
            for arm in ARMS:
                for budget in HORIZONS:
                    result = use(snapshot, w, arm, budget)
                    rows.append({"stratum": stratum, "world": w.name, "arm": arm,
                                 "budget": budget, "correct": audit(w, result["edges"], result["status"]),
                                 "actions": result["actions"], "expanded_nodes": result["meter"]["expanded_nodes"],
                                 "status": result["status"], "trace_hash": result["trace_hash"]})
    per_world = {}
    for row in rows:
        key = (row["stratum"], row["world"], row["arm"])
        per_world.setdefault(key, []).append(row["correct"] / 32)
    summary = {}
    for stratum in STRATA:
        summary[stratum] = {}
        for arm in ARMS:
            scores = [sum(v) / len(v) for k, v in per_world.items()
                      if k[0] == stratum and k[2] == arm]
            summary[stratum][arm] = round(sum(scores) / len(scores), 6)
    pairs = []
    for w in sorted({r["world"] for r in rows if r["stratum"] == "COMPOSITION"}):
        a = per_world["COMPOSITION", w, "LQ"]
        b = per_world["COMPOSITION", w, "LA"]
        pairs.append(round((sum(a) - sum(b)) / 4, 6))
    return {"status": "DISCLOSED_PREFLIGHT_ONLY_NOT_FORMAL",
            "limitation": "direct-only four-edge grammar; pulse-only query; no H4 gated search; same-process evaluator",
            "train_curve": [{"n": int(n), "structures": v["distinct_structures"],
                            "concepts": int(bool(v["motif"])), "digest": v["digest"]}
                           for n, v in snapshots.items()],
            "snapshot": snapshot, "worlds": 48, "audits_per_world": 32,
            "arms": ARMS, "budgets": HORIZONS, "strata": summary,
            "composition_paired_effect": round(sum(pairs) / len(pairs), 6),
            "composition_world_differences": pairs,
            "total_actions": sum(r["actions"] for r in rows),
            "total_expanded_nodes": sum(r["expanded_nodes"] for r in rows),
            "cpu_ms": round((process_time_ns() - t0) / 1e6, 3),
            "records_digest": digest(rows)}

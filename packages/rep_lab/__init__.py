"""G1-D: disclosed, bounded representation-repair research lab.

No access to formal TRAIN/DEV/FINAL or previous sealed evidence. No credentials.
ToySession runs in-process with its host: it is NOT a confidentiality boundary.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
from time import process_time_ns, perf_counter_ns

from packages.relational_world import (Action, InventedWorld, Observation, Relation,
    _validate_objects, step, validate_action, validate_state)
from packages.world_model import candidates, consistent_models, predicted_next

SCHEMA = "rep-g1d-toy-snapshot/1"
GRAMMAR = "two-relations-parity/1"
N_CURVE = (0, 1, 2, 3, 4, 8, 16, 32)
PASSES = (1, 2, 5, 10)
MAX_ATOMS = 728
MAX_PAIRS = 264628


def canonical_hash(obj: object) -> str:
    return sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":"), allow_nan=False).encode("utf8")).hexdigest()


def _key_edge(r: Relation) -> tuple[str, str, str, bool]:
    return (r.source, r.target, r.context or "", r.context_value)


def canonical_body(model: tuple[Relation, ...]) -> str:
    """Executable two-atom role structure independent of object ID spelling.

    Role numbers are introduced on first occurrence. Ordering of the two
    relation atoms is quotiented out. This does NOT invent new primitive types.
    """
    if type(model) is not tuple or len(model) not in (1, 2):
        raise ValueError("Only one or two typed relation atoms supported")
    options = []
    for ordered in (model, tuple(reversed(model))):
        role_ids: dict[str, int] = {}
        rows = []
        for r in ordered:
            if type(r) is not Relation or type(r.source) is not str or type(r.target) is not str:
                raise ValueError("Untrusted relation")
            for name in (r.source, r.target) + ((r.context,) if r.context is not None else ()):
                if type(name) is not str or not name:
                    raise ValueError("Invalid relation role")
                if name not in role_ids:
                    role_ids[name] = len(role_ids)
            rows.append([role_ids[r.source], role_ids[r.target],
                         -1 if r.context is None else role_ids[r.context],
                         r.context_value])
        options.append(json.dumps(rows, separators=(",", ":"), allow_nan=False))
    return min(options)


@dataclass(frozen=True, slots=True)
class DiagnosisV1:
    status: str
    search_complete: bool
    checked: int
    surviving: int
    evidence_digest: str
    witness_indices: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class RepairCandidateV1:
    model: tuple[Relation, ...]
    body: str
    body_hash: str
    evidence_digest: str
    complexity: int


@dataclass(frozen=True, slots=True)
class RepairResultV1:
    status: str
    search_complete: bool
    checked: int
    total_matches: int
    candidates: tuple[RepairCandidateV1, ...]


def _validate_evidence(objects: tuple[str, ...], evidence: tuple[Observation, ...]) -> None:
    _validate_objects(objects)
    if type(evidence) is not tuple:
        raise ValueError("Evidence must be an exact tuple")
    seen: dict[tuple[tuple[bool, ...], Action], tuple[bool, ...]] = {}
    alias = None
    for o in evidence:
        if (type(o) is not Observation or type(o.world_alias) is not str
                or not o.world_alias or o.object_ids != objects
                or type(o.object_ids) is not tuple):
            raise ValueError("Malformed or cross-world public evidence")
        validate_state(objects, o.before)
        validate_state(objects, o.after)
        validate_action(objects, o.action)
        if alias is None:
            alias = o.world_alias
        elif alias != o.world_alias:
            raise ValueError("Mixed-world transcript")
        key = (o.before, o.action)
        if key in seen and seen[key] != o.after:
            raise ValueError("Contradictory deterministic replay")
        seen[key] = o.after
        if o.action.kind == "set_state" and step(objects, o.before, o.action, ()) != o.after:
            raise ValueError("Invalid set_state outcome")


def _receipt(evidence: tuple[Observation, ...]) -> str:
    return canonical_hash([asdict(x) for x in evidence])


def diagnose_one_edge(objects: tuple[str, ...], evidence: tuple[Observation, ...],
                      max_candidates: int = 800) -> DiagnosisV1:
    """No mismatch certificate unless *all* one-edge candidates were checked."""
    try:
        _validate_evidence(objects, evidence)
    except ValueError as exc:
        status = "INCONSISTENT_REPLAYS" if "Contradictory" in str(exc) else "INVALID_EVIDENCE"
        return DiagnosisV1(status, False, 0, 0, "", ())
    all_models = candidates(objects, expressive=True)
    if type(max_candidates) is not int or max_candidates < 1:
        raise ValueError("Invalid search budget")
    if len(all_models) > max_candidates:
        return DiagnosisV1("SEARCH_EXHAUSTED", False, max_candidates, 0, _receipt(evidence), ())
    matches = consistent_models(objects, evidence, expressive=True)
    status = ("MODEL_CLASS_MISMATCH" if not matches else
              "IDENTIFIED" if len(matches) == 1 else "UNDERIDENTIFIED")
    return DiagnosisV1(status, True, len(all_models), len(matches),
                       _receipt(evidence), tuple(range(len(evidence))) if not matches else ())


def _delta_signature(objects: tuple[str, ...], evidence: tuple[Observation, ...],
                     model: tuple[Relation, ...]) -> int:
    result = 0
    n = len(objects)
    for index, o in enumerate(evidence):
        if o.action.kind != "pulse":
            continue
        after = step(objects, o.before, o.action, model)
        delta = sum(1 << j for j in range(n) if after[j] != o.before[j])
        result |= delta << (n * index)
    return result


def search_two_edges(objects: tuple[str, ...], evidence: tuple[Observation, ...],
                     max_pairs: int = 300000, max_keep: int = 128) -> RepairResultV1:
    """Complete bounded search; bitset XOR is exact for synchronous parity."""
    _validate_evidence(objects, evidence)
    if (type(max_pairs) is not int or max_pairs < 1 or
            type(max_keep) is not int or max_keep < 1 or max_keep > 4096):
        raise ValueError("Invalid repair budget")
    atoms = tuple(model[0] for model in candidates(objects) if len(model) == 1)
    truth = 0
    for i, obs in enumerate(evidence):
        if obs.action.kind == "pulse":
            truth |= sum(1 << j for j in range(len(objects))
                         if obs.before[j] != obs.after[j]) << (len(objects) * i)
    sigs = tuple(_delta_signature(objects, evidence, (r,)) for r in atoms)
    total_pairs = len(atoms) * (len(atoms) - 1) // 2
    checked, matches = 0, 0
    kept: list[RepairCandidateV1] = []
    receipt = _receipt(evidence)
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            if checked >= max_pairs:
                return RepairResultV1("SEARCH_EXHAUSTED", False, checked, matches, tuple(kept))
            checked += 1
            if sigs[i] ^ sigs[j] != truth:
                continue
            model = (atoms[i], atoms[j])
            matches += 1
            if len(kept) < max_keep:
                body = canonical_body(model)
                kept.append(RepairCandidateV1(model, body, canonical_hash(body), receipt, 2))
    status = "NO_TWO_EDGE_FIT" if not matches else (
        "CANDIDATE_LIMIT" if matches > max_keep else
        "IDENTIFIED" if matches == 1 else "UNDERIDENTIFIED")
    return RepairResultV1(status, checked == total_pairs, checked, matches, tuple(kept))


@dataclass(frozen=True, slots=True)
class TemplateV1:
    body: str
    body_hash: str
    support_worlds: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RepairSnapshotV1:
    schema: str
    grammar: str
    train_receipt: str
    train_count: int
    templates: tuple[TemplateV1, ...]
    atom_rank: tuple[tuple[str, int], ...]
    digest: str


def _snapshot_payload(s: RepairSnapshotV1) -> dict[str, object]:
    return {k: v for k, v in asdict(s).items() if k != "digest"}


def validate_snapshot(s: RepairSnapshotV1) -> None:
    if (type(s) is not RepairSnapshotV1 or type(s.schema) is not str or s.schema != SCHEMA
            or type(s.grammar) is not str or s.grammar != GRAMMAR
            or type(s.train_count) is not int or s.train_count < 0
            or type(s.train_receipt) is not str or len(s.train_receipt) != 64
            or type(s.digest) is not str or len(s.digest) != 64
            or type(s.templates) is not tuple or type(s.atom_rank) is not tuple):
        raise ValueError("Invalid Snapshot envelope")
    prev = ""
    for t in s.templates:
        if (type(t) is not TemplateV1 or type(t.body) is not str or
                type(t.body_hash) is not str or t.body_hash != canonical_hash(t.body)
                or type(t.support_worlds) is not tuple
                or any(type(w) is not str or not w for w in t.support_worlds)
                or t.support_worlds != tuple(sorted(set(t.support_worlds)))
                or len(t.support_worlds) < 3 or len(t.support_worlds) > s.train_count
                or t.body <= prev):
            raise ValueError("Invalid template body, types or provenance")
        # Parse body, allow only exact typed shape of two relation atoms.
        try:
            rows = json.loads(t.body)
        except json.JSONDecodeError as e:
            raise ValueError("Malformed body") from e
        if (type(rows) is not list or len(rows) != 2 or
                any(type(r) is not list or len(r) != 4 or
                    any(type(x) is not int or x < -1 or x > 5 for x in r[:3])
                    or type(r[3]) is not bool or r[0] == r[1]
                    or (r[2] != -1 and r[2] in (r[0], r[1])) for r in rows)):
            raise ValueError("Unsafe template body")
        prev = t.body
    for name, count in s.atom_rank:
        if (type(name) is not str or name not in ("direct", "gated_true", "gated_false")
                or type(count) is not int or count < 1):
            raise ValueError("Invalid rank statistics")
    if (s.atom_rank != tuple(sorted(s.atom_rank)) or
            len({a for a, _ in s.atom_rank}) != len(s.atom_rank) or
            s.digest != canonical_hash(_snapshot_payload(s))):
        raise ValueError("Tampered or noncanonical snapshot")



def instantiate_template(body: str, objects: tuple[str, ...],
                         max_bindings: int = 10000
                         ) -> tuple[tuple[Relation, ...], ...]:
    """Generate typed two-atom hypotheses from acquired role variables only."""
    _validate_objects(objects)
    if type(body) is not str or len(body) > 256 or type(max_bindings) is not int or not 1 <= max_bindings <= 10000:
        raise ValueError("Unsafe template constructor input")
    try:
        rows = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("Malformed template body") from exc
    if (type(rows) is not list or len(rows) != 2 or
        any(type(r) is not list or len(r) != 4 or
            any(type(v) is not int or v < -1 or v > 5 for v in r[:3]) or
            type(r[3]) is not bool or r[0] == r[1] or
            (r[2] != -1 and r[2] in (r[0], r[1])) for r in rows)):
        raise ValueError("Unsafe typed template rows")
    used = {v for r in rows for v in r[:3] if v >= 0}
    if used != set(range(len(used))) or not 2 <= len(used) <= len(objects):
        raise ValueError("Noncanonical or overspecified roles")
    count = 1
    for k in range(len(used)):
        count *= len(objects) - k
    if count > max_bindings:
        raise ValueError("Template binding budget exhausted")
    models = set()
    for roles in permutations(objects, len(used)):
        edges = []
        for src, tgt, ctx, enabled in rows:
            edges.append(Relation(roles[src], roles[tgt],
                                  roles[ctx] if ctx >= 0 else None, enabled))
        model = tuple(sorted(edges, key=_key_edge))
        if model[0] == model[1]:
            continue
        if canonical_body(model) != body:
            raise ValueError("Noncanonical body construction")
        models.add(model)
    return tuple(sorted(models, key=lambda m: tuple(_key_edge(r) for r in m)))


def _atom_kind(r: Relation) -> str:
    return "direct" if r.context is None else ("gated_true" if r.context_value else "gated_false")


def learn_snapshot(episodes: dict[str, tuple[Observation, ...]],
                   pair_budget: int = 300000) -> RepairSnapshotV1:
    """Sleep over public transcripts; only uniquely solved worlds add support."""
    if type(episodes) is not dict or any(type(k) is not str or not k for k in episodes):
        raise ValueError("Invalid episode storage")
    supports: dict[str, list[str]] = {}
    frequencies: dict[str, int] = {}
    receipt = []
    for alias, observations in sorted(episodes.items()):
        if (type(observations) is not tuple or not observations or
                any(type(o) is not Observation or o.world_alias != alias for o in observations)):
            raise ValueError("Invalid cross-world training transcript")
        objects = observations[0].object_ids
        diag = diagnose_one_edge(objects, observations, max_candidates=MAX_ATOMS + 1)
        if diag.status in ("INVALID_EVIDENCE", "INCONSISTENT_REPLAYS"):
            raise ValueError("Invalid training evidence")
        receipt.append([alias, _receipt(observations)])
        if diag.status != "MODEL_CLASS_MISMATCH":
            continue
        result = search_two_edges(objects, observations, pair_budget)
        if result.status != "IDENTIFIED":
            continue
        candidate = result.candidates[0]
        supports.setdefault(candidate.body, []).append(alias)
        for relation in candidate.model:
            kind = _atom_kind(relation)
            frequencies[kind] = frequencies.get(kind, 0) + 1
    templates = tuple(TemplateV1(body, canonical_hash(body), tuple(worlds))
                      for body, worlds in sorted(supports.items()) if len(worlds) >= 3)
    rank = tuple(sorted(frequencies.items()))
    base = RepairSnapshotV1(SCHEMA, GRAMMAR, canonical_hash(receipt),
                            len(episodes), templates, rank, "")
    result = RepairSnapshotV1(SCHEMA, GRAMMAR, base.train_receipt,
                              base.train_count, templates, rank,
                              canonical_hash(_snapshot_payload(base)))
    validate_snapshot(result)
    return result


def save_snapshot(snapshot: RepairSnapshotV1, path: Path) -> None:
    validate_snapshot(snapshot)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(snapshot), indent=2, sort_keys=True,
                               ensure_ascii=False, allow_nan=False) + "\n", encoding="utf8")


def load_snapshot(path: Path) -> RepairSnapshotV1:
    raw = json.loads(Path(path).read_text(encoding="utf8"))
    if type(raw) is not dict or set(raw) != set(RepairSnapshotV1.__dataclass_fields__):
        raise ValueError("Unknown Snapshot keys")
    if (type(raw["templates"]) is not list or type(raw["atom_rank"]) is not list):
        raise ValueError("Invalid serialized Snapshot")
    templates = []
    for x in raw["templates"]:
        if type(x) is not dict or set(x) != set(TemplateV1.__dataclass_fields__) or type(x["support_worlds"]) is not list:
            raise ValueError("Malformed template")
        templates.append(TemplateV1(x["body"], x["body_hash"], tuple(x["support_worlds"])))
    ranks = []
    for x in raw["atom_rank"]:
        if type(x) is not list or len(x) != 2:
            raise ValueError("Malformed rank")
        ranks.append(tuple(x))
    s = RepairSnapshotV1(raw["schema"], raw["grammar"], raw["train_receipt"],
                         raw["train_count"], tuple(templates), tuple(ranks), raw["digest"])
    validate_snapshot(s)
    return s


class ToySession:
    """Host-owned in-process adapter. Learners consume only act/state/observations."""
    def __init__(self, world: InventedWorld):
        self._world = world  # NOT a security boundary. Do not use for formal data.
        self.object_ids = world.object_ids
        self.state = (False,) * len(self.object_ids)
        self.observations: list[Observation] = []
        self.actions_charged = 0
        self.resets_charged = 0

    def act(self, action: Action) -> Observation:
        validate_action(self.object_ids, action)
        obs = self._world.probe(self.state, action)  # environment host only
        self.state = obs.after
        self.observations.append(obs)
        self.actions_charged += 1
        return obs

    def reset(self) -> None:
        self.state = (False,) * len(self.object_ids)
        self.resets_charged += 1

    def configure(self, desired: tuple[bool, ...]) -> None:
        """Physically reach desired Boolean state, paying for every set_state."""
        validate_state(self.object_ids, desired)
        for j, value in enumerate(desired):
            if self.state[j] != value:
                self.act(Action("set_state", self.object_ids[j], value))

    def pulse_from(self, desired: tuple[bool, ...], source: str) -> Observation:
        self.configure(desired)
        return self.act(Action("pulse", source))


def _fork_rules(ids: tuple[str, ...], index: int, variant: str = "fork") -> tuple[Relation, ...]:
    if variant == "fork":
        src = ids[index % 4]
        other = tuple(x for x in ids if x != src)
        return (Relation(src, other[0]), Relation(src, other[1]))
    if variant == "separate":
        return (Relation(ids[0], ids[1]), Relation(ids[2], ids[3]))
    if variant == "gated":
        return (Relation(ids[0], ids[1], ids[3], True),
                Relation(ids[0], ids[2]))
    raise ValueError("Unknown disclosed fixture kind")


def disclosed_world(index: int, role: str = "train", variant: str = "fork") -> InventedWorld:
    if type(index) is not int or index < 0 or role not in ("train", "toy-eval", "user"):
        raise ValueError("Invalid disclosed world")
    ids = tuple(f"{role}{index}-o{j}" for j in range(4))
    return InventedWorld(f"{role}{index}", ids, _fork_rules(ids, index, variant))


def full_public_episode(world: InventedWorld) -> tuple[tuple[Observation, ...], int]:
    """A charged, exhaustive *disclosed toy* calibration, not a viable formal budget."""
    session = ToySession(world)
    ids = session.object_ids
    for bits in product((False, True), repeat=len(ids)):
        for src in ids:
            session.pulse_from(tuple(bits), src)
    return tuple(session.observations), session.actions_charged


def passive_public_episode(world: InventedWorld) -> tuple[tuple[Observation, ...], int]:
    session = ToySession(world)
    for source in session.object_ids:
        session.act(Action("pulse", source))
    return tuple(session.observations), session.actions_charged


def _model_pick(models: tuple[tuple[Relation, ...], ...], mode: str,
                snapshot: RepairSnapshotV1 | None) -> tuple[Relation, ...]:
    if not models:
        raise ValueError("Cannot pick empty model set")
    template_weights = ({t.body: len(t.support_worlds) for t in snapshot.templates}
                        if snapshot and mode == "B3" else {})
    kinds = dict(snapshot.atom_rank) if snapshot else {}
    if mode in ("B2", "B3x"):
        return min(models, key=lambda m: (-sum(kinds.get(_atom_kind(r), 0) for r in m),
                                           tuple(_key_edge(r) for r in m)))
    if mode == "B3":
        return min(models, key=lambda m: (-template_weights.get(canonical_body(m), 0) if len(m) in (1, 2) else 0,
                                          -sum(kinds.get(_atom_kind(r), 0) for r in m),
                                          tuple(_key_edge(r) for r in m)))
    return min(models, key=lambda m: tuple(_key_edge(r) for r in m))


@dataclass(frozen=True, slots=True)
class PredictionV1:
    status: str
    after: tuple[bool, ...] | None
    checked: int
    diagnosis: str
    selected_model: tuple[Relation, ...] | None = None


def predict(objects: tuple[str, ...], evidence: tuple[Observation, ...],
            before: tuple[bool, ...], action: Action, mode: str,
            snapshot: RepairSnapshotV1 | None = None,
            train_memory: dict[str, tuple[Observation, ...]] | None = None,
            pair_budget: int = 300000) -> PredictionV1:
    if mode not in ("B0", "B1", "B2", "B3", "B3x", "B4"):
        raise ValueError("Unknown arm")
    _validate_evidence(objects, evidence)
    validate_state(objects, before)
    validate_action(objects, action)
    if mode in ("B2", "B3", "B3x"):
        if snapshot is None:
            raise ValueError("Missing trained Snapshot")
        validate_snapshot(snapshot)
    diag = diagnose_one_edge(objects, evidence)
    if mode == "B4":
        # Exact episodic retrieval, deliberately distinct mechanism diagnostic.
        for world in sorted(train_memory or {}):
            for o in train_memory[world]:
                if o.object_ids == objects and o.before == before and o.action == action:
                    return PredictionV1("PREDICTED", o.after, 0, diag.status)
        return PredictionV1("ABSTAIN", None, 0, diag.status)
    if diag.status in ("INVALID_EVIDENCE", "INCONSISTENT_REPLAYS", "SEARCH_EXHAUSTED"):
        return PredictionV1("ABSTAIN", None, diag.checked, diag.status)
    if mode == "B0" or diag.status != "MODEL_CLASS_MISMATCH":
        models = consistent_models(objects, evidence)
        if not models:
            return PredictionV1("ABSTAIN", None, diag.checked, diag.status)
        model = _model_pick(models, mode, snapshot)
        return PredictionV1("PREDICTED", predicted_next(objects, before, action, model),
                            diag.checked, diag.status, model)
    # A B3 acquired body is an executable typed candidate constructor, not
    # just a rank label. Check EVERY generated candidate against public facts.
    attempted = 0
    if mode == "B3" and snapshot is not None and snapshot.templates:
        fitting: set[tuple[Relation, ...]] = set()
        for template in snapshot.templates:
            try:
                generated = instantiate_template(template.body, objects)
            except ValueError:
                return PredictionV1("ABSTAIN", None, diag.checked + attempted, "TEMPLATE_BOUND_EXHAUSTED")
            for model in generated:
                attempted += 1
                if attempted > pair_budget:
                    return PredictionV1("ABSTAIN", None, diag.checked + attempted, "SEARCH_EXHAUSTED")
                if all(predicted_next(objects, o.before, o.action, model) == o.after
                       for o in evidence):
                    fitting.add(model)
        if fitting:
            model = _model_pick(tuple(sorted(fitting,
                key=lambda m: tuple(_key_edge(r) for r in m))), mode, snapshot)
            return PredictionV1("TEMPLATE_PRIOR_PREDICTION",
                                predicted_next(objects, before, action, model),
                                diag.checked + attempted, diag.status, model)
    # Unexplained evidence falls back to the same bounded full H2 search.
    result = search_two_edges(objects, evidence, pair_budget)
    if not result.search_complete or result.status in ("NO_TWO_EDGE_FIT", "CANDIDATE_LIMIT"):
        return PredictionV1("ABSTAIN", None, diag.checked + attempted + result.checked, result.status)
    model = _model_pick(tuple(c.model for c in result.candidates), mode, snapshot)
    return PredictionV1("PREDICTED", predicted_next(objects, before, action, model),
                        diag.checked + attempted + result.checked, diag.status, model)


def disclosed_training_worlds(n: int = 32) -> dict[str, tuple[Observation, ...]]:
    if type(n) is not int or n not in N_CURVE:
        raise ValueError("Only disclosed curve sizes supported")
    result = {}
    for i in range(n):
        world = disclosed_world(i)
        rows, _ = full_public_episode(world)
        result[f"train{i}"] = rows
    return result



def choose_cost_aware_query(objects: tuple[str, ...], current: tuple[bool, ...],
                            evidence: tuple[Observation, ...], remaining: int
                            ) -> tuple[tuple[bool, ...], str, int] | None:
    """Public-only cost-aware disagreement query; never looks at hidden rules.

    Charges every required set_state and the pulse. Search budget is a limit
    on the public hypothesis space; abstain rather than infer from exhaustion.
    """
    _validate_evidence(objects, evidence)
    validate_state(objects, current)
    if type(remaining) is not int or remaining < 0:
        raise ValueError("Invalid remaining charged budget")
    diag = diagnose_one_edge(objects, evidence)
    if diag.status == "MODEL_CLASS_MISMATCH":
        repairs = search_two_edges(objects, evidence)
        if not repairs.search_complete or repairs.status == "CANDIDATE_LIMIT":
            return None
        models = tuple(c.model for c in repairs.candidates)
    elif diag.status in ("UNDERIDENTIFIED", "IDENTIFIED"):
        models = consistent_models(objects, evidence)
    else:
        return None
    if len(models) < 2:
        return None
    # Rational score (distinct outcomes - 1) / paid action cost, no priors.
    best = None
    numerator, denominator = 0, 1
    for desired in product((False, True), repeat=len(objects)):
        desired = tuple(desired)
        moves = sum(x != y for x, y in zip(current, desired))
        cost = 1 + moves
        if cost > remaining:
            continue
        for source in objects:
            act = Action("pulse", source)
            distinct = len({predicted_next(objects, desired, act, model)
                            for model in models})
            gain = distinct - 1
            if (gain and (best is None or gain * denominator > numerator * cost
                          or (gain * denominator == numerator * cost
                              and cost < denominator))):
                best = (desired, source, cost)
                numerator, denominator = gain, cost
    return best


def active_public_episode(world: InventedWorld, budget: int = 4
                          ) -> tuple[tuple[Observation, ...], int]:
    """Disclosed comparator only: query selector receives public state/history."""
    if type(budget) is not int or not 1 <= budget <= 12:
        raise ValueError("Only bounded toy active budget supported")
    session = ToySession(world)
    while session.actions_charged < budget:
        choice = choose_cost_aware_query(session.object_ids, session.state,
                                         tuple(session.observations),
                                         budget - session.actions_charged)
        if choice is None:
            break
        desired, source, charged = choice
        previous = session.actions_charged
        session.pulse_from(desired, source)
        assert session.actions_charged == previous + charged
    return tuple(session.observations), session.actions_charged


def eval_audit(world: InventedWorld) -> tuple[tuple[bool, ...], Action, tuple[bool, ...]]:
    ids = world.object_ids
    for bit in product((False, True), repeat=4):
        for source in ids:
            before = tuple(bit)
            act = Action("pulse", source)
            # Audit truth is evaluator-only and must never enter public transcript.
            yield before, act, world.probe(before, act).after


def evaluate_disclosed(snapshot: RepairSnapshotV1,
                       memory: dict[str, tuple[Observation, ...]],
                       eval_worlds: int = 6) -> dict[str, object]:
    validate_snapshot(snapshot)
    counts = {arm: 0 for arm in ("B0", "B1", "B2", "B3", "B3x", "B4", "B5")}
    abstentions = {arm: 0 for arm in counts}
    checks = {arm: 0 for arm in counts}
    inference_cpu_ns = {arm: 0 for arm in counts}
    total = 0
    diagnostic = {}
    for i in range(eval_worlds):
        world = disclosed_world(100+i, "toy-eval", "fork" if i < eval_worlds-2 else "gated")
        transcript, charged = passive_public_episode(world)
        active_transcript, active_charged = active_public_episode(world, budget=charged)
        diag = diagnose_one_edge(world.object_ids, transcript)
        diagnostic[world._alias] = {"status": diag.status, "public_actions": charged,
                                   "active_actions": active_charged,
                                   "active_diagnosis": diagnose_one_edge(
                                        world.object_ids, active_transcript).status}
        # Freeze a single inferred world model per arm. Auditor-only queries
        # never update the model and are not part of the public transcript.
        audits = tuple(eval_audit(world))
        for arm in counts:
            started = process_time_ns()
            first_before, first_act, _ = audits[0]
            arm_evidence = active_transcript if arm == "B5" else transcript
            arm_mode = "B3" if arm == "B5" else arm
            selected = predict(world.object_ids, arm_evidence, first_before, first_act,
                               arm_mode, snapshot, memory)
            checks[arm] += selected.checked
            for before, act, answer in audits:
                total += (arm == "B0")
                if arm == "B4":
                    prediction = predict(world.object_ids, transcript, before, act,
                                         arm, snapshot, memory)
                    after = prediction.after
                elif selected.selected_model is not None:
                    after = predicted_next(world.object_ids, before, act, selected.selected_model)
                else:
                    after = None
                if after is None:
                    abstentions[arm] += 1
                elif after == answer:
                    counts[arm] += 1
            inference_cpu_ns[arm] += process_time_ns() - started
    return {"status": "DISCLOSED_ENGINEERING_ONLY", "worlds": eval_worlds,
            "audits_per_world": len(tuple(eval_audit(disclosed_world(100, "toy-eval")))),
            "total_per_arm": total, "correct": counts, "abstain": abstentions,
            "candidate_checks": checks, "inference_cpu_ns": inference_cpu_ns,
            "diagnoses": diagnostic}


def run_pilot() -> dict[str, object]:
    """No private data. Separate unique-world curve from replay idempotence."""
    start_cpu, start_wall = process_time_ns(), perf_counter_ns()
    train = disclosed_training_worlds(32)
    curve = []
    for n in N_CURVE:
        subset = dict(list(train.items())[:n])
        snapshot = learn_snapshot(subset)
        # Distinct experience increments, rather than fake repeated epochs.
        result = evaluate_disclosed(snapshot, subset, eval_worlds=6)
        curve.append({"unique_train_worlds": n, "snapshot_digest": snapshot.digest,
                      "template_bodies": [t.body for t in snapshot.templates],
                      "support_counts": [len(t.support_worlds) for t in snapshot.templates],
                      "correct": result["correct"], "abstain": result["abstain"],
                      "candidate_checks": result["candidate_checks"],
                      "inference_cpu_ns": result["inference_cpu_ns"]})
    repeated = {}
    for passes in PASSES:
        # Immutable evidence does not duplicate independent-world support.
        snapshot = learn_snapshot(train)
        repeated[str(passes)] = snapshot.digest
    final = learn_snapshot(train)
    charged_train_actions = sum(len(obs) for obs in train.values())
    return {"status": "DISCLOSED_ENGINEERING_ONLY_NOT_FORMAL",
            "train_worlds": len(train), "train_actions_charged": charged_train_actions,
            "curve": curve,
            "replay_digests": repeated,
            "replay_idempotent": len(set(repeated.values())) == 1,
            "final": evaluate_disclosed(final, train),
            "final_snapshot": final.digest,
            "cpu_ms": round((process_time_ns() - start_cpu)/1e6, 3),
            "wall_ms": round((perf_counter_ns() - start_wall)/1e6, 3)}

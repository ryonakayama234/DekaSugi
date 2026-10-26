"""EXP-0003A PR3: preregistered TRAIN/DREAM-only four-arm learning evidence.

No EXP-0003A DEV or FINAL generator/evaluator is imported or executed here.
Freeze rule, seed and scientific criteria: experiments/EXP-0003A/plan.md.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import math
from pathlib import Path
import random
from time import perf_counter, process_time
from typing import Literal, Sequence

from packages.evaluation import PrimitiveCallMeter, bounded_synthesize
from packages.exp0003a import (
    FAMILIES, METHOD, ID_VERSION, TRAIN_ALPHABET, TRAIN_TOTAL, TrainCase,
    _audit_ref, _example, _issue_wake_receipt, _private_train_rows, digest,
    generate_train, opaque_id, public_shape, sleep, wake, _source_metadata,
)
from packages.kernel import FEATURE_VERSION, features
from packages.learning import SkillCandidate, registry_with_skill, validate_skill
from packages.library import DEFAULT_PRIMITIVES, Registry
from packages.protocol import Example, TaskSpec, parse_task, program_to_dict
from packages.verification import verify

DREAM_MASTER = 410_000_000
DREAM_PER_FAMILY = 64
DREAM_POOL_SIZE = 512
DREAM_PER_ARM_PER_FAMILY = 12
DREAM_PER_ARM = 96
DREAM_RANDOM_MASTER = 510_000_000
POLICY_VERSION = "exp0003a-knn-cost-v1"
K = 5
MAX_DISTANCE = 0.18
MIN_CLOSE = 3
MIN_SUPPORT_ON = 4
MIN_CALL_DELTA = 2.0
ARMS = ("B1", "B2", "B3")


def _check_case(case: TrainCase) -> None:
    if case.task.task_id != opaque_id(case.task.examples):
        raise ValueError("TaskSpec public hash mismatch")
    if len(case.task.examples) != 2 or len(case.seeds) != 3:
        raise ValueError("Wrong task or audit cardinality")
    if (case.task.limits.max_ast_nodes, case.task.limits.max_candidates) != (4, 100):
        raise ValueError("Altered search budget")


def generate_dream_pool(train: Sequence[TrainCase]) -> tuple[TrainCase, ...]:
    """Exactly 512 frozen synthetic cases; collisions fail, never resample."""
    if len(train) != TRAIN_TOTAL:
        raise ValueError("TRAIN count mismatch")
    for case in train:
        _check_case(case)
    ids = {case.task.task_id for case in train}
    source_ids = {case.source_record_id for case in train}
    seeds = {seed for case in train for seed in case.seeds}
    if (len(ids), len(source_ids), len(seeds)) != (TRAIN_TOTAL, TRAIN_TOTAL, 480):
        raise ValueError("Duplicate TRAIN ID/source/seed")
    pool: list[TrainCase] = []
    for family_index, family in enumerate(FAMILIES):
        for index in range(DREAM_PER_FAMILY):
            example_seeds = tuple(
                DREAM_MASTER + 100_000 * family_index + 10 * index + j
                for j in range(3)
            )
            if any(seed in seeds for seed in example_seeds):
                raise ValueError("DREAM seed collision")
            seeds.update(example_seeds)
            examples = tuple(_example(family, index, j, example_seeds[j])
                             for j in range(3))
            public = (examples[0], examples[1])
            task_id = opaque_id(public)
            source_id = f"dream-f{family_index:02d}-i{index:03d}"
            if task_id in ids or source_id in source_ids:
                raise ValueError("Cross TRAIN/DREAM task or source collision")
            ids.add(task_id)
            source_ids.add(source_id)
            task = parse_task({**public_shape(public), "task_id": task_id})
            pool.append(TrainCase(task, examples[2], source_id, family, example_seeds))
    if (len(pool), len(ids), len(seeds)) != (512, 672, 2016):
        raise ValueError("Preregistered DREAM pool cardinality mismatch")
    return tuple(pool)


def _distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != 8 or len(b) != 8:
        raise ValueError("8D feature vector required")
    return sum(abs(x - y) for x, y in zip(a, b)) / 8.0


@dataclass(frozen=True, slots=True)
class PairedObservation:
    """Learner-facing public features + measured OFF/ON outcome only."""
    task_id: str
    vector: tuple[float, ...]
    prefer_on: bool
    off_calls: int
    on_calls: int
    off_candidates: int
    on_candidates: int
    off_correct: bool
    on_correct: bool
    on_audit_invalid: bool

    def to_dict(self) -> dict[str, object]:
        return {**asdict(self), "vector": list(self.vector)}


@dataclass(frozen=True, slots=True)
class PairedTrial:
    observation: PairedObservation
    off_evidence: dict[str, object]
    on_evidence: dict[str, object]
    off_search_cpu_ms: float
    on_search_cpu_ms: float
    off_audit_cpu_ms: float
    on_audit_cpu_ms: float
    off_search_wall_ms: float
    on_search_wall_ms: float
    off_audit_wall_ms: float
    on_audit_wall_ms: float


def _audited_trial(task: TaskSpec, audit: Example,
                   registry: Registry, learned: dict[str, SkillCandidate]
                   ) -> tuple[dict[str, object], int, int, bool, bool, float, float, float, float]:
    """Search sees public two examples; evaluator checks the third separately."""
    meter = PrimitiveCallMeter()
    cpu_start, wall_start = process_time(), perf_counter()
    found = bounded_synthesize(task, registry, learned, meter=meter)
    cpu_search, wall_search = (
        (process_time() - cpu_start) * 1000,
        (perf_counter() - wall_start) * 1000,
    )
    cpu_audit = wall_audit = 0.0
    correct = False
    if found.status == "solved":
        if found.program is None:
            raise ValueError("Solved status without program")
        cpu_start, wall_start = process_time(), perf_counter()
        # Search's trusted registry gate already checked implementations.
        # Reconstruct the canonical callable graph rather than trusting input.
        canonical = Registry(DEFAULT_PRIMITIVES)
        auditable = registry_with_skill(next(iter(learned.values())), canonical) if learned else canonical
        correct = verify(
            found.program, (audit,), auditable,
            max_nodes=task.limits.max_ast_nodes,
        ).matched
        cpu_audit, wall_audit = (
            (process_time() - cpu_start) * 1000,
            (perf_counter() - wall_start) * 1000,
        )
    elif found.status not in ("not_found", "budget_exhausted") or found.program is not None:
        raise ValueError("Unknown search status")
    invalid_solved = found.status == "solved" and not correct
    evidence = {
        "search": {key: value for key, value in found.to_dict().items()
                   if key != "elapsed_ms"},
        "audit_correct": correct, "audit_invalid_solved": invalid_solved,
        "meter": meter.to_dict(),
        "selected_ast": program_to_dict(found.program) if found.program else None,
    }
    return (evidence, found.tested_candidates, meter.total, correct,
            invalid_solved, cpu_search, wall_search, cpu_audit, wall_audit)


def paired_trial(case: TrainCase, skill: SkillCandidate) -> PairedTrial:
    """Independent public OFF/ON searches and third audits, no oracle input."""
    _check_case(case)
    canonical = Registry(DEFAULT_PRIMITIVES)
    validate_skill(skill, canonical)
    enabled = registry_with_skill(skill, canonical)
    off = _audited_trial(case.task, case.private_audit, canonical, {})
    on = _audited_trial(case.task, case.private_audit, enabled, {skill.skill_id: skill})
    off_e, off_candidates, off_calls, off_correct, _, off_cpu, off_wall, off_audit_cpu, off_audit_wall = off
    on_e, on_candidates, on_calls, on_correct, on_invalid, on_cpu, on_wall, on_audit_cpu, on_audit_wall = on
    if off_correct != on_correct:
        prefer_on = on_correct
    elif off_calls != on_calls:
        prefer_on = off_calls > on_calls
    else:
        prefer_on = off_candidates > on_candidates
    return PairedTrial(
        PairedObservation(
            case.task.task_id, features(case.task), prefer_on,
            off_calls, on_calls, off_candidates, on_candidates,
            off_correct, on_correct, on_invalid,
        ),
        off_e, on_e,
        off_cpu, on_cpu, off_audit_cpu, on_audit_cpu,
        off_wall, on_wall, off_audit_wall, on_audit_wall,
    )


def positive_train(trials: Sequence[PairedTrial]) -> tuple[PairedObservation, ...]:
    """Positive requires audited-correct ON and strictly fewer primitive calls."""
    if len({t.observation.task_id for t in trials}) != len(trials):
        raise ValueError("Duplicate paired trial public task ID")
    return tuple(t.observation for t in trials
                 if t.observation.on_correct
                 and t.observation.on_calls < t.observation.off_calls)


def _canonical_pool(pool: Sequence[TrainCase]) -> tuple[TrainCase, ...]:
    """Validate exact 512 IDs and return generator order, independent of input order."""
    if len(pool) != DREAM_POOL_SIZE:
        raise ValueError("DREAM pool must be 512 tasks")
    if len({c.task.task_id for c in pool}) != DREAM_POOL_SIZE:
        raise ValueError("Duplicate DREAM public ID")
    if len({c.source_record_id for c in pool}) != DREAM_POOL_SIZE:
        raise ValueError("Duplicate DREAM pool ID")
    by_id = {}
    for case in pool:
        _check_case(case)
        by_id[case.source_record_id] = case
    ordered = []
    for index, family in enumerate(FAMILIES):
        for j in range(DREAM_PER_FAMILY):
            source_id = f"dream-f{index:02d}-i{j:03d}"
            case = by_id.get(source_id)
            if case is None or case.family != family:
                raise ValueError("DREAM pool missing preregistered family/index")
            ordered.append(case)
    if len(ordered) != len(by_id):
        raise ValueError("Unexpected DREAM pool ID")
    return tuple(ordered)


def select_dream(
    pool: Sequence[TrainCase],
    strategy: Literal["random", "counterfactual"],
    *, positives: Sequence[PairedObservation] = (),
) -> tuple[TrainCase, ...]:
    """Family is only an evaluator stratum; selection score uses public 8D."""
    pool = _canonical_pool(pool)
    if strategy not in ("random", "counterfactual"):
        raise ValueError("Unknown DREAM strategy")
    if strategy == "counterfactual":
        if not positives or not any(x.on_correct and x.on_calls < x.off_calls for x in positives):
            raise ValueError("No audited positive TRAIN references")
        if len({x.task_id for x in positives}) != len(positives):
            raise ValueError("Duplicate positive reference")
        if any(not x.on_correct or x.on_calls >= x.off_calls
               for x in positives):
            raise ValueError("Invalid positive reference")
        points = tuple(x.vector for x in positives)
        if any(len(x) != 8 for x in points):
            raise ValueError("Positive feature dimensionality mismatch")
    selected: list[TrainCase] = []
    for index in range(8):
        group = tuple(pool[index * 64:(index + 1) * 64])
        if strategy == "random":
            order = list(range(64))
            random.Random(DREAM_RANDOM_MASTER + index).shuffle(order)
            selected.extend(group[j] for j in order[:12])
        else:
            ordered = sorted(group, key=lambda c: (
                min(_distance(features(c.task), p) for p in points),
                c.source_record_id,
            ))
            selected.extend(ordered[:12])
    if (len(selected) != DREAM_PER_ARM
            or len({c.task.task_id for c in selected}) != DREAM_PER_ARM):
        raise ValueError("DREAM selected cardinality mismatch")
    return tuple(selected)


def _snapshot_payload(snapshot: "ArmSnapshot") -> dict[str, object]:
    """Canonical semantic record: sort WAKE, retain selected DREAM order.

    Paired WAKE observations and their evaluator-issued provenance travel as
    aligned pairs. Their transport order does not affect KNN or semantic SHA.
    B2/B3 selected DREAM order is an explicit ID-v1 scientific commitment.
    """
    wake = sorted(
        zip(snapshot.observations[:TRAIN_TOTAL], snapshot.wake_episode_ids),
        key=lambda pair: pair[0].task_id,
    )
    canonical_observations = (
        [observation for observation, _ in wake]
        + list(snapshot.observations[TRAIN_TOTAL:])
    )
    canonical_wake_ids = [episode_id for _, episode_id in wake]
    observation_rows = [observation.to_dict()
                        for observation in canonical_observations]
    return {
        "schema_version": "exp0003a-policy-snapshot-v1",
        "method": METHOD, "id_version": ID_VERSION,
        "arm": snapshot.arm, "cycle_id": snapshot.cycle_id,
        "wake_episode_ids": canonical_wake_ids,
        "dream_case_ids": list(snapshot.dream_case_ids),
        "algorithm_version": snapshot.algorithm_version,
        "feature_version": snapshot.feature_version,
        "k": snapshot.k, "max_distance": snapshot.max_distance,
        "min_close": snapshot.min_close, "min_support_on": snapshot.min_support_on,
        "min_call_delta": snapshot.min_call_delta,
        "skill_id": snapshot.skill_id, "skill_body_sha256": snapshot.skill_body_sha256,
        "source_manifest_sha256": snapshot.source_manifest_sha256,
        "pool_public_input_sha256": snapshot.pool_public_input_sha256,
        "ordered_selected_pool_ids": list(snapshot.ordered_selected_pool_ids),
        "ordered_selected_task_ids": list(snapshot.ordered_selected_task_ids),
        "training_ids": [x.task_id for x in canonical_observations],
        "observations_sha256": digest(observation_rows),
        "observations": observation_rows,
        "status": "TRAIN_DREAM_ENGINEERING_UNFROZEN",
    }


@dataclass(frozen=True, slots=True)
class ArmSnapshot:
    arm: Literal["B1", "B2", "B3"]
    observations: tuple[PairedObservation, ...]
    skill_id: str
    skill_body_sha256: str
    source_manifest_sha256: str
    pool_public_input_sha256: str
    ordered_selected_pool_ids: tuple[str, ...]
    ordered_selected_task_ids: tuple[str, ...]
    cycle_id: str = "exp0003a-cycle-v1"
    wake_episode_ids: tuple[str, ...] = ()
    dream_case_ids: tuple[str, ...] = ()
    algorithm_version: str = POLICY_VERSION
    feature_version: str = FEATURE_VERSION
    k: int = K
    max_distance: float = MAX_DISTANCE
    min_close: int = MIN_CLOSE
    min_support_on: int = MIN_SUPPORT_ON
    min_call_delta: float = MIN_CALL_DELTA

    def validate(self) -> None:
        if (self.arm not in ARMS or self.algorithm_version != POLICY_VERSION
                or self.cycle_id != "exp0003a-cycle-v1"):
            raise ValueError("Unknown arm/cycle/policy version")
        if (len(self.wake_episode_ids) != 160
                or self.wake_episode_ids != tuple("wake:" + o.task_id
                    for o in self.observations[:160])):
            raise ValueError("WAKE source episode references mismatch")
        if len(self.dream_case_ids) != (0 if self.arm == "B1" else 96):
            raise ValueError("DREAM case provenance mismatch")
        if self.dream_case_ids != tuple(self.arm.lower() + ":" + pool_id
                                        for pool_id in self.ordered_selected_pool_ids):
            raise ValueError("DREAM case provenance mismatch")
        if self.arm not in ARMS or self.algorithm_version != POLICY_VERSION:
            raise ValueError("Unknown arm or policy version")
        if self.feature_version != FEATURE_VERSION or (
            self.k, self.max_distance, self.min_close, self.min_support_on,
            self.min_call_delta) != (5, .18, 3, 4, 2.0):
            raise ValueError("Altered KNN policy method")
        if (self.skill_id != "skill_" + self.skill_body_sha256[:16]
                or len(self.skill_body_sha256) != 64):
            raise ValueError("Unbound skill body")
        if (len(self.observations) != (160 if self.arm == "B1" else 256)
                or len({o.task_id for o in self.observations}) != len(self.observations)):
            raise ValueError("Bad training IDs or cardinality")
        for o in self.observations:
            if (not o.task_id.startswith("t-") or len(o.task_id) != 66
                    or any(ch not in "0123456789abcdef" for ch in o.task_id[2:])):
                raise ValueError("Non-opaque learner ID")
            if (len(o.vector) != 8 or any(not math.isfinite(x) for x in o.vector)
                    or any(not 0 <= x <= 1 for x in o.vector[:2])
                    or not -1 <= o.vector[2] <= 1):
                raise ValueError("Malformed 8D public features")
            if (any(type(x) is not int or x < 0 for x in (
                    o.off_calls, o.on_calls, o.off_candidates, o.on_candidates))
                    or type(o.prefer_on) is not bool
                    or type(o.off_correct) is not bool
                    or type(o.on_correct) is not bool
                    or type(o.on_audit_invalid) is not bool):
                raise ValueError("Invalid paired observation")
        n = 0 if self.arm == "B1" else 96
        if (len(self.ordered_selected_pool_ids) != n
                or len(self.ordered_selected_task_ids) != n
                or len(set(self.ordered_selected_pool_ids)) != n
                or len(set(self.ordered_selected_task_ids)) != n):
            raise ValueError("Incorrect DREAM selected IDs")
        if ([o.task_id for o in self.observations[160:]]
                != list(self.ordered_selected_task_ids)):
            raise ValueError("Selected DREAM observation/task order mismatch")
        if self.arm != "B1":
            for family_index in range(8):
                group = self.ordered_selected_pool_ids[family_index * 12:(family_index + 1) * 12]
                if any(not x.startswith(f"dream-f{family_index:02d}-i") for x in group):
                    raise ValueError("DREAM family strata mismatch")
        if any(
            type(x) is not str or len(x) != 64
            or any(ch not in "0123456789abcdef" for ch in x)
            for x in (self.skill_body_sha256, self.source_manifest_sha256,
                      self.pool_public_input_sha256)
        ):
            raise ValueError("Malformed source/pool/skill hashes")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        result = _snapshot_payload(self)
        return {**result, "policy_snapshot_sha256": digest(result)}

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "ArmSnapshot":
        if not isinstance(raw, dict):
            raise ValueError("Bad snapshot")
        data = dict(raw)
        checksum = data.pop("policy_snapshot_sha256", None)
        if checksum != digest(data):
            raise ValueError("Policy snapshot hash mismatch")
        if (data.get("schema_version") != "exp0003a-policy-snapshot-v1"
                or data.get("method") != METHOD or data.get("id_version") != ID_VERSION
                or data.get("status") != "TRAIN_DREAM_ENGINEERING_UNFROZEN"):
            raise ValueError("Unsupported snapshot schema/method")
        rows = tuple(PairedObservation(
            **{**row, "vector": tuple(row["vector"])}) for row in data["observations"])
        if data["training_ids"] != [x.task_id for x in rows] or (
            data["observations_sha256"] != digest([x.to_dict() for x in rows])):
            raise ValueError("Inconsistent snapshot observation provenance")
        snapshot = cls(
            arm=data["arm"], observations=rows,
            skill_id=data["skill_id"], skill_body_sha256=data["skill_body_sha256"],
            source_manifest_sha256=data["source_manifest_sha256"],
            pool_public_input_sha256=data["pool_public_input_sha256"],
            ordered_selected_pool_ids=tuple(data["ordered_selected_pool_ids"]),
            ordered_selected_task_ids=tuple(data["ordered_selected_task_ids"]),
            cycle_id=data["cycle_id"],
            wake_episode_ids=tuple(data["wake_episode_ids"]),
            dream_case_ids=tuple(data["dream_case_ids"]),
            algorithm_version=data["algorithm_version"],
            feature_version=data["feature_version"],
            k=data["k"], max_distance=data["max_distance"],
            min_close=data["min_close"], min_support_on=data["min_support_on"],
            min_call_delta=data["min_call_delta"],
        )
        if snapshot.to_dict() != raw:
            raise ValueError("Non-canonical policy snapshot")
        return snapshot


@dataclass(frozen=True, slots=True)
class Decision:
    action: Literal["OFF", "ON"]
    reason: str
    neighbors: tuple[str, ...]
    nearest_distance: float
    close_support: int
    on_support: int
    mean_call_saving: float


def choose(task: TaskSpec, snapshot: ArmSnapshot) -> Decision:
    """Pre-solve public I/O only; no audit, family, seed or oracle input."""
    snapshot.validate()
    if len(task.examples) != 2 or task.task_id != opaque_id(task.examples):
        raise ValueError("Untrusted public inference task")
    vec = features(task)
    neighbors = sorted((
        (_distance(vec, obs.vector), obs.task_id, obs)
        for obs in snapshot.observations
    ), key=lambda x: (x[0], x[1]))[:K]
    if len(neighbors) != 5:
        raise ValueError("Missing KNN observations")
    near = sum(d <= MAX_DISTANCE for d, _, _ in neighbors)
    on_count = sum(int(obs.prefer_on) for _, _, obs in neighbors)
    saving = sum(obs.off_calls - obs.on_calls for _, _, obs in neighbors) / 5
    veto = any(obs.off_correct and obs.on_audit_invalid
               for _, _, obs in neighbors)
    if near < MIN_CLOSE:
        action, reason = "OFF", "insufficient_support"
    elif veto:
        action, reason = "OFF", "audit_safety_veto"
    elif on_count < MIN_SUPPORT_ON:
        action, reason = "OFF", "insufficient_on_votes"
    elif saving < MIN_CALL_DELTA:
        action, reason = "OFF", "insufficient_call_saving"
    else:
        action, reason = "ON", "cost_supported"
    return Decision(action, reason, tuple(x[1] for x in neighbors),
                    neighbors[0][0], near, on_count, saving)


def _trial_cost(trials: Sequence[PairedTrial]) -> dict[str, float | int]:
    return {
        "off_search_cpu_ms": sum(t.off_search_cpu_ms for t in trials),
        "off_search_wall_ms": sum(t.off_search_wall_ms for t in trials),
        "on_search_cpu_ms": sum(t.on_search_cpu_ms for t in trials),
        "on_search_wall_ms": sum(t.on_search_wall_ms for t in trials),
        "off_audit_cpu_ms": sum(t.off_audit_cpu_ms for t in trials),
        "off_audit_wall_ms": sum(t.off_audit_wall_ms for t in trials),
        "on_audit_cpu_ms": sum(t.on_audit_cpu_ms for t in trials),
        "on_audit_wall_ms": sum(t.on_audit_wall_ms for t in trials),
        "off_primitive_calls": sum(t.observation.off_calls for t in trials),
        "on_primitive_calls": sum(t.observation.on_calls for t in trials),
    }


def _case_rows(cases: Sequence[TrainCase]) -> list[dict[str, object]]:
    return [{
        "pool_id": c.source_record_id, "family": c.family,
        "seeds": list(c.seeds), "public_task": {
            **public_shape(c.task.examples), "task_id": c.task.task_id,
        }, "audit": asdict(c.private_audit),
        "audit_evidence_ref": _audit_ref(c.task.task_id, c.private_audit),
    } for c in cases]


def run_train_dream() -> tuple[dict[str, object], dict[str, object]]:
    """One exact 160+512 engineering run; no holdout generator or evaluation."""
    total_cpu, total_wall = process_time(), perf_counter()
    start_cpu, start_wall = process_time(), perf_counter()
    train = generate_train()
    pool = generate_dream_pool(train)
    generator_cpu_ms = (process_time() - start_cpu) * 1000
    generator_wall_ms = (perf_counter() - start_wall) * 1000
    if set(c.task.task_id for c in train) & set(c.task.task_id for c in pool):
        raise ValueError("TRAIN/DREAM collision")
    # Issue the receipts only from actually audited WAKE results, never
    # restore caller-created success flags or prewritten benchmark solutions.
    start_cpu, start_wall = process_time(), perf_counter()
    episodes = tuple(wake(c.task, private_audit=c.private_audit) for c in train)
    receipts = tuple(_issue_wake_receipt(e) for e in episodes)
    wake_cpu_ms = (process_time() - start_cpu) * 1000
    wake_wall_ms = (perf_counter() - start_wall) * 1000
    start_cpu, start_wall = process_time(), perf_counter()
    proposals = sleep(episodes, trusted_receipts=receipts)
    sleep_cpu_ms = (process_time() - start_cpu) * 1000
    sleep_wall_ms = (perf_counter() - start_wall) * 1000
    if not proposals or proposals[0].status != "candidate":
        raise ValueError("TRAIN SLEEP produced no approved proposal")
    skill = proposals[0].candidate
    validate_skill(skill, Registry(DEFAULT_PRIMITIVES))

    start_cpu, start_wall = process_time(), perf_counter()
    train_trials = tuple(paired_trial(c, skill) for c in train)
    train_paired_cpu_ms = (process_time() - start_cpu) * 1000
    train_paired_wall_ms = (perf_counter() - start_wall) * 1000
    positives = positive_train(train_trials)
    if not positives:
        raise ValueError("B3 cannot run without audited cost-positive WAKE")
    start_cpu, start_wall = process_time(), perf_counter()
    b2_cases = select_dream(pool, "random")
    b3_cases = select_dream(pool, "counterfactual", positives=positives)
    selection_cpu_ms = (process_time() - start_cpu) * 1000
    selection_wall_ms = (perf_counter() - start_wall) * 1000
    start_cpu, start_wall = process_time(), perf_counter()
    # A case common to B2 and B3 is independently measured once then its
    # identical observation is copied into each independent snapshot. Its
    # audit and primitive cost is measured, not generated from a hidden oracle.
    selected_unique = {c.task.task_id: c for c in b2_cases + b3_cases}
    dream_trials = {
        k: paired_trial(c, skill) for k, c in selected_unique.items()
    }
    dream_paired_cpu_ms = (process_time() - start_cpu) * 1000
    dream_paired_wall_ms = (perf_counter() - start_wall) * 1000

    train_ids = tuple(c.task.task_id for c in train)
    pool_rows = _case_rows(pool)
    pool_public = [{
        "pool_id": c.source_record_id,
        "task_id": c.task.task_id,
        "public_task_sha256": c.task.task_id[2:],
    } for c in pool]
    train_raw_rows = _private_train_rows(train)
    full_rows = train_raw_rows + pool_rows
    source_hash = digest(full_rows)
    # ID-v1: canonical JSON list of full public 64hex SHA256 values in
    # family-index/task-index order; not the selection or private IDs.
    pool_public_hash = digest([c.task.task_id[2:] for c in pool])
    snapshot_cost_cpu, snapshot_cost_wall = process_time(), perf_counter()
    snapshots = {}
    for arm, selected in (
        ("B1", ()), ("B2", b2_cases), ("B3", b3_cases),
    ):
        observations = (
            tuple(t.observation for t in train_trials)
            + tuple(dream_trials[c.task.task_id].observation for c in selected)
        )
        snap = ArmSnapshot(
            arm, observations, skill.skill_id, skill.body_hash,
            source_hash, pool_public_hash,
            tuple(c.source_record_id for c in selected),
            tuple(c.task.task_id for c in selected),
            wake_episode_ids=tuple("wake:" + task_id for task_id in train_ids),
            dream_case_ids=tuple(arm.lower() + ":" + c.source_record_id
                                 for c in selected),
        )
        snapshots[arm] = snap.to_dict()
        if ArmSnapshot.from_dict(snapshots[arm]) != snap:
            raise ValueError("Policy snapshot roundtrip failed")
    snapshot_cpu_ms = (process_time() - snapshot_cost_cpu) * 1000
    snapshot_wall_ms = (perf_counter() - snapshot_cost_wall) * 1000
    if tuple(snapshots) != ARMS:
        raise ValueError("Arm snapshot order mismatch")
    source = _source_metadata()
    source["pr3_source_file_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    source["feature_source_file_sha256"] = sha256(
        Path(__import__("packages.kernel", fromlist=["features"]).__file__).read_bytes()
    ).hexdigest()
    selection = {
        arm: {
            "ordered_selected_pool_ids": [
                c.source_record_id for c in cases],
            "ordered_selected_task_ids": [c.task.task_id for c in cases],
            "ordered_dream_case_ids": [
                arm.lower() + ":" + c.source_record_id for c in cases
            ],
            "selected_sha256": digest([{
                "pool_id": c.source_record_id, "task_id": c.task.task_id
            } for c in cases]),
        } for arm, cases in (("B2", b2_cases), ("B3", b3_cases))
    }
    public = {
        "experiment_id": "EXP-0003A", "phase": "TRAIN_DREAM_ENGINEERING",
        "method": METHOD, "id_version": ID_VERSION,
        "state": "pr3_train_dream_no_holdout",
        "source": source, "feature_version": FEATURE_VERSION,
        "algorithm_version": POLICY_VERSION,
        "train_task_count": len(train), "dream_pool_count": len(pool),
        "dream_selected_per_arm": DREAM_PER_ARM,
        "selected_distinct_total": len(dream_trials),
        "pool_public_input_sha256": pool_public_hash,
        "source_manifest_sha256": source_hash,
        "pool_public_ids": pool_public,
        "top_skill": skill.to_dict(),
        "wake_positive_count": len(positives),
        "positive_train_ids_sha256": digest([o.task_id for o in positives]),
        "wake_status": {x: sum(e.status == x for e in episodes)
                        for x in ("success", "audit_rejected", "not_found", "budget_exhausted")},
        "selection": selection, "snapshots": snapshots,
        "snapshot_hashes": {arm: snapshots[arm]["policy_snapshot_sha256"]
                            for arm in ARMS},
        "train_paired_observations_sha256": digest([
            x.observation.to_dict() for x in train_trials
        ]),
        "dream_paired_observations_sha256": digest([
            dream_trials[c.task.task_id].observation.to_dict()
            for c in selected_unique.values()
        ]),
        "primitive_measurements": {
            "train": _trial_cost(train_trials),
            "dream_unique": _trial_cost(tuple(dream_trials.values())),
        },
        "cost_ms": {
            "generator_cpu": generator_cpu_ms, "generator_wall": generator_wall_ms,
            "wake_cpu": wake_cpu_ms, "wake_wall": wake_wall_ms,
            "sleep_cpu": sleep_cpu_ms, "sleep_wall": sleep_wall_ms,
            "train_paired_cpu": train_paired_cpu_ms,
            "train_paired_wall": train_paired_wall_ms,
            "dream_selection_cpu": selection_cpu_ms,
            "dream_selection_wall": selection_wall_ms,
            "dream_paired_cpu": dream_paired_cpu_ms,
            "dream_paired_wall": dream_paired_wall_ms,
            "snapshot_cpu": snapshot_cpu_ms, "snapshot_wall": snapshot_wall_ms,
            "total_cpu": (process_time() - total_cpu) * 1000,
            "total_wall": (perf_counter() - total_wall) * 1000,
        },
        "registry_promotion": "not_authorized",
        "dev_or_final_evaluated": False,
        "limitations": (
            "TRAIN/DREAM engineering only; selection by near-positive public features "
            "does not guarantee hard negatives or unknown-task advantage."
        ),
    }
    private = {
        "schema_version": "exp0003a-pr3-evaluator-evidence-v1",
        "method": METHOD, "partition": "TRAIN_DREAM",
        "source_manifest_sha256": source_hash,
        "pool_public_input_sha256": pool_public_hash,
        "train_rows": train_raw_rows,
        "dream_rows": pool_rows,
        "wake_receipts": [asdict(x) for x in receipts],
        "train_paired_trials": [{
            "task_id": c.task.task_id,
            "audit_evidence_ref": _audit_ref(c.task.task_id, c.private_audit),
            "off": t.off_evidence, "on": t.on_evidence,
        } for c, t in zip(train, train_trials)],
        "dream_paired_trials": [{
            "pool_id": c.source_record_id,
            "task_id": c.task.task_id,
            "audit_evidence_ref": _audit_ref(c.task.task_id, c.private_audit),
            "off": dream_trials[c.task.task_id].off_evidence,
            "on": dream_trials[c.task.task_id].on_evidence,
        } for c in selected_unique.values()],
    }
    if digest(private["train_rows"] + private["dream_rows"]) != source_hash:
        raise ValueError("Private evidence manifest mismatch")
    return public, private

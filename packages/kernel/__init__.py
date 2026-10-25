"""EXP-0002B: deterministic, preregistered, TRAIN-only contextual skill selector.

Method and limits come exclusively from experiments/EXP-0002B/plan-v2.md.
No FINAL search, audit or learned-policy evaluation is exposed here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
from time import perf_counter, process_time
from typing import Literal

from packages.evaluation import PrimitiveCallMeter, TRAIN as SKILL_TRAIN, bounded_synthesize
from packages.library import DEFAULT_PRIMITIVES, Registry
from packages.learning import SkillCandidate, discover_skills, registry_with_skill
from packages.protocol import Example, TaskSpec, parse_task
from packages.verification import verify

Split = Literal["train", "dev", "final"]
FAMILIES = ("identity", "trim", "lower", "upper", "normalize", "reverse", "replace_first")
MASTERS = {"train": 10_000_000, "dev": 20_000_000, "final": 30_000_000}
ALPHABETS = {"train": "ABCDEF", "dev": "GHIJKL", "final": "MNOPQR"}
COUNTS = {"train": 24, "dev": 8, "final": 16}
WHITESPACE = {
    "train": ((" ", " "), ("  ", ""), ("", "  ")),
    "dev": (("\t", " "), (" ", "\t"), ("  ", " ")),
    "final": (("\n", " "), ("\t", "\t"), ("   ", " \n")),
}
SKILL_ID = "skill_8fe1361cb5014f85"
SKILL_HASH = "8fe1361cb5014f8503e4a57392e45f4fc7607e788fdd598f66668fbc11338eff"
FEATURE_VERSION = "task-features-v1"
ALGORITHM_VERSION = "knn-cost-v1"
MEASUREMENT_VERSION = "runtime-canonical-v1"
K = 5
MAX_DISTANCE = 0.18
MIN_CLOSE = 3
MIN_SUPPORT_ON = 4
MIN_CALL_DELTA = 2.0


def digest(obj: object) -> str:
    """Canonical JSON/SHA-256, independent of dict order and whitespace."""
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ExperimentTask:
    """The withheld audit/labels live here, NEVER inside the learner's TaskSpec."""
    task: TaskSpec
    audit: Example
    family: str
    partition: Split
    seeds: tuple[int, int, int]


def _seed(split: Split, family_index: int, index: int, example_index: int) -> int:
    return MASTERS[split] + 100000 * family_index + 100 * index + example_index


def generate_partition(split: Split) -> tuple[ExperimentTask, ...]:
    """Follow plan-v2 exactly; never feed family, seed, audit or split to the policy."""
    if split not in MASTERS:
        raise ValueError("Unknown experiment partition")
    families = FAMILIES if split == "final" else FAMILIES[:-1]
    result: list[ExperimentTask] = []
    for k, family in enumerate(families):
        for i in range(COUNTS[split]):
            examples: list[Example] = []
            seeds: list[int] = []
            for j in range(3):
                seed = _seed(split, k, i, j)
                rng = random.Random(seed)
                alphabet = ALPHABETS[split]
                while True:
                    length = rng.randrange(3, 8)
                    token = "".join(rng.choice(alphabet) for _ in range(length))
                    if len(set(token)) >= 2 and token != token[::-1]:
                        break
                if family == "upper":
                    token = token.lower()
                prefix, suffix = WHITESPACE[split][(i + j) % 3]
                if family == "identity":
                    inp, out = token, token
                elif family == "trim":
                    inp, out = prefix + token + suffix, token
                elif family == "lower":
                    inp, out = token, token.lower()
                elif family == "upper":
                    inp, out = token, token.upper()
                elif family == "normalize":
                    inp, out = prefix + token + suffix, token.lower()
                elif family == "reverse":
                    inp, out = token, token[::-1]
                else:
                    inp, out = token, "Z" + token[1:]
                examples.append(Example(inp, out))
                seeds.append(seed)
            task = parse_task({
                "schema_version": "0.1",
                "task_id": f"{split}-{family}-{i:03d}",
                "domain": "string_to_string",
                "examples": [{"input": e.input, "output": e.output} for e in examples[:2]],
                "limits": {"max_ast_nodes": 4, "max_candidates": 100},
            })
            result.append(ExperimentTask(task, examples[2], family, split, tuple(seeds)))
    return tuple(result)


def _dataset_record(item: ExperimentTask) -> dict[str, object]:
    return {
        "id": item.task.task_id,
        "family": item.family,
        "partition": item.partition,
        "seeds": list(item.seeds),
        "public": [asdict(e) for e in item.task.examples],
        "audit": asdict(item.audit),
        "max_ast_nodes": item.task.limits.max_ast_nodes,
        "max_candidates": item.task.limits.max_candidates,
    }


def dataset_manifest() -> dict[str, object]:
    """Hash all frozen split content; NO synthesis or final-policy execution."""
    splits = {name: generate_partition(name) for name in ("train", "dev", "final")}
    seeds = [seed for group in splits.values() for item in group for seed in item.seeds]
    if len(seeds) != 912 or len(set(seeds)) != 912:
        raise ValueError("Split RNG seed overlap or unexpected task count")
    if tuple(map(len, splits.values())) != (144, 48, 112):
        raise ValueError("Unexpected preregistered partition sizes")
    records = {name: [_dataset_record(x) for x in group] for name, group in splits.items()}
    return {
        "partition_counts": {name: len(group) for name, group in splits.items()},
        "unique_rng_seeds": len(set(seeds)),
        "dataset_sha256": digest(records),
        "split_sha256": {name: digest(rows) for name, rows in records.items()},
        "generator_source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "method": "EXP-0002B-PLAN-V2",
        "published_seeds_not_blinded": True,
    }


def features(task: TaskSpec) -> tuple[float, ...]:
    """Only the TWO visible I/O pairs; no IDs, hidden audit, or success result."""
    if len(task.examples) != 2:
        raise ValueError("task-features-v1 requires exactly two public examples")
    pairs = [(e.input, e.output) for e in task.examples]
    mean = lambda values: sum(values) / 2.0
    ascii_inputs = "".join(x for x, _ in pairs)
    ascii_outputs = "".join(y for _, y in pairs)
    alpha_in = [c for c in ascii_inputs if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"]
    alpha_out = [c for c in ascii_outputs if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"]
    vals = (
        mean(min(len(x), 16) / 16 for x, _ in pairs),
        mean(min(len(y), 16) / 16 for _, y in pairs),
        mean(max(-1.0, min(1.0, (len(y) - len(x)) / 16)) for x, y in pairs),
        mean(float(x != x.strip()) for x, _ in pairs),
        sum(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in alpha_in) / len(alpha_in) if alpha_in else 0.0,
        sum(c in "abcdefghijklmnopqrstuvwxyz" for c in alpha_out) / len(alpha_out) if alpha_out else 0.0,
        mean(float(x == y) for x, y in pairs),
        mean(sum(a == b for a, b in zip(x, y)) / max(len(x), len(y), 1) for x, y in pairs),
    )
    return tuple(vals)


@dataclass(frozen=True, slots=True)
class TrainingObservation:
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


@dataclass(frozen=True, slots=True)
class PolicySnapshot:
    """Immutable versioned metadata. Hash protects the serializable contents."""
    observations: tuple[TrainingObservation, ...]
    dataset_sha256: str
    generator_source_sha256: str
    skill_body_sha256: str
    algorithm_version: str = ALGORITHM_VERSION
    feature_version: str = FEATURE_VERSION
    k: int = K
    max_distance: float = MAX_DISTANCE
    min_close: int = MIN_CLOSE
    min_on_support: int = MIN_SUPPORT_ON
    min_call_delta: float = MIN_CALL_DELTA

    def payload(self) -> dict[str, object]:
        values = asdict(self)
        values["training_ids"] = [o.task_id for o in self.observations]
        values["training_observations_sha256"] = digest([asdict(o) for o in self.observations])
        return values

    def to_dict(self) -> dict[str, object]:
        values = self.payload()
        values["policy_sha256"] = digest(values)
        return values

    @staticmethod
    def from_dict(raw: dict[str, object]) -> PolicySnapshot:
        obj = dict(raw)
        checksum = obj.pop("policy_sha256")
        obj.pop("training_ids")
        obj.pop("training_observations_sha256")
        objects = tuple(TrainingObservation(
            **{**p, "vector": tuple(p["vector"])}) for p in obj.pop("observations"))
        snapshot = PolicySnapshot(observations=objects, **obj)
        if snapshot.to_dict()["policy_sha256"] != checksum:
            raise ValueError("PolicySnapshot content hash mismatch")
        return snapshot


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    action: Literal["OFF", "ON"]
    reason: str
    neighbors: tuple[str, ...]
    on_support: int
    close_support: int
    mean_call_saving: float
    nearest_distance: float
    inference_wall_ms: float


def choose(task: TaskSpec, snapshot: PolicySnapshot) -> PolicyDecision:
    started = perf_counter()
    vec = features(task)
    if (snapshot.algorithm_version != ALGORITHM_VERSION
            or snapshot.feature_version != FEATURE_VERSION
            or snapshot.skill_body_sha256 != SKILL_HASH
            or (snapshot.k, snapshot.max_distance, snapshot.min_close,
                snapshot.min_on_support, snapshot.min_call_delta)
            != (K, MAX_DISTANCE, MIN_CLOSE, MIN_SUPPORT_ON, MIN_CALL_DELTA)):
        raise ValueError("Unsupported or altered policy method")
    nearest = sorted(
        ((sum(abs(a-b) for a, b in zip(vec, row.vector)) / 8.0, row.task_id, row)
         for row in snapshot.observations),
        key=lambda t: (t[0], t[1]),
    )[:5]
    if len(nearest) != K:
        raise ValueError("Five TRAIN observations are required")
    close = sum(distance <= MAX_DISTANCE for distance, _, _ in nearest)
    support = sum(int(row.prefer_on) for _, _, row in nearest)
    gain = sum(row.off_calls - row.on_calls for _, _, row in nearest) / 5
    veto = any(row.off_correct and row.on_audit_invalid for _, _, row in nearest)
    if close < MIN_CLOSE:
        action, reason = "OFF", "insufficient_support"
    elif veto:
        action, reason = "OFF", "audit_safety_veto"
    elif support < MIN_SUPPORT_ON:
        action, reason = "OFF", "insufficient_on_votes"
    elif gain < MIN_CALL_DELTA:
        action, reason = "OFF", "insufficient_call_saving"
    else:
        action, reason = "ON", "cost_supported"
    return PolicyDecision(action, reason,
                          tuple(task_id for _, task_id, _ in nearest),
                          support, close, gain, nearest[0][0],
                          (perf_counter() - started) * 1000)


def _candidate() -> SkillCandidate:
    candidates = discover_skills(SKILL_TRAIN)
    if len(candidates) != 1:
        raise ValueError("EXP-0002 candidate changed")
    skill = candidates[0]
    if skill.skill_id != SKILL_ID or skill.body_hash != SKILL_HASH:
        raise ValueError("Skill candidate does not match frozen protocol")
    return skill


def train() -> dict[str, object]:
    """Full-information, TRAIN-only fit. No DEV/FINAL outcome is computed."""
    manifest = dataset_manifest()
    skill = _candidate()
    base = Registry(DEFAULT_PRIMITIVES)
    enabled = registry_with_skill(skill, base)
    learned = {skill.skill_id: skill}
    rows: list[TrainingObservation] = []
    begin_wall, begin_cpu = perf_counter(), process_time()
    training_calls = 0
    for item in generate_partition("train"):
        off_meter, on_meter = PrimitiveCallMeter(), PrimitiveCallMeter()
        off = bounded_synthesize(item.task, base, meter=off_meter)
        on = bounded_synthesize(item.task, enabled, learned, meter=on_meter)
        off_valid = (off.status == "solved" and off.program is not None
                     and verify(off.program, (item.audit,), base,
                                max_nodes=item.task.limits.max_ast_nodes).matched)
        on_valid = (on.status == "solved" and on.program is not None
                    and verify(on.program, (item.audit,), enabled,
                               max_nodes=item.task.limits.max_ast_nodes).matched)
        on_invalid = on.status == "solved" and not on_valid
        if off_valid != on_valid:
            prefer_on = on_valid
        elif off_meter.total != on_meter.total:
            prefer_on = off_meter.total > on_meter.total
        else:
            prefer_on = off.tested_candidates > on.tested_candidates
        rows.append(TrainingObservation(
            item.task.task_id, features(item.task), prefer_on,
            off_meter.total, on_meter.total, off.tested_candidates,
            on.tested_candidates, bool(off_valid), bool(on_valid), bool(on_invalid)))
        training_calls += off_meter.total + on_meter.total
    wall, cpu = (perf_counter() - begin_wall) * 1000, (process_time() - begin_cpu) * 1000
    snapshot = PolicySnapshot(
        tuple(rows), str(manifest["dataset_sha256"]),
        str(manifest["generator_source_sha256"]), skill.body_hash)
    return {
        "experiment_id": "EXP-0002B",
        "phase": "TRAIN_ONLY",
        "protocol": "EXP-0002B-PLAN-V2",
        "state": "policy_trained_no_dev_or_final_outcome",
        "training_task_count": len(rows),
        "training_primitive_invocations": training_calls,
        "training_wall_ms": wall,
        "training_cpu_ms": cpu,
        "manifest": manifest,
        "snapshot": snapshot.to_dict(),
        "limitations": "TRAIN full-information observations only. No DEV or FINAL outcome; cost excludes macro discovery and global system CPU.",
    }


def _source_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              check=True, text=True, timeout=3).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def preflight() -> dict[str, object]:
    return {"experiment_id": "EXP-0002B", "phase": "PREFLIGHT",
            "source_commit": _source_commit(), "manifest": dataset_manifest(),
            "final_outcomes_opened": False}


def train_report() -> dict[str, object]:
    result = train()
    result["source_commit"] = _source_commit()
    result["final_outcomes_opened"] = False
    return result

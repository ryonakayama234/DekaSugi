"""EXP-0003A PR2: TRAIN-only Wake-Sleep foundation.

No DEV/FINAL/DREAM generation, policy choice, or library promotion in this module.
The sole method authority is experiments/EXP-0003A/plan.md (ID-v1).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import platform
import random
import sys
from time import perf_counter, process_time
from typing import Literal, Sequence

from packages.evaluation import PrimitiveCallMeter, bounded_synthesize
from packages.learning import (
    SkillCandidate, _operation_ids, _subexpressions, validate_skill,
)
from packages.library import DEFAULT_PRIMITIVES, Primitive, Registry
from packages.protocol import (
    Call, Example, Program, TaskSpec, check_program, parse_task,
    program_hash, program_to_dict,
)
from packages.verification import verify


METHOD = "EXP-0003A-PLAN-V1"
ID_VERSION = "ID-v1"
FAMILIES = (
    "identity", "trim", "lower", "upper", "normalize_lower",
    "normalize_upper", "reverse_ood", "replace_first_ood",
)
TRAIN_ALPHABET = "abcdeFGHIJ"
TRAIN_MASTER = 110_000_000
TRAIN_COUNT = 20
TRAIN_TOTAL = 160
WHITESPACE = ((" ", ""), ("  ", " "), ("\t", "\n"))


def digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def public_shape(examples: tuple[Example, Example]) -> dict[str, object]:
    if len(examples) != 2:
        raise ValueError("Exactly two public examples required")
    return {
        "schema_version": "0.1", "domain": "string_to_string",
        "limits": {"max_ast_nodes": 4, "max_candidates": 100},
        "examples": [{"input": e.input, "output": e.output} for e in examples],
    }


def opaque_id(examples: tuple[Example, Example]) -> str:
    return "t-" + digest(public_shape(examples))


@dataclass(frozen=True, slots=True)
class TrainCase:
    """Evaluator-only wrapper; never send this to the learner."""
    task: TaskSpec
    private_audit: Example
    source_record_id: str
    family: str
    seeds: tuple[int, int, int]


def _token(seed: int, family: str) -> str:
    rng = random.Random(seed)
    for _ in range(4096):
        n = rng.randrange(3, 8)
        token = "".join(rng.choice(TRAIN_ALPHABET) for _ in range(n))
        if len(set(token)) < 2 or token == token[::-1]:
            continue
        if family in ("lower", "normalize_lower") and not any(x.isupper() for x in token):
            continue
        if family in ("upper", "normalize_upper") and not any(x.islower() for x in token):
            continue
        return token
    raise ValueError("Preregistered rejection limit exceeded")


def _example(family: str, index: int, example_index: int, seed: int) -> Example:
    token = _token(seed, family)
    prefix, suffix = WHITESPACE[(index + example_index) % 3]
    if family == "identity":
        return Example(token, token)
    if family == "trim":
        return Example(prefix + token + suffix, token)
    if family == "lower":
        return Example(token, token.lower())
    if family == "upper":
        return Example(token, token.upper())
    if family == "normalize_lower":
        return Example(prefix + token + suffix, token.lower())
    if family == "normalize_upper":
        return Example(prefix + token + suffix, token.upper())
    if family == "reverse_ood":
        return Example(token, token[::-1])
    if family == "replace_first_ood":
        return Example(token, "Z" + token[1:])
    raise ValueError("Unknown preregistered family")


def generate_train() -> tuple[TrainCase, ...]:
    """Generate only TRAIN160. Never instantiate or score DEV/FINAL/DREAM."""
    cases: list[TrainCase] = []
    seen_tasks: set[str] = set()
    seen_seeds: set[int] = set()
    for family_index, family in enumerate(FAMILIES):
        for index in range(TRAIN_COUNT):
            seeds = tuple(TRAIN_MASTER + 100_000 * family_index
                          + 10 * index + j for j in range(3))
            if any(seed in seen_seeds for seed in seeds):
                raise ValueError("RNG seed collision")
            seen_seeds.update(seeds)
            examples = tuple(_example(family, index, j, seeds[j]) for j in range(3))
            public = (examples[0], examples[1])
            task_id = opaque_id(public)
            if task_id in seen_tasks:
                raise ValueError("Duplicate public task or SHA-256 collision")
            seen_tasks.add(task_id)
            task = parse_task({**public_shape(public), "task_id": task_id})
            if len(task.examples) != 2 or task.task_id != task_id:
                raise ValueError("Public task contract mismatch")
            cases.append(TrainCase(
                task, examples[2], f"train-f{family_index:02d}-i{index:03d}",
                family, seeds,
            ))
    if len(cases) != TRAIN_TOTAL or len(seen_seeds) != 3 * TRAIN_TOTAL:
        raise ValueError("Preregistered TRAIN cardinality mismatch")
    return tuple(cases)


def private_train_manifest(cases: Sequence[TrainCase]) -> dict[str, object]:
    """Private generator/evaluator manifest, never a learner argument."""
    rows = [{
        "source_record_id": c.source_record_id,
        "family": c.family,
        "seeds": list(c.seeds),
        "task_id": c.task.task_id,
        "public_task_sha256": c.task.task_id[2:],
        "audit": asdict(c.private_audit),
    } for c in cases]
    if len(rows) != TRAIN_TOTAL or len(set(c.source_record_id for c in cases)) != TRAIN_TOTAL:
        raise ValueError("Bad manifest cardinality")
    return {
        "method": METHOD, "id_version": ID_VERSION, "partition": "TRAIN",
        "count": len(rows), "private_rows_sha256": digest(rows),
        "ordered_source_ids_sha256": digest([x["source_record_id"] for x in rows]),
        "ordered_public_ids_sha256": digest([x["task_id"] for x in rows]),
    }


def _trusted_audit_meter(meter: PrimitiveCallMeter) -> Registry:
    """Independent one-example verifier, only with canonical primitive callables."""
    primitives: list[Primitive] = []
    for canonical in DEFAULT_PRIMITIVES:
        def wrapped(value: str, *, _p: Primitive = canonical) -> str:
            meter.record(_p.op_id)
            return _p.implementation(value)
        primitives.append(Primitive(
            canonical.op_id, canonical.input_type, canonical.output_type,
            canonical.semantics_version, wrapped,
        ))
    return Registry(tuple(primitives))


@dataclass(frozen=True, slots=True)
class WakeEpisode:
    task_id: str
    episode_id: str
    public_task_sha256: str
    public_search_status: str
    status: Literal["success", "audit_rejected", "not_found", "budget_exhausted"]
    program_ast: Program | None
    trace_sha256: str
    tested_candidates: int
    primitive_invocations: int
    audit_correct: bool
    audit_evidence_ref: str
    audit_primitive_invocations: int
    search_cpu_ms: float
    search_wall_ms: float
    audit_cpu_ms: float
    audit_wall_ms: float

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "wake-episode-v1",
            "episode_id": self.episode_id, "task_id": self.task_id,
            "public_task_sha256": self.public_task_sha256,
            "public_search_status": self.public_search_status,
            "status": self.status,
            "program_ast": program_to_dict(self.program_ast) if self.program_ast else None,
            "trace_sha256": self.trace_sha256,
            "tested_candidates": self.tested_candidates,
            "primitive_invocations": self.primitive_invocations,
            "audit_correct": self.audit_correct,
            "audit_evidence_ref": self.audit_evidence_ref,
            "audit_primitive_invocations": self.audit_primitive_invocations,
            "search_cpu_ms": self.search_cpu_ms, "search_wall_ms": self.search_wall_ms,
            "audit_cpu_ms": self.audit_cpu_ms, "audit_wall_ms": self.audit_wall_ms,
        }


def wake(task: TaskSpec, *, private_audit: Example) -> WakeEpisode:
    """One public search, then one independent audit. No audit-guided retry."""
    if len(task.examples) != 2 or opaque_id(task.examples) != task.task_id:
        raise ValueError("Untrusted public TaskSpec or task hash")
    if task.limits.max_ast_nodes != 4 or task.limits.max_candidates != 100:
        raise ValueError("Non-preregistered search budget")
    canonical = Registry(DEFAULT_PRIMITIVES)
    public_meter = PrimitiveCallMeter()
    start_cpu, start_wall = process_time(), perf_counter()
    search = bounded_synthesize(task, canonical, meter=public_meter)
    search_cpu_ms = (process_time() - start_cpu) * 1000
    search_wall_ms = (perf_counter() - start_wall) * 1000
    audit_meter = PrimitiveCallMeter()
    audit_correct = False
    audit_cpu_ms = audit_wall_ms = 0.0
    if search.status == "solved":
        if search.program is None:
            raise ValueError("Solved search without AST")
        check_program(search.program, canonical.signatures, max_nodes=4)
        start_cpu, start_wall = process_time(), perf_counter()
        audit_correct = verify(
            search.program, (private_audit,), _trusted_audit_meter(audit_meter),
            max_nodes=4,
        ).matched
        audit_cpu_ms = (process_time() - start_cpu) * 1000
        audit_wall_ms = (perf_counter() - start_wall) * 1000
        status = "success" if audit_correct else "audit_rejected"
    elif search.status in ("not_found", "budget_exhausted") and search.program is None:
        status = search.status
    else:
        raise ValueError("Unrecognized search result")
    audit_ref = "audit-sha256:" + digest({
        "task_id": task.task_id, "private_example": asdict(private_audit),
    })
    return WakeEpisode(
        task_id=task.task_id, episode_id="wake:" + task.task_id,
        public_task_sha256=task.task_id[2:],
        public_search_status=search.status, status=status,
        program_ast=search.program, trace_sha256=search.trace_sha256,
        tested_candidates=search.tested_candidates,
        primitive_invocations=public_meter.total,
        audit_correct=audit_correct, audit_evidence_ref=audit_ref,
        audit_primitive_invocations=audit_meter.total,
        search_cpu_ms=search_cpu_ms, search_wall_ms=search_wall_ms,
        audit_cpu_ms=audit_cpu_ms, audit_wall_ms=audit_wall_ms,
    )


@dataclass(frozen=True, slots=True)
class SkillProposal:
    proposal_id: str
    candidate: SkillCandidate
    source_episode_ids: tuple[str, ...]
    status: Literal["candidate"] = "candidate"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "skill-proposal-v1",
            "proposal_id": self.proposal_id, "candidate": self.candidate.to_dict(),
            "source_episode_ids": list(self.source_episode_ids),
            "candidate_body_sha256": self.candidate.body_hash,
            "status": self.status,
        }


def sleep(episodes: Sequence[WakeEpisode]) -> tuple[SkillProposal, ...]:
    """Extract skill from audited-success recorded ASTs, never re-synthesize."""
    if len({e.task_id for e in episodes}) != len(episodes):
        raise ValueError("Duplicate episode task ID")
    canonical = Registry(DEFAULT_PRIMITIVES)
    groups: dict[str, tuple[Call, set[str]]] = {}
    for episode in episodes:
        if episode.task_id != "t-" + episode.public_task_sha256:
            raise ValueError("Episode task hash mismatch")
        if episode.status != "success":
            if episode.audit_correct:
                raise ValueError("Inconsistent audit verdict")
            continue
        if not episode.audit_correct or episode.public_search_status != "solved":
            raise ValueError("Unaudited success cannot enter SLEEP")
        if episode.program_ast is None:
            raise ValueError("Successful episode without program")
        check_program(episode.program_ast, canonical.signatures, max_nodes=4)
        observed: set[str] = set()
        for subtree in _subexpressions(episode.program_ast):
            key = program_hash(subtree)
            if key in observed:
                continue
            observed.add(key)
            if key not in groups:
                groups[key] = subtree, set()
            groups[key][1].add(episode.task_id)
    proposals: list[SkillProposal] = []
    for body_hash, (body, task_ids) in groups.items():
        if len(task_ids) < 2:
            continue
        skill = SkillCandidate(
            skill_id="skill_" + body_hash[:16],
            body_ast=body, body_hash=body_hash,
            dependencies=_operation_ids(body),
            provenance=tuple(sorted(task_ids)), occurrences=len(task_ids),
        )
        validate_skill(skill, canonical)
        proposals.append(SkillProposal(
            proposal_id="proposal:" + skill.skill_id,
            candidate=skill,
            source_episode_ids=tuple("wake:" + task_id for task_id in skill.provenance),
        ))
    return tuple(sorted(
        proposals, key=lambda p: (-p.candidate.occurrences, p.candidate.skill_id),
    ))


def train_report() -> dict[str, object]:
    """TRAIN engineering evidence; never opens DEV/FINAL/DREAM."""
    cases = generate_train()
    manifest = private_train_manifest(cases)
    episodes = tuple(wake(case.task, private_audit=case.private_audit) for case in cases)
    proposals = sleep(episodes)
    stats = {status: sum(e.status == status for e in episodes)
             for status in ("success", "audit_rejected", "not_found", "budget_exhausted")}
    rows = [e.to_dict() for e in episodes]
    proposals_rows = [p.to_dict() for p in proposals]
    public_tasks = [{
        "task_id": case.task.task_id,
        "public_examples": [asdict(x) for x in case.task.examples],
    } for case in cases]
    return {
        "experiment_id": "EXP-0003A", "phase": "TRAIN", "status": "engineering",
        "method": METHOD, "id_version": ID_VERSION,
        "partition_counts": {"TRAIN": TRAIN_TOTAL},
        "public_tasks_sha256": digest(public_tasks),
        "private_manifest": manifest, "episodes": rows,
        "episodes_sha256": digest([
            {k: v for k, v in row.items() if not k.endswith("_ms")} for row in rows
        ]),
        "wake_status": stats, "proposals": proposals_rows,
        "proposals_sha256": digest(proposals_rows),
        "top_proposal_id": proposals[0].proposal_id if proposals else None,
        "functional_gate": "candidate_found" if proposals else "failed_no_candidate",
        "registry_promotion": "not_authorized",
        "preregistered_final_evaluated": False,
        "source_runtime": {"python": sys.version.split()[0], "platform": platform.platform()},
        "measurement": "runtime-canonical-v1",
        "notes": "Public search costs and separate audit costs are not the same as total CPU benefit.",
    }

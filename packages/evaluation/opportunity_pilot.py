"""OPPORTUNITY-001-PILOT-V1: deterministic fresh TRAIN-only source generator.

PRE-SCORING/manifest-only artifact. This module MUST NOT import a search
evaluator, infer a policy, run paired trials, touch DEV/FINAL or publish the
third audit example. Its method authority is experiments/OPPORTUNITY-001/pilot-v1.md.
"""
from __future__ import annotations

from hashlib import sha256
import json
import random
from typing import Sequence

from packages.exp0003a import TrainCase, opaque_id, public_shape
from packages.protocol import Example, TaskSpec, parse_task

METHOD = "OPPORTUNITY-001-PILOT-V1"
FAMILIES = (
    "identity", "trim", "lower", "upper",
    "normalize_lower", "normalize_upper",
    "reverse_ood", "replace_first_ood",
)
COUNT_PER_FAMILY = 8
TOTAL = 64
MASTER = 910_000_000
ALPHABET = "uvwxYQ03"
WHITESPACE = ((" ", ""), ("  ", " "), ("\t", "\n"))


def seed_for(family_index: int, task_index: int, example_index: int) -> int:
    if (type(family_index) is not int or not 0 <= family_index < len(FAMILIES)
            or type(task_index) is not int or not 0 <= task_index < 8
            or type(example_index) is not int or not 0 <= example_index < 3):
        raise ValueError("Invalid PILOT-V1 index")
    return MASTER + family_index * 100_000 + task_index * 10 + example_index


def source_id_for(family_index: int, task_index: int) -> str:
    """Deterministic evaluator-only ID; explicit function for collision tests."""
    if (type(family_index) is not int or not 0 <= family_index < len(FAMILIES)
            or type(task_index) is not int or not 0 <= task_index < COUNT_PER_FAMILY):
        raise ValueError("Invalid PILOT-V1 source index")
    return f"op-pilot-f{family_index:02d}-i{task_index:03d}"


def _token(seed: int, family: str) -> str:
    rng = random.Random(seed)
    for _ in range(4096):
        n = rng.randrange(3, 8)
        token = "".join(rng.choice(ALPHABET) for _ in range(n))
        if len(set(token)) < 2 or token == token[::-1]:
            continue
        if family in ("lower", "normalize_lower") and not any(c.isupper() for c in token):
            continue
        if family in ("upper", "normalize_upper") and not any(c.islower() for c in token):
            continue
        return token
    raise ValueError("Pilot token rejection budget exceeded")


def _example(family: str, task_index: int,
             example_index: int, seed: int) -> Example:
    token = _token(seed, family)
    prefix, suffix = WHITESPACE[(task_index + example_index) % 3]
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
    raise ValueError("Unknown PILOT-V1 family")


def generate_train_pilot() -> tuple[TrainCase, ...]:
    """64 deterministic TRAIN task wrappers. No search/evaluation is performed."""
    cases: list[TrainCase] = []
    seen_ids: set[str] = set()
    seen_source: set[str] = set()
    seen_seeds: set[int] = set()
    for family_index, family in enumerate(FAMILIES):
        for index in range(COUNT_PER_FAMILY):
            seeds = tuple(seed_for(family_index, index, j) for j in range(3))
            if any(s in seen_seeds for s in seeds):
                raise ValueError("Duplicate PILOT-V1 seed")
            seen_seeds.update(seeds)
            examples = tuple(
                _example(family, index, j, seeds[j]) for j in range(3))
            if len({(e.input, e.output) for e in examples}) != 3:
                raise ValueError("Non-distinct public/audit example; stop without resampling")
            public = (examples[0], examples[1])
            task_id = opaque_id(public)
            source_id = source_id_for(family_index, index)
            if task_id in seen_ids or source_id in seen_source:
                raise ValueError("Duplicate pilot task/source ID")
            seen_ids.add(task_id)
            seen_source.add(source_id)
            task: TaskSpec = parse_task({**public_shape(public), "task_id": task_id})
            if (len(task.examples) != 2 or task.limits.max_ast_nodes != 4
                    or task.limits.max_candidates != 100):
                raise ValueError("Pilot public task budget drift")
            cases.append(TrainCase(
                task, examples[2], source_id, family, seeds,
            ))
    if (len(cases), len(seen_ids), len(seen_source), len(seen_seeds)) != (
            TOTAL, TOTAL, TOTAL, 3 * TOTAL):
        raise ValueError("Incomplete pilot population")
    return tuple(cases)


def public_manifest(cases: Sequence[TrainCase]) -> tuple[dict[str, object], ...]:
    """Public only; excludes third audit, family, seed and source record."""
    if len(cases) != TOTAL:
        raise ValueError("Pilot manifest requires exactly 64 tasks")
    ids: set[str] = set()
    rows: list[dict[str, object]] = []
    for item in cases:
        task = item.task
        if task.task_id in ids or task.task_id != opaque_id(task.examples):
            raise ValueError("Duplicate or noncanonical public task")
        ids.add(task.task_id)
        rows.append({"task_id": task.task_id, **public_shape(task.examples)})
    return tuple(rows)


def canonical_public_digest(cases: Sequence[TrainCase]) -> str:
    rows = public_manifest(cases)
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def public_preflight() -> dict[str, object]:
    """Hash-only output for a future source-first frozen manifest, NO score."""
    cases = generate_train_pilot()
    return {
        "method": METHOD,
        "schema_version": "opportunity-pilot-preflight-v1",
        "status": "public_manifest_generated_no_scoring",
        "task_count": len(cases),
        "family_strata": len(FAMILIES),
        "public_manifest_sha256": canonical_public_digest(cases),
        "third_audit_examples_disclosed": False,
        "paired_trials_executed": 0,
        "dev_or_final_evaluated": False,
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Fresh TRAIN pilot public hash only")
    parser.add_argument("--mode", required=True, choices=("hash-only",))
    args = parser.parse_args()
    if args.mode != "hash-only":
        raise ValueError("No evaluation mode in generator")
    print(json.dumps(public_preflight(), sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

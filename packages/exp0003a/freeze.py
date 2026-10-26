"""EXP-0003A PR4: immutable split/source/learner preflight; NEVER scores DEV/FINAL.

Preregistered frozen method: experiments/EXP-0003A/plan.md.
This module may GENERATE withheld reference outputs to HASH immutable datasets.
It must never synthesize/verify/choose an action on either withheld partition.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from hashlib import sha1, sha256
import json
from pathlib import Path
import platform
import random
import sys
from typing import Literal

from packages.exp0003a import (
    FAMILIES, ID_VERSION, METHOD, TRAIN_ALPHABET, TRAIN_MASTER, TRAIN_TOTAL,
    TrainCase, _audit_ref, _private_train_rows, digest, generate_train,
    opaque_id, public_shape, WHITESPACE,
)
from packages.exp0003a.pr3 import (
    DREAM_POOL_SIZE, ArmSnapshot, generate_dream_pool, run_train_dream,
    _case_rows,
)
from packages.protocol import Example, parse_task

SPLIT_ORDER = ("train", "dream", "dev", "final")
COUNTS = {"train": 20, "dream": 64, "dev": 8, "final": 16}
MASTERS = {
    "train": 110_000_000, "dream": 410_000_000,
    "dev": 210_000_000, "final": 310_000_000,
}
ALPHABETS = {
    "train": TRAIN_ALPHABET, "dream": TRAIN_ALPHABET,
    "dev": "klmnoPQRST", "final": "uvwxyUVWXY",
}
SOURCE_FILES = (
    "experiments/EXP-0003A/plan.md",
    "packages/exp0003a/__init__.py",
    "packages/exp0003a/pr3.py",
    "packages/exp0003a/pr3_cli.py",
    "packages/exp0003a/freeze.py",
    "packages/exp0003a/freeze_cli.py",
    "packages/kernel/__init__.py",
    "packages/evaluation/__init__.py",
    "packages/learning/__init__.py",
    "packages/library/__init__.py",
    "packages/protocol/__init__.py",
    "packages/runtime/__init__.py",
    "packages/synthesis/__init__.py",
    "packages/verification/__init__.py",
)
FREEZE_FILE = Path(__file__).resolve().parents[2] / "experiments/EXP-0003A/freeze-v1.json"
SCHEMA = "EXP-0003A-FREEZE-V1"


def _token_for(seed: int, family: str, alphabet: str) -> str:
    """Independent literal realization of plan-v1, parameterized by alphabet."""
    rng = random.Random(seed)
    for _ in range(4096):
        n = rng.randrange(3, 8)
        token = "".join(rng.choice(alphabet) for _ in range(n))
        if len(set(token)) < 2 or token == token[::-1]:
            continue
        if family in ("lower", "normalize_lower") and not any(x.isupper() for x in token):
            continue
        if family in ("upper", "normalize_upper") and not any(x.islower() for x in token):
            continue
        return token
    raise ValueError("Preregistered rejection limit exceeded")


def _example_for(family: str, index: int, j: int,
                 seed: int, alphabet: str) -> Example:
    token = _token_for(seed, family, alphabet)
    prefix, suffix = WHITESPACE[(index + j) % 3]
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
    raise ValueError("Unknown frozen family")


def generate_partition(split: Literal["train", "dream", "dev", "final"]
                       ) -> tuple[TrainCase, ...]:
    """Generate public+withheld reference examples, without evaluating any task."""
    if split not in SPLIT_ORDER:
        raise ValueError("Unregistered EXP-0003A split")
    cases: list[TrainCase] = []
    task_ids: set[str] = set()
    provenance_ids: set[str] = set()
    seeds_seen: set[int] = set()
    for k, family in enumerate(FAMILIES):
        for index in range(COUNTS[split]):
            seeds = tuple(MASTERS[split] + 100000*k + 10*index + j
                          for j in range(3))
            if seeds_seen.intersection(seeds):
                raise ValueError("Duplicate RNG seed in partition")
            seeds_seen.update(seeds)
            examples = tuple(
                _example_for(family, index, j, seeds[j], ALPHABETS[split])
                for j in range(3)
            )
            public = (examples[0], examples[1])
            task_id = opaque_id(public)
            source_id = f"{split}-f{k:02d}-i{index:03d}"
            if task_id in task_ids or source_id in provenance_ids:
                raise ValueError("Duplicate task ID or source provenance")
            task_ids.add(task_id)
            provenance_ids.add(source_id)
            task = parse_task({**public_shape(public), "task_id": task_id})
            cases.append(TrainCase(task, examples[2], source_id, family, seeds))
    if (len(cases) != 8 * COUNTS[split]
            or len(seeds_seen) != len(cases) * 3):
        raise ValueError("Preregistered partition cardinality mismatch")
    return tuple(cases)


def _record(case: TrainCase) -> dict[str, object]:
    return {
        "source_record_id": case.source_record_id,
        "family": case.family,
        "seeds": list(case.seeds),
        "task_id": case.task.task_id,
        "public_task_sha256": case.task.task_id[2:],
        "public_task": {
            **public_shape(case.task.examples), "task_id": case.task.task_id,
        },
        "audit": asdict(case.private_audit),
        "audit_evidence_ref": _audit_ref(case.task.task_id, case.private_audit),
    }


def dataset_hashes() -> dict[str, object]:
    """All split data SHA256 with cross-partition ID/seed fail-closed checks.

    DEV/FINAL outputs exist only transiently as generator-private reference data.
    No hidden records are saved or handed to a policy/evaluator in this phase.
    """
    train = generate_train()
    dream = generate_dream_pool(train)
    if train != generate_partition("train"):
        raise ValueError("Independent TRAIN generator drift from PR2")
    if dream != generate_partition("dream"):
        raise ValueError("Independent DREAM generator drift from PR3")
    partitions = {
        "train": train, "dream": dream,
        "dev": generate_partition("dev"),
        "final": generate_partition("final"),
    }
    if tuple(partitions) != SPLIT_ORDER or [len(partitions[s]) for s in SPLIT_ORDER] != [160, 512, 64, 128]:
        raise ValueError("EXP-0003A preflight counts changed")
    all_cases = [case for s in SPLIT_ORDER for case in partitions[s]]
    n = len(all_cases)
    source_ids = [c.source_record_id for c in all_cases]
    public_ids = [c.task.task_id for c in all_cases]
    seeds = [seed for case in all_cases for seed in case.seeds]
    if n != 864 or len(set(source_ids)) != n or len(set(public_ids)) != n or len(set(seeds)) != 3*n:
        raise ValueError("ID-v1 cross-split task/source/seed collision")
    records = {name: [_record(case) for case in partitions[name]]
               for name in SPLIT_ORDER}
    if records["train"] != _private_train_rows(train):
        raise ValueError("TRAIN raw record mismatch")
    # PR3 Dream uses its own evaluator-specific record schema; both must
    # describe the exact same ordered pool with opaque public task hashes.
    legacy_dream_rows = _case_rows(dream)
    if any(
        x["pool_id"] != y["source_record_id"]
        or x["seeds"] != y["seeds"]
        or x["audit"] != y["audit"]
        or x["audit_evidence_ref"] != y["audit_evidence_ref"]
        or x["public_task"] != y["public_task"]
        for x, y in zip(legacy_dream_rows, records["dream"])
    ):
        raise ValueError("DREAM raw record mismatch")
    duplicates = {}
    for split in SPLIT_ORDER:
        all_inputs = [example.input for case in partitions[split]
                      for example in (*case.task.examples, case.private_audit)]
        counts = Counter(all_inputs)
        duplicates[split] = sum(n - 1 for n in counts.values() if n > 1)
    return {
        "split_order": list(SPLIT_ORDER),
        "partition_counts": {s: len(partitions[s]) for s in SPLIT_ORDER},
        "alphabets": ALPHABETS,
        "masters": MASTERS,
        "all_task_count": n, "all_seed_count": len(set(seeds)),
        "dataset_sha256": digest(records),
        "split_sha256": {s: digest(records[s]) for s in SPLIT_ORDER},
        "ordered_public_task_ids_sha256": {
            s: digest([c.task.task_id for c in partitions[s]]) for s in SPLIT_ORDER
        },
        "ordered_source_ids_sha256": {
            s: digest([c.source_record_id for c in partitions[s]]) for s in SPLIT_ORDER
        },
        "duplicate_example_input_count": duplicates,
        "pr3_source_manifest_sha256": digest(
            records["train"] + legacy_dream_rows
        ),
        "dream_pool_public_input_sha256": digest([
            case.task.task_id[2:] for case in dream
        ]),
        "raw_dev_or_final_rows_exported": False,
        "dev_or_final_scored": False,
    }


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_hashes() -> dict[str, object]:
    """Pin real Git blob hashes AND raw file hashes; no self-referential freeze file."""
    records = {}
    for relpath in SOURCE_FILES:
        path = _root() / relpath
        raw = path.read_bytes()
        git_blob = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        records[relpath] = {
            "git_blob_sha1": git_blob, "raw_sha256": sha256(raw).hexdigest(),
        }
    return {
        "files": records,
        "git_blob_manifest_sha256": digest({
            path: value["git_blob_sha1"] for path, value in records.items()
        }),
    }


def freeze_payload() -> dict[str, object]:
    """Rebuild deterministic data, selections and policy from TRAIN/DREAM only."""
    if platform.python_implementation() != "CPython" or sys.version_info[:2] != (3, 12):
        raise ValueError("Freeze generation and validation require CPython 3.12")
    dataset = dataset_hashes()
    report, evidence = run_train_dream()
    source = source_hashes()
    if report["dev_or_final_evaluated"] or report["registry_promotion"] != "not_authorized":
        raise ValueError("Illegal evaluation/promotion in freeze preflight")
    if report["source_manifest_sha256"] != dataset["pr3_source_manifest_sha256"]:
        raise ValueError("PR3 source manifest mismatch")
    if report["pool_public_input_sha256"] != dataset["dream_pool_public_input_sha256"]:
        raise ValueError("PR3 pool public manifest mismatch")
    if digest(evidence["train_rows"] + evidence["dream_rows"]) != report["source_manifest_sha256"]:
        raise ValueError("Evaluator private source evidence mismatch")
    arm_hashes = {}
    for arm in ("B1", "B2", "B3"):
        raw = report["snapshots"][arm]
        snap = ArmSnapshot.from_dict(raw)
        if snap.skill_body_sha256 != report["top_skill"]["body_hash"]:
            raise ValueError("PR3 skill candidate drift")
        if snap.source_manifest_sha256 != report["source_manifest_sha256"]:
            raise ValueError("PR3 source binding drift")
        if snap.pool_public_input_sha256 != report["pool_public_input_sha256"]:
            raise ValueError("PR3 pool binding drift")
        if raw["policy_snapshot_sha256"] != report["snapshot_hashes"][arm]:
            raise ValueError("PR3 snapshot manifest drift")
        arm_hashes[arm] = raw["policy_snapshot_sha256"]
    if [len(evidence["train_rows"]), len(evidence["dream_rows"])] != [160, 512]:
        raise ValueError("Evaluator evidence count drift")
    selected = report["selection"]
    if any(
        len(selected[arm]["ordered_selected_pool_ids"]) != 96
        for arm in ("B2", "B3")
    ):
        raise ValueError("Dream selection count drift")
    if report["wake_positive_count"] <= 0:
        raise ValueError("Missing audited TRAIN positive")
    return {
        "schema_version": SCHEMA, "experiment_id": "EXP-0003A",
        "plan": METHOD, "id_version": ID_VERSION,
        "python_implementation": platform.python_implementation(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "split_data": dataset,
        "sources": source,
        "policy": {
            "top_skill_id": report["top_skill"]["skill_id"],
            "top_skill_body_sha256": report["top_skill"]["body_hash"],
            "snapshot_sha256": arm_hashes,
            "b2_selected_sha256": selected["B2"]["selected_sha256"],
            "b3_selected_sha256": selected["B3"]["selected_sha256"],
            "b2_ordered_selected_pool_ids": selected["B2"]["ordered_selected_pool_ids"],
            "b3_ordered_selected_pool_ids": selected["B3"]["ordered_selected_pool_ids"],
            "b2_ordered_selected_task_ids": selected["B2"]["ordered_selected_task_ids"],
            "b3_ordered_selected_task_ids": selected["B3"]["ordered_selected_task_ids"],
            "train_cost_positive_count": report["wake_positive_count"],
        },
        "holdout_scoring_permitted": False,
        "registry_promotion_permitted": False,
        "status": "SOURCE_DATA_TRAIN_DREAM_PREDEV_LOCK",
    }


def preflight_record() -> dict[str, object]:
    """Immutable hash-covered manifest. No holdout scorer is reachable."""
    payload = freeze_payload()
    return {**payload, "freeze_payload_sha256": digest(payload)}


def verify_frozen(*, path: Path = FREEZE_FILE) -> dict[str, object]:
    """Fail closed on ANY source/data/selection/policy/environment drift."""
    if not path.is_file():
        raise FileNotFoundError("No reviewed EXP-0003A freeze file")
    raw = json.loads(path.read_text(encoding="utf-8"))
    expected = preflight_record()
    if raw != expected:
        raise ValueError(
            "Freeze drift / noncanonical evidence: frozen file differs from "
            "regenerated source, split, skill, selection or policy"
        )
    return raw

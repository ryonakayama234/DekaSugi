"""ACTIVE-001 Gate F: unscored public-context opportunity census.

No target, Oracle, held-out scoring or episode runner enters this API. A
public-context partition represents all classes with identical *public*
outputs. The report weights it by class count, not by arbitrary syntax count.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import combinations
import json

from packages.inquiry_world import INPUTS, build_catalog, input_split, validate_split

SCHEMA = "active-feasibility/1"
FIXTURE_SPLIT_SEED = 20261030  # Engineering-only. NOT a scientific split lock.


@dataclass(frozen=True, slots=True)
class StructuralReport:
    schema: str
    role: str
    fixture_seed: int
    world_digest: str
    split_digest: str
    semantic_class_count: int
    public_pair_count: int
    potential_task_count: int
    public_context_count: int
    f0_contexts: int
    f1_contexts: int
    f2_contexts: int
    f3_contexts: int
    f0_task_weight: int
    f1_task_weight: int
    f2_task_weight: int
    f3_task_weight: int
    positive_query_task_weight_sum: int
    query_opportunity_denominator: int
    max_version_space_size: int
    f4_status: str
    context_sha256: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _count_informative_queries(indices: list[int], query_vectors: tuple[tuple[str, ...], ...], count_q: int) -> int:
    """Independent of the active-learning policy; no Gini or Oracle execution."""
    first = query_vectors[indices[0]]
    if all(query_vectors[idx] == first for idx in indices[1:]):
        return 0
    return sum(any(query_vectors[idx][position] != first[position] for idx in indices[1:])
               for position in range(count_q))


def census_fixture(*, split_seed: int = FIXTURE_SPLIT_SEED) -> StructuralReport:
    """Enumerate ALL public-context partitions for an explicit invented split.

    Only the historical synthetic fixture seed is accepted. A future source
    freeze must use an independently approved different API and protocol.
    """
    if type(split_seed) is not int or split_seed != FIXTURE_SPLIT_SEED:
        raise ValueError("Gate F only accepts the approved invented fixture seed")
    catalog = build_catalog()
    split = input_split(split_seed)
    validate_split(split)
    if len(INPUTS) != 156 or len(catalog.classes) != 878 or catalog.syntax_count != 4681:
        raise AssertionError("finite world has drifted")
    if len(split.public_ids) != 28 or len(split.query_ids) != 64 or len(split.audit_ids) != 64:
        raise AssertionError("fixture split drifted")
    pairs = tuple(combinations(split.public_ids, 2))
    if len(pairs) != 378:
        raise AssertionError("public pair count changed")
    query_vectors = tuple(tuple(cls.output_signature[q] for q in split.query_ids)
                          for cls in catalog.classes)
    f_context = Counter()
    f_weight = Counter()
    positive_weight = 0
    max_h = 0
    transcript_hash = sha256()
    for p1, p2 in pairs:
        partitions: dict[tuple[str, str], list[int]] = defaultdict(list)
        for index, cls in enumerate(catalog.classes):
            partitions[(cls.output_signature[p1], cls.output_signature[p2])].append(index)
        for (y1, y2), indices in sorted(partitions.items()):
            n = len(indices)
            max_h = max(max_h, n)
            positive = 0 if n == 1 else _count_informative_queries(indices, query_vectors, 64)
            status = "F1" if n == 1 else "F2" if positive == 0 else "F3"
            f_context[status] += 1
            f_weight[status] += n
            positive_weight += n * positive
            # Public observations and structural counts ONLY. No target identity,
            # Oracle answer, hidden label, held-out score or query transcript.
            row = (p1, p2, y1, y2, n, status, positive)
            transcript_hash.update(json.dumps(row, ensure_ascii=False,
                                             separators=(",", ":")).encode("utf-8") + b"\n")
    potential_count = len(catalog.classes) * len(pairs)
    if sum(f_weight.values()) != potential_count or f_context["F0"]:
        raise AssertionError("invalid population partition accounting")
    if positive_weight < 0 or positive_weight > potential_count * 64:
        raise AssertionError("invalid informational opportunity mass")
    return StructuralReport(
        SCHEMA, "invented-public-structure-only/no-scoring/no-source-freeze",
        split_seed, catalog.universe_digest, split.split_digest,
        len(catalog.classes), len(pairs), potential_count, sum(f_context.values()),
        *(f_context[f"F{i}"] for i in range(4)),
        *(f_weight[f"F{i}"] for i in range(4)),
        positive_weight, potential_count * 64, max_h,
        "not_computed; adaptive second-query advantage requires separate reviewed algorithm",
        transcript_hash.hexdigest(),
    )

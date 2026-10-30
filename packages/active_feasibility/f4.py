"""ACTIVE-001 F4 bounded structural probe on invented predicted-output vectors.

No learner, Oracle, official target, evaluator-only label, or scored episode.
This function is a *context-local* definition and reference implementation,
not an authorization to run the 91,367-context Gate F census for F4.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class F4Probe:
    status: str
    semantic_classes: int
    query_count: int
    work_upper_bound: int
    fixed_identified: int | None
    adaptive_identified: int | None
    f4: bool | None
    best_fixed_pair: tuple[int, int] | None
    best_adaptive_first: int | None
    adaptive_second_by_answer: tuple[tuple[str, int], ...] | None


def _uniquely_identified(values: tuple[object, ...]) -> int:
    counts = Counter(values)
    return sum(count for count in counts.values() if count == 1)


def probe_f4(vectors: tuple[tuple[str, ...], ...],
             *, max_work: int = 50_000) -> F4Probe:
    """Compare strict adaptive vs fixed DISTINCT two-question identification.

    Each row is one semantic class in the same nonempty public-context H.
    Columns are permitted question IDs in a stable ascending order. Contents
    are *hypothetical model predictions*, not true answers. F4 is nested in
    F3: this function makes no assumption about realized heldout utility.

    N(H) = max_{q1<q2} sum_h [h is unique under outputs(q1,q2)].
    A(H) = max_{q1} sum_{answer y} max_{q2!=q1}
           sum_{h in H with output(q1)=y} [h unique under output(q2)].
    Thus A >= N; strict F4 iff A > N. Ties use ascending question IDs;
    second-question choices within each first-response group also use IDs
    in ascending order. Singleton blocks count as one identification.
    """
    if type(vectors) is not tuple or not 1 <= len(vectors) <= 276:
        raise ValueError("context must have 1..276 exact tuple semantic classes")
    if type(max_work) is not int or not 0 <= max_work <= 5_000_000:
        raise ValueError("max_work must be exact int in [0, 5_000_000]")
    first = vectors[0]
    if type(first) is not tuple or not 2 <= len(first) <= 64:
        raise ValueError("at least two and at most 64 query columns required")
    qcount = len(first)
    if any(type(row) is not tuple or len(row) != qcount or
           any(type(value) is not str or len(value) > 64 for value in row)
           for row in vectors):
        raise ValueError("rows must contain exact str predictions and fixed columns")
    n = len(vectors)
    # Conservative count of tuple/partition comparisons, not measured CPU ns.
    upper = 2 * n * qcount * (qcount - 1)
    if upper > max_work:
        return F4Probe("not_computed/resource_budget", n, qcount, upper,
                       None, None, None, None, None, None)

    best_fixed = -1
    fixed_pair = None
    for i in range(qcount):
        for j in range(i + 1, qcount):
            identified = _uniquely_identified(tuple((row[i], row[j])
                                                  for row in vectors))
            if identified > best_fixed:
                best_fixed, fixed_pair = identified, (i, j)

    best_adaptive = -1
    best_first = None
    best_choices = None
    for first_q in range(qcount):
        groups: dict[str, list[tuple[str, ...]]] = defaultdict(list)
        for row in vectors:
            groups[row[first_q]].append(row)
        identified_total = 0
        choice_by_answer = []
        for answer in sorted(groups):
            block = groups[answer]
            best_second_value = -1
            best_second = None
            for second_q in range(qcount):
                if second_q == first_q:
                    continue
                identified = _uniquely_identified(tuple(row[second_q] for row in block))
                if identified > best_second_value:
                    best_second_value, best_second = identified, second_q
            identified_total += best_second_value
            choice_by_answer.append((answer, best_second))
        if identified_total > best_adaptive:
            best_adaptive = identified_total
            best_first = first_q
            best_choices = tuple(choice_by_answer)
    if not 0 <= best_fixed <= best_adaptive <= n:
        raise AssertionError("adaptive identification must dominate fixed pairs")
    return F4Probe("computed", n, qcount, upper, best_fixed, best_adaptive,
                   best_adaptive > best_fixed, fixed_pair, best_first,
                   best_choices)

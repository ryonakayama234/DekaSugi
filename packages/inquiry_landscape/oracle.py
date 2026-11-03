"""Pure exact closed-class predictive inquiry: state-independent binary probes.

Every action is legal; at most 2 paid questions; optional early stop.
Only an evaluator calls this code; its models are NOT learner inputs.
The public oracle uses the population mixture, not the chosen world identity.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from .source import Model


@dataclass(frozen=True, slots=True)
class Certificate:
    status: str
    scope: str
    numerator_adaptive: int
    numerator_fixed: int
    denominator: int
    optimal_policy: tuple
    best_fixed: tuple[int, ...]
    root_contingent_gap: tuple[int, int, int]
    branch_actions_differ: bool

    @property
    def gain(self) -> int:
        return self.numerator_adaptive - self.numerator_fixed

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "scope": self.scope,
            "numerator_adaptive": self.numerator_adaptive,
            "numerator_fixed": self.numerator_fixed,
            "gain_numerator": self.gain,
            "denominator": self.denominator,
            "optimal_policy": self.optimal_policy,
            "best_fixed": list(self.best_fixed),
            "root_contingent_gap": list(self.root_contingent_gap),
            "branch_actions_differ": self.branch_actions_differ,
        }


def _check(models: tuple[Model, ...]) -> None:
    if type(models) is not tuple or not 1 <= len(models) <= 2000:
        raise ValueError("invalid model collection")
    for m in models:
        if type(m) is not Model or type(m.weight) is not int or not 1 <= m.weight <= 10000:
            raise ValueError("invalid exact weighted model")
        for tup in (m.questions, m.audit):
            if type(tup) is not tuple or len(tup) != 3 or any(type(i) is not int or i not in (0, 1) for i in tup):
                raise ValueError("invalid bit tuple")


def compress_models(models: tuple[Model, ...]) -> tuple[Model, ...]:
    """Exact lossless aggregation of identical observable+audit signatures."""
    _check(models)
    counts = {}
    for m in models:
        key = (m.questions, m.audit)
        counts[key] = counts.get(key, 0) + m.weight
    return tuple(Model(questions, audit, weight) for (questions, audit), weight in sorted(counts.items()))


def certify(models: tuple[Model, ...], scope: str) -> Certificate:
    if type(scope) is not str or scope not in ("WORLD_KNOWN", "PUBLIC_MIXTURE"):
        raise ValueError("invalid scope")
    rows = compress_models(models)
    all_indices = tuple(range(len(rows)))
    den = 3 * sum(m.weight for m in rows)

    @lru_cache(maxsize=None)
    def payoff(indices: tuple[int, ...]) -> int:
        mass = sum(rows[i].weight for i in indices)
        return sum(abs(sum(rows[i].weight * (1 if rows[i].audit[p] == 0 else -1)
                           for i in indices)) for p in range(3)) if mass else 0

    @lru_cache(maxsize=None)
    def policy(indices: tuple[int, ...], steps: int) -> tuple[int, tuple]:
        best = (payoff(indices), ("stop",))
        if steps == 0:
            return best
        for action in range(3):
            groups = tuple(tuple(i for i in indices if rows[i].questions[action] == y) for y in (0, 1))
            score, children = 0, []
            for members in groups:
                if members:
                    subscore, subtree = policy(members, steps - 1)
                    score += subscore
                    children.append(subtree)
                else:
                    children.append(("unreachable",))
            # Tie prefer stop then smaller action: only strictly better updates.
            if score > best[0]:
                best = (score, ("ask", action, tuple(children)))
        return best

    best_ad, tree = policy(all_indices, 2)
    best_fixed = (-1, ())
    for length in range(3):
        for schedule in product(range(3), repeat=length):
            groups = {}
            for i, m in enumerate(rows):
                signature = tuple(m.questions[a] for a in schedule)
                groups.setdefault(signature, []).append(i)
            score = sum(payoff(tuple(group)) for group in groups.values())
            if score > best_fixed[0]:
                best_fixed = (score, schedule)

    # Fixed common first action: compare contingent branch choice against
    # the best common second action, *holding the root fixed*.
    per_root = []
    for root in range(3):
        partitions = [tuple(i for i in all_indices if rows[i].questions[root] == y) for y in (0, 1)]
        adaptive = sum(policy(g, 1)[0] for g in partitions if g)
        fixed = max(sum(
            payoff(g) if action is None else sum(
                payoff(tuple(i for i in g if rows[i].questions[action] == y)) for y in (0, 1))
            for g in partitions if g) for action in (None, 0, 1, 2))
        per_root.append(adaptive - fixed)
    if best_ad < best_fixed[0] or any(i < 0 for i in per_root):
        raise AssertionError("impossible: adaptive less than fixed")
    changed = (tree[0] == "ask" and len(tree) == 3 and
               all(branch[0] == "ask" for branch in tree[2]) and
               tree[2][0][1] != tree[2][1][1])
    return Certificate("CERTIFIED_CLOSED_CLASS", scope, best_ad, best_fixed[0], den,
                       tree, best_fixed[1], tuple(per_root), changed)

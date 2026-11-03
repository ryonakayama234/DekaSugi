"""Exact finite public inquiry opportunities; evaluator/source side only.

Uniform prior, common initial visible state, one irreversible B-step session.
Adaptive policies branch on public outcomes; open-loop plans do not.
Utility is terminal MAP law identification, NOT learned-policy utility.
"""
from __future__ import annotations
from itertools import product
from functools import lru_cache
from time import monotonic
from . import ACTIONS, Law, _transition


def certify(laws: tuple[Law, ...], budget: int, *, initial_state: int = 0,
            max_plans: int = 4000, max_nodes: int = 250000,
            deadline_seconds: float = 120) -> dict:
    if type(laws) is not tuple or not 2 <= len(laws) <= 8 or any(type(x) is not Law for x in laws):
        raise ValueError("2..8 declared Laws required")
    if len(set(laws)) != len(laws):
        raise ValueError("repeated syntax: invalid closed class")
    if type(budget) is not int or not 1 <= budget <= 8 or type(initial_state) is not int or not 0 <= initial_state < 32:
        raise ValueError("budget/state")
    if any(type(v) is not int or v <= 0 for v in (max_plans, max_nodes)):
        raise ValueError("resource limits")
    if type(deadline_seconds) not in (int, float) or not 0 < deadline_seconds <= 3600:
        return {"status": "NOT_CERTIFIED", "reason": "INVALID_DEADLINE"}
    if len(ACTIONS) ** budget > max_plans:
        return {"status": "NOT_CERTIFIED", "reason": "OPEN_LOOP_PLAN_CAP",
                "plans_required": len(ACTIONS) ** budget}
    deadline = monotonic() + deadline_seconds
    explored = 0
    idxs = tuple(range(len(laws)))

    class Exhausted(Exception):
        pass

    def check():
        if monotonic() >= deadline:
            raise Exhausted("PROOF_DEADLINE")

    @lru_cache(maxsize=None)
    def best_adaptive(indices: tuple[int, ...], x: int, h: tuple, b: int):
        nonlocal explored
        check()
        explored += 1
        if explored > max_nodes:
            raise Exhausted("ADAPTIVE_NODE_CAP")
        if len(indices) == 1 or b == 0:
            return 1, None
        best = (0, None)
        for a in ACTIONS:
            check()
            groups = {}
            for j in indices:
                check()
                y, _ = _transition(laws[j], x, h, a)
                groups.setdefault(y, []).append(j)
            total = 0
            subtrees = {}
            for y, group in sorted(groups.items()):
                value, subtree = best_adaptive(tuple(group), y, (h + (a,))[-2:], b - 1)
                total += value
                subtrees[str(y)] = subtree
            if total > best[0]:
                best = (total, {"action": list(a), "branches": subtrees})
        check()
        return best

    try:
        adaptive_count, tree = best_adaptive(idxs, initial_state, (), budget)
        best_open = -1
        best_schedule = None
        evaluated = 0
        for schedule in product(ACTIONS, repeat=budget):
            check()
            observations = set()
            for model in laws:
                x, h = initial_state, ()
                outputs = []
                for a in schedule:
                    check()
                    x, h = _transition(model, x, h, a)
                    outputs.append(x)
                observations.add(tuple(outputs))
            evaluated += 1
            value = len(observations)
            if value > best_open:
                best_open = value
                best_schedule = schedule
        check()
        return {"status": "CERTIFIED_CLOSED_CLASS",
                "objective": "uniform_prior_terminal_MAP_law_accuracy",
                "closed_class_size": len(laws), "budget": budget,
                "initial_state": initial_state,
                "adaptive_value": adaptive_count / len(laws),
                "open_loop_value": best_open / len(laws),
                "adaptive_gain": (adaptive_count - best_open) / len(laws),
                "adaptive_tree": tree,
                "best_open_loop_schedule": [list(a) for a in best_schedule],
                "evaluated_open_loop_plans": evaluated,
                "visited_adaptive_nodes": explored,
                "guarantee": "exact_only_for_this_closed_class_prior_state_budget"}
    except Exhausted as e:
        return {"status": "NOT_CERTIFIED", "reason": str(e),
                "visited_adaptive_nodes": explored}

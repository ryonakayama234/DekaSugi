"""EXP-ACTIVE-002 G0A: exact evaluator-only finite inquiry-opportunity proof.

Synthetic calibration only. This module does not train, query a real world,
read historical sources, or expose evaluator-only audit labels to learners.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import isfinite
from time import monotonic


@dataclass(frozen=True, slots=True)
class ClosedWorld:
    """Evaluator-private bounded deterministic Markov tables.

    transitions[law][public_state][action] -> next public state;
    legal[public_state][action] -> bool, common to all laws;
    audit_probes[probe] -> (public_state, action), a heldout legal query.
    Positive integer priors are weights, not a learned probability model.
    """

    prior: tuple[int, ...]
    transitions: tuple[tuple[tuple[int, ...], ...], ...]
    legal: tuple[tuple[bool, ...], ...]
    audit_probes: tuple[tuple[int, int], ...]
    initial_state: int
    budget: int


def _canonical(world: ClosedWorld) -> tuple[int, int, int, int]:
    """Validate exact built-in tree types before any table access/math."""
    if type(world) is not ClosedWorld or type(world.prior) is not tuple:
        raise ValueError("noncanonical closed world")
    k = len(world.prior)
    if not 2 <= k <= 8 or any(type(w) is not int or not 1 <= w <= 1000
                               for w in world.prior):
        raise ValueError("prior must contain 2..8 positive bounded exact integers")
    if type(world.legal) is not tuple or not 2 <= len(world.legal) <= 8:
        raise ValueError("invalid public state table")
    n = len(world.legal)
    if type(world.legal[0]) is not tuple or not 1 <= len(world.legal[0]) <= 5:
        raise ValueError("invalid action table width")
    a = len(world.legal[0])
    if any(type(row) is not tuple or len(row) != a or
           any(type(flag) is not bool for flag in row) for row in world.legal):
        raise ValueError("legal action mask must use exact bool entries")
    if (type(world.initial_state) is not int or
        not 0 <= world.initial_state < n or
        type(world.budget) is not int or not 0 <= world.budget <= 4):
        raise ValueError("invalid initial state or finite step budget")
    if (type(world.transitions) is not tuple or len(world.transitions) != k or
        any(type(rows) is not tuple or len(rows) != n or
            any(type(row) is not tuple or len(row) != a or
                any(type(y) is not int or not 0 <= y < n for y in row)
                for row in rows) for rows in world.transitions)):
        raise ValueError("noncanonical public transition tables")
    if type(world.audit_probes) is not tuple or not 1 <= len(world.audit_probes) <= 8:
        raise ValueError("invalid evaluator-only probe table")
    p = len(world.audit_probes)
    if any(type(probe) is not tuple or len(probe) != 2 or
           any(type(v) is not int for v in probe) or
           not 0 <= probe[0] < n or not 0 <= probe[1] < a or
           not world.legal[probe[0]][probe[1]] for probe in world.audit_probes):
        raise ValueError("evaluator probes must be typed legal state-action pairs")
    if len(set(world.audit_probes)) != p:
        raise ValueError("repeated evaluator audit probes")
    return k, n, a, p


class _Cap(Exception):
    pass


def certify(world: ClosedWorld, *, max_plans: int = 10000,
            max_nodes: int = 100000, max_transitions: int = 2000000,
            deadline_seconds: float = 15.0) -> dict:
    """Prove optimum adaptive/nonadaptive expected *predictive* utility.

    Every evaluated probe has +1 correct, -1 wrong, 0 abstain. The oracle
    predicts one label or abstains per probe at each terminal information set.
    Return exact integer numerators with shared positive denominator.
    Open-loop may stop early but cannot choose actions based on observations.
    """
    k, n, actions, probes = _canonical(world)
    for v in (max_plans, max_nodes, max_transitions):
        if type(v) is not int or not 1 <= v <= 10000000:
            raise ValueError("invalid positive integral proof limit")
    if (type(deadline_seconds) not in (float, int) or
        not isfinite(deadline_seconds) or not 0 < deadline_seconds <= 3600):
        raise ValueError("invalid finite deadline")
    candidate_schedules = sum(actions ** b for b in range(world.budget + 1))
    if candidate_schedules > max_plans:
        return {"status": "NOT_CERTIFIED", "reason": "OPEN_LOOP_PLAN_CAP",
                "schedules_required": candidate_schedules}

    deadline = monotonic() + deadline_seconds
    nodes = transitions = 0
    weights = world.prior
    total_weight = sum(weights)
    all_indices = tuple(range(k))

    def check() -> None:
        if monotonic() >= deadline:
            raise _Cap("PROOF_DEADLINE")

    def transition(i: int, state: int, action: int) -> int:
        nonlocal transitions
        check()
        transitions += 1
        if transitions > max_transitions:
            raise _Cap("TRANSITION_CAP")
        return world.transitions[i][state][action]

    @lru_cache(maxsize=None)
    def payoff(indices: tuple[int, ...]) -> int:
        """Unnormalized Bayes-optimal terminal score, integer exact."""
        mass = sum(weights[i] for i in indices)
        answer = 0
        for probe in range(probes):
            support: dict[int, int] = {}
            for i in indices:
                audit_state, audit_action = world.audit_probes[probe]
                label = world.transitions[i][audit_state][audit_action]
                support[label] = support.get(label, 0) + weights[i]
            # Choosing the modal label earns 2*mass(mode)-mass; abstain earns 0.
            answer += max(0, 2 * max(support.values()) - mass)
        return answer

    @lru_cache(maxsize=None)
    def optimal(indices: tuple[int, ...], state: int, steps: int):
        nonlocal nodes
        check()
        nodes += 1
        if nodes > max_nodes:
            raise _Cap("ADAPTIVE_NODE_CAP")
        best_score, best_tree = payoff(indices), None  # legal stop
        if steps == 0:
            return best_score, best_tree
        for action in range(actions):
            if not world.legal[state][action]:
                continue
            groups: dict[int, list[int]] = {}
            for i in indices:
                y = transition(i, state, action)
                groups.setdefault(y, []).append(i)
            total = 0
            branches = []
            for y, subset in sorted(groups.items()):
                score, subtree = optimal(tuple(subset), y, steps - 1)
                total += score
                branches.append((y, subtree))
            if total > best_score:  # deterministic tie: stop then action index
                best_score, best_tree = total, (action, tuple(branches))
        return best_score, best_tree

    def tree_json(tree):
        if tree is None:
            return {"stop": True}
        action, branches = tree
        return {"action": action,
                "on_public_state": [{"state": state, "next": tree_json(next_tree)}
                                    for state, next_tree in branches]}

    try:
        adaptive_score, policy = optimal(all_indices, world.initial_state,
                                         world.budget)
        best_score = -1
        best_schedule: tuple[int, ...] | None = None
        legal_schedules = 0
        scanned = 0
        for length in range(world.budget + 1):
            for sequence in product(range(actions), repeat=length):
                check()
                scanned += 1
                groups: dict[tuple[int, ...], list[int]] = {}
                admissible = True
                for law in all_indices:
                    state = world.initial_state
                    observed = []
                    for a in sequence:
                        if not world.legal[state][a]:
                            admissible = False
                            break
                        state = transition(law, state, a)
                        observed.append(state)
                    if not admissible:
                        break
                    groups.setdefault(tuple(observed), []).append(law)
                if not admissible:
                    continue  # not a legal open-loop schedule under every law
                legal_schedules += 1
                score = sum(payoff(tuple(group)) for group in groups.values())
                if score > best_score:
                    best_score, best_schedule = score, sequence
        check()
        if adaptive_score < best_score:
            raise AssertionError("adaptive optimum smaller than legal open loop")
        return {
            "status": "CERTIFIED_CLOSED_CLASS", "objective": "terminal_predictive_utility_plus1_minus1_abstain0",
            "scope": "exact_only_for_this_closed_world_prior_initial_budget_audit",
            "class_size": k, "initial_state": world.initial_state,
            "budget": world.budget, "audit_probes": probes,
            "prior_total_weight": total_weight,
            "score_denominator": total_weight * probes,
            "adaptive_score_numerator": adaptive_score,
            "open_loop_score_numerator": best_score,
            "gain_numerator": adaptive_score - best_score,
            "optimal_adaptive_policy": tree_json(policy),
            "best_legal_open_loop_schedule": list(best_schedule),
            "scanned_open_loop_schedules": scanned,
            "legal_open_loop_schedules": legal_schedules,
            "visited_adaptive_nodes": nodes,
            "evaluated_transitions": transitions,
        }
    except _Cap as e:
        return {"status": "NOT_CERTIFIED", "reason": str(e),
                "visited_adaptive_nodes": nodes,
                "evaluated_transitions": transitions}

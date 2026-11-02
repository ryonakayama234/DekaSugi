"""Invented G0b-A engineering tests. ZERO historical runs, holdouts, learners or score."""
import unittest
from itertools import permutations

from packages.rep005_g0b import (
    ACTIONS, HISTORIES, FULL_CELLS, Action, Edge, Law, Literal, law,
    transition, full_signature, role_key, permute_action, permute_law,
    permute_state, reachable_domain, memoryless_contradiction,
    adaptive_identification, action_opportunity, witness_pilot_worlds,
    pilot_census,
)


def independently_written_reference(model, state, history, action):
    """Second simple list-of-bits specification, intentionally unlike bitmask engine."""
    before = [(state // (2 ** i)) % 2 for i in range(4)]
    output = before[:]
    if action.kind == "set":
        output[action.obj] = action.value
    toggles = [0, 0, 0, 0]
    for edge in model.edges:
        relevant = [action] + list(reversed(history))
        if edge.lag >= len(relevant):
            continue
        source_action = relevant[edge.lag]
        if source_action.kind != "pulse" or source_action.obj != edge.source:
            continue
        guard_true = True
        for check in edge.guard:
            if check.kind == "bit":
                valid = before[check.obj] == check.value
            elif check.lag > len(history):
                valid = False
            else:
                old = history[-check.lag]
                valid = (old.obj == check.obj and old.kind == check.kind[5:] and
                         (check.kind != "prev_set" or old.value == check.value))
            guard_true = guard_true and valid
        if guard_true:
            toggles[edge.target] += 1
    final = sum(((output[i] + toggles[i]) % 2) * (2 ** i) for i in range(4))
    return final, (history + (action,))[-2:]


class CausalWorldSyntheticTests(unittest.TestCase):
    def test_finite_domain_and_action_types(self):
        self.assertEqual(len(ACTIONS), 12)
        self.assertEqual(len(HISTORIES), 157)
        self.assertEqual(16 * len(HISTORIES) * len(ACTIONS), FULL_CELLS)
        self.assertEqual(len(set(ACTIONS)), 12)
        for bad in (lambda: Action("set", True, 0),
                    lambda: Action("pulse", 0, 0),
                    lambda: Action("set", 4, 1),
                    lambda: Action("set", 0, False),
                    lambda: Action("exec", 0)):
            with self.assertRaises(ValueError):
                bad()
        with self.assertRaises(ValueError):
            transition(law(), True, (), ACTIONS[0])
        with self.assertRaises(ValueError):
            transition(law(), 0, (Action("pulse", 0),) * 3, ACTIONS[0])

    def test_pre_action_set_xor_and_parity(self):
        delayed = law(Edge(0, 1, 1))
        # Preceding pulse triggers lag1 even when the current action sets target bit to 0.
        self.assertEqual(transition(delayed, 0, (Action("pulse", 0),),
                                    Action("set", 1, 0))[0], 2)
        self.assertEqual(transition(delayed, 0, (), Action("set", 1, 0))[0], 0)
        cancel = law(Edge(0, 1), Edge(0, 1, 0, (Literal("bit", 2, 1),)))
        self.assertEqual(transition(cancel, 4, (), Action("pulse", 0))[0], 4)
        self.assertEqual(transition(cancel, 0, (), Action("pulse", 0))[0], 2)
        conditioned = law(Edge(0, 1, 0, (Literal("bit", 2, 1),)))
        self.assertEqual(transition(conditioned, 4, (), Action("pulse", 0))[0], 6)

    def test_guard_canonical_rejections(self):
        with self.assertRaises(ValueError):
            law(Edge(0, 0))
        with self.assertRaises(ValueError):
            law(Edge(0, 1, 3))
        with self.assertRaises(ValueError):
            Edge(0, 1, 0, (Literal("bit", 1, 1), Literal("bit", 1, 0)))
        with self.assertRaises(ValueError):
            Edge(0, 1, 0, (Literal("prev_pulse", 0, -1, 1), Literal("prev_pulse", 2, -1, 1)))
        with self.assertRaises(ValueError):
            Law((Edge(1, 0), Edge(0, 1)))
        with self.assertRaises(ValueError):
            law(Edge(0, 1), Edge(0, 1))

    def test_second_reference_on_complete_30k_cell_signatures(self):
        for name, model in witness_pilot_worlds():
            self.assertEqual(len(full_signature(model)), FULL_CELLS, name)
            index = 0
            signature = full_signature(model)
            for visible in range(16):
                for history in HISTORIES:
                    for action in ACTIONS:
                        ref, hist = independently_written_reference(model, visible, history, action)
                        got, new_hist = transition(model, visible, history, action)
                        self.assertEqual((got, new_hist), (ref, hist), (name, index))
                        self.assertEqual(signature[index], ref, (name, index))
                        index += 1
            self.assertEqual(index, FULL_CELLS)

    def test_all_24_renamings_are_transition_equivariant(self):
        fixtures = witness_pilot_worlds()
        for label, model in fixtures:
            canonical = role_key(model)
            for perm in permutations(range(4)):
                remapped = permute_law(model, perm)
                self.assertEqual(role_key(remapped), canonical, label)
                for state in (0, 3, 10, 15):
                    for history in ((), (Action("pulse", 0),),
                                    (Action("pulse", 2), Action("set", 3, 1))):
                        h2 = tuple(permute_action(x, perm) for x in history)
                        for action in ACTIONS:
                            src, h_new = transition(model, state, history, action)
                            dst, h2_new = transition(remapped, permute_state(state, perm), h2,
                                                     permute_action(action, perm))
                            self.assertEqual(dst, permute_state(src, perm), label)
                            self.assertEqual(h2_new, tuple(permute_action(x, perm) for x in h_new), label)

    def test_reachable_domain_is_not_all_defined_domain(self):
        model = law()
        reach = reachable_domain(model, 1)
        self.assertEqual(len(reach), 12)
        self.assertLess(len(reach), FULL_CELLS)
        self.assertEqual(len(full_signature(model)), FULL_CELLS)
        with self.assertRaises(ValueError):
            reachable_domain(model, 9)

    def test_memoryless_counterexample_exists_only_for_actual_lag(self):
        lag = law(Edge(0, 1, 1))
        evidence = memoryless_contradiction(lag, 3)
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence["state"], 0)
        self.assertNotEqual(evidence["successor_a"], evidence["successor_b"])
        self.assertIsNone(memoryless_contradiction(law(Edge(0, 1)), 3))

    def test_id_unid_and_exhaustion_are_not_conflated(self):
        fixed, direct, delayed = law(), law(Edge(0, 1)), law(Edge(0, 1, 1))
        self.assertEqual(adaptive_identification((fixed, direct), 1)["status"], "ID")
        self.assertEqual(adaptive_identification((fixed, delayed), 1)["status"], "UNID")
        self.assertEqual(adaptive_identification((fixed, delayed), 2)["status"], "ID")
        self.assertEqual(adaptive_identification((fixed, direct), 1, max_nodes=0)["status"],
                         "NOT_CERTIFIED")
        with self.assertRaises(ValueError):
            adaptive_identification((fixed, law()), 8)

    def test_exact_achievable_opportunity_vs_repeat_fixed_action(self):
        fixed, direct = law(), law(Edge(0, 1))
        found = action_opportunity((fixed, direct), 1)
        self.assertEqual(found["status"], "POSITIVE")
        self.assertEqual(found["optimal_value"], 1.0)
        self.assertEqual(found["baseline_value"], 0.5)
        self.assertIsNotNone(found["feasible_policy_tree"])
        self.assertEqual(action_opportunity((fixed, direct), 0)["status"],
                         "NO_OPPORTUNITY")
        self.assertEqual(action_opportunity((fixed, direct), 1, max_nodes=0)["status"],
                         "NOT_CERTIFIED")

    def test_source_only_census_does_not_overclaim_independence(self):
        report = pilot_census()
        self.assertEqual(report["status"], "G0B_STOP_FULL_GRAMMAR_NOT_ENUMERATED")
        self.assertEqual(report["fixture_instances"], 8)
        self.assertLessEqual(report["distinct_full_semantics"], 8)
        self.assertLessEqual(report["typed_role_orbits"], 8)
        self.assertEqual(report["independent_family_count"], "NOT_CERTIFIED")
        self.assertEqual(report["science_train_score"], "NOT_RUN")
        self.assertEqual(report["sample_identification"]["status"], "ID")
        self.assertEqual(report["sample_action_opportunity"]["status"], "POSITIVE")


if __name__ == "__main__":
    unittest.main()

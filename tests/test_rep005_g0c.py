"""Independent finite-world source calibration, NOT learned intelligence."""
import itertools
import unittest
from packages.rep005_g0c import (
    ACTIONS, HISTORIES, DOMAIN_CELLS, Atom, Edge, Law, guards, law,
    compose, generate, signature, transition, permute_law,
    full_semantic_orbit_equivalence, census, PRODUCTIONS,
)
from packages.rep005_g0c.opportunity import certify


def independent_reference(model, before, history, action):
    """Separate specification-style bit transition, not production evaluator."""
    bits = [(before >> i) & 1 for i in range(5)]
    if action[0] == "set":
        bits[action[1]] = action[2]
    for edge in model.edges:
        k = len(history) - edge.lag if edge.lag else None
        event = action if edge.lag == 0 else history[k] if k is not None and k >= 0 else None
        if event != ("pulse", edge.source, -1):
            continue
        conditions = []
        for atom in edge.guard:
            if atom.kind == "bit":
                conditions.append((before >> atom.role) % 2 == atom.value)
            else:
                j = len(history) - atom.lag
                conditions.append(j >= 0 and history[j] == (atom.kind, atom.role, atom.value))
        if all(conditions):
            bits[edge.target] = 1 - bits[edge.target]
    return sum(bit << i for i, bit in enumerate(bits)), (history + (action,))[-2:]


class SourceTests(unittest.TestCase):
    def test_five_bit_domain_and_reference_all_cells(self):
        self.assertEqual(DOMAIN_CELLS, 115680)
        for label in ("direct", "lag1", "guard_bit", "and_guard", "chain", "join"):
            model = compose(label, (0, 1, 2))
            full = signature(model)
            self.assertEqual(len(full), DOMAIN_CELLS)
            at = 0
            for x in range(32):
                for h in HISTORIES:
                    for action in ACTIONS:
                        self.assertEqual(full[at], independent_reference(model, x, h, action)[0],
                                         (label, x, h, action))
                        at += 1

    def test_composition_and_negative_alias(self):
        direct = compose("direct", (0, 1, 2))
        alias = compose("split_guard_alias", (3, 4, 2))
        self.assertEqual(full_semantic_orbit_equivalence(direct, alias)["status"], "ALIAS")
        self.assertEqual(full_semantic_orbit_equivalence(
            direct, compose("lag1", (0, 1, 2)))["status"], "NONALIAS")
        self.assertEqual(full_semantic_orbit_equivalence(
            direct, direct, deadline_seconds=-1)["status"], "NOT_CERTIFIED")

    def test_permutation_semantics(self):
        original = compose("and_guard", (0, 1, 2))
        for p in itertools.permutations(range(5)):
            renamed = permute_law(original, p)
            before = 3
            past = (("pulse", 2, -1),)
            action = ("pulse", 0, -1)
            old = transition(original, before, past, action)[0]
            rename_mask = lambda n: sum(((n >> i) & 1) << p[i] for i in range(5))
            new = transition(renamed, rename_mask(before),
                             (("pulse", p[2], -1),), ("pulse", p[0], -1))[0]
            self.assertEqual(new, rename_mask(old))
        # Three full-domain orbit proofs, not 120 redundant expensive proofs.
        for p in (tuple(range(5)), (1, 2, 3, 4, 0), (4, 3, 2, 1, 0)):
            self.assertEqual(full_semantic_orbit_equivalence(
                original, permute_law(original, p))["status"], "ALIAS")

    def test_semantic_guard_and_parity(self):
        model = law(Edge(0, 1, 0, guards(Atom("bit", 2, 0))),
                    Edge(0, 1, 0, guards(Atom("bit", 2, 1))))
        for x in range(32):
            self.assertEqual(transition(model, x, (), ("pulse", 0, -1))[0], x ^ 2)
        # Two simultaneously triggered edges targeting B XOR-cancel.
        both = law(Edge(0, 1), Edge(0, 1, 0, guards(Atom("bit", 2, 1))))
        self.assertEqual(transition(both, 4, (), ("pulse", 0, -1))[0], 4)
        self.assertEqual(transition(both, 0, (), ("pulse", 0, -1))[0], 2)
        with self.assertRaises(ValueError):
            Law((object(),))
        class UncheckedEdge(Edge):
            def __post_init__(self):
                pass
        with self.assertRaises(ValueError):
            Law((UncheckedEdge(0, 5),))
        with self.assertRaises(ValueError):
            Edge(0, 1, 0, guards(Atom("bit", 2, 0), Atom("bit", 2, 1)))
        with self.assertRaises(ValueError):
            transition(model, 0, (), ("pulse", True, -1))
        with self.assertRaises(ValueError):
            compose("direct", (0, 0, 2))

    def test_generator_interleaving_and_census(self):
        proposals = list(generate(24))
        self.assertEqual(len(proposals), 24)
        self.assertEqual({z["source_root"] for z in proposals},
                         {"production/" + p for p in PRODUCTIONS})
        cert = census(12, deadline_seconds=90)
        self.assertEqual(cert["status"], "CERTIFIED_CLOSED_COHORT")
        self.assertEqual(cert["nonalias_role_orbits"], 11)
        self.assertEqual(cert["records"][10]["orbit_alias_of"], "g0c-0001")
        self.assertIsNone(cert["independent_scientific_family_count"])
        self.assertEqual(census(12, deadline_seconds=0)["status"], "NOT_CERTIFIED")

    def test_opportunity_adaptive_vs_open_loop_real_positive(self):
        members = tuple(compose(PRODUCTIONS[i], (0, 1, 2)) for i in (0, 3, 4, 6))
        result = certify(members, 3)
        self.assertEqual(result["status"], "CERTIFIED_CLOSED_CLASS")
        self.assertEqual(result["adaptive_value"], 1.0)
        self.assertEqual(result["open_loop_value"], 0.75)
        self.assertEqual(result["adaptive_gain"], 0.25)
        self.assertEqual(result["evaluated_open_loop_plans"], 3375)
        self.assertIsNotNone(result["adaptive_tree"])
        # Independently replay the public-outcome policy witness on each Law.
        trajectories = set()
        for model in members:
            x, h, node = 0, (), result["adaptive_tree"]
            observations = []
            while node is not None:
                action = tuple(node["action"])
                x, h = independent_reference(model, x, h, action)
                observations.append((action, x))
                node = node["branches"][str(x)]
            trajectories.add(tuple(observations))
        self.assertEqual(len(trajectories), len(members))

    def test_opportunity_null_and_resource_stop(self):
        members = (compose("direct", (0, 1, 2)), compose("guard_bit", (0, 1, 2)))
        result = certify(members, 2)
        self.assertEqual(result["status"], "CERTIFIED_CLOSED_CLASS")
        self.assertEqual(result["adaptive_gain"], 0.0)
        too_many_plans = certify(members, 4)
        self.assertEqual(too_many_plans["status"], "NOT_CERTIFIED")
        self.assertEqual(too_many_plans["reason"], "OPEN_LOOP_PLAN_CAP")
        cut = certify(members, 2, max_nodes=1)
        self.assertEqual(cut["status"], "NOT_CERTIFIED")


if __name__ == "__main__":
    unittest.main()


class ExpressibilityTests(unittest.TestCase):
    def test_old_h0_complete_membership_and_nonmembership(self):
        from packages.rep005_g0c.expressibility import certify_old_h0
        self.assertEqual(certify_old_h0(compose("direct", (0, 1, 2)))["status"], "IN_H0")
        self.assertEqual(certify_old_h0(compose("split_guard_alias", (0, 1, 2)))["status"], "IN_H0")
        outside = certify_old_h0(compose("guard_bit", (0, 1, 2)))
        self.assertEqual(outside["status"], "OUTSIDE_H0")
        self.assertEqual(outside["mismatch_witnesses"], 61)
        self.assertEqual(certify_old_h0(compose("guard_bit", (0, 1, 2)), deadline_seconds=0)["status"], "NOT_CERTIFIED")


class DeadlineRegressionTests(unittest.TestCase):
    def test_nan_and_infinity_cannot_certify(self):
        from packages.rep005_g0c.expressibility import certify_old_h0
        model = compose("direct", (0, 1, 2))
        other = compose("guard_bit", (0, 1, 2))
        for invalid in (float("nan"), float("inf"), -float("inf")):
            self.assertEqual(census(12, deadline_seconds=invalid)["status"], "NOT_CERTIFIED")
            self.assertEqual(full_semantic_orbit_equivalence(model, other, deadline_seconds=invalid)["status"], "NOT_CERTIFIED")
            self.assertEqual(certify_old_h0(model, deadline_seconds=invalid)["status"], "NOT_CERTIFIED")
            self.assertEqual(certify((model, other), 2, deadline_seconds=invalid)["status"], "NOT_CERTIFIED")
            with self.assertRaises(ValueError):
                signature(model, deadline_at=invalid)

"""G0 method-only synthetic tests. No learned model, scoring or hidden split."""
from __future__ import annotations

import importlib.util
from itertools import permutations
from pathlib import Path
import sys
import unittest


PATH = Path(__file__).resolve().parents[1] / "experiments/EXP-REP-005/g0_witness.py"
SPEC = importlib.util.spec_from_file_location("rep005_g0_witness_feasibility", PATH)
assert SPEC is not None and SPEC.loader is not None
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class G0FiniteWitnessTest(unittest.TestCase):
    def setUp(self):
        self.world = m.PrivateFixture()

    def test_three_paid_actions_are_minimal(self):
        self.assertIsNone(m.find_minimum_witness(self.world, 2))
        # Exact size-3 public-law enumeration: 12^3 legal paid sequences.
        from itertools import product
        self.assertEqual(sum(
            m.memoryless_conflict(m.public_trace(self.world, seq)) is not None
            for seq in product(m.all_actions(), repeat=3)
        ), 1)
        shortest = m.find_minimum_witness(self.world, 3)
        self.assertEqual(shortest, (
            m.Action("pulse", 0),
            m.Action("set", 0, 0),
            m.Action("pulse", 0),
        ))
        trace = m.public_trace(self.world, shortest)
        self.assertEqual([e.state_before for e in trace], [0, 0, 0])
        self.assertEqual([e.state_after for e in trace], [0, 0, 2])
        self.assertEqual(sum(e.paid_cost for e in trace), 3)
        self.assertEqual(m.memoryless_conflict(trace), (0, 2))
        self.assertGreater(m.public_consistent_hplus(trace), 0)

    def test_four_step_illustration_still_valid(self):
        a = m.Action
        trace = m.public_trace(self.world, (
            a("set", 0, 0), a("pulse", 0), a("set", 1, 0),
            a("pulse", 0),
        ))
        self.assertEqual([e.state_after for e in trace], [0, 2, 0, 0])
        self.assertEqual(m.memoryless_conflict(trace), (1, 3))
        self.assertGreater(m.public_consistent_hplus(trace), 0)

    def test_all_24_role_renamings_preserve_witness(self):
        a = m.Action
        origin = (a("pulse", 0), a("set", 0, 0), a("pulse", 0))
        for permutation in permutations(range(4)):
            world = m.permuted(self.world, permutation)
            trace = m.public_trace(world, m.permute_actions(origin, permutation))
            with self.subTest(permutation=permutation):
                self.assertIsNotNone(m.memoryless_conflict(trace))
                self.assertGreater(m.public_consistent_hplus(trace), 0)

    def test_positive_memoryless_world_is_not_falsely_rejected(self):
        memoryless = m.PrivateFixture(mode="always")
        a = m.Action
        trace = m.public_trace(memoryless, (
            a("pulse", 0), a("set", 1, 0), a("pulse", 0),
        ))
        self.assertIsNone(m.memoryless_conflict(trace))
        self.assertGreater(m.public_consistent_hplus(trace), 0)

    def test_no_free_or_forged_public_events(self):
        t = m.public_trace(self.world, (
            m.Action("pulse", 0), m.Action("set", 0, 0),
            m.Action("pulse", 0),
        ))
        forged = list(t)
        forged[1] = m.PublicEvent(1, 0, m.Action("set", 0, 0), 0, 0)
        with self.assertRaisesRegex(ValueError, "chronology"):
            m.memoryless_conflict(tuple(forged))
        forged[1] = m.PublicEvent(1, 1, m.Action("set", 0, 0), 0, 1)
        with self.assertRaisesRegex(ValueError, "chronology"):
            m.public_consistent_hplus(tuple(forged))

    def test_strict_typed_actions(self):
        for args in [("set", 0, False), ("pulse", 0, 0),
                     ("set", True, 0), ("pulse", 4, None)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                m.Action(*args)

    def test_pilot_fixture_role_orbits_fail_eighty_family_gate(self):
        # Structural upper bound, not an assertion of 14 independent families.
        # Source/target are distinct; guard is source/target/other;
        # guard value and lag give 2x2 variants; always/never add one each.
        upper = m.fixture_role_orbit_upper_bound()
        self.assertEqual(upper, {
            "always": 1, "never": 1, "guard": 12, "total": 14
        })
        self.assertLess(upper["total"], 80)
        self.assertLess(upper["guard"], 20)
        self.assertLess(upper["always"] + upper["never"], 20)

    def test_g0_receipt_explicitly_not_certified_or_scored(self):
        receipt = m.audit()
        self.assertEqual(receipt["role_permutations_checked"], 24)
        self.assertEqual(receipt["shortest_charged_actions"], 3)
        self.assertTrue(receipt["h0_universal_memoryless_conflict"])
        self.assertFalse(receipt["learning_performed"])
        self.assertFalse(receipt["scoring_performed"])
        self.assertFalse(receipt["distinct_structural_families_verified"])
        self.assertEqual(receipt["pilot_fixture_role_orbit_upper_bound"]["total"], 14)
        self.assertFalse(receipt["family_gate_passed"])


if __name__ == "__main__":
    unittest.main()

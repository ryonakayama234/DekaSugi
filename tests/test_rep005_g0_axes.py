"""REP005 G0 source-only synthetic tests; no sealed data, learning or scoring."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

FILE = Path(__file__).resolve().parents[1] / "experiments/EXP-REP-005/g0_axes.py"
SPEC = importlib.util.spec_from_file_location("rep005_g0_axes", FILE)
assert SPEC is not None and SPEC.loader is not None
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class OrthogonalG0Test(unittest.TestCase):
    def test_representation_axis_is_exclusive(self):
        for h0, hp, expected in (
            (True, True, m.Representation.H0),
            (False, True, m.Representation.HPLUS),
            (False, False, m.Representation.OUTSIDE),
        ):
            self.assertIs(m.classify_representation(
                h0_complete_fit=h0, hplus_complete_fit=hp), expected)
        self.assertIs(m.classify_representation(
            h0_complete_fit=False, hplus_complete_fit=False,
            stochastic_or_invalid=True), m.Representation.STOCHASTIC)
        self.assertIs(m.classify_representation(
            h0_complete_fit=False, hplus_complete_fit=False, exhaustive=False),
            m.Representation.UNCERTIFIED)

    def test_representation_and_identification_cross_not_four_exclusive_strata(self):
        cells = set()
        for rep in (m.Representation.H0, m.Representation.HPLUS):
            for ident in (m.Identification.IDENTIFIABLE,
                          m.Identification.UNIDENTIFIABLE):
                cells.add(m.primary_cell(m.Classification(rep, ident, True)))
        self.assertEqual(len(cells), 4)
        self.assertIsNone(m.primary_cell(m.Classification(
            m.Representation.OUTSIDE, m.Identification.IDENTIFIABLE, True)))

    def test_expected_outside_is_successful_negative_g2(self):
        for rep in (m.Representation.H0, m.Representation.HPLUS,
                    m.Representation.OUTSIDE, m.Representation.STOCHASTIC):
            case = m.Classification(rep, m.Identification.IDENTIFIABLE, True)
            self.assertTrue(m.g2_diagnostic_gate((case,)))
        self.assertFalse(m.g2_diagnostic_gate((m.Classification(
            m.Representation.OUTSIDE, m.Identification.UNCERTIFIED, False),)))
        self.assertFalse(m.g2_diagnostic_gate(()))

    def test_no_false_exhaustive_or_illegal_membership(self):
        with self.assertRaises(ValueError):
            m.classify_representation(h0_complete_fit=True, hplus_complete_fit=False)
        with self.assertRaises(ValueError):
            m.classify_representation(h0_complete_fit=False,
                                      hplus_complete_fit=True,
                                      stochastic_or_invalid=True)
        with self.assertRaises(ValueError):
            m.classify_representation(h0_complete_fit=1, hplus_complete_fit=True)
        with self.assertRaises(ValueError):
            m.Classification(m.Representation.H0, m.Identification.UNCERTIFIED, True)

    def test_exact_adaptive_horizon_positive_and_negative(self):
        yes = (m.w.PrivateFixture(mode="always"), m.w.PrivateFixture(mode="never"))
        no = (m.w.PrivateFixture(source=0, target=1, mode="never"),
              m.w.PrivateFixture(source=1, target=0, mode="never"))
        self.assertIs(m.identify_finite_class(yes, 0).status,
                      m.Identification.UNIDENTIFIABLE)
        self.assertIs(m.identify_finite_class(yes, 1).status,
                      m.Identification.IDENTIFIABLE)
        self.assertIs(m.identify_finite_class(no, 8).status,
                      m.Identification.UNCERTIFIED)
        self.assertEqual(m.identify_finite_class(no, 8).reason, "SEMANTIC_ALIASES")
        short = (m.w.PrivateFixture(mode="guard"),
                 m.w.PrivateFixture(mode="never"))
        self.assertIs(m.identify_finite_class(short, 1).status,
                      m.Identification.UNIDENTIFIABLE)
        self.assertIs(m.identify_finite_class(short, 2).status,
                      m.Identification.IDENTIFIABLE)

    def test_search_ceiling_not_misreported_as_unidentifiable(self):
        yes = (m.w.PrivateFixture(mode="always"), m.w.PrivateFixture(mode="never"))
        result = m.identify_finite_class(yes, 8, max_nodes=1)
        self.assertIs(result.status, m.Identification.UNCERTIFIED)
        self.assertFalse(result.complete)

    def test_exact_semantic_aliases_not_confused_with_budget_limit(self):
        same1 = m.w.PrivateFixture(source=0, target=1, mode="never")
        same2 = m.w.PrivateFixture(source=1, target=0, mode="never")
        different = m.w.PrivateFixture(source=0, target=1, mode="guard")
        sig1 = m.restricted_semantic_signature(same1)
        self.assertEqual(len(sig1), 30144)
        self.assertEqual(sig1, m.restricted_semantic_signature(same2))
        self.assertNotEqual(sig1, m.restricted_semantic_signature(different))
        self.assertEqual(m.identify_finite_class((same1, same2), 8).reason,
                         "SEMANTIC_ALIASES")
        with self.assertRaises(ValueError):
            m.restricted_semantic_signature(m.w.PrivateFixture(lag=3))

    def test_declared_hypothesis_contract(self):
        with self.assertRaises(ValueError):
            m.identify_finite_class((m.w.PrivateFixture(lag=3),), 8)
        with self.assertRaises(ValueError):
            m.identify_finite_class((m.w.PrivateFixture(),), 9)
        with self.assertRaises(ValueError):
            m.identify_finite_class((), 2)

    def test_existing_fixture_upper_bound_fails_families_gate(self):
        d = m.preflight()
        self.assertEqual(d["pilot_structural_orbit_UPPER_BOUND"],
                         {"always": 1, "never": 1, "guard": 12, "total": 14})
        self.assertEqual(d["inherited_witness_length"], 3)
        self.assertFalse(d["pilot_can_supply_80_independent_families"])
        self.assertFalse(d["80_independent_families_certified"])
        self.assertEqual(d["aliased_pair"], "SEMANTIC_ALIASES")
        self.assertEqual(d["restricted_signature_outcomes"], 30144)
        self.assertFalse(d["learning_performed"])
        self.assertFalse(d["scoring_performed"])


if __name__ == "__main__":
    unittest.main()

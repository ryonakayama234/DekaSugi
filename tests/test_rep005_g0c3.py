"""Synthetic engineering; no paid TRAIN, old sealed data, or learner evaluation."""
import unittest
from time import monotonic
from packages.rep005_g0c import compose, permute_law, full_semantic_orbit_equivalence
from packages.rep005_g0c3 import VERSION, draw_root, full_invariant, orbit_census, panels, run


class CausalFamilyTests(unittest.TestCase):
    def test_deterministic_indexed_roots(self):
        for i in (0, 1, 17, 47):
            self.assertEqual(draw_root(i), draw_root(i))
            self.assertEqual(draw_root(i)["root_id"], f"root-{i:04d}")

    def test_slots_and_scientific_gate(self):
        r = run(4, proof_seconds=30, panel_seconds=10)
        self.assertEqual(r["distribution"], VERSION)
        self.assertEqual(r["syntax_attempt_slots"], 8)
        self.assertEqual(r["valid_roots"] + r["invalid_roots"], 4)
        self.assertEqual(len(r["orbit"]["records"]), 4)
        self.assertEqual(r["inquiry"]["attempted"], 1)
        self.assertIsNone(r["independent_scientific_family_count"])
        self.assertEqual(r["real_paid_train_actions"], 0)

    def test_bad_indices_are_rejected(self):
        for value in (True, -1, 48, 1.5):
            with self.assertRaises(ValueError):
                draw_root(value)
        for value in (True, 3, 52):
            with self.assertRaises(ValueError):
                run(value)

    def test_nonfinite_proof_budgets_are_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), 0):
            with self.assertRaises(ValueError):
                run(4, proof_seconds=value)

    def test_full_invariant_sound_on_alias_and_delay(self):
        a = compose("direct", (0, 1, 2))
        alias = compose("split_guard_alias", (0, 1, 2))
        delay = compose("lag1", (0, 1, 2))
        end = monotonic() + 60
        self.assertEqual(full_invariant(a, deadline_at=end),
                         full_invariant(alias, deadline_at=end))
        self.assertNotEqual(full_invariant(a, deadline_at=end),
                            full_invariant(delay, deadline_at=end))

    def test_invariant_under_role_permutation(self):
        model = compose("and_guard", (0, 1, 2))
        variant = permute_law(model, (3, 4, 0, 2, 1))
        end = monotonic() + 60
        self.assertEqual(full_invariant(model, deadline_at=end),
                         full_invariant(variant, deadline_at=end))
        self.assertEqual(full_semantic_orbit_equivalence(model, variant)["status"], "ALIAS")

    def test_incomplete_invariant_never_certifies(self):
        with self.assertRaises(TimeoutError):
            full_invariant(compose("direct", (0, 1, 2)), deadline_at=0.0)

    def test_census_never_counts_unknown_as_scientific_family(self):
        r = orbit_census(tuple(draw_root(i) for i in range(4)), proof_seconds=0.000000001)
        self.assertEqual(len(r["records"]), 4)
        self.assertIsNone(r["independent_scientific_family_count"])
        self.assertLessEqual(r["certified_orbits_lower_bound"], r["orbit_upper_bound"])

    def test_invalid_panel_remains_denominator(self):
        roots = tuple(dict(root_id=f"root-{i:04d}", status="INVALID",
                           reason="FIXTURE", model=None) for i in range(4))
        r = panels(roots)
        self.assertEqual(r["invalid"], 1)
        self.assertEqual((r["opportunity_lower_bound"], r["opportunity_upper_bound"]), (0.0, 1.0))

    def test_duplicate_panel_never_resampled(self):
        model = compose("direct", (0, 1, 2))
        roots = tuple(dict(root_id=f"root-{i:04d}", status="VALID", model=model)
                      for i in range(4))
        r = panels(roots)
        self.assertEqual(r["records"][0]["reason"], "DUPLICATE_LAW_NO_REPLACEMENT")

    def test_unknown_root_blocks_later_new_orbit_claim(self):
        from unittest.mock import patch
        names = ("direct", "guard_bit", "lag1")
        roots = tuple(dict(root_id=f"root-{i:04d}", status="VALID",
                           model=compose(name, (0, 1, 2)))
                      for i, name in enumerate(names))
        with patch("packages.rep005_g0c3.full_invariant", return_value=(1,)), \
             patch("packages.rep005_g0c3.full_semantic_orbit_equivalence",
                   return_value={"status": "NOT_CERTIFIED"}):
            result = orbit_census(roots, proof_seconds=10)
        self.assertEqual(result["certified_orbits_lower_bound"], 1)
        self.assertEqual(result["orbit_upper_bound"], 3)
        self.assertEqual([x["status"] for x in result["records"]],
                         ["CERTIFIED_NEW_ORBIT", "NOT_CERTIFIED", "NOT_CERTIFIED"])

    def test_challenge_positive_is_not_natural_sample(self):
        from packages.rep005_g0c.opportunity import certify
        m = tuple(compose(name, (0, 1, 2))
                  for name in ("direct", "guard_bit", "guard_pulse", "chain"))
        self.assertEqual(certify(m, 3)["adaptive_gain"], 0.25)
        self.assertEqual(certify(m[:2], 2)["adaptive_gain"], 0.0)


if __name__ == "__main__":
    unittest.main()

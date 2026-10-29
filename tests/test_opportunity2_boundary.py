"""Invented-only independent boundary calibration checks."""
from __future__ import annotations
from itertools import product
import unittest
from scripts import opportunity2_boundary as b


class BoundaryTests(unittest.TestCase):
    def test_counts_support_and_distinct_product_oracle(self) -> None:
        off, on = b.enumerate_eligible(b.PRIMITIVES), b.enumerate_eligible(b.EXTENDED)
        self.assertEqual((len(off), len(on)), (40, 47))
        self.assertEqual({b.expand(p) for p in on}, set(off))
        weights = {"trim": 1, "lower": 1, "upper": 1, b.MACRO: 2}
        for registry, expected in ((b.PRIMITIVES, 40), (b.EXTENDED, 47)):
            witness = {p for n in range(4) for p in product(registry, repeat=n)
                       if 1 + sum(weights[o] for o in p) <= 4}
            self.assertEqual(len(witness), expected)
            self.assertEqual(witness, set(b.enumerate_eligible(registry)))

    def test_fixed_bfs_and_budget_witness(self) -> None:
        self.assertEqual(b.enumerate_eligible(b.EXTENDED)[4], (b.MACRO,))
        self.assertEqual(b.enumerate_eligible(b.PRIMITIVES)[5], ("trim", "lower"))
        r = b.calibrate()
        self.assertEqual(r["budget_5"]["off"]["status"], "budget_exhausted")
        self.assertEqual(r["budget_5"]["on"]["status"], "solved")
        self.assertEqual(r["budget_100"]["off"]["tested"], 6)
        self.assertEqual(r["budget_100"]["on"]["tested"], 5)

    def test_restricted_ascii_negative_witness(self) -> None:
        for p in b.enumerate_eligible(b.EXTENDED):
            self.assertIn(b.apply(p, "fiz"), ("fiz", "FIZ"))
            self.assertNotEqual(b.apply(p, "fiz"), "zif")

    def test_fail_closed(self) -> None:
        for bad in (["trim"], (), ("trim",), ("trim", "exec")):
            with self.assertRaises(b.BoundaryError):
                b.enumerate_eligible(bad)
        for bad in (0, 101, True, "5"):
            with self.assertRaises(b.BoundaryError):
                b.first_match(b.PRIMITIVES, bad)
        with self.assertRaises(b.BoundaryError):
            b.expand(("exec",))
        with self.assertRaises(b.BoundaryError):
            b.apply(("lower",), 12)

    def test_no_live_experiment_claim(self) -> None:
        r = b.calibrate()
        self.assertEqual(r["new_real_scored_tasks"], 0)
        self.assertFalse(r["scoring_authorized"])
        self.assertFalse(r["historical_skill_source_authenticated"])
        self.assertFalse(r["independent_review_completed"])
        self.assertNotIn("private_audit", r)


if __name__ == "__main__":
    unittest.main()

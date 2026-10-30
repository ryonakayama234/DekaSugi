"""P3 synthetic-only numerical-statistics tests. No learner or scorer imports."""
import json
import math
import sys
import unittest
from packages.active_statistics import (
    student_t_critical, paired_t_interval, hoeffding_interval,
    hoeffding_sufficient_n, nominal_normal_positive_power,
    simulate_invented, invented_p3_report,
)


class P3SyntheticStatisticsTests(unittest.TestCase):
    def test_student_t_reference_quantiles(self):
        # Widely known reference quantiles, df=1, 29 and 4095.
        self.assertAlmostEqual(student_t_critical(1), 12.706204736, places=5)
        self.assertAlmostEqual(student_t_critical(29), 2.045229642, places=5)
        self.assertAlmostEqual(student_t_critical(4095), 1.960544, places=3)
        self.assertAlmostEqual(student_t_critical(29), student_t_critical(29))
        for bad in (True, 0, 10001, 2.0):
            with self.subTest(df=bad), self.assertRaises(ValueError):
                student_t_critical(bad)

    def test_bounded_difference_intervals_and_zero_variance(self):
        d = (-1., 0., 0., 1.)
        t = paired_t_interval(d)
        h = hoeffding_interval(d)
        self.assertEqual(t.mean, 0.)
        self.assertLess(t.lower, 0.)
        self.assertGreater(t.upper, 0.)
        self.assertFalse(t.positive_evidence)
        self.assertEqual(h.status, "computed_conservative")
        self.assertAlmostEqual(h.upper, math.sqrt(2*math.log(40)/4))
        zero = paired_t_interval((0.,)*64)
        self.assertEqual(zero.status, "zero_sample_variance")
        self.assertFalse(zero.positive_evidence)
        self.assertEqual((zero.lower, zero.upper), (-1., 1.))
        # Review-found false-positive counterexample: a rare-loss IID null
        # can generate a strictly positive constant sample (P ~ 66% at N4096).
        # This MUST NOT become any positive inferential evidence.
        rare_null_all_positive = paired_t_interval((1./9999.,)*4096)
        self.assertEqual(rare_null_all_positive.status, "zero_sample_variance")
        self.assertFalse(rare_null_all_positive.positive_evidence)
        self.assertEqual((rare_null_all_positive.lower,
                          rare_null_all_positive.upper), (-1., 1.))
        for n, constant in ((8138, 0.0059), (3, 0.1),
                            (4096, 1./9999.)):
            with self.subTest(n=n, constant=constant):
                rounded = paired_t_interval((constant,)*n)
                self.assertEqual(rounded.status, "zero_sample_variance")
                self.assertEqual((rounded.lower, rounded.upper), (-1., 1.))
                self.assertFalse(rounded.positive_evidence)
        for constant in (0.25, 1.0, -1.0):
            with self.subTest(constant=constant):
                bad = paired_t_interval((constant,)*16)
                self.assertFalse(bad.positive_evidence)
                self.assertEqual(bad.status, "zero_sample_variance")
        self.assertTrue(hoeffding_interval((0.,)*64).lower < 0)
        for bad in ((True, 0.), ("0", 0.), (0., float("nan")), (2., 0.), (0.,), [0., 0.]):
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                paired_t_interval(bad)

    def test_analytic_power_and_distribution_free_sufficient_n(self):
        self.assertEqual(hoeffding_sufficient_n(), 8138)
        z = nominal_normal_positive_power(4096)
        self.assertGreater(z, .88)
        self.assertLess(z, .90)
        self.assertEqual(hoeffding_sufficient_n(delta=.05), 8138)
        for bad in (True, -0.05, 0.0, 2):
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                hoeffding_sufficient_n(delta=bad)
        with self.assertRaises(ValueError):
            nominal_normal_positive_power(True)

    def test_monte_carlo_is_reproducible_and_unscored(self):
        a = simulate_invented(n=512, repeats=4)
        self.assertEqual(a, simulate_invented(n=512, repeats=4))
        self.assertEqual(len(a), 7)
        for case in a:
            self.assertGreaterEqual(case["t_coverage_fraction"], 0.)
            self.assertLessEqual(case["t_coverage_fraction"], 1.)
            self.assertGreaterEqual(case["hoeffding_coverage_fraction"], 0.)
        for bad in (0, 100, True, 1024):
            with self.subTest(n=bad), self.assertRaises(ValueError):
                simulate_invented(n=bad, repeats=1)

    def test_actual_invented_statistical_receipt(self):
        # No actual scored task or target is generated. MC noise is descriptive
        # and must not be turned into hard pass/fail efficacy gates.
        report = invented_p3_report(repeats=100)
        self.assertEqual(report["official_scored_active001_tasks"], 0)
        self.assertFalse(report["formal_source_or_seed_freeze"])
        self.assertEqual(len(report["distributions"]), 21)
        rare_null = [case for case in report["distributions"]
                     if case["law"] == "rare_negative_null" and case["n"] == 4096]
        self.assertEqual(len(rare_null), 1)
        self.assertGreater(rare_null[0]["t_zero_sample_variance"], 0)
        self.assertEqual(rare_null[0]["t_positive_fraction"], 0.)
        self.assertEqual(report["hoeffding_sufficient_n"], 8138)
        self.assertEqual(report["proposed_n_t"], 4096)
        for forbidden in ("target_id", "audit_labels", "heldout_accuracy",
                          "oracle_answer", "actual_task_scores"):
            self.assertNotIn(forbidden, report)
        print("ACTIVE001_P3_INVENTED_STAT_RECEIPT=" +
              json.dumps(report, sort_keys=True), file=sys.stderr, flush=True)


if __name__ == "__main__":
    unittest.main()

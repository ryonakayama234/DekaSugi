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
        self.assertEqual(len(a), 6)
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
        self.assertEqual(len(report["distributions"]), 18)
        self.assertEqual(report["hoeffding_sufficient_n"], 8138)
        self.assertEqual(report["proposed_n_t"], 4096)
        for forbidden in ("target_id", "audit_labels", "heldout_accuracy",
                          "oracle_answer", "actual_task_scores"):
            self.assertNotIn(forbidden, report)
        print("ACTIVE001_P3_INVENTED_STAT_RECEIPT=" +
              json.dumps(report, sort_keys=True), file=sys.stderr, flush=True)


if __name__ == "__main__":
    unittest.main()

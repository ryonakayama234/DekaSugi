"""Synthetic-only F0-C statistical sanity; NO target truth/score access."""
import unittest
from math import sqrt,log
from packages.concept_f0c import Design,paired_hoeffding_radius,approximate_joint_success_power,illustrative_design_table

class AnalyticPreflightTests(unittest.TestCase):
    def test_bounded_two_sided_hoeffding(self):
        d=Design()
        self.assertAlmostEqual(paired_hoeffding_radius(d),sqrt(2*log(40)/2048))
        self.assertTrue(.059<paired_hoeffding_radius(d)<.061)
    def test_boundary_pass_probability_is_half_not_eighty_percent(self):
        for q in (.20,.50,.80):
            self.assertAlmostEqual(approximate_joint_success_power(.10,q),.5,places=12)
    def test_power_monotone_hypothetical(self):
        for q in (.20,.50,.80):
            self.assertGreater(approximate_joint_success_power(.15,q),
                               approximate_joint_success_power(.12,q))
            self.assertGreater(approximate_joint_success_power(.12,q,design_effect=1.0),
                               approximate_joint_success_power(.12,q,design_effect=4.0))
    def test_degenerate_and_invalid_scenarios(self):
        self.assertEqual(approximate_joint_success_power(1.0,1.0),1.0)
        self.assertEqual(approximate_joint_success_power(0.0,0.0),0.0)
        for args in ((.12,.11),(.12,1.2),(True,.5),(.12,True)):
            with self.assertRaises(ValueError):
                approximate_joint_success_power(*args)
        for d in (Design(tasks=1),Design(tasks=100000)):
            self.assertGreater(paired_hoeffding_radius(d),0)
        with self.assertRaises(ValueError):
            Design(tasks=True)
        with self.assertRaises(ValueError):
            approximate_joint_success_power(.12,.5,design_effect=.9)
    def test_table_is_always_explicitly_unscored(self):
        table=illustrative_design_table()
        self.assertEqual(len(table["scenarios"]),27)
        self.assertTrue(table["no_score_or_activation"])
        self.assertIn("NOT_A_SCIENTIFIC_RESULT",table["scope"])
        self.assertEqual(table["primary_unit"],"task, never 64 correlated audit inputs")

if __name__=="__main__": unittest.main()

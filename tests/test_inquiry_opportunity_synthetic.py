"""G0A evaluator-only constructed fixtures; never a scored learner cohort."""
from __future__ import annotations

from dataclasses import replace
import unittest

from packages.inquiry_opportunity import ClosedWorld, certify


def fixture(*, prior=(1, 1, 1, 1), audit_probes=None, legal=None, budget=2):
    # Q0 splits A/B. QA discriminates within A; QB within B. Any
    # precommitted <=2 action sequence leaves one pair ambiguous.
    signatures = ((0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 0, 1))
    # State 2 is legal but unreachable from initial 0 in this fixture;
    # prediction probes therefore test a separate legal public input context.
    return ClosedWorld(
        prior=prior,
        transitions=tuple((row, row, row) for row in signatures),
        legal=legal if legal is not None else ((True, True, True),) * 3,
        audit_probes=audit_probes if audit_probes is not None else ((2, 0), (2, 1), (2, 2)),
        initial_state=0, budget=budget)


class ExactPredictiveOpportunityTests(unittest.TestCase):
    def test_constructed_early_branch_is_strictly_adaptive_positive(self):
        r = certify(fixture())
        self.assertEqual(r["status"], "CERTIFIED_CLOSED_CLASS")
        self.assertEqual(r["score_denominator"], 12)
        self.assertEqual(r["adaptive_score_numerator"], 12)
        self.assertEqual(r["open_loop_score_numerator"], 10)
        self.assertEqual(r["gain_numerator"], 2)
        self.assertEqual(r["optimal_adaptive_policy"]["action"], 0)
        self.assertEqual(r["scanned_open_loop_schedules"], 13)

    def test_constant_audit_has_no_predictive_value_of_identification(self):
        w = fixture()
        # Every law's state-2 probe zero: predictions are trivial even if
        # public 0/1 transitions still permit identifying the hidden law.
        w = replace(w, transitions=tuple((rows[0], rows[1], (0, 0, 0))
                                           for rows in w.transitions))
        r = certify(w)
        self.assertEqual(r["gain_numerator"], 0)
        self.assertEqual(r["adaptive_score_numerator"], 12)
        self.assertEqual(r["open_loop_score_numerator"], 12)
        self.assertEqual(r["optimal_adaptive_policy"], {"stop": True})

    def test_no_information_is_null_not_expressive_failure(self):
        w = fixture()
        w = replace(w, transitions=tuple(((0, 0, 0), (0, 0, 0), rows[2])
                                         for rows in w.transitions))
        r = certify(w)
        self.assertEqual(r["status"], "CERTIFIED_CLOSED_CLASS")
        self.assertEqual(r["gain_numerator"], 0)
        self.assertEqual(r["adaptive_score_numerator"], 4)
        self.assertEqual(r["open_loop_score_numerator"], 4)

    def test_nonuniform_priors_exact_rational(self):
        r = certify(fixture(prior=(3, 1, 1, 1)))
        self.assertEqual(r["score_denominator"], 18)
        self.assertEqual(r["adaptive_score_numerator"], 18)
        self.assertEqual(r["open_loop_score_numerator"], 16)
        self.assertEqual(r["gain_numerator"], 2)

    def test_state_specific_legality_rejects_nonadaptive_invalid_schedule(self):
        w = fixture(legal=((True, True, False), (True, False, True), (True, True, True)))
        r = certify(w)
        self.assertEqual(r["status"], "CERTIFIED_CLOSED_CLASS")
        self.assertEqual(r["adaptive_score_numerator"], 12)
        self.assertGreater(r["gain_numerator"], 0)
        self.assertLess(r["legal_open_loop_schedules"], r["scanned_open_loop_schedules"])
        for i in range(4):
            state = 0
            for a in r["best_legal_open_loop_schedule"]:
                self.assertTrue(w.legal[state][a])
                state = w.transitions[i][state][a]

    def test_zero_budget_and_single_step_include_legal_stop(self):
        for b in (0, 1):
            with self.subTest(budget=b):
                r = certify(fixture(budget=b))
                self.assertEqual(r["status"], "CERTIFIED_CLOSED_CLASS")
                self.assertEqual(r["gain_numerator"], 0)
        self.assertEqual(certify(fixture(budget=0))["scanned_open_loop_schedules"], 1)

    def test_plan_node_transition_resource_caps_fail_closed(self):
        self.assertEqual(certify(fixture(), max_plans=1)["reason"], "OPEN_LOOP_PLAN_CAP")
        self.assertEqual(certify(fixture(), max_nodes=1)["reason"], "ADAPTIVE_NODE_CAP")
        self.assertEqual(certify(fixture(), max_transitions=1)["reason"], "TRANSITION_CAP")

    def test_strict_types_and_invalid_tables_are_rejected(self):
        w = fixture()
        for bad in (
            replace(w, budget=True),
            replace(w, prior=(True, 1, 1, 1)),
            replace(w, prior=(0, 1, 1, 1)),
            replace(w, legal=((1, True, True), (True, True, True), (True, True, True))),
            replace(w, initial_state=-1),
            replace(w, audit_probes=((2, False),)),
            replace(w, transitions=tuple(((0, 0, 0), (0, 0, 3), (0, 0, 0)) for _ in range(4))),
            replace(w, prior=list(w.prior)),
            replace(w, legal=(list(w.legal[0]), w.legal[1])),
        ):
            with self.subTest(bad=repr(bad)[:80]), self.assertRaises(ValueError):
                certify(bad)
        class MaliciousTuple(tuple):
            def __iter__(self):
                raise AssertionError("should not iterate attacker subtype")
        with self.assertRaises(ValueError):
            certify(replace(w, prior=MaliciousTuple(w.prior)))
        with self.assertRaises(ValueError):
            certify(w, max_nodes=True)
        with self.assertRaises(ValueError):
            certify(w, deadline_seconds=float("nan"))


if __name__ == "__main__":
    unittest.main()

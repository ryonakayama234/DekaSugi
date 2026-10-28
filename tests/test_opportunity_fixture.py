"""OPPORTUNITY-001 synthetic-only fixture calibration. No research task generation."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from packages.evaluation.opportunity import (
    PHASE, SCHEMA, classify_fixture, summarize_fixtures,
)


LOCK = {
    "dataset_sha256": "a" * 64,
    "skill_sha256": "b" * 64,
    "policy_sha256": "c" * 64,
    "primitive_sha256": "d" * 64,
    "source_commit": "e" * 40,
    "meter_version": "runtime-canonical-v1",
    "budget_id": "synthetic-fixed-budget",
}


def trial(correct=True, calls=10, *, status=None, budget=None):
    return {
        "audit_status": "verified",
        "audited_correct": correct,
        "search_status": status or ("solved" if correct else "not_found"),
        "primitive_calls": calls,
        "tested_candidates": 12,
        "false_solved": False,
        "budget_id": budget or LOCK["budget_id"],
    }


def row(index=1, *, off=None, on=None, choice="OFF"):
    return {
        "schema_version": SCHEMA, "phase": PHASE,
        "task_id": f"fx-{index:03d}",
        "source_lock": deepcopy(LOCK),
        "policy_choice": choice,
        "policy_decision_before_trials": True,
        "trials": {
            "OFF": off if off is not None else trial(True, 9),
            "ON": on if on is not None else trial(True, 5),
        },
    }


class OpportunitySyntheticTests(unittest.TestCase):

    def test_both_correct_cost_and_tie(self):
        on = classify_fixture(row(choice="OFF"), LOCK)
        self.assertEqual((on.classification, on.excess_calls, on.best_action),
                         ("both_correct_on_cheaper", 4, "ON"))
        off = classify_fixture(row(off=trial(True, 4), on=trial(True, 9),
                                   choice="ON"), LOCK)
        self.assertEqual((off.classification, off.excess_calls), (
            "both_correct_off_cheaper", 5))
        tie = classify_fixture(row(off=trial(True, 5), on=trial(True, 5),
                                   choice="ON"), LOCK)
        self.assertEqual(tie.classification, "both_correct_tie")
        self.assertEqual(tie.best_action, "OFF")
        self.assertEqual(tie.excess_calls, 0)
        self.assertFalse(tie.unique_best)

    def test_correctness_over_cost(self):
        on_only = classify_fixture(row(
            off=trial(False, 0), on=trial(True, 50), choice="OFF"), LOCK)
        self.assertEqual(on_only.classification, "on_only_correct")
        self.assertTrue(on_only.missed_success)
        self.assertIsNone(on_only.excess_calls)
        off_only = classify_fixture(row(
            off=trial(True, 70), on=trial(False, 0), choice="ON"), LOCK)
        self.assertEqual(off_only.classification, "off_only_correct")
        self.assertTrue(off_only.lost_success)
        self.assertIsNone(off_only.excess_calls)

    def test_neither_correct_is_unknown_not_zero_regret(self):
        r = classify_fixture(row(off=trial(False, 5), on=trial(False, 3)), LOCK)
        self.assertEqual(r.classification, "neither_correct")
        self.assertTrue(r.comparison_valid)
        self.assertIsNone(r.excess_calls)
        self.assertIsNone(r.best_action)

    def test_missing_and_budget_non_comparable_are_separate(self):
        missing = {
            "audit_status": "missing", "audited_correct": None,
            "search_status": None, "primitive_calls": None,
            "tested_candidates": None, "false_solved": False,
            "budget_id": LOCK["budget_id"],
        }
        mr = classify_fixture(row(off=missing), LOCK)
        self.assertEqual(mr.classification, "not_observed")
        self.assertFalse(mr.comparison_valid)
        nr = classify_fixture(row(on=trial(True, 5, budget="another")), LOCK)
        self.assertEqual(nr.classification, "non_comparable")
        self.assertFalse(nr.comparison_valid)

    def test_aggregate_counts_and_denominators(self):
        rows = [
            row(1, choice="OFF"),
            row(2, off=trial(True, 4), on=trial(True, 9), choice="ON"),
            row(3, off=trial(True, 5), on=trial(True, 5), choice="ON"),
            row(4, off=trial(False, 0), on=trial(True, 50), choice="OFF"),
            row(5, off=trial(True, 70), on=trial(False, 0), choice="ON"),
            row(6, off=trial(False, 5), on=trial(False, 3)),
            row(7, on=trial(True, 4, budget="other")),
        ]
        missing = {
            "audit_status": "missing", "audited_correct": None,
            "search_status": None, "primitive_calls": None,
            "tested_candidates": None, "false_solved": False,
            "budget_id": LOCK["budget_id"],
        }
        rows.append(row(8, off=missing))
        result = summarize_fixtures(rows, LOCK)
        self.assertEqual(result["paired_valid_count"], 6)
        self.assertEqual(result["not_observed_count"], 1)
        self.assertEqual(result["non_comparable_count"], 1)
        self.assertEqual(result["choice_sensitivity_numerator"], 4)
        self.assertEqual(result["choice_sensitivity_denominator"], 6)
        self.assertEqual(result["unique_better_action_count"], 4)
        self.assertEqual(result["policy_decision_error_count"], 4)
        self.assertEqual(result["policy_decision_error_denominator"], 4)
        self.assertEqual(result["both_correct_cost_denominator"], 3)
        self.assertEqual(result["policy_excess_calls_sum"], 9)
        self.assertEqual(result["policy_missed_success_count"], 1)
        self.assertEqual(result["policy_lost_success_count"], 1)
        self.assertEqual(result["best_of_two_success_count"], 5)
        self.assertEqual(result["best_of_two_success_denominator"], 6)
        self.assertNotIn("task_id", result)
        self.assertNotIn("private_audit", json.dumps(result))
        again = summarize_fixtures(list(reversed(rows)), LOCK)
        # Aggregate counts are order-invariant; input provenance records order.
        for key in result:
            if key != "input_sha256":
                self.assertEqual(result[key], again[key])

    def test_empty_input_is_not_a_scientific_zero(self):
        report = summarize_fixtures([], LOCK)
        self.assertEqual(report["paired_valid_count"], 0)
        self.assertEqual(report["choice_sensitivity_denominator"], 0)
        self.assertEqual(report["uncertainty"],
                         "not_estimated_for_synthetic_fixtures")

    def test_duplicates_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            summarize_fixtures([row(), row()], LOCK)

    def test_private_metadata_injections_rejected(self):
        bad = row()
        bad["family"] = "reverse"
        with self.assertRaisesRegex(ValueError, "private field"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["trials"]["ON"]["private_audit_example"] = "SECRET"
        with self.assertRaisesRegex(ValueError, "private field"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["source_lock"]["source_record_id"] = "PRIVATE"
        with self.assertRaisesRegex(ValueError, "private field"):
            classify_fixture(bad, LOCK)

    def test_wrong_identity_or_real_data_rejected(self):
        bad = row()
        bad["source_lock"]["skill_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "pinned"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["phase"] = "FINAL"
        with self.assertRaisesRegex(ValueError, "forbidden"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["schema_version"] = "opportunity-record/0.1"
        with self.assertRaisesRegex(ValueError, "forbidden"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["task_id"] = "t-" + "a"*64
        with self.assertRaisesRegex(ValueError, "synthetic"):
            classify_fixture(bad, LOCK)

    def test_untrusted_decision_order_rejected(self):
        bad = row()
        bad["policy_decision_before_trials"] = False
        with self.assertRaisesRegex(ValueError, "before"):
            classify_fixture(bad, LOCK)

    def test_false_solved_hard_stop(self):
        bad = row()
        bad["trials"]["OFF"]["false_solved"] = True
        with self.assertRaisesRegex(ValueError, "safety"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["trials"]["ON"]["audited_correct"] = False
        with self.assertRaisesRegex(ValueError, "false solution"):
            classify_fixture(bad, LOCK)

    def test_inconsistent_status_and_missing_rejected(self):
        bad = row()
        bad["trials"]["ON"]["search_status"] = "not_found"
        with self.assertRaisesRegex(ValueError, "unsolved"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["trials"]["OFF"]["audit_status"] = "missing"
        with self.assertRaisesRegex(ValueError, "mixed missing"):
            classify_fixture(bad, LOCK)

    def test_negative_nan_boolean_counts_rejected(self):
        for count in (-1, float("nan"), True, 2.4):
            with self.subTest(count=repr(count)):
                bad = row()
                bad["trials"]["OFF"]["primitive_calls"] = count
                with self.assertRaisesRegex(ValueError, "invalid primitive_calls"):
                    classify_fixture(bad, LOCK)
        bad = row()
        bad["trials"]["ON"]["tested_candidates"] = -7
        with self.assertRaisesRegex(ValueError, "invalid tested_candidates"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["trials"]["ON"]["audited_correct"] = 1
        with self.assertRaisesRegex(ValueError, "bool"):
            classify_fixture(bad, LOCK)

    def test_invalid_meter_version_and_unexpected_keys(self):
        bad = row()
        bad["source_lock"]["meter_version"] = "runtime-canonical-v2"
        with self.assertRaisesRegex(ValueError, "meter"):
            classify_fixture(bad, LOCK)
        bad = row()
        bad["policy_choice"] = "DO_NOT_CARE"
        with self.assertRaisesRegex(ValueError, "choice"):
            classify_fixture(bad, LOCK)

    def test_no_runtime_generation_or_evaluation_imports(self):
        import inspect
        import packages.evaluation.opportunity as module
        text = inspect.getsource(module)
        self.assertNotIn("from packages.exp0003a", text)
        self.assertNotIn("from packages.kernel", text)
        self.assertNotIn("from packages.metrology", text)
        self.assertNotIn("generate_train(", text)
        self.assertNotIn("bounded_synthesize(", text)


if __name__ == "__main__":
    unittest.main()

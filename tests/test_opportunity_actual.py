"""OPPORTUNITY-001 real-record adapter unit tests: synthetic tuples only."""
from __future__ import annotations

from copy import deepcopy
import json
import math
import unittest

from packages.evaluation.opportunity_actual import (
    classify_pair, normalize_audited_trial, public_redacted_pair,
)


def fake(correct=True, calls=7, *, solved=None):
    solved = correct if solved is None else solved
    evidence = {
        "search": {"status": "solved" if solved else "not_found",
                   "tested_candidates": 10, "trace_sha256": "f"*64},
        "audit_correct": correct,
        "audit_invalid_solved": False,
        "meter": {"primitive_invocations": calls, "by_op": {}},
        "selected_ast": {"node": "Input"} if solved else None,
    }
    return (evidence, 10, calls, correct, False, 1.2, 2.3, .4, .5)


class OpportunityActualAdapterTests(unittest.TestCase):
    def test_canonical_pair_cost_regret(self):
        off = normalize_audited_trial(fake(True, 12), arm="OFF")
        on = normalize_audited_trial(fake(True, 4), arm="ON")
        res = classify_pair(off, on, {"B1": "OFF", "B2": "ON", "B3": "OFF"})
        self.assertEqual(res["classification"], "both_correct_on_cheaper")
        self.assertEqual(res["unique_better_action"], "ON")
        self.assertEqual(res["policies"]["B1"]["excess_calls"], 8)
        self.assertEqual(res["policies"]["B2"]["excess_calls"], 0)
        self.assertEqual(res["policies"]["B1"]["decision_error"], True)

    def test_correctness_has_priority_to_cost(self):
        off = normalize_audited_trial(fake(False, 0), arm="OFF")
        on = normalize_audited_trial(fake(True, 80), arm="ON")
        res = classify_pair(off, on, {"B1": "OFF", "B2": "ON", "B3": "ON"})
        self.assertEqual(res["classification"], "on_only_correct")
        self.assertIsNone(res["policies"]["B1"]["excess_calls"])
        self.assertTrue(res["policies"]["B1"]["missed_success"])
        self.assertFalse(res["policies"]["B2"]["missed_success"])

    def test_neither_correct_regret_unknown(self):
        off = normalize_audited_trial(fake(False, 1), arm="OFF")
        on = normalize_audited_trial(fake(False, 2), arm="ON")
        res = classify_pair(off, on, {"B1": "OFF", "B2": "ON", "B3": "OFF"})
        self.assertEqual(res["classification"], "neither_correct")
        self.assertIsNone(res["unique_better_action"])
        self.assertIsNone(res["policies"]["B1"]["excess_calls"])
        self.assertIsNone(res["policies"]["B2"]["decision_error"])
        self.assertFalse(res["best_of_two_correct"])

    def test_both_correct_tie_no_unique_best(self):
        off = normalize_audited_trial(fake(True, 5), arm="OFF")
        on = normalize_audited_trial(fake(True, 5), arm="ON")
        result = classify_pair(off, on, {a:"OFF" for a in ("B1","B2","B3")})
        self.assertEqual(result["classification"], "both_correct_tie")
        self.assertIsNone(result["unique_better_action"])
        self.assertEqual(result["policies"]["B1"]["excess_calls"], 0)
        self.assertIsNone(result["policies"]["B1"]["decision_error"])

    def test_false_solved_is_hard_stop(self):
        bad = list(fake(True, 5))
        bad[4] = True
        with self.assertRaisesRegex(ValueError, "false_solved"):
            normalize_audited_trial(tuple(bad), arm="OFF")
        bad = list(fake(False, 5, solved=True))
        with self.assertRaisesRegex(ValueError, "Unaudited"):
            normalize_audited_trial(tuple(bad), arm="ON")

    def test_meter_and_audit_mismatch_stop(self):
        bad = list(fake(True, 6))
        bad[0] = deepcopy(bad[0])
        bad[0]["meter"]["primitive_invocations"] = 3
        with self.assertRaisesRegex(ValueError, "meter mismatch"):
            normalize_audited_trial(tuple(bad), arm="OFF")
        bad = list(fake(True, 6))
        bad[0] = deepcopy(bad[0])
        bad[0]["audit_correct"] = False
        with self.assertRaisesRegex(ValueError, "label mismatch"):
            normalize_audited_trial(tuple(bad), arm="OFF")

    def test_invalid_phase_timing_and_negative_boolean_counts(self):
        for value in (-1, True, float("nan"), 1.2):
            bad = list(fake())
            bad[2] = value
            with self.assertRaises(ValueError):
                normalize_audited_trial(tuple(bad), arm="ON")
        bad = list(fake())
        bad[5] = float("inf")
        with self.assertRaisesRegex(ValueError, "time"):
            normalize_audited_trial(tuple(bad), arm="ON")

    def test_private_field_injection_rejected(self):
        bad = list(fake())
        bad[0] = deepcopy(bad[0])
        bad[0]["private_audit"] = {"input": "secret"}
        with self.assertRaisesRegex(ValueError, "private fields"):
            normalize_audited_trial(tuple(bad), arm="OFF")

    def test_bad_choice_shape_and_swapped_arms(self):
        off = normalize_audited_trial(fake(), arm="OFF")
        on = normalize_audited_trial(fake(), arm="ON")
        with self.assertRaisesRegex(ValueError, "choice set"):
            classify_pair(off, on, {"B1":"ON"})
        with self.assertRaisesRegex(ValueError, "arm identity"):
            classify_pair(on, off, {"B1":"OFF","B2":"ON","B3":"OFF"})

    def test_public_record_redacts_third_audit(self):
        result = public_redacted_pair(
            "t-"+"a"*64, fake(True, 11), fake(True, 7),
            {"B1":"OFF","B2":"ON","B3":"OFF"}, "c"*64)
        raw = json.dumps(result, sort_keys=True)
        self.assertEqual(result["schema_version"], "opportunity-paired-evidence-v1")
        self.assertEqual(result["trials"]["ON"]["primitive_calls"], 7)
        for word in ("private_audit", "source_record_id", "family", "seeds", "audit_input", "audit_output"):
            self.assertNotIn(word, raw)
        self.assertEqual(len(result["audit_commitment_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()

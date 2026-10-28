"""Synthetic-only negative controls for OPPORTUNITY-001 real tuple normalizer."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from packages.evaluation.opportunity_actual import (
    classify_pair, normalize_audited_trial, public_redacted_pair,
)

TASK = "t-" + "a" * 64
CHOICES = {"B1": "OFF", "B2": "ON", "B3": "OFF"}


def fake(correct=True, calls=7, *, solved=None, task_id=TASK):
    solved = correct if solved is None else solved
    selected = {"node_kind": "input", "type": "String"} if solved else None
    return ({
        "search": {
            "task_id": task_id, "status": "solved" if solved else "not_found",
            "solved": solved, "program": selected, "tested_candidates": 10,
            "max_nodes": 4, "max_candidates": 100, "trace_sha256": "f"*64,
        },
        "audit_correct": correct,
        "audit_invalid_solved": False,
        "meter": {"primitive_invocations": calls,
                  "by_op": {"trim": calls} if calls else {}},
        "selected_ast": deepcopy(selected),
    }, 10, calls, correct, False, 1.2, 2.3, .4, .5)


def tamper(field, value, *, calls=7):
    raw = list(fake(True, calls))
    raw[0] = deepcopy(raw[0])
    if isinstance(field, tuple):
        raw[0][field[0]][field[1]] = value
    else:
        raw[0][field] = value
    return tuple(raw)


class OpportunityActualAdapterTests(unittest.TestCase):
    def test_canonical_pair_cost_regret(self):
        off = normalize_audited_trial(fake(True, 12), arm="OFF")
        on = normalize_audited_trial(fake(True, 4), arm="ON")
        res = classify_pair(off, on, CHOICES)
        self.assertEqual(res["classification"], "both_correct_on_cheaper")
        self.assertEqual(res["unique_better_action"], "ON")
        self.assertEqual(res["policies"]["B1"]["excess_calls"], 8)
        self.assertEqual(res["policies"]["B2"]["excess_calls"], 0)
        self.assertTrue(res["policies"]["B1"]["decision_error"])

    def test_correctness_dominates_cost(self):
        off = normalize_audited_trial(fake(False, 0), arm="OFF")
        on = normalize_audited_trial(fake(True, 80), arm="ON")
        res = classify_pair(off, on, CHOICES)
        self.assertEqual(res["classification"], "on_only_correct")
        self.assertIsNone(res["policies"]["B1"]["excess_calls"])
        self.assertTrue(res["policies"]["B1"]["missed_success"])
        self.assertFalse(res["policies"]["B2"]["missed_success"])

    def test_off_only_correct(self):
        off = normalize_audited_trial(fake(True, 3), arm="OFF")
        on = normalize_audited_trial(fake(False, 0), arm="ON")
        res = classify_pair(off, on, CHOICES)
        self.assertEqual(res["classification"], "off_only_correct")
        self.assertTrue(res["policies"]["B2"]["lost_success"])
        self.assertIsNone(res["policies"]["B2"]["excess_calls"])

    def test_neither_correct_regret_unknown(self):
        off = normalize_audited_trial(fake(False, 1), arm="OFF")
        on = normalize_audited_trial(fake(False, 2), arm="ON")
        res = classify_pair(off, on, CHOICES)
        self.assertEqual(res["classification"], "neither_correct")
        self.assertIsNone(res["unique_better_action"])
        self.assertIsNone(res["policies"]["B1"]["excess_calls"])
        self.assertIsNone(res["policies"]["B2"]["decision_error"])
        self.assertFalse(res["best_of_two_correct"])

    def test_correct_tie(self):
        off = normalize_audited_trial(fake(True, 5), arm="OFF")
        on = normalize_audited_trial(fake(True, 5), arm="ON")
        res = classify_pair(off, on, CHOICES)
        self.assertEqual(res["classification"], "both_correct_tie")
        self.assertIsNone(res["unique_better_action"])
        self.assertEqual(res["policies"]["B1"]["excess_calls"], 0)
        self.assertIsNone(res["policies"]["B2"]["decision_error"])

    def test_false_solved_hard_stop(self):
        raw = list(fake())
        raw[4] = True
        with self.assertRaisesRegex(ValueError, "false_solved"):
            normalize_audited_trial(tuple(raw), arm="OFF")
        with self.assertRaisesRegex(ValueError, "Unaudited"):
            normalize_audited_trial(fake(False, 5, solved=True), arm="ON")

    def test_meter_and_audit_mismatch(self):
        with self.assertRaisesRegex(ValueError, "meter mismatch"):
            normalize_audited_trial(tamper(("meter", "primitive_invocations"), 3), arm="OFF")
        with self.assertRaisesRegex(ValueError, "label mismatch"):
            normalize_audited_trial(tamper("audit_correct", False), arm="OFF")

    def test_meter_by_op_strict_canonical_sum(self):
        for value in ({"trim": 999}, {"trim": 2, "lower": 2}, {"skill": 7},
                      {"trim": True}, {"trim": 7.0}, {"trim": -7},
                      {"trim": 0, "lower": 7}, {}, {"lower": "7"}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "by_op"):
                normalize_audited_trial(tamper(("meter", "by_op"), value), arm="ON")
        normalize_audited_trial(fake(False, 0), arm="OFF")

    def test_trace_rejects_private_object_or_invalid_hash(self):
        for value in ({"private_audit": {"input": "SECRET"}}, "SECRET", None,
                      "F"*64, "g"*64, 24):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "trace SHA256"):
                normalize_audited_trial(tamper(("search", "trace_sha256"), value), arm="OFF")

    def test_search_program_solved_status_consistency(self):
        for field, value in (
            ("solved", False), ("program", None), ("program", {"different": True}),
            ("status", "not_found"),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                normalize_audited_trial(tamper(("search", field), value), arm="OFF")
        with self.assertRaisesRegex(ValueError, "private fields"):
            normalize_audited_trial(tamper(("search", "private_third"), "SECRET"), arm="OFF")

    def test_budget_and_task_identity(self):
        raw1 = fake(True, 5)
        raw2 = fake(True, 4, task_id="t-" + "b"*64)
        with self.assertRaisesRegex(ValueError, "task identity"):
            classify_pair(normalize_audited_trial(raw1, arm="OFF"),
                          normalize_audited_trial(raw2, arm="ON"), CHOICES)
        for name, value in (("max_nodes", 5), ("max_candidates", 99)):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "budget"):
                normalize_audited_trial(tamper(("search", name), value), arm="ON")
        with self.assertRaisesRegex(ValueError, "task IDs mismatch"):
            public_redacted_pair(TASK, raw1, raw2, CHOICES, "c"*64)

    def test_invalid_phase_timing_and_counts(self):
        for value in (-1, True, float("nan"), 1.2):
            raw = list(fake())
            raw[2] = value
            with self.assertRaises(ValueError):
                normalize_audited_trial(tuple(raw), arm="ON")
        raw = list(fake())
        raw[5] = float("inf")
        with self.assertRaisesRegex(ValueError, "time"):
            normalize_audited_trial(tuple(raw), arm="ON")

    def test_private_field_injection(self):
        with self.assertRaisesRegex(ValueError, "private fields"):
            normalize_audited_trial(tamper("private_audit", {"input": "SECRET"}), arm="OFF")
        raw = list(fake())
        raw[0] = deepcopy(raw[0])
        raw[0]["meter"]["private_audit"] = "SECRET"
        with self.assertRaisesRegex(ValueError, "private fields"):
            normalize_audited_trial(tuple(raw), arm="OFF")

    def test_bad_choices_swapped_arm(self):
        off = normalize_audited_trial(fake(), arm="OFF")
        on = normalize_audited_trial(fake(), arm="ON")
        with self.assertRaisesRegex(ValueError, "choice set"):
            classify_pair(off, on, {"B1": "ON"})
        with self.assertRaisesRegex(ValueError, "arm identity"):
            classify_pair(on, off, CHOICES)

    def test_public_redacted_record(self):
        result = public_redacted_pair(TASK, fake(True, 11), fake(True, 7),
                                      CHOICES, "c"*64)
        raw = json.dumps(result, sort_keys=True)
        self.assertEqual(result["schema_version"], "opportunity-paired-evidence-v1")
        self.assertEqual(result["trials"]["ON"]["primitive_calls"], 7)
        for word in ("private_audit", "source_record_id", "family", "seeds",
                     "audit_input", "audit_output", "SECRET"):
            self.assertNotIn(word, raw)
        self.assertEqual(len(result["audit_commitment_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()

"""METRO-0001 CAL-01 preregistered synthetic calibration tests."""
from __future__ import annotations

from copy import deepcopy
import unittest

from packages.metrology import (
    EvidenceError, SUMMARY_SHA256, analyze, calibrate, canonical_bytes,
    digest, gold_evidence, seal, validate, _tampered_case,
)


class CAL01Test(unittest.TestCase):
    def test_f01_gold_exact_summary_and_sha(self):
        r = analyze(gold_evidence())
        self.assertEqual(r["status"], "comparable")
        self.assertEqual(r["summary_sha256"], SUMMARY_SHA256)
        self.assertEqual(r["summary"], {
            "arm_totals": {
                "OFF": {"audited_correct": 2, "candidate_count": 12,
                        "primitive_invocations": 24},
                "ON": {"audited_correct": 2, "candidate_count": 12,
                       "primitive_invocations": 27},
            },
            "paired": {"OFF_minus_ON_calls": -3},
            "task_count": 3,
        })

    def test_f02_permutation_has_same_semantic_hash(self):
        a = gold_evidence()
        b = list(reversed(deepcopy(a)))
        self.assertEqual(analyze(a), analyze(b))
        self.assertEqual(digest(a) != digest(b), True)

    def test_f03_duplicate_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "duplicate_record"):
            analyze(_tampered_case("F03"))

    def test_f04_missing_audit_rejected_even_if_resealed(self):
        with self.assertRaisesRegex(EvidenceError, "missing_or_extra_field"):
            analyze(_tampered_case("F04"))

    def test_f05_tampering_detected(self):
        with self.assertRaisesRegex(EvidenceError, "invalid_hash"):
            analyze(_tampered_case("F05"))

    def test_f06_individually_valid_incompatible_units(self):
        evidence = _tampered_case("F06")
        for record in evidence:
            validate(record)
        result = analyze(evidence)
        self.assertEqual(result["status"], "non_comparable")
        self.assertEqual(result["reason"], "metric_mismatch")
        self.assertNotIn("summary", result)

    def test_invalid_single_observation_unit_fails_closed(self):
        data = gold_evidence()
        data[0]["observation"]["unit"] = "ns"
        data[0] = seal(data[0])
        with self.assertRaisesRegex(EvidenceError, "invalid_unit"):
            analyze(data)

    def test_valid_budget_change_is_non_comparable_not_invalid(self):
        rows = gold_evidence()
        rows[1]["trial_ref"]["limits"]["max_candidates"] = 99
        rows[1] = seal(rows[1])
        validate(rows[1])
        report = analyze(rows)
        self.assertEqual(report["status"], "non_comparable")
        self.assertEqual(report["reason"], "budget_mismatch")
        self.assertNotIn("summary", report)

    def test_invalid_budget_not_accepted(self):
        rows = gold_evidence()
        rows[1]["trial_ref"]["limits"]["max_candidates"] = 0
        rows[1] = seal(rows[1])
        with self.assertRaisesRegex(EvidenceError, "invalid_budget"):
            analyze(rows)

    def test_false_solved_audit_mismatch_rejected(self):
        rows = gold_evidence()
        rows[0]["trial_ref"]["audit_correct"] = False
        rows[0] = seal(rows[0])
        with self.assertRaisesRegex(EvidenceError, "inconsistent_verification"):
            analyze(rows)

    def test_fixture_manifest_retains_all_raw_cases_and_hashes(self):
        from packages.metrology import fixture_manifest
        manifest = fixture_manifest()
        self.assertEqual(len(manifest["cases"]), 8)
        for case in manifest["cases"]:
            self.assertEqual(case["raw_rows_sha256"], digest(case["raw_rows"]))
        self.assertEqual(manifest["cases"][0]["raw_rows"], gold_evidence())

    def test_f07_partition_leak_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "partition_leak"):
            analyze(_tampered_case("F07"))

    def test_f08_invalid_time_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "invalid_value"):
            analyze(_tampered_case("F08"))

    def test_nonfinite_transport_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "invalid_serialization"):
            canonical_bytes({"cpu_process_ns": float("nan")})

    def test_calibrate_all_fixture_expectations(self):
        r = calibrate()
        self.assertEqual(r["status"], "engineering_fixture_pass")
        self.assertEqual(len(r["cases"]), 8)
        self.assertTrue(all(x["result"] == "pass" for x in r["cases"]))

    def test_reducer_read_only_original_data(self):
        evidence = gold_evidence()
        before = deepcopy(evidence)
        analyze(evidence)
        self.assertEqual(evidence, before)

    def test_m3_existing_canonical_meter_does_not_change_synthesis(self):
        # Synthetic publicly visible examples only; does not access any
        # EXP-0003A DEV/FINAL data or execute private evaluations.
        from packages.evaluation import PrimitiveCallMeter, bounded_synthesize
        from packages.library import DEFAULT_REGISTRY
        from packages.protocol import parse_task, program_to_dict

        task = parse_task({
            "schema_version": "0.1", "task_id": "metro-m3-synthetic",
            "domain": "string_to_string",
            "examples": [
                {"input": "  RED  ", "output": "red"},
                {"input": " Blue ", "output": "blue"},
            ],
            "limits": {"max_ast_nodes": 4, "max_candidates": 100},
        })
        plain = bounded_synthesize(task, DEFAULT_REGISTRY)
        metered = bounded_synthesize(task, DEFAULT_REGISTRY,
                                     meter=PrimitiveCallMeter())
        self.assertEqual(plain.status, metered.status)
        self.assertEqual(plain.tested_candidates, metered.tested_candidates)
        self.assertEqual(plain.trace_sha256, metered.trace_sha256)
        self.assertEqual(
            program_to_dict(plain.program) if plain.program is not None else None,
            program_to_dict(metered.program) if metered.program is not None else None,
        )


if __name__ == "__main__":
    unittest.main()

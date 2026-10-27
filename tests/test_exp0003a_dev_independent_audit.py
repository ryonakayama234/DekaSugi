"""Synthetic-only independent audit tests. Does not score DEV or FINAL."""
from __future__ import annotations
from copy import deepcopy
from unittest import TestCase

from scripts.audit_exp0003a_dev_evidence import ARMS, FAMILIES, audit, digest


def synthetic_evidence():
    # 64 deliberately made-up tasks; never call EXP-0003A dataset generator.
    records, rows = [], []
    for i in range(64):
        shape = {"schema_version": "0.1", "domain": "string_to_string",
                 "limits": {"max_ast_nodes": 4, "max_candidates": 100},
                 "examples": [{"input": "x" + str(i), "output": "x" + str(i)},
                              {"input": "y" + str(i), "output": "y" + str(i)}]}
        tid = "t-" + digest(shape)
        private_audit = {"input": "synthetic", "output": "synthetic"}
        ref = "audit-sha256:" + digest({"task_id": tid, "private_example": private_audit})
        records.append({
            "source_record_id": f"dev-f{i // 8:02d}-i{i % 8:03d}",
            "family": FAMILIES[i // 8], "seeds": [i * 10 + j for j in range(3)],
            "task_id": tid, "public_task_sha256": tid[2:],
            "public_task": dict(shape, task_id=tid),
            "audit": private_audit, "audit_evidence_ref": ref,
        })
        arms = {}
        for a in ARMS:
            inv = 2 if a == "B2" else 1
            arms[a] = {
                "audit_ref": ref, "policy_snapshot_sha256": None if a == "B0" else a,
                "decision": "OFF", "audited_correct": False,
                "false_solved": False, "tested_candidates": 3,
                "primitive_invocations": inv, "search": {"tested_candidates": 3,
                "task_id": tid, "status": "not_found", "solved": False,
                "program": None}, "selected_ast": None,
                "meter": {"primitive_invocations": inv,
                          "by_op": {"trim": inv}},
                "policy_inference_cpu_ms": 0.0, "policy_inference_wall_ms": 0.0,
                "search_cpu_ms": 0.0, "search_wall_ms": 0.0,
                "audit_cpu_ms": 0.0, "audit_wall_ms": 0.0,
            }
        rows.append({"task_id": tid, "arms": arms})
    freeze = {"freeze_payload_sha256": "test-seal",
              "policy": {"snapshot_sha256": {a: a for a in ARMS[1:]}},
              "split_data": {"split_sha256": {"dev": digest(records)}}}
    pub = {"phase": "DEV_ENGINEERING", "source_commit": "a" * 40,
           "freeze_payload_sha256": "test-seal", "final_evaluated": False,
           "registry_promoted": False, "dev_dataset_sha256": digest(records),
           "snapshot_sha256": {a: a for a in ARMS[1:]},
           "trial_rows": rows, "summary": {}, "phase_cost_ms": {
               "asset_load_cost_ms": {
                   "freeze_verify_cpu": 1.0, "second_train_dream_replay_cpu": 2.0,
                   "snapshot_validation_cpu": 1.0, "asset_load_total_cpu": 4.0,
                   "freeze_verify_wall": 1.0, "second_train_dream_replay_wall": 2.0,
                   "snapshot_validation_wall": 1.0, "asset_load_total_wall": 4.0,
               }}}
    prv = {"phase": "DEV_ENGINEERING", "source_commit": "a" * 40,
           "dev_dataset_sha256": digest(records), "source_records": records,
           "public_trial_rows_sha256": digest(rows)}
    return pub, prv, freeze


class IndependentAuditTests(TestCase):
    def test_raw_digest_fails_closed(self):
        pub, prv, freeze = synthetic_evidence()
        prv["public_trial_rows_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Public trial evidence digest"):
            audit(pub, prv, freeze, 'a' * 40)

    def test_private_split_fails_closed(self):
        pub, prv, freeze = synthetic_evidence()
        prv["source_records"][0]["seeds"][0] = -1
        with self.assertRaisesRegex(ValueError, "Private DEV raw split"):
            audit(pub, prv, freeze, 'a' * 40)

    def test_forbid_b0_policy_on(self):
        pub, prv, freeze = synthetic_evidence()
        pub["trial_rows"][0]["arms"]["B0"]["decision"] = "ON"
        prv["public_trial_rows_sha256"] = digest(pub["trial_rows"])
        with self.assertRaisesRegex(ValueError, "Illegal arm decision"):
            audit(pub, prv, freeze, 'a' * 40)

    def test_forbid_noncanonical_meter(self):
        pub, prv, freeze = synthetic_evidence()
        pub["trial_rows"][0]["arms"]["B1"]["meter"]["primitive_invocations"] = 999
        prv["public_trial_rows_sha256"] = digest(pub["trial_rows"])
        with self.assertRaisesRegex(ValueError, "Canonical meter/search"):
            audit(pub, prv, freeze, 'a' * 40)

    def test_meter_per_op_tamper_rejected(self):
        pub, prv, freeze = synthetic_evidence()
        pub["trial_rows"][0]["arms"]["B2"]["meter"]["by_op"]["trim"] = 3
        prv["public_trial_rows_sha256"] = digest(pub["trial_rows"])
        with self.assertRaisesRegex(ValueError, "Meter by_op breakdown"):
            audit(pub, prv, freeze, "a" * 40)

    def test_search_audit_contradiction_rejected(self):
        pub, prv, freeze = synthetic_evidence()
        trial = pub["trial_rows"][0]["arms"]["B2"]
        trial["audited_correct"] = True
        prv["public_trial_rows_sha256"] = digest(pub["trial_rows"])
        with self.assertRaisesRegex(ValueError, "Audit/search verdict"):
            audit(pub, prv, freeze, "a" * 40)

    def test_mismatched_runner_sha_rejected(self):
        pub, prv, freeze = synthetic_evidence()
        with self.assertRaisesRegex(ValueError, "Source SHA mismatch"):
            audit(pub, prv, freeze, "b" * 40)

    def test_synthetic_success_independent_recount(self):
        pub, prv, freeze = synthetic_evidence()
        totals = {}
        for a in ARMS:
            totals[a] = {
                "audited_correct": 0, "false_solved": 0,
                "tested_candidates": 192,
                "primitive_invocations": 128 if a == "B2" else 64,
                "selected_on": 0,
                "policy_inference_cpu_ms": 0.0, "policy_inference_wall_ms": 0.0,
                "search_cpu_ms": 0.0, "search_wall_ms": 0.0,
                "audit_cpu_ms": 0.0, "audit_wall_ms": 0.0,
            }
        pub["summary"] = {
            "task_count": 64, "arm_totals": totals,
            "ood_false_on_counts": {a: 0 for a in ARMS},
            "family_summary": {
                f: {a: {"audited_correct": 0,
                        "primitive_invocations": 16 if a == "B2" else 8}
                    for a in ARMS} for f in FAMILIES
            },
            "paired_B2_minus_B3": {
                "primitive_invocations": 64,
                "tested_candidates": 0,
                "audited_correct_B3_minus_B2": 0,
                "primitive_regressions": 0,
                "primitive_improvements": 64,
                "family_cluster_bootstrap_95pct_total_calls_delta": [64, 64],
                "bootstrap_seed": 260303, "bootstrap_rounds": 1000,
            },
        }
        result = audit(pub, prv, freeze, "a" * 40)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["arm_trial_count"], 256)
        self.assertTrue(result["audit_cpu_wall_comparison"]
                        ["integer_and_hash_fields_compared_exactly"])

        # Last-bit binary64 scorer/auditor differences must be tolerated,
        # but only for CPU/wall totals, never integer counts or SHA.
        pub["summary"]["arm_totals"]["B1"]["policy_inference_cpu_ms"] = 5e-11
        tolerated = audit(pub, prv, freeze, "a" * 40)
        self.assertAlmostEqual(
            tolerated["audit_cpu_wall_comparison"]
            ["largest_observed_abs_difference_ms"], 5e-11)

        # A substantive CPU drift must still fail closed.
        pub["summary"]["arm_totals"]["B1"]["policy_inference_cpu_ms"] = 0.001
        with self.assertRaisesRegex(ValueError, "Arm CPU/wall total exceeds"):
            audit(pub, prv, freeze, "a" * 40)

        # Numeric tolerance is never applied to primitive-call counts.
        pub["summary"]["arm_totals"]["B1"]["policy_inference_cpu_ms"] = 0.0
        pub["summary"]["arm_totals"]["B2"]["primitive_invocations"] += 1
        with self.assertRaisesRegex(ValueError, "Arm integer/verdict totals"):
            audit(pub, prv, freeze, "a" * 40)

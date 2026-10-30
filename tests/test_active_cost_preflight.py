"""ACTIVE-001 P2: allowlisted synthetic cost instrumentation only."""
import json
import sys
import unittest

from packages.active_cost import (
    extrapolate_cpu_ns, measure_invented_fixture, workload_counts,
)


class P2SyntheticCostTests(unittest.TestCase):
    def test_nominal_counts_are_exact_and_not_scores(self):
        old = workload_counts(4096, include_b1plus=False)
        future = workload_counts(4096, include_b1plus=True)
        self.assertEqual((old["arm_episodes"], old["maximum_query_calls"],
                          old["model_predictions"]),
                         (28672, 49152, 1835008))
        self.assertEqual((future["arm_episodes"], future["maximum_query_calls"],
                          future["model_predictions"]),
                         (49152, 90112, 3145728))
        for n in (512, 1024, 4096):
            self.assertEqual(workload_counts(n, include_b1plus=True)["arm_episodes"], 12*n)

    def test_reject_bad_inputs(self):
        for bad in (True, 0, 4095, 8192, 512.0):
            with self.subTest(n=bad), self.assertRaises(ValueError):
                workload_counts(bad, include_b1plus=False)
        with self.assertRaises(ValueError):
            workload_counts(512, include_b1plus=1)
        for bad in (True, 0, 4, 1.0):
            with self.subTest(repeats=bad), self.assertRaises(ValueError):
                measure_invented_fixture(repeats=bad)

    def test_actual_invented_cpu_receipt(self):
        result = measure_invented_fixture(repeats=2)
        self.assertEqual(result["schema"], "active001-cpu-preflight/invented-only/1")
        self.assertEqual(result["scientific_scored_tasks"], 0)
        self.assertEqual(result["structural_context_count"], 91367)
        self.assertEqual(result["structural_f4"], "NOT_COMPUTED")
        self.assertEqual(len(result["projections"]), 6)
        phases = result["phase_ns"]
        self.assertEqual(phases["gate_f_census"]["repeats"], 1)
        for phase in phases.values():
            self.assertGreaterEqual(phase["median_cpu_ns"], 0)
            self.assertGreaterEqual(phase["median_wall_ns"], 0)
            self.assertEqual(len(phase["cpu_ns"]), phase["repeats"])
        self.assertGreaterEqual(result["process_maxrss_kib_after"],
                                result["process_maxrss_kib_before"])
        forbidden = ("target_id", "audit_labels", "heldout_accuracy",
                     "oracle_answer", "preregistered_score")
        for key in forbidden:
            self.assertNotIn(key, result)
        # The CI log is the REAL per-run source of measurements. Do not
        # freeze machine-dependent numbers into source or assert thresholds.
        print("ACTIVE001_P2_CPU_RECEIPT=" + json.dumps(result, sort_keys=True),
              file=sys.stderr, flush=True)


if __name__ == "__main__":
    unittest.main()

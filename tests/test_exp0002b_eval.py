"""EXP-0002B freeze-gated evaluation tests; NEVER invoke DEV or FINAL outcomes."""
import json
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from packages.kernel import generate_partition, train, PolicySnapshot, _candidate
from packages.kernel.evaluation import (
    FROZEN_RECORD, _bootstrap, _oracle_choice, _score, _trial,
    evaluate_record, load_and_check_freeze, run_evaluation, summarize,
)
from packages.library import DEFAULT_PRIMITIVES, Registry
from packages.learning import registry_with_skill


class FreezeGatedEvaluationTests(unittest.TestCase):
    def test_snapshot_matches_freeze_before_any_dev_final_outcome(self):
        fixed, manifest, evidence, snapshot = load_and_check_freeze()
        self.assertEqual(snapshot.to_dict()["policy_sha256"], fixed["policy_sha256"])
        self.assertEqual(manifest["dataset_sha256"], fixed["dataset_sha256"])
        self.assertEqual(manifest["generator_source_sha256"],
                         fixed["generator_source_sha256"])
        self.assertEqual(evidence["training_task_count"], 144)
        self.assertEqual(len(fixed["frozen_execution_source_git_blob_sha1"]), 9)
        self.assertEqual(fixed["partitions"], {"train": 144, "dev": 48, "final": 112})

    def test_tamper_fails_closed_before_dev_evaluation(self):
        obj = json.loads(FROZEN_RECORD.read_text(encoding="utf-8"))
        obj["policy_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-freeze.json"
            path.write_text(json.dumps(obj), encoding="utf-8")
            with patch("packages.kernel.evaluation.evaluate_record",
                       side_effect=AssertionError("DEV search was invoked")):
                with self.assertRaisesRegex(ValueError, "Freeze mismatch: policy"):
                    run_evaluation("dev", freeze_path=path)
        with self.assertRaises(ValueError):
            run_evaluation("invalid")

    def test_runtime_source_mismatch_fails_closed_before_any_outcomes(self):
        original = json.loads(FROZEN_RECORD.read_text(encoding="utf-8"))
        forged = json.loads(json.dumps(original))
        forged["frozen_execution_source_git_blob_sha1"]["packages/runtime/__init__.py"] = "0"*40
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-sources.json"
            path.write_text(json.dumps(forged), encoding="utf-8")
            with patch("packages.kernel.evaluation.evaluate_record",
                       side_effect=AssertionError("DEV search executed")):
                with self.assertRaisesRegex(ValueError, "execution source manifest"):
                    run_evaluation("dev", freeze_path=path)
        from packages.kernel.evaluation import _git_blob_hash
        original_hash = _git_blob_hash(Path(__file__).resolve().parents[1] /
                                      "packages/runtime/__init__.py")
        with patch("packages.kernel.evaluation._git_blob_hash", return_value="0"*40):
            with self.assertRaisesRegex(ValueError, "execution source"):
                load_and_check_freeze()
        self.assertEqual(len(original_hash), 40)

    def test_train_only_fixture_uses_independent_three_arms(self):
        evidence = train()
        policy = PolicySnapshot.from_dict(evidence["snapshot"])
        skill = _candidate()
        base = Registry(DEFAULT_PRIMITIVES)
        enabled = registry_with_skill(skill, base)
        item = next(x for x in generate_partition("train") if x.family == "normalize")
        with patch("packages.kernel.evaluation.choose", wraps=__import__(
                "packages.kernel.evaluation", fromlist=["choose"]).choose) as chooser:
            report = evaluate_record(item, policy, skill, base, enabled)
        self.assertEqual(chooser.call_count, 1)
        self.assertEqual(chooser.call_args.args[0], item.task)
        self.assertEqual(report["partition"], "train")
        self.assertEqual(report["off"]["audit_correct"], True)
        self.assertEqual(report["on"]["audit_correct"], True)
        self.assertEqual(report["learned"]["audit_correct"], True)
        selected = report["on"] if report["policy_decision"]["action"] == "ON" else report["off"]
        self.assertEqual(report["learned"]["search"]["trace_sha256"],
                         selected["search"]["trace_sha256"])
        self.assertEqual(report["learned"]["primitive_invocations"],
                         selected["primitive_invocations"])
        self.assertEqual(report["oracle_source_action"], "ON")
        self.assertNotIn("audit", report["policy_decision"])
        self.assertNotIn("family", report["policy_decision"])
        for arm in ("off", "on", "learned"):
            self.assertGreaterEqual(report[arm]["trial_cpu_ms_including_audit"], 0)
            self.assertGreaterEqual(report[arm]["trial_wall_ms_including_audit"], 0)
        self.assertGreaterEqual(report["policy_inference_cpu_ms"], 0)

    def test_oracle_correctness_priority_and_tie_off(self):
        a = {"audit_correct": True, "primitive_invocations": 9,
             "search": {"tested_candidates": 6}}
        b = {"audit_correct": False, "primitive_invocations": 2,
             "search": {"tested_candidates": 2}}
        self.assertEqual(_oracle_choice(a, b), "OFF")
        self.assertEqual(_oracle_choice(b, a), "ON")
        self.assertEqual(_oracle_choice(a, dict(a)), "OFF")

    def test_summary_statistics_on_synthetic_train_only_fixture(self):
        policy = PolicySnapshot.from_dict(train()["snapshot"])
        skill = _candidate()
        base = Registry(DEFAULT_PRIMITIVES)
        enabled = registry_with_skill(skill, base)
        item = next(x for x in generate_partition("train") if x.family == "identity")
        row = evaluate_record(item, policy, skill, base, enabled)
        costs = train()
        out = summarize([row], costs, "dev")
        self.assertEqual(out["comparison"]["off"]["tasks"], 1)
        self.assertEqual(out["policy_adoption"], "not_applicable")
        self.assertEqual(out["numeric_acceptance_gates"], {})
        self.assertEqual(out["bootstrap"]["resamples"], 1000)
        self.assertIn("trial_cpu_ms_including_audit", out["comparison"]["off"])
        self.assertIn("inference_cpu_ms", out["policy_decisions"])
        # Do not evaluate any actual FINAL instance in this test suite.


if __name__ == "__main__":
    unittest.main()

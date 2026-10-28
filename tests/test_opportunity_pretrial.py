"""OPPORTUNITY-001 pretrial decision sealing; no new paired search."""
from __future__ import annotations

from dataclasses import dataclass
import ast
from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import json
from unittest import TestCase, mock

from packages.evaluation.opportunity_pilot import generate_train_pilot
from scripts import prepare_opportunity_decisions as pretrial
from scripts import verify_opportunity_legacy_sources as legacy_gate


@dataclass(frozen=True)
class DummyDecision:
    action: str
    reason: str = "fixture_only"


class PretrialGateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = generate_train_pilot()

    def fake(self, cases=None, chooser=None):
        policy = {k: object() for k in pretrial.ARMS}
        calls = []
        def choose(task, snapshot):
            self.assertEqual(len(task.examples), 2)
            self.assertFalse(hasattr(task, "private_audit"))
            calls.append(task.task_id)
            return DummyDecision("OFF")
        manifest = pretrial._build_decision_manifest(
            cases if cases is not None else self.cases,
            policy, {k: "a"*64 for k in pretrial.ARMS},
            "b"*64, chooser if chooser is not None else choose)
        return manifest, calls

    def test_all_choices_before_any_outcome_contract(self):
        result,calls = self.fake()
        self.assertEqual(len(calls), 64*3)
        self.assertEqual(len(result["payload"]["decisions"]), 64)
        self.assertEqual(len({r["task_id"] for r in result["payload"]["decisions"]}), 64)
        self.assertEqual(result["payload"]["paired_trials_executed"], 0)
        self.assertIs(result["payload"]["dev_or_final_evaluated"], False)
        text = json.dumps(result["payload"])
        for excluded in ("private_audit", "source_record_id", "family", "seeds",
                         "search", "selected_ast", "hidden"):
            self.assertNotIn(excluded, text)

    def test_inference_cost_accounted_separately_not_in_sealed_digest(self):
        a,_=self.fake()
        b,_=self.fake()
        self.assertEqual(a["payload_sha256"], b["payload_sha256"])
        self.assertEqual(len(a["payload_sha256"]), 64)
        self.assertIn("inference_cost_ms", a)
        self.assertNotIn("inference_cost_ms", a["payload"])
        self.assertTrue(all(x >= 0 for x in a["inference_cost_ms"]["policy_cpu"].values()))

    def test_duplicate_public_id_fail_closed(self):
        duplicates = list(self.cases)
        duplicates[2] = duplicates[1]
        with self.assertRaisesRegex(ValueError, "64 unique"):
            self.fake(duplicates)

    def test_wrong_budget_and_policy_shape_fail_closed(self):
        from dataclasses import replace
        case = self.cases[0]
        malformed = list(self.cases)
        malformed[0] = replace(case, task=replace(case.task,
                                                 limits=replace(case.task.limits, max_candidates=200)))
        with self.assertRaisesRegex(ValueError, "budget"):
            self.fake(malformed)
        with self.assertRaisesRegex(ValueError, "snapshots"):
            pretrial._build_decision_manifest(self.cases, {"B1":object()},
                                             {"B1":"a"*64}, "b"*64,
                                             lambda task,policy: DummyDecision("OFF"))

    def test_bad_action_and_reason_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Invalid pretrial"):
            self.fake(chooser=lambda t,s: DummyDecision("SKIP"))
        with self.assertRaisesRegex(ValueError, "reason"):
            self.fake(chooser=lambda t,s: DummyDecision("ON", ""))

    def test_reducer_does_not_import_scorer_or_old_dev_generator(self):
        text=inspect.getsource(pretrial)
        for word in ("bounded_synthesize(", "_audited_trial(", "paired_trial(",
                     "evaluate_case(", "generate_dev(", "generate_final(",
                     "run_dev(", "run_final("):
            self.assertNotIn(word, text)

    def test_historic_source_verifier_is_stdlib_only_and_complete(self):
        info = legacy_gate.verify_legacy_source_bytes()
        self.assertEqual(info["verified_source_count"], 14)
        self.assertFalse(info["dev_or_final_generated"])
        src = inspect.getsource(legacy_gate)
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(all(not alias.name.startswith("packages")
                                    for alias in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertFalse((node.module or "").startswith("packages"))
            if isinstance(node, ast.Call):
                name = (node.func.id if isinstance(node.func, ast.Name)
                        else node.func.attr if isinstance(node.func, ast.Attribute)
                        else "")
                self.assertNotIn(name, {"generate_partition", "verify_frozen",
                                        "dataset_hashes", "preflight_record"})

    def test_historic_source_gate_rejects_tampering_before_import(self):
        with TemporaryDirectory() as dirname:
            root = Path(dirname)
            files = set(legacy_gate.SOURCE_FILES) | {legacy_gate.FROZEN_FILE}
            for path in sorted(files):
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((legacy_gate.ROOT / path).read_bytes())
            legacy_gate.verify_legacy_source_bytes(root)
            with (root/"packages/learning/__init__.py").open("ab") as stream:
                stream.write(b"\\n# unreviewed import-time change\\n")
            with self.assertRaisesRegex(ValueError, "source byte drift"):
                legacy_gate.verify_legacy_source_bytes(root)

    def test_legacy_partition_generators_cannot_be_reentered(self):
        # Existing legacy verify_frozen generates DEV/FINAL for hash preflight;
        # this new chooser MUST NOT invoke that path.
        from packages.exp0003a import freeze
        with mock.patch.object(freeze, "generate_partition",
                               side_effect=AssertionError("FORBIDDEN: old holdout generation")):
            with mock.patch.object(freeze, "verify_frozen",
                                   side_effect=AssertionError("FORBIDDEN: legacy freeze preflight")):
                record = pretrial.build_pretrial_decisions()
        self.assertEqual(record["payload"]["paired_trials_executed"], 0)
        self.assertEqual(len(record["payload"]["decisions"]), 64)

    def test_real_readonly_pretrial_choices_can_be_reconstructed(self):
        result = pretrial.build_pretrial_decisions()
        self.assertEqual(len(result["payload"]["decisions"]), 64)
        self.assertEqual(result["payload"]["paired_trials_executed"], 0)
        self.assertEqual(result["payload"]["source_manifest_sha256"],
                         "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85")
        self.assertEqual(len(result["payload_sha256"]), 64)
        self.assertIn(result["payload"]["decisions"][0]["choices"]["B1"]["action"], ("ON", "OFF"))


if __name__ == "__main__":
    import unittest
    unittest.main()

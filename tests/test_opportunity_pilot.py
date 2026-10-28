"""OPPORTUNITY-001-PILOT-V1 source/hash-only tests, never score any tasks."""
from __future__ import annotations

from dataclasses import replace
import inspect
import json
import unittest
from unittest import mock

from packages.exp0003a import generate_train, opaque_id, public_shape
from packages.evaluation.opportunity_pilot import (
    ALPHABET, COUNT_PER_FAMILY, FAMILIES, MASTER, TOTAL,
    canonical_public_digest, generate_train_pilot, public_manifest,
    public_preflight, seed_for,
)


class OpportunityPilotGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = generate_train_pilot()

    def test_complete_fixed_population(self):
        self.assertEqual(len(self.cases), TOTAL)
        self.assertEqual(TOTAL, 64)
        self.assertEqual(COUNT_PER_FAMILY, 8)
        self.assertEqual(len(FAMILIES), 8)
        self.assertEqual(len({c.task.task_id for c in self.cases}), 64)
        self.assertEqual(len({c.source_record_id for c in self.cases}), 64)
        self.assertEqual(len({seed for c in self.cases for seed in c.seeds}), 192)

    def test_frozen_seed_formula_and_boundaries(self):
        self.assertEqual(MASTER, 910_000_000)
        for f in range(8):
            for i in range(8):
                case = self.cases[f * 8 + i]
                self.assertEqual(case.family, FAMILIES[f])
                self.assertEqual(case.source_record_id, f"op-pilot-f{f:02d}-i{i:03d}")
                self.assertEqual(case.seeds, tuple(
                    910000000 + f * 100000 + i * 10 + j for j in range(3)))
        for bad in [(-1, 0, 0), (8, 0, 0), (0, 8, 0),
                    (0, 0, 3), (False, 0, 0)]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                seed_for(*bad)

    def test_public_id_and_budget_contract(self):
        for case in self.cases:
            self.assertEqual(case.task.task_id, opaque_id(case.task.examples))
            self.assertEqual(case.task.limits.max_ast_nodes, 4)
            self.assertEqual(case.task.limits.max_candidates, 100)
            self.assertEqual(len(case.task.examples), 2)
            self.assertEqual(case.task.domain, "string_to_string")
            self.assertEqual(case.task.schema_version, "0.1")
            self.assertEqual(len(case.seeds), 3)

    def test_audit_examples_distinct_and_not_in_public_manifest(self):
        for case in self.cases:
            e1, e2 = case.task.examples
            self.assertNotEqual((e1.input, e1.output),
                                (e2.input, e2.output))
            self.assertNotIn((case.private_audit.input, case.private_audit.output),
                             ((e1.input, e1.output), (e2.input, e2.output)))
        raw = json.dumps(public_manifest(self.cases), ensure_ascii=False)
        self.assertNotIn("private_audit", raw)
        self.assertNotIn("family", raw)
        self.assertNotIn("seeds", raw)
        self.assertNotIn("source_record_id", raw)

    def test_semantic_transform_families(self):
        for case in self.cases:
            for ex in case.task.examples + (case.private_audit,):
                f = case.family
                if f == "identity":
                    expected = ex.input
                elif f == "trim":
                    expected = ex.input.strip()
                elif f == "lower":
                    expected = ex.input.lower()
                elif f == "upper":
                    expected = ex.input.upper()
                elif f == "normalize_lower":
                    expected = ex.input.strip().lower()
                elif f == "normalize_upper":
                    expected = ex.input.strip().upper()
                elif f == "reverse_ood":
                    expected = ex.input[::-1]
                    self.assertNotEqual(ex.input, expected)
                elif f == "replace_first_ood":
                    expected = "Z" + ex.input[1:]
                    self.assertNotEqual(ex.input, expected)
                else:
                    self.fail("Unexpected family")
                self.assertEqual(ex.output, expected)

    def test_alphabet_fixed_and_replacement_symbol_excluded(self):
        self.assertEqual(ALPHABET, "uvwxYQ03")
        self.assertNotIn("Z", ALPHABET)
        self.assertEqual(len(set(ALPHABET)), len(ALPHABET))

    def test_old_train_ids_are_distinct_without_old_dev_or_final(self):
        old_train = generate_train()  # public legacy TRAIN only
        old_ids = {c.task.task_id for c in old_train}
        self.assertFalse(old_ids & {c.task.task_id for c in self.cases})

    def test_public_manifest_canonical_and_repeatable(self):
        rows = public_manifest(self.cases)
        self.assertEqual(len(rows), 64)
        for c, row in zip(self.cases, rows):
            self.assertEqual(row["task_id"], c.task.task_id)
            self.assertEqual(row["examples"], public_shape(c.task.examples)["examples"])
        self.assertEqual(canonical_public_digest(self.cases),
                         canonical_public_digest(generate_train_pilot()))
        self.assertEqual(len(canonical_public_digest(self.cases)), 64)

    def test_public_preflight_no_scoring_or_private_payload(self):
        preflight = public_preflight()
        self.assertEqual(preflight["task_count"], 64)
        self.assertEqual(preflight["family_strata"], 8)
        self.assertEqual(preflight["paired_trials_executed"], 0)
        self.assertFalse(preflight["dev_or_final_evaluated"])
        self.assertFalse(preflight["third_audit_examples_disclosed"])
        self.assertEqual(preflight["public_manifest_sha256"],
                         canonical_public_digest(self.cases))
        self.assertEqual(preflight["status"], "public_manifest_generated_no_scoring")

    def test_manifest_rejects_duplicate_task_id_and_count(self):
        with self.assertRaisesRegex(ValueError, "64"):
            public_manifest(self.cases[:63])
        bad = list(self.cases)
        bad[1] = bad[0]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            public_manifest(bad)
        bad = list(self.cases)
        bad[1] = replace(bad[1], task=replace(
            bad[1].task, task_id="t-" + "f"*64))
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            public_manifest(bad)

    def test_no_scoring_or_old_holdout_import_path(self):
        from packages.evaluation import opportunity_pilot as module
        text = inspect.getsource(module)
        for unsafe in ("generate_partition(", "run_dev(",
                       "bounded_synthesize(", "run_train_dream(",
                       "def evaluate_case(", "from packages.exp0003a_dev"):
            self.assertNotIn(unsafe, text)


    def test_injected_duplicate_source_id_aborts(self):
        from packages.evaluation import opportunity_pilot as module
        with unittest.mock.patch.object(module, "source_id_for",
                                        return_value="op-pilot-f00-i000"):
            with self.assertRaisesRegex(ValueError, "Duplicate pilot task/source ID"):
                module.generate_train_pilot()

    def test_injected_duplicate_seed_aborts(self):
        from packages.evaluation import opportunity_pilot as module
        original_seed_for = module.seed_for
        def repeated_seed(f, i, j):
            return original_seed_for(f, 0, j)
        with unittest.mock.patch.object(module, "seed_for", side_effect=repeated_seed):
            with self.assertRaisesRegex(ValueError, "Duplicate PILOT-V1 seed"):
                module.generate_train_pilot()

    def test_injected_duplicate_public_task_id_aborts(self):
        from packages.evaluation import opportunity_pilot as module
        with unittest.mock.patch.object(module, "opaque_id", return_value="t-" + "a" * 64):
            with self.assertRaisesRegex(ValueError, "Duplicate pilot task/source ID"):
                module.generate_train_pilot()

    def test_injected_duplicate_audit_and_public_example_abort(self):
        from packages.evaluation import opportunity_pilot as module
        original_example = module._example
        for repeated_index in (1, 2):
            def repeated_example(family, i, j, seed):
                if j == repeated_index:
                    idx = module.FAMILIES.index(family)
                    return original_example(family, i, 0, module.seed_for(idx, i, 0))
                return original_example(family, i, j, seed)
            with self.subTest(repeated_index=repeated_index):
                with unittest.mock.patch.object(module, "_example",
                                                side_effect=repeated_example):
                    with self.assertRaisesRegex(ValueError, "Non-distinct public/audit"):
                        module.generate_train_pilot()

    def test_source_id_indices_reject_boolean_and_out_of_range(self):
        from packages.evaluation import opportunity_pilot as module
        self.assertEqual(module.source_id_for(0, 0), "op-pilot-f00-i000")
        for bad in [(False, 0), (-1, 0), (8, 0), (0, 8)]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    module.source_id_for(*bad)


if __name__ == "__main__":
    unittest.main()

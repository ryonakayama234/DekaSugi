"""Gate F design-only tests: never score targets, Oracle or withheld audit labels."""
import unittest
from itertools import combinations
from collections import defaultdict

from packages.active_feasibility import census_fixture, _count_informative_queries
from packages.inquiry_world import build_catalog, input_split


class GateFStructuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = census_fixture()

    def test_exact_population_accounting(self):
        r = self.report
        self.assertEqual(r.role, "invented-public-structure-only/no-scoring/no-source-freeze")
        self.assertEqual(r.potential_task_count, 878 * 378)
        self.assertEqual(r.public_context_count, sum((r.f0_contexts, r.f1_contexts, r.f2_contexts, r.f3_contexts)))
        self.assertEqual(r.potential_task_count, sum((r.f0_task_weight, r.f1_task_weight, r.f2_task_weight, r.f3_task_weight)))
        self.assertEqual((r.f0_contexts, r.f0_task_weight), (0, 0))
        self.assertEqual(r.f1_contexts, r.f1_task_weight)
        self.assertLessEqual(r.positive_query_task_weight_sum, r.query_opportunity_denominator)
        self.assertEqual(r.f4_status.split(";")[0], "not_computed")

    def test_stable_invented_census_regression(self):
        """Exact synthetic structure only: NO target truth or score is observed."""
        r = self.report
        self.assertEqual((r.f1_contexts, r.f2_contexts, r.f3_contexts),
                         (37643, 5866, 47858))
        self.assertEqual((r.f1_task_weight, r.f2_task_weight, r.f3_task_weight),
                         (37643, 12130, 282111))
        self.assertEqual(r.public_context_count, 91367)
        self.assertEqual(r.positive_query_task_weight_sum, 11459844)
        self.assertEqual(r.max_version_space_size, 276)
        self.assertEqual(r.context_sha256,
                         "9c135ace8f815e4b3ac2465c9918833c3becd43781faeedc36314c28c9203f12")
        self.assertEqual(r.split_digest,
                         "cbabb2d8f22e2cc73e69c82ae88733bfcfec97e4a6f749c66bf68e3ee2ca4c49")

    def test_repeat_determinism_and_fixture_guards(self):
        self.assertEqual(census_fixture(), self.report)
        for seed in (True, 0, -1, 20261031, None, 20261030.0):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                census_fixture(split_seed=seed)

    def test_reference_bruteforce_small_public_context(self):
        """Check no Gini-import or target oracle needed to find informative q."""
        catalog = build_catalog()
        split = input_split(20261030)
        query_vectors = tuple(tuple(c.output_signature[q] for q in split.query_ids)
                              for c in catalog.classes)
        p1, p2 = next(iter(combinations(split.public_ids, 2)))
        partitions = defaultdict(list)
        for i, cls in enumerate(catalog.classes):
            partitions[(cls.output_signature[p1], cls.output_signature[p2])].append(i)
        seen_f3 = False
        for indices in partitions.values():
            actual = _count_informative_queries(indices, query_vectors, 64) if len(indices)>1 else 0
            expected = sum(len({catalog.classes[i].output_signature[q] for i in indices})>1
                           for q in split.query_ids)
            self.assertEqual(actual, expected)
            seen_f3 |= actual > 0
        self.assertTrue(seen_f3)

    def test_absence_of_evaluator_contract(self):
        keys = set(self.report.to_dict())
        self.assertTrue({"world_digest", "split_digest", "f3_task_weight", "context_sha256"} <= keys)
        for forbidden in ("target_id", "oracle_answer", "audit_labels", "heldout_accuracy", "score"):
            self.assertNotIn(forbidden, keys)


if __name__ == "__main__":
    unittest.main()

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

    def test_full_population_independent_signature_proof(self):
        """Second exact derivation, without the Gate-F query-count helper."""
        cat = build_catalog()
        split = input_split(20261030)
        tally = {"F1": [0, 0], "F2": [0, 0], "F3": [0, 0]}
        qids = split.query_ids
        for p1, p2 in combinations(split.public_ids, 2):
            groups = defaultdict(list)
            for cls in cat.classes:
                groups[(cls.output_signature[p1], cls.output_signature[p2])].append(cls)
            for block in groups.values():
                if len(block) == 1:
                    label = "F1"
                else:
                    first = block[0].output_signature
                    label = "F2" if all(all(cls.output_signature[q] == first[q] for q in qids)
                                         for cls in block[1:]) else "F3"
                tally[label][0] += 1
                tally[label][1] += len(block)
        self.assertEqual(tally, {"F1": [37643, 37643],
                                 "F2": [5866, 12130],
                                 "F3": [47858, 282111]})

    def test_absence_of_evaluator_contract(self):
        keys = set(self.report.to_dict())
        self.assertTrue({"world_digest", "split_digest", "f3_task_weight", "context_sha256"} <= keys)
        for forbidden in ("target_id", "oracle_answer", "audit_labels", "heldout_accuracy", "score"):
            self.assertNotIn(forbidden, keys)



class GateF4OperationalTests(unittest.TestCase):
    """Independent tiny invented worlds only; no real Gate-F full census."""

    def test_strict_two_question_adaptation(self):
        from packages.active_feasibility.f4 import probe_f4
        # First q splits 0/1 into two class pairs; q2 distinguishes the
        # left group while q3 distinguishes the right group.
        rows = (("0", "0", "0"), ("0", "1", "0"),
                ("1", "0", "0"), ("1", "0", "1"))
        p = probe_f4(rows)
        self.assertEqual((p.status, p.fixed_identified, p.adaptive_identified,
                          p.f4), ("computed", 2, 4, True))
        self.assertEqual(p.best_fixed_pair, (0, 1))
        self.assertEqual(p.best_adaptive_first, 0)
        self.assertEqual(p.adaptive_second_by_answer, (("0", 1), ("1", 2)))

    def test_exhaustive_independent_reference(self):
        """Brute-force fixed pairs and *all* response-conditioned second maps."""
        from itertools import product
        from collections import Counter
        from packages.active_feasibility.f4 import probe_f4
        worlds = (
            (("0", "0", "0"), ("0", "1", "0"),
             ("1", "0", "0"), ("1", "0", "1")),
            (("0", "0"), ("1", "0")),
            (("z", "z", "z"), ("z", "z", "z"), ("z", "z", "z")),
            (("z", "z"),),
            (("0", "0", "1"), ("1", "0", "0"), ("1", "1", "0")),
        )
        for rows in worlds:
            with self.subTest(rows=rows):
                nq = len(rows[0])
                N = 0
                for q1 in range(nq):
                    for q2 in range(q1 + 1, nq):
                        sigs = tuple((r[q1], r[q2]) for r in rows)
                        counts = Counter(sigs)
                        N = max(N, sum(counts[x] == 1 for x in sigs))
                A = 0
                for q1 in range(nq):
                    answers = tuple(sorted(set(r[q1] for r in rows)))
                    q2_choices = tuple(j for j in range(nq) if j != q1)
                    for mapping in product(q2_choices, repeat=len(answers)):
                        signature = {
                            i: (r[q1], r[mapping[answers.index(r[q1])]])
                            for i, r in enumerate(rows)
                        }
                        counts = Counter(signature.values())
                        A = max(A, sum(counts[sig] == 1 for sig in signature.values()))
                report = probe_f4(rows)
                self.assertEqual((report.fixed_identified,
                                  report.adaptive_identified), (N, A))
                self.assertEqual(report.f4, A > N)

    def test_indistinguishable_does_not_become_identified(self):
        from packages.active_feasibility.f4 import probe_f4
        p = probe_f4((("x", "x"), ("x", "x"), ("x", "x")))
        self.assertEqual((p.fixed_identified, p.adaptive_identified), (0, 0))
        self.assertIs(p.f4, False)

    def test_cost_guard_returns_unknown_not_false(self):
        from packages.active_feasibility.f4 import probe_f4
        rows = tuple(("0",)*64 for _ in range(100))
        p = probe_f4(rows)
        self.assertEqual(p.status, "not_computed/resource_budget")
        self.assertIsNone(p.f4)
        self.assertIsNone(p.fixed_identified)
        self.assertIsNone(p.adaptive_identified)
        self.assertGreater(p.work_upper_bound, 50_000)

    def test_invalid_rows_and_exact_cost_type(self):
        from packages.active_feasibility.f4 import probe_f4
        bad_rows = ((), (("0",),), (("0","1"),("0",)),
                    (("0","1"),("0",1)), (("0","1"),["1","0"]))
        for x in bad_rows:
            with self.subTest(rows=repr(x)), self.assertRaises(ValueError):
                probe_f4(x)
        for budget in (True, -1, 5_000_001, 2.0):
            with self.subTest(budget=repr(budget)), self.assertRaises(ValueError):
                probe_f4((("a", "b"),), max_work=budget)


if __name__ == "__main__":
    unittest.main()

"""ACTIVE-001 synthetic invented-fixture-only tests. Never access historical runs."""
import unittest
from dataclasses import replace

from packages.inquiry_world import ALPHABET, INPUTS, OPERATIONS, build_catalog, execute, input_split
from packages.active_learning import (start, partitions, propose_disagreement, propose_random,
                                      make_answer, update, no_informative_query, final_program)


class SyntheticActiveQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.split = input_split(20261030)
        cls.first, cls.second = cls.split.public_ids[:2]
        cls.public = ((cls.first, INPUTS[cls.first]), (cls.second, INPUTS[cls.second]))

    def test_world_is_finite_and_stable(self):
        self.assertEqual(len(INPUTS), 156)
        self.assertEqual(len(set(INPUTS)), 156)
        self.assertEqual(self.catalog.syntax_count, 4681)
        self.assertLess(len(self.catalog.classes), 4681)
        self.assertEqual(len(self.catalog.by_id), len(self.catalog.classes))
        self.assertEqual(len(self.split.public_ids), 28)
        self.assertEqual(len(self.split.query_ids), 64)
        self.assertEqual(len(self.split.audit_ids), 64)
        self.assertEqual(len(set(self.split.public_ids + self.split.query_ids + self.split.audit_ids)), 156)

    def test_primitive_semantics_and_type_guards(self):
        self.assertEqual(execute(("trim", "lower"), " A "), "a")
        self.assertEqual(execute(("reverse",), "ab"), "ba")
        self.assertEqual(execute(("drop_first",), ""), "")
        self.assertEqual(execute(("drop_last",), ""), "")
        self.assertEqual(execute(("replace_first_a_b",), "aa"), "ba")
        self.assertEqual(execute(("append_a",), "Ab"), "Aba")
        for bad in ((("__import__",), "a"), (("lower",) * 5, "a"), ((), "q"), ([], "a")):
            with self.assertRaises(ValueError):
                execute(*bad)
        with self.assertRaises(ValueError):
            input_split(True)

    def test_max_disagreement_is_true_argmax(self):
        s = start("toy", self.public, self.split, self.catalog)
        if s.status == "ambiguous":
            p = propose_disagreement(s, self.catalog)
            self.assertIsNotNone(p)
            self.assertGreater(p.gini_numerator, 0)
            self.assertEqual(p.gini_denominator, len(s.class_ids) ** 2)
            self.assertEqual(p.gini_numerator, max(len(s.class_ids)**2 - sum(n*n for _, n in partitions(s, self.catalog, i)) for i in s.available_query_ids))
            self.assertEqual(p.input_id, min(i for i in s.available_query_ids if len(s.class_ids)**2 - sum(n*n for _, n in partitions(s, self.catalog, i)) == p.gini_numerator))
            self.assertEqual(propose_disagreement(s, self.catalog), p)
            target = self.catalog.by_id[s.class_ids[-1]]
            new = update(s, p, make_answer(p, target.output_signature[p.input_id]), self.catalog)
            self.assertLessEqual(len(new.class_ids), len(s.class_ids))
            self.assertIn(target.class_id, new.class_ids)
            with self.assertRaises(ValueError):
                update(new, p, make_answer(p, "bad"), self.catalog)

    def test_random_control_and_zero_budget(self):
        s = start("toy", self.public, self.split, self.catalog)
        baseline = start("toy", self.public, self.split, self.catalog, max_questions=0)
        self.assertEqual(baseline.class_ids, s.class_ids)
        self.assertIn(baseline.status, ("budget_exhausted", "identified"))
        if s.status == "ambiguous":
            p = propose_random(s, self.catalog, seed=8)
            self.assertIsNotNone(p)
            self.assertEqual(p, propose_random(s, self.catalog, seed=8))
            self.assertIn(p.input_id, self.split.query_ids)
            self.assertEqual(final_program(s, self.catalog), final_program(baseline, self.catalog))

    def test_invalid_and_inconsistent(self):
        with self.assertRaises(ValueError):
            start("bad", ((self.split.query_ids[0], "a"), self.public[1]), self.split, self.catalog)
        with self.assertRaises(ValueError):
            start("bad", (self.public[0], self.public[0]), self.split, self.catalog)
        s = start("toy", self.public, self.split, self.catalog)
        if s.status == "ambiguous":
            p = propose_disagreement(s, self.catalog)
            with self.assertRaises(ValueError):
                update(s, replace(p, gini_numerator=999), make_answer(p, "hello"), self.catalog)
            with self.assertRaises(ValueError):
                update(s, p, replace(make_answer(p, "hello"), receipt_digest="0"), self.catalog)
            self.assertEqual(update(s, p, make_answer(p, "not-in-language"), self.catalog).status, "model_inconsistent")
            with self.assertRaises(ValueError):
                no_informative_query(s, self.catalog)


if __name__ == "__main__":
    unittest.main()

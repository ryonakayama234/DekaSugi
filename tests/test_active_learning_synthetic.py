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
        self.assertEqual(s.status, "ambiguous", "critical fixture must exercise query path")
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
        self.assertEqual(s.status, "ambiguous", "critical fixture must exercise query path")
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
        self.assertEqual(s.status, "ambiguous", "critical fixture must exercise query path")
        p = propose_disagreement(s, self.catalog)
        with self.assertRaises(ValueError):
            update(s, replace(p, gini_numerator=999), make_answer(p, "hello"), self.catalog)
        with self.assertRaises(ValueError):
            update(s, p, replace(make_answer(p, "hello"), receipt_digest="0"), self.catalog)
        self.assertEqual(update(s, p, make_answer(p, "not-in-language"), self.catalog).status, "model_inconsistent")
        with self.assertRaises(ValueError):
            no_informative_query(s, self.catalog)



class SyntheticInformativeUniformTests(unittest.TestCase):
    """P1 / B1+ engineered on invented public data; never evaluate heldouts."""

    @classmethod
    def setUpClass(cls):
        import random
        cls.catalog = build_catalog()
        cls.split = input_split(20261030)
        a, b = cls.split.public_ids[:2]
        cls.examples = ((a, INPUTS[a]), (b, INPUTS[b]))
        cls.random = random

    def session(self, task="b1plus"):
        return start(task, self.examples, self.split, self.catalog)

    def informative(self, session):
        """Independent reference: distinct semantic outputs, not production Gini."""
        asked = {answer[0] for answer in session.answers}
        return tuple(q for q in session.available_query_ids if q not in asked
                     and len({self.catalog.by_id[cid].output_signature[q]
                              for cid in session.class_ids}) > 1)

    def test_positive_only_and_exact_seeded_reference(self):
        from packages.active_learning import propose_informative_random
        s = self.session()
        allowed = self.informative(s)
        self.assertTrue(allowed)
        for seed in (0, 1, 8, 19, 2**63 - 1):
            p = propose_informative_random(s, self.catalog, seed=seed)
            expected = self.random.Random(
                f"active001-informative-uniform-v1:{seed}:{s.commitment()}"
            ).choice(list(allowed))
            self.assertEqual(p.input_id, expected)
            self.assertIn(p.input_id, allowed)
            self.assertGreater(p.gini_numerator, 0)
            self.assertEqual(p.policy, "informative-uniform-v1")
            self.assertEqual(p, propose_informative_random(s, self.catalog, seed=seed))

    def test_original_b1_b2_semantics_and_rng_domain_unchanged(self):
        s = self.session()
        seed = 8
        old_b1 = propose_random(s, self.catalog, seed=seed)
        expected = self.random.Random(
            f"active001-random-v1:{seed}:{s.commitment()}"
        ).choice(list(s.available_query_ids))
        self.assertEqual(old_b1.input_id, expected)
        self.assertEqual(old_b1.policy, "uniform-random-v1")
        b2 = propose_disagreement(s, self.catalog)
        self.assertEqual(b2.input_id, min(
            q for q in self.informative(s)
            if len(s.class_ids)**2 - sum(
                sum(1 for cid in s.class_ids
                    if self.catalog.by_id[cid].output_signature[q] == output)**2
                for output in {
                    self.catalog.by_id[cid].output_signature[q]
                    for cid in s.class_ids
                }
            ) == b2.gini_numerator
        ))

    def test_full_replay_after_answer_and_second_question(self):
        from packages.active_learning import propose_informative_random
        s = self.session()
        target = self.catalog.by_id[s.class_ids[-1]]
        p = propose_informative_random(s, self.catalog, seed=37)
        s2 = update(s, p, make_answer(p, target.output_signature[p.input_id]),
                    self.catalog)
        self.assertIn(target.class_id, s2.class_ids)
        self.assertEqual(len(s2.trace), 1)
        self.assertEqual(s2.trace[0][0], p)
        self.assertEqual(final_program(s2, self.catalog),
                         self.catalog.by_id[s2.class_ids[0]].program)
        if s2.status == "ambiguous":
            p2 = propose_informative_random(s2, self.catalog, seed=38)
            self.assertIsNotNone(p2)
            self.assertNotEqual(p2.input_id, p.input_id)
            self.assertIn(p2.input_id, self.informative(s2))
            s3 = update(s2, p2, make_answer(
                p2, target.output_signature[p2.input_id]), self.catalog)
            self.assertIn(s3.status, ("identified", "budget_exhausted"))
            self.assertEqual(len(s3.trace), 2)
            self.assertIn(target.class_id, s3.class_ids)
        else:
            self.assertIn(s2.status, ("identified", "query_unidentifiable",
                                      "budget_exhausted"))

    def test_no_informative_context_stops_without_question(self):
        from collections import defaultdict
        from itertools import combinations
        from packages.active_learning import propose_informative_random
        # An F2 context is invented afresh from the fixed public/query split.
        # This reference calculation never opens audit-only target labels.
        example = None
        for a, b in combinations(self.split.public_ids, 2):
            groups = defaultdict(list)
            for cls in self.catalog.classes:
                groups[(cls.output_signature[a], cls.output_signature[b])].append(cls)
            for outputs, group in groups.items():
                if len(group) > 1 and all(
                    len({cls.output_signature[q] for cls in group}) == 1
                    for q in self.split.query_ids
                ):
                    example = ((a, outputs[0]), (b, outputs[1]))
                    break
            if example is not None:
                break
        self.assertIsNotNone(example, "Gate F's F2 context must exist")
        s = start("unidentifiable", example, self.split, self.catalog)
        self.assertEqual(s.status, "ambiguous")
        self.assertEqual(self.informative(s), ())
        self.assertIsNone(propose_informative_random(s, self.catalog, seed=0))
        terminal = no_informative_query(s, self.catalog)
        self.assertEqual(terminal.status, "query_unidentifiable")
        self.assertIsNone(propose_informative_random(terminal, self.catalog, seed=0))

    def test_tampering_bad_seed_and_budget_rejected(self):
        from packages.active_learning import propose_informative_random
        s = self.session()
        for bad in (-1, 2**63, True, "8", 0.0):
            with self.subTest(seed=repr(bad)), self.assertRaises(ValueError):
                propose_informative_random(s, self.catalog, seed=bad)
        p = propose_informative_random(s, self.catalog, seed=8)
        target = self.catalog.by_id[s.class_ids[0]]
        a = make_answer(p, target.output_signature[p.input_id])
        for bad in (replace(p, random_seed=True),
                    replace(p, random_seed=9),
                    replace(p, policy="uniform-random-v1"),
                    replace(p, input_id=s.available_query_ids[-1]),
                    replace(p, gini_numerator=0)):
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                update(s, bad, a, self.catalog)
        updated = update(s, p, a, self.catalog)
        with self.assertRaises(ValueError):
            final_program(replace(updated, class_ids=("fake",)), self.catalog)
        zero = start("zero", self.examples, self.split, self.catalog, max_questions=0)
        self.assertIsNone(propose_informative_random(zero, self.catalog, seed=0))

    def test_mixed_history_is_replayed_but_not_scored(self):
        from packages.active_learning import propose_informative_random
        s = self.session()
        target = self.catalog.by_id[s.class_ids[-1]]
        p = propose_informative_random(s, self.catalog, seed=7)
        s2 = update(s, p, make_answer(
            p, target.output_signature[p.input_id]), self.catalog)
        if s2.status == "ambiguous":
            q = propose_disagreement(s2, self.catalog)
            s3 = update(s2, q, make_answer(
                q, target.output_signature[q.input_id]), self.catalog)
            self.assertEqual(tuple(p.policy for p, _ in s3.trace),
                             ("informative-uniform-v1", "max-disagreement-v1"))
            self.assertEqual(len(s3.trace), 2)
        # Scientific arm isolation (one policy per arm) belongs to evaluator PR.


if __name__ == "__main__":
    unittest.main()

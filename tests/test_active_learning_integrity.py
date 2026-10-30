"""Adversarial ACTIVE-001 invented fixtures only. No historical experiment imports."""
import unittest
from dataclasses import replace

from packages.inquiry_world import build_catalog, input_split, INPUTS, validate_split
from packages.active_learning import (
    start, partitions, propose_disagreement, propose_random,
    make_answer, update, _new_proposal, final_program,
)


class QueryIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.split = input_split(20261030)
        a, b = cls.split.public_ids[:2]
        cls.public = ((a, INPUTS[a]), (b, INPUTS[b]))

    def session(self):
        s = start("integrity", self.public, self.split, self.catalog)
        self.assertEqual(s.status, "ambiguous")
        return s

    def test_validate_partition_before_exposure(self):
        validate_split(self.split)
        damaged = (
            replace(self.split, query_ids=self.split.audit_ids),
            replace(self.split, query_ids=tuple(sorted(
                (self.split.public_ids[0],) + self.split.query_ids[1:]))),
            replace(self.split, split_digest="0" * 64),
            replace(self.split, public_ids=self.split.public_ids[:-1] + (True,)),
        )
        for wrong in damaged:
            with self.subTest(wrong=repr(wrong)[:50]), self.assertRaises(ValueError):
                start("bad", self.public, wrong, self.catalog)

    def test_session_reconstructs_canonical_classes_and_budget(self):
        s = self.session()
        p = propose_disagreement(s, self.catalog)
        self.assertIsNotNone(p)
        forged = (
            replace(s, class_ids=(s.class_ids[0],) * 3),
            replace(s, class_ids=s.class_ids[:-1]),
            replace(s, max_questions=0),
            replace(s, status="identified"),
            replace(s, available_query_ids=self.split.audit_ids),
            replace(s, public_examples=((self.split.audit_ids[0], "a"), self.public[1])),
            replace(s, answers=((p.input_id, "bogus", "a" * 64),)),
            replace(s, answers=((p.input_id, "bogus", "a" * 64),
                                (p.input_id, "bogus", "a" * 64))),
        )
        for wrong in forged:
            with self.subTest(wrong=repr(wrong)[:65]), self.assertRaises(ValueError):
                propose_disagreement(wrong, self.catalog)

    def test_policy_claim_must_replay_true_maximum(self):
        s = self.session()
        optimal = propose_disagreement(s, self.catalog)
        self.assertIsNotNone(optimal)
        inferior = next(i for i in s.available_query_ids if
                        len(s.class_ids)**2 - sum(n*n for _, n in
                        partitions(s, self.catalog, i)) < optimal.gini_numerator)
        fake = _new_proposal(s, self.catalog, inferior, "max-disagreement-v1")
        self.assertLess(fake.gini_numerator, optimal.gini_numerator)
        with self.assertRaises(ValueError):
            update(s, fake, make_answer(fake, "a"), self.catalog)

    def test_seeded_random_control_replays_selection(self):
        s = self.session()
        p = propose_random(s, self.catalog, seed=7)
        self.assertIsNotNone(p)
        self.assertEqual(p.random_seed, 7)
        target = self.catalog.by_id[s.class_ids[-1]]
        after = update(s, p, make_answer(p, target.output_signature[p.input_id]),
                       self.catalog)
        self.assertIn(target.class_id, after.class_ids)
        with self.assertRaises(ValueError):
            update(s, replace(p, random_seed=8), make_answer(p, "a"), self.catalog)
        other = next(i for i in s.available_query_ids if i != p.input_id)
        fake = _new_proposal(s, self.catalog, other, "uniform-random-v1",
                             random_seed=7)
        with self.assertRaises(ValueError):
            update(s, fake, make_answer(fake, "a"), self.catalog)

    def test_terminal_budget_is_not_reopenable(self):
        s = self.session()
        b0 = start("integrity", self.public, self.split, self.catalog,
                   max_questions=0)
        self.assertEqual(b0.status, "budget_exhausted")
        self.assertIsNone(propose_disagreement(b0, self.catalog))
        self.assertIsNotNone(final_program(b0, self.catalog))
        with self.assertRaises(ValueError):
            propose_disagreement(replace(b0, status="ambiguous"), self.catalog)
        p = propose_disagreement(s, self.catalog)
        target = self.catalog.by_id[s.class_ids[-1]]
        after = update(s, p, make_answer(p, target.output_signature[p.input_id]),
                       self.catalog)
        self.assertLessEqual(len(after.class_ids), len(s.class_ids))


if __name__ == "__main__":
    unittest.main()

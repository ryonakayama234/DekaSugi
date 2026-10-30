"""ACTIVE-001 synthetic-only regression for equality-preserving container subclasses.

No historical scorer, evaluator, or sealed source is imported.
"""
from dataclasses import replace
import unittest

from packages.inquiry_world import INPUTS, build_catalog, input_split
from packages.active_learning import (
    final_program, make_answer, no_informative_query, partitions,
    propose_disagreement, propose_random, start, update,
)


class LyingIds(tuple):
    """Retains tuple equality, but iteration supplies the first ID repeatedly."""
    def __iter__(self):
        if not self:
            return iter(())
        return iter((self[0],) * len(self))


class EqualStr(str):
    """Subclasses may preserve equality while adding caller behavior."""
    pass


class EqualInt(int):
    pass


class SessionContainerBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.split = input_split(20261030)
        a, b = cls.split.public_ids[:2]
        cls.public = ((a, INPUTS[a]), (b, INPUTS[b]))

    def begin(self):
        s = start('container-boundary', self.public, self.split, self.catalog)
        self.assertEqual(s.status, 'ambiguous')
        self.assertGreater(len(s.class_ids), 1)
        return s

    def test_equal_but_lying_class_ids_are_rejected(self):
        s = self.begin()
        bad = replace(s, class_ids=LyingIds(s.class_ids))
        self.assertEqual(bad, s, 'reproduce dataclass equality blind spot')
        self.assertNotEqual(tuple(iter(bad.class_ids)), s.class_ids)
        for check in (
            lambda: propose_disagreement(bad, self.catalog),
            lambda: propose_random(bad, self.catalog, seed=1),
            lambda: partitions(bad, self.catalog, self.split.query_ids[0]),
            lambda: final_program(bad, self.catalog),
            lambda: no_informative_query(bad, self.catalog),
        ):
            with self.subTest(check=repr(check)), self.assertRaises(ValueError):
                check()
        self.assertIsNotNone(propose_disagreement(s, self.catalog))

    def test_individual_class_id_subclasses_rejected(self):
        s = self.begin()
        bad = replace(s, class_ids=(EqualStr(s.class_ids[0]),) + s.class_ids[1:])
        self.assertEqual(bad, s)
        with self.assertRaises(ValueError):
            propose_disagreement(bad, self.catalog)

    def test_compact_answer_storage_requires_exact_inner_tuples(self):
        s = self.begin()
        p = propose_disagreement(s, self.catalog)
        target = self.catalog.by_id[s.class_ids[-1]]
        q = update(s, p, make_answer(p, target.output_signature[p.input_id]), self.catalog)
        forged = replace(q, answers=(LyingIds(q.answers[0]),))
        self.assertEqual(forged, q)
        with self.assertRaises(ValueError):
            final_program(forged, self.catalog)

    def test_session_status_and_digest_subclasses_rejected(self):
        s = self.begin()
        for forged in (
            replace(s, status=EqualStr(s.status)),
            replace(s, pool_digest=EqualStr(s.pool_digest)),
        ):
            self.assertEqual(forged, s)
            with self.assertRaises(ValueError):
                propose_disagreement(forged, self.catalog)

    def test_proposal_bool_fields_cannot_pass_int_equality(self):
        s = self.begin()
        p = propose_disagreement(s, self.catalog)
        # bool is an int subclass; compare-equal data must still be rejected.
        # gini denominator is >1 here, but step=0 and `False` are equal.
        forged = replace(p, step=False)
        self.assertEqual(forged, p)
        target = self.catalog.by_id[s.class_ids[-1]]
        with self.assertRaises(ValueError):
            update(s, forged, make_answer(p, target.output_signature[p.input_id]), self.catalog)
        with self.assertRaises(ValueError):
            make_answer(forged, 'a')

    def test_historical_answer_fields_reject_equal_subclasses(self):
        s = self.begin()
        p = propose_disagreement(s, self.catalog)
        target = self.catalog.by_id[s.class_ids[-1]]
        q = update(s, p, make_answer(p, target.output_signature[p.input_id]), self.catalog)
        old_p, old_a = q.trace[0]
        forged_answer = replace(old_a, step=EqualInt(old_a.step))
        bad = replace(q, trace=((old_p, forged_answer),))
        self.assertEqual(bad, q)
        with self.assertRaises(ValueError):
            final_program(bad, self.catalog)


if __name__ == '__main__':
    unittest.main()

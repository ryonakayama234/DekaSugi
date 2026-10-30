"""Review-driven P2 reproduction: a mappingproxy over a dict subclass is not frozen.

Fixed finite synthetic world only, no historical evaluator or source data.
"""
from dataclasses import replace
from types import MappingProxyType
import unittest

from packages.inquiry_world import INPUTS, build_catalog, input_split
from packages.active_learning import (
    final_program, make_answer, no_informative_query, partitions,
    propose_disagreement, propose_random, start, update,
)


class LyingLookup(dict):
    """Dictionary equality is ordinary, but indexing returns fabricated classes."""
    def __getitem__(self, key):
        c = super().__getitem__(key)
        return replace(c, output_signature=("forged",) * len(INPUTS),
                       program=("append_a",))


class ProxyLookupCanonicalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.split = input_split(20261030)
        a, b = cls.split.public_ids[:2]
        cls.public = ((a, INPUTS[a]), (b, INPUTS[b]))

    def test_mappingproxy_over_dict_subclass_cannot_change_gini_or_stop(self):
        baseline = start("lookup-canary", self.public, self.split, self.catalog)
        correct = propose_disagreement(baseline, self.catalog)
        self.assertIsNotNone(correct)
        underlying = LyingLookup(self.catalog.by_id)
        forged = replace(self.catalog, by_id=MappingProxyType(underlying))
        self.assertEqual(forged, self.catalog, "reproduce equality blind spot")
        self.assertEqual(underlying[next(iter(underlying))].output_signature,
                         ("forged",) * len(INPUTS))
        with_forged = start("lookup-canary", self.public, self.split, forged)
        self.assertEqual(with_forged, baseline)
        self.assertEqual(propose_disagreement(with_forged, forged), correct)
        self.assertEqual(partitions(with_forged, forged, correct.input_id),
                         partitions(baseline, self.catalog, correct.input_id))
        with self.assertRaises(ValueError):
            no_informative_query(with_forged, forged)
        self.assertEqual(final_program(with_forged, forged),
                         final_program(baseline, self.catalog))

    def test_answer_update_and_history_are_canonical_under_lying_lookup(self):
        s = start("lookup-progression", self.public, self.split, self.catalog)
        liar = replace(self.catalog, by_id=MappingProxyType(LyingLookup(self.catalog.by_id)))
        target = self.catalog.by_id[s.class_ids[-1]]
        p = propose_disagreement(s, liar)
        self.assertIsNotNone(p)
        y = target.output_signature[p.input_id]
        answer = make_answer(p, y)
        result = update(s, p, answer, liar)
        truth = update(s, p, answer, self.catalog)
        self.assertEqual(result, truth)
        self.assertIn(target.class_id, result.class_ids)
        self.assertEqual(final_program(result, liar), final_program(result, self.catalog))
        self.assertEqual(propose_disagreement(result, liar),
                         propose_disagreement(result, self.catalog))

    def test_seeded_random_never_uses_external_lookup(self):
        s = start("lookup-random", self.public, self.split, self.catalog)
        liar = replace(self.catalog, by_id=MappingProxyType(LyingLookup(self.catalog.by_id)))
        for seed in (0, 7, 19):
            self.assertEqual(propose_random(s, liar, seed=seed),
                             propose_random(s, self.catalog, seed=seed))

    def test_mutation_after_validation_cannot_poison_prediction(self):
        underlying = LyingLookup(self.catalog.by_id)
        proxy = replace(self.catalog, by_id=MappingProxyType(underlying))
        s = start("lookup-mutate", self.public, self.split, proxy)
        baseline = propose_disagreement(s, self.catalog)
        self.assertIsNotNone(baseline)
        # The wrapper remains a MappingProxyType while the underlying mapping changes.
        first = next(iter(underlying))
        underlying[first] = replace(underlying[first],
                                    output_signature=("wrong",) * len(INPUTS))
        # A changed, genuinely non-equivalent lookup must be rejected or have no
        # influence; here the explicit integrity gate correctly rejects it.
        with self.assertRaises(ValueError):
            propose_disagreement(s, proxy)
        self.assertEqual(propose_disagreement(s, self.catalog), baseline)


if __name__ == "__main__":
    unittest.main()

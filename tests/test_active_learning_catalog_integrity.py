"""ACTIVE-001 synthetic-only canonical Catalog integrity negative fixtures.

No scorer, private ledger, historic TRAIN/DEV/FINAL or external Oracle.
"""
from dataclasses import replace
from types import MappingProxyType
import unittest

from packages.inquiry_world import INPUTS, build_catalog, input_split
from packages.active_learning import (
    start, propose_disagreement, final_program, no_informative_query,
)


class CanonicalCatalogIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.split = input_split(20261030)
        a, b = cls.split.public_ids[:2]
        cls.public = ((a, INPUTS[a]), (b, INPUTS[b]))

    def session(self):
        s = start("catalog-integrity", self.public, self.split, self.catalog)
        self.assertEqual(s.status, "ambiguous")
        self.assertIsNotNone(propose_disagreement(s, self.catalog))
        return s

    def test_forged_by_id_signatures_cannot_suppress_informative_question(self):
        s = self.session()
        # Reproduce the P2: classes and universe_digest are unchanged but the
        # lookup maps every hypothesis to the same constant output signature.
        lookup = {cid: replace(c, output_signature=("forged",) * len(INPUTS))
                  for cid, c in self.catalog.by_id.items()}
        forged = replace(self.catalog, by_id=MappingProxyType(lookup))
        with self.assertRaises(ValueError):
            propose_disagreement(s, forged)
        with self.assertRaises(ValueError):
            no_informative_query(s, forged)
        with self.assertRaises(ValueError):
            final_program(s, forged)

    def test_start_rejects_noncanonical_class_outputs(self):
        first = self.catalog.classes[0]
        bogus = replace(first, output_signature=("x",) * len(INPUTS))
        altered = replace(self.catalog, classes=(bogus,) + self.catalog.classes[1:])
        with self.assertRaises(ValueError):
            start("bad", self.public, self.split, altered)

    def test_representative_program_and_id_must_match(self):
        c = self.catalog.classes[0]
        bogus = replace(c, program=("upper",))
        changed = replace(self.catalog, by_id=MappingProxyType({
            **self.catalog.by_id, c.class_id: bogus
        }))
        with self.assertRaises(ValueError):
            start("bad", self.public, self.split, changed)
        changed_id = replace(c, class_id="forged-id")
        wrong_order = replace(self.catalog, classes=(changed_id,) + self.catalog.classes[1:])
        with self.assertRaises(ValueError):
            start("bad", self.public, self.split, wrong_order)

    def test_lookup_keys_count_and_class_order_are_canonical(self):
        mapping = dict(self.catalog.by_id)
        mapping.pop(next(iter(mapping)))
        for altered in (
            replace(self.catalog, by_id=MappingProxyType(mapping)),
            replace(self.catalog, syntax_count=0),
            replace(self.catalog, classes=self.catalog.classes[::-1]),
            replace(self.catalog, universe_digest="0" * 64),
        ):
            with self.subTest(kind=repr(altered)[:50]), self.assertRaises(ValueError):
                start("bad", self.public, self.split, altered)

    def test_untrusted_mutable_lookup_denied_even_if_equal(self):
        mutable = replace(self.catalog, by_id=dict(self.catalog.by_id))
        with self.assertRaises(ValueError):
            start("bad", self.public, self.split, mutable)

    def test_fresh_independent_canonical_build_is_accepted(self):
        a = self.session()
        same = build_catalog()
        b = start("catalog-integrity", self.public, self.split, same)
        self.assertEqual(a, b)
        self.assertEqual(propose_disagreement(a, same),
                         propose_disagreement(a, self.catalog))


if __name__ == "__main__":
    unittest.main()

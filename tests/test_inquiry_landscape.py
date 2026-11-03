"""Independent G0B finite-engineering references; no learner or historic evaluator."""
from itertools import product
import unittest

from packages.inquiry_landscape.source import (DOMAIN, Model, enumerate_worlds,
                                                world_from_choices, semantic_signature)
from packages.inquiry_landscape.oracle import certify
from packages.inquiry_landscape.analysis import build_report, canonical_json, report_digest


def reference_score(models, schedule):
    """Enumerate all terminal predictions or abstention, no modal-score formula."""
    group = {}
    for m in models:
        answers = tuple(m.questions[a] for a in schedule)
        group.setdefault(answers, []).append(m)
    score = 0
    for g in group.values():
        for probe in range(3):
            payoff = []
            for guess in (None, 0, 1):
                payoff.append(sum(0 if guess is None else (m.weight if m.audit[probe] == guess
                                  else -m.weight) for m in g))
            score += max(payoff)
    return score


def reference_optima(models):
    """Explicitly enumerate fixed schedules and every two-stage policy on binary answers."""
    fixed = max(reference_score(models, schedule) for length in range(3)
                for schedule in product(range(3), repeat=length))
    ad = reference_score(models, ())
    for a in range(3):
        ad = max(ad, reference_score(models, (a,)))
        for b0, b1 in product((None, 0, 1, 2), repeat=2):
            groups = [[m for m in models if m.questions[a] == y] for y in (0, 1)]
            score = sum(reference_score(tuple(g), (() if b is None else (b,))) for g, b in zip(groups,(b0,b1)))
            ad = max(ad,score)
    return ad, fixed


class G0BIndependentTests(unittest.TestCase):
    def test_full_source_exact_partition_and_public_mask(self):
        ws=enumerate_worlds()
        self.assertEqual(len(ws),512)
        self.assertEqual(sum(w.partition == 'EXT448_NEW' for w in ws),448)
        self.assertEqual(len({semantic_signature(w) for w in ws}),512)
        for w in ws:
            self.assertEqual(len(w.models),4)
            self.assertEqual({m.audit for m in w.models}, {(0,0,0),(0,1,1),(1,0,1),(1,1,0)})
            self.assertTrue(all(i in (0,1) for m in w.models for i in m.questions))

    def test_reference_512_worlds(self):
        for w in enumerate_worlds():
            r=certify(w.models,'WORLD_KNOWN')
            ad, fixed=reference_optima(w.models)
            self.assertEqual((r.numerator_adaptive,r.numerator_fixed),(ad,fixed),w.source_id)
            self.assertEqual(r.denominator,12)

    def test_reference_448_public_mixture(self):
        new=tuple(m for w in enumerate_worlds() if w.partition=='EXT448_NEW' for m in w.models)
        ad, fixed=reference_optima(new)
        r=certify(new,'PUBLIC_MIXTURE')
        self.assertEqual((ad,fixed),(1040,1040))
        self.assertEqual((r.numerator_adaptive,r.numerator_fixed),(ad,fixed))
        self.assertEqual(r.denominator,5376)
        self.assertEqual(r.best_fixed,(1,2))

    def test_expected_census(self):
        r=build_report()
        self.assertEqual((r['EXT448_NEW']['world_oracle_positive'],r['EXT448_NEW']['world_oracle_zero']),(25,423))
        self.assertEqual((r['CAL64_DISCLOSED']['world_oracle_positive'],r['CAL64_DISCLOSED']['world_oracle_zero']),(2,62))
        self.assertEqual(r['EXT448_NEW']['public_oracle']['gain_numerator'],0)
        self.assertEqual(r['CAL64_DISCLOSED']['public_oracle']['gain_numerator'],0)
        self.assertEqual(len(canonical_json(r).encode()),len(canonical_json(build_report()).encode()))
        self.assertEqual(report_digest(r),report_digest(build_report()))

    def test_strict_adversarial_invalid(self):
        w=world_from_choices((0,0,0))
        for bad in ((),(True,0,0),(8,0,0),[0,0,0],(0,0),(-1,0,0)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                world_from_choices(bad)
        for bad in (tuple(),tuple(w.models[:1])+('malicious',),
                    tuple(Model(m.questions, m.audit, True) for m in w.models)):
            with self.assertRaises(ValueError):
                certify(bad,'WORLD_KNOWN')


if __name__=='__main__':
    unittest.main()

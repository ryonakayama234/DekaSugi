"""Synthetic/source-only proof obligations, no authorized K0 or CAL."""
import itertools
import unittest
from fractions import Fraction
from world_cal.k0_b import scan_k0b_pairs
from world_cal.k0_c import exhaustive_k0c_curve,SPACE_SYNTAX_LOWER_BOUND
from math import comb
from world_cal.k0_coverage import (
    CoverageUnknown, law_cell_count, exact_cell_mass, iter_law_pairs,
    bounded_pair_cell_indices, path_index_cardinality,
    status_when_not_exhausted,
)
from world_cal.abstract_support import verified_rows

class IndexProofTests(unittest.TestCase):
    def test_registered_law_pair_bijection(self):
        pairs=list(iter_law_pairs())
        self.assertEqual(len(pairs), comb(384,2))
        self.assertEqual(len({(a[0],b[0]) for a,b in pairs}),73536)
        self.assertTrue(all(a[0]<b[0] for a,b in pairs))
    def test_all_phase_counts_by_the_same_per_law_formula(self):
        rows=verified_rows()
        for phase,count in {"TRAIN":663552,"CAL":663552,
                            "G1":663552,"G2":239616}.items():
            self.assertEqual(sum(law_cell_count(row,phase) for row in rows),count)
            self.assertEqual(sum((law_cell_count(row,phase)*exact_cell_mass(row,phase)
                                  for row in rows),Fraction(0)),Fraction(1))
    def test_fixed_trial_support_cardinality_and_cap_fail_closed(self):
        a,b=next(iter_law_pairs())
        n=path_index_cardinality(a,b,"TRAIN",2)
        self.assertGreater(n,0)
        index=bounded_pair_cell_indices(a,b,"TRAIN",cap=1)
        self.assertEqual(len(next(index)),2)
        with self.assertRaisesRegex(CoverageUnknown,"STOP_UNKNOWN"):
            next(index)
        self.assertEqual(status_when_not_exhausted(
            law_pairs_complete=True,trial_lengths_fixed=False,
            demo_exclusion_verified=True,histories_complete=True),"UNKNOWN")
    def test_bare_boolean_cannot_claim_complete_k0(self):
        self.assertEqual(scan_k0b_pairs([],complete_support=True)["status"],"UNKNOWN")
        self.assertEqual(exhaustive_k0c_curve(
            cells=[],space_candidates=[],space_complete=True,
            support_complete=True,b_final=4096,control_curves={})["status"],"UNKNOWN")
    def test_full_typed_space_cannot_fit_literal_node_cap(self):
        self.assertEqual(SPACE_SYNTAX_LOWER_BOUND, 14**63)
        self.assertGreater(SPACE_SYNTAX_LOWER_BOUND,2_000_000)
        result=exhaustive_k0c_curve(
            cells=[],space_candidates=[],
            space_complete={"typed_space_exhausted":True,
                            "control_curves_exhausted":True,
                            "canonical_space_sha256":"arbitrary",
                            "canonical_space_count":SPACE_SYNTAX_LOWER_BOUND},
            support_complete={"law_instance_demo_support_exhausted":True,
                              "weights_audited":True},
            b_final=4096,control_curves={},cap=2_000_000)
        self.assertEqual(result["status"],"UNKNOWN")
        self.assertEqual(result["lower_bound"],str(14**63))
    def test_unbounded_trial_counts_not_claimed_complete(self):
        a,b=next(iter_law_pairs())
        with self.assertRaises(CoverageUnknown):
            path_index_cardinality(a,b,"TRAIN",0)
        with self.assertRaises(CoverageUnknown):
            path_index_cardinality(a,b,"TRAIN",2,demos_per_law=2)

if __name__=="__main__":unittest.main()

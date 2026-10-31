"""Invented-only class-pool feasibility: never a real source/seed/scorer."""
from dataclasses import replace
import unittest
from packages.concept_world import build_catalog
from packages.concept_preflight import synthetic_pool_preview,validate_preview,preflight_metrics

class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=build_catalog()
        cls.preview=synthetic_pool_preview(cls.catalog)
    def test_sizes_and_disjointness(self):
        m=preflight_metrics(self.preview,self.catalog)
        self.assertEqual(m["population_classes"],895)
        self.assertEqual(m["class_counts"],{"TRAIN":358,"DEV":179,"FINAL":358})
        self.assertEqual(m["family_counts"]["TRAIN"],{"plain":12,"conditional":346})
        self.assertEqual(m["family_counts"]["DEV"],{"plain":6,"conditional":173})
        self.assertEqual(m["family_counts"]["FINAL"],{"plain":11,"conditional":347})
        self.assertFalse(m["formal_train_or_final_authorized"])
        self.assertGreater(m["expected_repeated_class_draws_if_uniform_iid"],1600)
        self.assertLess(m["paired_hoeffding_95_radius"],.061)
    def test_determinism(self):
        self.assertEqual(self.preview,synthetic_pool_preview(self.catalog))
        validate_preview(replace(self.preview),self.catalog)
    def test_same_digest_forgery_denied(self):
        ids=list(self.preview.train_class_ids)
        ids[0]=self.preview.final_class_ids[0]
        tampered=replace(self.preview,train_class_ids=tuple(ids))
        self.assertEqual(tampered.commitment,self.preview.commitment)
        with self.assertRaises(ValueError):validate_preview(tampered,self.catalog)
        with self.assertRaises(ValueError):preflight_metrics(tampered,self.catalog)
    def test_no_custom_private_seed(self):
        with self.assertRaises(ValueError):synthetic_pool_preview(self.catalog,salt="real-private-seed")
    def test_malformed_catalog(self):
        c=self.catalog
        sig=list(c.class_signatures);sig[1]=sig[0]
        with self.assertRaises(ValueError):synthetic_pool_preview(replace(c,class_signatures=tuple(sig)))

if __name__=="__main__":
    unittest.main()

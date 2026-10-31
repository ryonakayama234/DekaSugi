"""Invented TRAIN-only learning; no DEV/FINAL scoring."""
import dataclasses
import unittest
from packages.concept_world import Program, build_catalog, digest
from packages.concept_learning import (
    _template_from_pair,simulate_train,induce_concepts,recommend_programs,context_bucket,validate_snapshot,_snapshot_payload)

class ConceptLearningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.random,cls.random_snapshot=simulate_train(20261031,256,"random")
        cls.active,cls.active_snapshot=simulate_train(20261031,256,"active")

    def test_actual_train_and_snapshot(self):
        self.assertEqual(len(self.random),256)
        self.assertEqual(len(self.active),256)
        self.assertEqual(sum(e.train_verified_success for e in self.random),105)
        self.assertEqual(sum(e.train_verified_success for e in self.active),231)
        self.assertTrue(self.active_snapshot.concept_library)
        self.assertEqual(len(self.active_snapshot.concept_library),8)
        self.assertTrue(all(len(c.support_task_ids)>=3 and c.compression_gain>0
                            and c.parameter_count<=2 for c in self.active_snapshot.concept_library))
        self.assertNotEqual(self.random_snapshot.snapshot_digest,self.active_snapshot.snapshot_digest)
        # All semantic fields and TRAIN provenance, not just IDs and gain, are bound.
        self.assertEqual(self.active_snapshot.snapshot_digest,digest(_snapshot_payload(self.active_snapshot)))
        self.assertEqual(self.random_snapshot.snapshot_digest,digest(_snapshot_payload(self.random_snapshot)))
        validate_snapshot(self.active_snapshot,build_catalog())

    def test_no_secret_target_in_episodes(self):
        for e in self.active+self.random:
            fields=dataclasses.asdict(e)
            self.assertFalse(set(fields).intersection({"target","target_id","audit_labels","seed_root"}))
            self.assertLessEqual(len(e.queried_input_ids),2)
            self.assertEqual(len(set(e.queried_input_ids)),len(e.queried_input_ids))
            self.assertTrue(0<=context_bucket(e.public_input_ids,e.public_answers)<64)

    def test_typed_anti_unification(self):
        a=Program("contains_a",("trim","lower"),("reverse","upper"))
        b=Program("contains_a",("trim","upper"),("reverse","upper"))
        self.assertEqual(_template_from_pair(a,b),("contains_a",("trim",None),("reverse","upper")))
        self.assertIsNone(_template_from_pair(Program(None,("trim",)),b))

    def test_replay(self):
        repeated,snapshot=simulate_train(20261031,256,"active")
        self.assertEqual(repeated,self.active)
        self.assertEqual(snapshot.snapshot_digest,self.active_snapshot.snapshot_digest)

    def test_public_only_inference_order(self):
        cat=build_catalog()
        e=self.active[7]
        possible=tuple(i for i,sig in enumerate(cat.class_signatures)
                       if all(sig[q]==answer for q,answer in zip(e.public_input_ids,e.public_answers)))
        ranked=recommend_programs(self.active_snapshot,cat,e.public_input_ids,e.public_answers,possible)
        self.assertEqual(len(ranked),min(64,len(possible)))
        self.assertEqual(len(set(ranked)),len(ranked))
        self.assertTrue(set(ranked).issubset(set(possible)))


    def test_reject_forged_catalog_for_learning_and_recommendation(self):
        from dataclasses import replace
        catalog=build_catalog()
        signatures=list(catalog.class_signatures)
        signatures[1]=signatures[0]
        forged=replace(catalog,class_signatures=tuple(signatures))
        e=self.active[7]
        candidates=tuple(i for i,sig in enumerate(catalog.class_signatures)
                         if all(sig[q]==answer for q,answer in zip(e.public_input_ids,e.public_answers)))
        with self.assertRaises(ValueError):
            recommend_programs(self.active_snapshot,forged,e.public_input_ids,e.public_answers,candidates)
        with self.assertRaises(ValueError):
            induce_concepts(self.active,forged)


    def test_snapshot_body_support_and_policy_tampering_rejected(self):
        from dataclasses import replace
        cat=build_catalog()
        snap=self.active_snapshot
        c=snap.concept_library[0]
        e=self.active[7]
        candidates=tuple(i for i,sig in enumerate(cat.class_signatures)
                         if all(sig[q]==answer for q,answer in zip(e.public_input_ids,e.public_answers)))
        variants=[
            replace(c,support_task_ids=()),
            replace(c,parameter_count=99),
            replace(c,then_pattern=tuple(reversed(c.then_pattern))),
            replace(c,compression_gain=c.compression_gain+1),
            replace(c,concept_id="f"*64),
        ]
        for altered in variants:
            corrupted=replace(snap,concept_library=(altered,)+snap.concept_library[1:])
            with self.assertRaises(ValueError):
                recommend_programs(corrupted,cat,e.public_input_ids,e.public_answers,candidates)
            # Even if an attacker recalculates the local digest, the semantic
            # invariants and concept identity are still checked.
            forged=replace(corrupted,snapshot_digest=digest(_snapshot_payload(corrupted)))
            if altered != c:
                with self.assertRaises(ValueError):
                    validate_snapshot(forged,cat)
        changed=replace(snap,policy_success_counts=())
        with self.assertRaises(ValueError):
            validate_snapshot(changed,cat)
        altered=replace(snap,train_receipt_digest="0"*64)
        with self.assertRaises(ValueError):
            validate_snapshot(altered,cat)
        malformed=replace(snap,policy_success_counts=((64,"bad",0),))
        with self.assertRaises(ValueError):
            validate_snapshot(malformed,cat)
        # Untampered clone is accepted.
        validate_snapshot(replace(snap),cat)

    def test_invalid_data_and_no_final_mode(self):
        for kwargs in ({"arm":"final"},{"task_count":257},{"task_count":0},{"seed":True}):
            with self.assertRaises(ValueError): simulate_train(**kwargs)
        with self.assertRaises(ValueError): induce_concepts(self.active,build_catalog(),max_concepts=9)

if __name__=="__main__": unittest.main()

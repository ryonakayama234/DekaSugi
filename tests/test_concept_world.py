"""Invented-only G1 structural tests: never run any official study labels."""
import unittest
from packages.concept_world import (Program, inputs, chains, enumerate_programs, execute,
    execution_cost, split_inputs, build_catalog, query_argmax, query_disagreement)

class ConceptWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()

    def test_syntax_and_population(self):
        self.assertEqual(len(inputs()), 156)
        self.assertEqual(len(set(inputs())), 156)
        self.assertEqual(len(chains()), 43)
        all_programs = enumerate_programs()
        self.assertEqual(len(all_programs), 3741)
        self.assertEqual(len({p.program_id for p in all_programs}), 3741)

    def test_conditional_and_primitives(self):
        self.assertEqual(execute(Program(None,("trim","lower"))," A "),"a")
        self.assertEqual(execute(Program("contains_a",("reverse",),("upper",)),"ba"),"ab")
        self.assertEqual(execute(Program("contains_a",("reverse",),("upper",)),"Ab"),"AB")
        self.assertEqual(execute(Program("is_empty",("append_a",),("drop_first",)),""),"a")
        self.assertEqual(execute(Program(None,("drop_first",)),""),"")
        program=Program("is_empty",("append_a",),("drop_first","lower"))
        self.assertEqual(execution_cost(program,""),2)
        self.assertEqual(execution_cost(program,"AB"),3)

    def test_reject_bad_programs(self):
        cases=[lambda: Program(None,("unknown",)),
               lambda: Program("untrusted",()),
               lambda: Program(None,(),("lower",)),
               lambda: Program(None,("trim",)*3),
               lambda: Program(None,("trim",),["lower"])]
        for case in cases:
            with self.assertRaises(ValueError): case()
        with self.assertRaises(ValueError): execute(Program(None,()),None)
        with self.assertRaises(ValueError): split_inputs(True)

    def test_partition(self):
        a=split_inputs(20261031)
        self.assertEqual(a,split_inputs(20261031))
        self.assertEqual((len(a.public_ids),len(a.query_ids),len(a.audit_ids)),(28,64,64))
        self.assertEqual(len(set(a.public_ids+a.query_ids+a.audit_ids)),156)
        self.assertNotEqual(a.commitment,split_inputs(20261030).commitment)

    def test_semantic_class_dedup(self):
        c=self.catalog
        self.assertEqual(sum(c.class_sizes),3741)
        self.assertEqual(len(c.representatives),895)
        self.assertEqual(len(set(c.class_signatures)),895)
        self.assertEqual(sum(p.predicate_id is not None for p in c.representatives),866)
        self.assertEqual(c.world_digest,build_catalog().world_digest)


    def test_forged_catalog_signatures_cannot_mask_informative_queries(self):
        from dataclasses import replace
        original = self.catalog
        signatures = list(original.class_signatures)
        signatures[1] = signatures[0]
        tampered = replace(original, class_signatures=tuple(signatures))
        self.assertEqual(tampered.world_digest, original.world_digest)
        pair = (0, 1)
        allowed = split_inputs(20261031).query_ids
        self.assertIsNotNone(query_argmax(original, pair, allowed))
        with self.assertRaises(ValueError):
            query_argmax(tampered, pair, allowed)
        with self.assertRaises(ValueError):
            query_disagreement(tampered, pair, allowed[0])
        # Separate but correct constructed copy remains accepted.
        self.assertEqual(query_argmax(replace(original), pair, allowed),
                         query_argmax(original, pair, allowed))

    def test_gini_and_invalid_question_ids(self):
        c=self.catalog
        selected=tuple(range(30))
        query=split_inputs(20261031).query_ids
        best=query_argmax(c,selected,query)
        self.assertIn(best,query)
        self.assertEqual(query_disagreement(c,selected,best),
            max(query_disagreement(c,selected,i) for i in query))
        self.assertIsNone(query_argmax(c,(0,),query))
        for invalid in ((query[0],query[0]),(156,)):
            with self.assertRaises(ValueError): query_argmax(c,selected,invalid)
        for invalid in ((0,0),()):
            with self.assertRaises(ValueError): query_disagreement(c,invalid,query[0])

if __name__ == "__main__":
    unittest.main()

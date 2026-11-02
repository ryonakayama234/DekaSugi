import tempfile
import unittest
from pathlib import Path
from packages.rep004 import (EDGES,catalog,worlds_by_family,study_manifest,learn,save,load,world_for,Session,
                            paid_train,consistent,concept_ast,validate_body,execute_body,committed_use,audit,activation_fixture,compose_ast,execute_composition,
                            ARMS,BUDGETS,step,sig,digest)

class Rep004(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.manifest=study_manifest();cls.snap=learn(8)

    def test_grammar_and_family_cardinality(self):
        self.assertEqual(len(EDGES),60)
        self.assertEqual(len(catalog()),1735)
        self.assertEqual(len(worlds_by_family()),85)
        self.assertEqual(len(set(self.manifest['train_families'])),32)
        self.assertEqual(len(set(self.manifest['composition'])&set(self.manifest['train_families'])),0)

    def test_paid_train_does_not_use_gold_in_induction(self):
        e,trace=paid_train(world_for(self.manifest['train_families'][0],1))
        self.assertEqual(len(trace),100)
        self.assertEqual(len({sig(x) for x in consistent(trace)}),1)
        self.assertEqual(trace[-1]['ordinal'],100)

    def test_snapshot_roundtrip_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'snap.json'
            save(self.snap,p)
            self.assertEqual(load(p),self.snap)
            raw=p.read_text().replace('"paid_actions":800','"paid_actions":801')
            p.write_text(raw)
            with self.assertRaises(ValueError):load(p)

    def test_true_ast_interpreter_and_mutation(self):
        edge=(0,1,2,1)
        body={'ast':concept_ast(edge),'body_hash':digest(concept_ast(edge)),
              'support':3,'positive':['fixture'],'negative':[],'status':'candidate'}
        validate_body(body)
        binding={'source':0,'target':1,'guard':2}
        self.assertEqual(execute_body(body,4,('pulse',0,None),binding),6)
        self.assertEqual(execute_body(body,0,('pulse',0,None),binding),0)
        body2={**body,'ast':concept_ast((0,1,2,0))}
        body2['body_hash']=digest(body2['ast'])
        self.assertNotEqual(execute_body(body,4,('pulse',0,None),binding),
                            execute_body(body2,4,('pulse',0,None),binding))

    def test_commit_before_score(self):
        w=world_for(self.manifest['composition'][0],500)
        c=committed_use(self.snap,w,'LQ',2)
        self.assertIn(c['status'],('ABSTAIN','COMMITTED'))
        self.assertLessEqual(c['meter']['actions'],2)
        self.assertIn(audit(w,c),range(65))
        c['commit_digest']='forged'
        with self.assertRaises(ValueError):audit(w,c)


    def test_actual_first_paid_query_switch(self):
        snap=learn(64)
        fixture=activation_fixture(snap)
        self.assertTrue(fixture['differs'],fixture)
        self.assertGreater(fixture['body_invocations'],0)
        self.assertEqual(fixture['paid_conditioning'],2)

    def test_composition_body_prestate(self):
        a=compose_ast('CHAIN')
        b={'ast':a,'body_hash':digest(a),'support':3,'positive':['fixture'],'negative':[],'status':'candidate'}
        edges=((0,1,-1,-1),(1,2,0,1))
        self.assertEqual(execute_composition(b,1,('pulse',0,None),edges),3)
        self.assertEqual(execute_composition(b,1,('pulse',1,None),edges),5)

    def test_all_arms_run_on_fresh_world(self):
        w=world_for(self.manifest['composition'][1],501)
        for arm in ARMS:
            c=committed_use(self.snap,w,arm,1)
            self.assertLessEqual(len(c['trace']),1)
            self.assertEqual(c['meter']['actions'],len(c['trace']))

if __name__=='__main__':unittest.main()
import tempfile
import unittest
from pathlib import Path
from packages.rep004 import (EDGES,catalog,worlds_by_family,study_manifest,learn,save,load,world_for,Session,
                            paid_train,consistent,concept_ast,validate_body,execute_body,committed_use,audit,activation_fixture,compose_ast,execute_composition,
                            ARMS,BUDGETS,step,sig,digest)

class Rep004(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.manifest=study_manifest();cls.snap=learn(8)

    def test_role_binding_counterexample_and_all_permutations(self):
        from packages.rep004 import concept_matches, PERMS, relabel
        # This guarded example used to match guard=2 but fail on guard=3.
        snap=learn(64)
        guarded=((0,1,2,0),)
        expected=concept_matches(snap,guarded)
        self.assertGreater(expected,0)
        self.assertEqual(expected,concept_matches(snap,((0,1,3,0),)))
        for edge in EDGES:
            candidate=(edge,)
            original=concept_matches(snap,candidate)
            for perm in PERMS:
                self.assertEqual(original,concept_matches(snap,relabel(candidate,perm)),
                                 (edge,perm))
                for state in range(16):
                    mapped=sum(((state>>j)&1)<<perm[j] for j in range(4))
                    for source in range(4):
                        action=('pulse',source,None)
                        pa=('pulse',perm[source],None)
                        result=step(state,action,candidate)
                        presult=step(mapped,pa,relabel(candidate,perm))
                        self.assertEqual(sum(((result>>j)&1)<<perm[j] for j in range(4)),presult)
        # Full pre-state XOR semantics, all 16 states/actions, across 24 renamings.
        from packages.rep004 import _composition_equivalent, motif
        two=(((0,1,-1,-1),(1,2,3,1)),((0,2,3,0),(0,2,3,1)))
        for edges in two:
            for perm in PERMS:
                renamed=relabel(edges,perm)
                self.assertTrue(_composition_equivalent(motif(renamed),renamed))

    def test_static_macro_independence_from_learned_library(self):
        from packages.rep004 import weights_for
        models=list(catalog())[:80]
        z=learn(0);full=learn(64)
        def measured(s):
            meter={'body_invocations':0}
            return weights_for(models,s,'STATIC-MACRO',meter)
        a,b=measured(z),measured(full)
        self.assertEqual(a,b)
        self.assertTrue(any(v>1 for v in a))
        self.assertEqual(weights_for(models,z,'FA',None),[1.0]*len(models))

    def test_optional_guard_is_not_an_arbitrary_fixed_index(self):
        from packages.rep004 import execute_body
        edge=(3,2,-1,-1)
        ast=concept_ast(edge)
        body={'ast':ast,'body_hash':digest(ast),'support':3,'positive':['fixture'],
              'negative':[],'status':'candidate'}
        binding={'source':3,'target':2,'guard':None}
        for state in range(16):
            for action in (('pulse',i,None) for i in range(4)):
                self.assertEqual(execute_body(body,state,action,binding),step(state,action,(edge,)))
        with self.assertRaises(ValueError):
            execute_body(body,0,('pulse',3,None),{'source':3,'target':2,'guard':3})

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
        self.assertIsInstance(fixture['paid_conditioning'],int)
        self.assertGreaterEqual(fixture['paid_conditioning'],0)
        self.assertLessEqual(fixture['paid_conditioning'],7)
        self.assertGreater(fixture['paths_checked'],0)

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
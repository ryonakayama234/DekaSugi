"""Artificial-only. No formal seed, HOLDOUT or legacy CAL imports."""
import unittest
from fractions import Fraction
from packages.world_lean.core import (State, Session, Fault, TOKENS, SYMS, OPS,
    MAX_STEPS, step, execute, digest, canonical)
from packages.world_lean.learner import Learner, infer, demo_candidates, _snap, _from_record
from packages.world_lean.analysis import aulc, binomial_one_sided, paired_summary, B
from world_lean_evaluator.fixture import (Recipe, train_recipes, FIXTURE_STREAMS,
    examples, target, body, random_train_blocks, audit_ambiguity)
from world_lean_evaluator.gate import negative_boundary_fixture,reachability_fixture

class WorldFixture(unittest.TestCase):
    def setUp(self):self.s=State(('A','B','C','D'),2)
    def test_11_types_14_tokens(self):
        self.assertEqual(len(OPS),11);self.assertEqual(len(TOKENS),14)
    def test_move_end_noop_clear(self):
        t=State(('A','B'),0,(0,0))
        self.assertEqual(step(t,('MOVE_LEFT',None)),State(('A','B'),0))
        self.assertEqual(step(State(('A',),1),('MOVE_RIGHT',None)),State(('A',),1))
    def test_anchor_extend_copy_clear_paste(self):
        x=State(('A','B','C','D'),1)
        for a in ('SET_ANCHOR','EXTEND_RIGHT','EXTEND_RIGHT','COPY'):
            x=step(x,(a,None))
        self.assertEqual(x.selection,(1,3));self.assertEqual(x.clipboard,('B','C'))
        x=step(x,('CLEAR_SELECTION',None))
        x=step(x,('PASTE',None))
        self.assertEqual(x,State(('A','B','C','B','C','D'),5,None,('B','C')))
    def test_copy_empty_preserves_clipboard(self):
        x=State(('A','B'),1,(1,1),('D',))
        self.assertEqual(step(x,('COPY',None)),x)
    def test_delete_nonempty_selection_both_directions(self):
        x=State(('A','B','C'),2,(0,2))
        self.assertEqual(step(x,('DELETE_BACK',None)),State(('C',),0))
        self.assertEqual(step(x,('DELETE_RIGHT',None)),State(('C',),0))
    def test_delete_empty_selection_and_edges(self):
        x=State(('A',),0,(0,0))
        self.assertEqual(step(x,('DELETE_BACK',None)),State(('A',),0))
        self.assertEqual(step(State(('A',),1),('DELETE_RIGHT',None)),State(('A',),1))
    def test_selection_replace_and_full_overflow_atomic(self):
        x=State(tuple('A'*16),1,(0,1),('B','C'))
        self.assertEqual(step(x,('PASTE',None)),x)
        self.assertEqual(step(State(tuple('A'*16),1),('INSERT','B')),
                         State(tuple('A'*16),1))
        z=State(('A','B','C'),2,(1,2))
        self.assertEqual(step(z,('INSERT','D')),State(('A','D','C'),2))
    def test_invalid_token_fault(self):
        with self.assertRaises(Fault):step(self.s,('NEW_OP',None))
        with self.assertRaises(Fault):step(self.s,('INSERT','E'))
        with self.assertRaises(Fault):State(('A',),1,(1,0))
    def test_finish_4_fields_and_12_calls_no_early_end(self):
        target_state=State(('A','B'),1,None,('D',))
        s=Session(State(('A','B'),1,None,('C',)))
        s.apply('finish',target_state)
        self.assertFalse(s.result)
        x=Session(State(('A','B'),1))
        for _ in range(11):x.apply(('MOVE_LEFT',None),State(('A','B'),0))
        self.assertFalse(x.finished)
        x.apply(('MOVE_LEFT',None),State(('A','B'),0))
        self.assertTrue(x.finished);self.assertTrue(x.result)
        with self.assertRaises(Fault):x.apply('finish',State(('A','B'),0))
    def test_ast_bound_fault_and_call_off(self):
        a=['SEQ', *[['OP','MOVE_LEFT'] for _ in range(13)]]
        with self.assertRaises(Fault):execute(a,self.s)
        library={'0000000000000000':['OP','MOVE_LEFT']}
        self.assertEqual(execute(['CALL','0000000000000000'],self.s,library)[2],True)
        with self.assertRaises(Fault):execute(['CALL','0000000000000000'],self.s,library,allow_calls=False)
        deeply={'0000000000000000':['SEQ',*[['OP','MOVE_LEFT'] for _ in range(30)]]}
        with self.assertRaises(Fault):execute(['CALL','0000000000000000'],self.s,deeply)
    def test_finish_not_primitive(self):
        self.assertNotIn('finish',OPS)
    def test_generator_train_only_nonunique_rejection(self):
        self.assertEqual(len(train_recipes()),24)
        r=train_recipes()[0];e=examples(r,FIXTURE_STREAMS[0]);self.assertEqual(len(e),8)
        self.assertEqual(len({digest(x.record()) for x,y in e}),8)
        self.assertEqual([target(r,s)==goal for s,goal in e],[True]*8)
        from world_lean_evaluator.fixture import condition
        self.assertEqual([condition(r.condition,s) for s,_ in e],
                         [True]*3+[False]*3+[True,False])
    def test_no_formal_rng_api(self):
        with self.assertRaises(ValueError):examples(Recipe(0,0,1),'formal-seed')
        with self.assertRaises(ValueError):random_train_blocks('holdout',512)

class LearnerFixture(unittest.TestCase):
    def test_empty_snapshot_and_shared_off(self):
        learner=Learner();snap=learner.snapshot()
        self.assertEqual(_snap(snap)['library'],{})
        self.assertEqual(_snap(snap)['events'],0)
        self.assertEqual(snap,learner.snapshot())
    def test_training_child_checkpoints_digest_replay(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from shutil import copyfile
        from world_lean_evaluator.gate import child_request
        import base64, hashlib
        blocks=random_train_blocks(FIXTURE_STREAMS[0],8)
        src=Path(__file__).resolve().parents[1]/'packages/world_lean'
        with TemporaryDirectory() as temp:
            root=Path(temp);public=root/'world_lean';public.mkdir()
            for name in ('__init__.py','core.py','learner.py','child_entry.py','protocol.py'):
                copyfile(src/name,public/name)
            request={'mode':'train','blocks':list(blocks)}
            x=child_request(root,request)
            y=child_request(root,request)
            self.assertTrue(x['ok']);self.assertEqual(x,y)
            output=x['data']
            self.assertEqual(output['events'],64)
            self.assertEqual(set(output['checkpoints_b64']),{'0'})
            self.assertEqual(output['snapshot_sha256'],hashlib.sha256(
                base64.b64decode(output['snapshot_b64'])).hexdigest())

    def test_train_64_update_order_and_off(self):
        learner=Learner()
        blocks=random_train_blocks(FIXTURE_STREAMS[0],8)
        for ep in blocks:learner.add_block(ep)
        self.assertEqual(learner.events,64)
        self.assertEqual(learner.updates,1)
        self.assertLessEqual(len(learner.library),64)
        self.assertLessEqual(learner.update_receipts[0]['constructed'],1024)
        self.assertLessEqual(learner.update_receipts[0]['verified'],128)
        snap=learner.snapshot()
        e=examples(Recipe(1,3,1),FIXTURE_STREAMS[0])
        full=infer(snap,'FULL',e[:6],e[6][0])
        off=infer(snap,'OFF',e[:6],e[6][0])
        static=infer(snap,'STATIC-RANK',e[:6],e[6][0])
        lookup=infer(snap,'LOOKUP',e[:6],e[6][0])
        self.assertEqual(snap,learner.snapshot())
        for ans in (full,off,static,lookup):
            self.assertIn(ans['status'],('SUBMITTED','ABSTAIN','FAULT'))
            self.assertLessEqual(ans['checked'],128)
        self.assertFalse(off['used_ast'])
        self.assertFalse(static['used_ast'])
    def test_legacy_four_demo_payload_rejected(self):
        block=random_train_blocks(FIXTURE_STREAMS[0],1)[0]
        self.assertEqual(len(block['demos']),6)
        block['demos']=block['demos'][:4]
        with self.assertRaises(Fault):_from_record(block)

    def test_inference_rejects_legacy_four_demo_input(self):
        demo=examples(train_recipes()[0],FIXTURE_STREAMS[0])
        with self.assertRaises(Fault):demo_candidates(demo[:4])

    def test_source_cannot_hide_invalid_transition(self):
        obj=random_train_blocks(FIXTURE_STREAMS[0],1)[0]
        obj['observations'][1]['cursor']=99
        with self.assertRaises(Fault):Learner().add_block(obj)
    def test_6_demo_static_reach(self):
        result=reachability_fixture()
        self.assertEqual(set(result),{'local_insert','local_delete','copy','conditional'})
    def test_ambiguity_train_only(self):
        a=audit_ambiguity(FIXTURE_STREAMS[0])
        self.assertEqual(a['recipe_scope'],'TRAIN_ONLY')
        self.assertEqual(a['queries'],48)

class BoundaryFixture(unittest.TestCase):
    def test_import_root_separation(self):
        r=negative_boundary_fixture()
        self.assertTrue(r['extra_target_seed_keys_rejected'])
        self.assertTrue(r['private_root_absent'])
        self.assertFalse(r['learner_imports_evaluator'])

class ProtocolGateFixture(unittest.TestCase):
    def test_formal_call_fail_closed(self):
        from world_lean_evaluator.protocol import formal_run, formal_generation, OwnerEvaluationAuthorizationRequired
        for fn in (formal_run,formal_generation):
            with self.assertRaises(OwnerEvaluationAuthorizationRequired):fn()

class AnalyzerFixture(unittest.TestCase):
    def test_exact_area_and_sign(self):
        self.assertEqual(aulc((48,48,48,48,48)),Fraction(1))
        self.assertEqual(aulc((0,0,0,0,0)),Fraction(0))
        self.assertEqual(aulc((0,48,48,48,48)),Fraction(15,16))
        self.assertEqual(binomial_one_sided(12),Fraction(2517,65536))
    def test_paired_shape(self):
        x=tuple({'FULL':(48,)*5,'OFF':(0,)*5,
                 'STATIC-RANK':(0,)*5,'LOOKUP':(0,)*5} for _ in range(16))
        y=paired_summary(x,123)
        self.assertTrue(y['main_effect_gate'])
        self.assertEqual(y['paired']['OFF']['wins'],16)

if __name__=='__main__':unittest.main()

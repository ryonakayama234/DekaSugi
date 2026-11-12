"""Artificial fixtures only: no official generation or activation."""
import ast
import base64
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from packages.world_lean.core import canonical, digest
from packages.world_lean import protocol as public
from world_lean_evaluator import protocol as evaluator
from world_lean_evaluator import formal as f
from world_lean_evaluator.fixture import FIXTURE_STREAMS, audit_ambiguity

class FormalRepair(unittest.TestCase):
    def root(self,temporary):return Path(temporary)/'run'
    def test_numeric_contract_reexports_all_original_constants(self):
        names=('WORLD','N_REPLICATES','B','TRAIN_BODY_PAIRS','HELD_OUT_PAIR_PLAN','DEMOS_PER_LAW',
               'QUERIES_PER_LAW','EXTRA_DIAG_QUERIES_PER_LAW','DRAW_LIMIT','MAX_WALL_SECONDS','MAX_CPU_SECONDS','MAX_SAVE_BYTES')
        for name in names:self.assertEqual(getattr(public,name),getattr(evaluator,name))
        self.assertEqual(public.DEMOS_PER_LAW,6)
        self.assertEqual(public.B,(0,512,1024,2048,4096))
        self.assertEqual(public.N_REPLICATES,16)
    def test_two_and_only_two_design_corrections(self):
        before=(f.REPO/'docs/research/WORLD-LEAN-EXPERIMENT-DESIGN-20261112-02.md').read_bytes()
        after=(f.REPO/f.DESIGN).read_bytes()
        self.assertEqual(after,before.replace('6×12=48'.encode(),'6×12=72'.encode()).replace('TRAIN更新の4検証例'.encode(),'TRAIN更新の6検証例'.encode()))
    def test_six_demo_ambiguity_exact_reproduction(self):
        result=[audit_ambiguity(s) for s in FIXTURE_STREAMS]
        self.assertEqual([r['ambiguous_queries'] for r in result],[0,2,2,0])
        self.assertEqual(sum(r['queries'] for r in result),192)
    def test_without_explicit_resume_no_official_seed(self):
        with TemporaryDirectory() as tmp:
            root=self.root(tmp);f.freeze_manifest(root)
            with patch.object(f.os,'urandom',side_effect=AssertionError('entropy forbidden')):
                with self.assertRaises(evaluator.OwnerEvaluationAuthorizationRequired):f.generate(root)
            self.assertFalse((root/'generation-started.json').exists())
            self.assertFalse((root/'private').exists())
    def test_synthetic_profile_cannot_be_passed_as_official(self):
        with TemporaryDirectory() as tmp:
            root=self.root(tmp);f.freeze_manifest(root,dry_run=True)
            with self.assertRaises(f.IntegrityError):f.generate(root,dry_run=False)
    def test_manifest_tamper_rejected_before_seed(self):
        with TemporaryDirectory() as tmp:
            root=self.root(tmp);f.freeze_manifest(root,dry_run=True)
            value=f.load(root/'manifest.json');value['demos_per_law']=4
            (root/'manifest.json').write_bytes(canonical(value))
            (root/'manifest.sha256').write_text(digest(value)+'\n')
            with self.assertRaises(f.IntegrityError):f.generate(root,dry_run=True)
            self.assertFalse((root/'private').exists())
    def test_manifest_lock_commitment_disagreement_rejected(self):
        with TemporaryDirectory() as tmp:
            root=self.root(tmp);f.freeze_manifest(root,dry_run=True)
            bad=f.load(f.REPO/f.LOCK);bad['source_digest']='0'*64
            original=f.load
            def loads(path):return bad if Path(path)==f.REPO/f.LOCK else original(path)
            with patch.object(f,'load',side_effect=loads):
                with self.assertRaises(f.IntegrityError):f.generate(root,dry_run=True)
            self.assertFalse((root/'private').exists())
    def test_source_byte_tamper_rejected(self):
        lock=f.load(f.REPO/f.LOCK);lock['file_sha256']=dict(lock['file_sha256'])
        first=next(iter(lock['file_sha256']));lock['file_sha256'][first]='0'*64
        with patch.object(f,'load',return_value=lock):
            with self.assertRaises(f.IntegrityError):f.verify_lock()
    def test_no_evaluation_without_all_snapshot_barrier(self):
        with TemporaryDirectory() as tmp:
            root=self.root(tmp);value=f.freeze_manifest(root,dry_run=True)
            with self.assertRaises(FileNotFoundError):
                f.evaluate_all(root,value,[],None,None,{'manifest':digest(value),'snapshot_sha256':{}})
    def test_generated_data_tamper_fail_closed(self):
        with TemporaryDirectory() as tmp:
            root=self.root(tmp);f.freeze_manifest(root,dry_run=True);f.generate(root,dry_run=True)
            (root/'private/replicate-0.json').write_bytes(b'{}\n')
            with self.assertRaises(f.IntegrityError):f.run(root,dry_run=True)
            self.assertFalse((root/'snapshots-fixed.json').exists())
    def test_generation_is_once_only(self):
        with TemporaryDirectory() as tmp:
            root=self.root(tmp);f.freeze_manifest(root,dry_run=True);f.generate(root,dry_run=True)
            with self.assertRaises(FileExistsError):f.generate(root,dry_run=True)
    def test_missing_artifact_is_not_success(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):f.verify_artifacts(Path(tmp),{'missing.json':'0'*64})
    def test_resource_stop_is_not_completed(self):
        with TemporaryDirectory() as tmp:
            root=self.root(tmp);value=f.freeze_manifest(root,dry_run=True)
            value['wall_cap']=0
            with self.assertRaises(f.ResourceStop):f.Budget(root,value).check()
    def test_private_root_unavailable_and_forbidden_keys_rejected(self):
        with TemporaryDirectory() as tmp:
            private=Path(tmp)/'private';private.mkdir();(private/'master.bin').write_bytes(b'ARTIFICIAL-CANARY')
            with f.public_root() as root:
                value={'wall_cap':100,'cpu_cap':100,'save_cap':10000000}
                budget=f.Budget(Path(tmp),value)
                probe,_=f.child(root,{'mode':'boundary_probe'},budget)
                self.assertFalse(probe['evaluator_importable'])
                self.assertFalse(probe['private_relative_readable'])
                self.assertNotIn(str(private),probe['sys_path'])
                with self.assertRaises(f.IntegrityError):
                    f.child(root,{'mode':'train','blocks':[],'holdout':str(private)},budget)
                with self.assertRaises(f.IntegrityError):
                    f.child(root,{'mode':'infer','snapshot_b64':'','arm':'FULL','demos':[],
                                  'query':{},'target':'ARTIFICIAL-CANARY'},budget)
    def test_exact_AND_analyzer_on_invented_counts_only(self):
        from packages.world_lean.analysis import scientific_decision
        seeds=tuple({'FULL':(48,)*5,'OFF':(0,)*5,'STATIC-RANK':(0,)*5,'LOOKUP':(0,)*5} for _ in range(16))
        groups={k:(8,10) for k in ('true','false','with_copy','without_copy','p0','p1','p2','p3')}
        result=scientific_decision(seeds,groups=groups,ambiguous=(0,768),usage_seed_count=12,bootstrap_seed=123)
        self.assertEqual(result['status'],'LEAN_B_EFFICIENCY_CANDIDATE')
        self.assertTrue(result['all_AND_passed'])
        with self.assertRaises(ValueError):
            scientific_decision(seeds[:-1],groups=groups,ambiguous=(0,768),usage_seed_count=12,bootstrap_seed=123)
        result=scientific_decision(seeds,groups=groups,ambiguous=(77,768),usage_seed_count=11,bootstrap_seed=123)
        self.assertFalse(result['all_AND_passed'])
        self.assertIn('SPEC_INSUFFICIENT',result['stops'])
        self.assertIn('ACQUIRED_USAGE_INSUFFICIENT',result['stops'])
    def test_artificial_stream_branch_balance_duplicate_rejection(self):
        recipe=f.train_recipes()[0];master=b'artificial-sampler-unit-fixture'
        self.assertEqual([f.Stream(master,0,'fixture',0,0).uint(37) for _ in range(3)],
                         [f.Stream(master,0,'fixture',0,0).uint(37) for _ in range(3)])
        seen=set();states=[]
        for i,wants in enumerate([True]*3+[False]*3+[True,False]):
            x,y=f.draw(master,0,'ARTIFICIAL_TRAIN_ONLY',0,i,recipe,wants,seen)
            self.assertEqual(f.condition(recipe.condition,x),wants)
            self.assertEqual(f.target(recipe,x),y);states.append(digest(x.record()))
        self.assertEqual(len(set(states)),8)
        with patch.object(f,'DRAW_LIMIT',0):
            with self.assertRaises(f.IntegrityError):f.draw(master,0,'ARTIFICIAL',0,0,recipe,True,set())
    def test_roundtrip_full_stage_order_and_deterministic_replay(self):
        with TemporaryDirectory() as tmp:
            result=[];deterministic=[]
            for name in ('a','b'):
                root=Path(tmp)/name;calls=[];original=f.child
                def observed(child_root,message,budget):
                    if message['mode']=='infer':self.assertTrue((root/'snapshots-fixed.json').exists())
                    else:self.assertFalse((root/'snapshots-fixed.json').exists())
                    calls.append(message['mode'])
                    return original(child_root,message,budget)
                # Dry-run MUST never call official entropy or official realization.
                with patch.object(f,'child',side_effect=observed),patch.object(f,'realization',side_effect=AssertionError('official recipe generation forbidden')),patch.object(f.os,'urandom',side_effect=AssertionError('official entropy forbidden')):
                    result.append(f.dry_run(root))
                self.assertEqual(calls[:3],['train']*3)
                self.assertEqual(calls[3:],['infer']*24)
                self.assertEqual(result[-1]['query_rows'],24)
                self.assertEqual(result[-1]['scientific_decision'],'NOT_RUN')
                self.assertEqual((root/'private/master.bin').read_bytes(),f.SYNTHETIC_SEED)
                receipt=f.load(root/'snapshots-fixed.json')
                for b in (0,64):
                    self.assertEqual(receipt['snapshot_sha256'][f'snapshots/0/FULL/{b}.json'],receipt['snapshot_sha256'][f'snapshots/0/OFF/{b}.json'])
                    for arm in ('STATIC-RANK','LOOKUP'):
                        self.assertEqual(f.load(root/f'snapshots/0/{arm}/{b}.json')['library'],{})
                deterministic.append({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in root.rglob('*') if p.is_file() and 'metadata' not in p.name and p.name!='budget-origin.json'})
                with self.assertRaises(FileExistsError):f.run(root,dry_run=True)
            self.assertEqual(result[0],result[1]);self.assertEqual(deterministic[0],deterministic[1])

if __name__=='__main__':unittest.main()

"""Additional pre-authorization synthetic correctness/guard tests. No CAL run."""
import hashlib
import math
import pathlib
import tempfile
import unittest
from fractions import Fraction

from world_cal.gtheta import aggregate_law
from world_cal.inference import bootstrap_vectors, bootstrap_vectors_cached
from world_cal.id_only import (features, parent_fold_ids,
    cross_validated_macro_auc,IDOnlyUnknown)
from world_cal.k0_b import K0Hypothesis,solve_k0b_pair,scan_k0b_pairs
from world_cal.k0_c import exhaustive_k0c_curve
from world_cal.power_engine import run_one_repetition
from world_cal.power_route import PowerUnknown
from world_cal.prf import uniform53
from world_cal.role_boundary import verify_role_stage, verify_role_code_bundle, SandboxUnknown
from world_cal.sampford import waterfill
from world_cal.sampford_grouped import grouped_inclusions,draw_grouped
from world_cal.world import State,World


class RulingGoldens(unittest.TestCase):
    def test_fourteen_tokens_not_horizon(self):
        w=World(tuple("ABCD"),horizon=24)
        self.assertEqual(len(w.legal_actions()),14)
        self.assertEqual(sum(x[0]=="INSERT" for x in w.legal_actions()),4)

    def test_binary64_upper_and_lower(self):
        self.assertEqual(uniform53(bytes.fromhex("ff"*32)),math.nextafter(1.0,0.0))
        self.assertGreater(uniform53(bytes(32)),0)

    def test_family_contrast_uses_two_b_endpoints(self):
        def gates(v1,v2):
            return tuple(tuple((val,)*4 for _ in range(9))
                         for val in (v1,v2))
        rows={"FULL":gates(1,0),"H+":gates(1,1)}
        rows.update({a:gates(0,0) for a in
                     ("OFF","PRED-ONLY","REC","RANK-ONLY","FIXED-IF","LOOKUP")})
        scores=aggregate_law(rows)
        self.assertEqual(scores["contrast"],-.5)
        self.assertEqual(scores["contrast_g1"],0)
        self.assertEqual(scores["contrast_g2"],-1)

    def test_sampford_certainty_transition(self):
        q=(1/160,)*72+(1/480,)*264
        for n in (2,4,159,160,161,335,336):
            p=waterfill(q,n)
            first,joint=grouped_inclusions(p)
            self.assertAlmostEqual(math.fsum(first),n,places=9)
            self.assertTrue(all(joint[0][i]>0 for i in range(1,336)))
            self.assertLess(max(abs(math.fsum(row)-(n-1)*first[i])
                                for i,row in enumerate(joint)),1e-10)
            if n>=160:self.assertEqual(sum(x==1 for x in first),72 if n<336 else 336)
            if n==2:
                sample=draw_grouped(first,iter([.2]*337))
                self.assertEqual(len(sample),2)


class GuardGoldens(unittest.TestCase):
    def test_bootstrap_cached_bitwise_equivalent(self):
        sample=[0,1,2,3]
        q=[.25]*4
        pi=[.5]*4
        parents=["p0","p0","p1","p2"]
        outcomes={i:tuple((i+1)*(j+1)/77 for j in range(9))
                  for i in sample}
        draws=[["p0","p1","p2"],["p1","p1","p0"],["p2","p0","p0"]]
        slow=bootstrap_vectors(sample,q,pi,outcomes,parents,draws)
        fast=bootstrap_vectors_cached(sample,q,pi,outcomes,parents,draws)
        self.assertEqual(slow,fast)

    def test_id_only_folds_and_logistic(self):
        labels=[i%4 for i in range(20)]
        parents=["P%d"%(i//4) for i in range(20)]
        tags=["public-%d-%02d"%(i%4,i) for i in range(20)]
        self.assertEqual(set(parent_fold_ids(parents)),set(range(5)))
        auc=cross_validated_macro_auc(tags,labels,parents)
        self.assertTrue(0<=auc<=1)
        with self.assertRaises(IDOnlyUnknown):
            cross_validated_macro_auc(tags,[0]*20,parents)

    def test_k0b_two_laws_same_public_goal_tiny_fixture(self):
        initial=State(())
        left=K0Hypothesis("L",(initial,),lambda t,b:b==("A",),"same-demo")
        right=K0Hypothesis("R",(initial,),lambda t,b:b==("A",),"same-demo")
        out=solve_k0b_pair(left,right,mode="EVAL",horizon=1,cap=100)
        self.assertEqual(out["status"],"PASS")
        self.assertEqual(scan_k0b_pairs([],complete_support=False)["status"],"UNKNOWN")

    def test_unknown_oracle_and_denied_simulation(self):
        self.assertEqual(exhaustive_k0c_curve(cells=[],space_candidates=[],
               space_complete=False,support_complete=False,b_final=4096,
               control_curves={})["status"],"UNKNOWN")
        with self.assertRaises(PowerUnknown):
            run_one_repetition(q=[.5,.5],parent_ids=["A","B"],n=2,
                   scenario_id="GTHETA-BASE-01",repetition=0,key=bytes(32))

    def test_learner_cannot_mount_abstract_oracle_code_or_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            (root/"entry.py").write_text("print('safe')",encoding="utf-8")
            self.assertEqual(verify_role_code_bundle("LEARNER_ARMS",root,"entry.py"),root)
            oracle=root/"world_cal";oracle.mkdir()
            (oracle/"abstract_support.py").write_text("pass",encoding="utf-8")
            with self.assertRaises(SandboxUnknown):
                verify_role_code_bundle("LEARNER_ARMS",root,"entry.py")
            (oracle/"abstract_support.py").unlink()
            (root/"private_truth.json").write_text("{}")
            with self.assertRaises(SandboxUnknown):
                verify_role_code_bundle("LEARNER_ARMS",root,"entry.py")

    def test_os_staging_rejects_private_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            (root/"public").mkdir()
            path=root/"public"/"trace"
            path.write_bytes(b"public fixture only")
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertTrue(verify_role_stage("LEARNER_ARMS",root,
                                              {"public/trace":digest}))
            (root/"private").mkdir()
            (root/"private"/"verifier_truth").write_text("secret marker")
            with self.assertRaises(SandboxUnknown):
                verify_role_stage("LEARNER_ARMS",root,{"public/trace":digest})

if __name__=="__main__":unittest.main()

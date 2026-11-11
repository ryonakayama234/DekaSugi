"""Synthetic golden, negative privilege and reproducibility tests: never CAL or power simulation."""
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys
import unittest
from fractions import Fraction

from world_cal.world import State, World, rename
from world_cal.generator_contract import load_verified, abstract_quota_counts, SourceMismatch
from world_cal.space import Node, enumerate_unique, ASTFault, validate
from world_cal.prf import hmac_sha256, uniform53, box_muller, phi, encode_parts
from world_cal.gtheta import load_model, marginal_table, trapezoid, binary_outcome, ar1_path
from world_cal.sampford import exact_subset_law, inclusion, waterfill, SamplingUnknown
from world_cal.inference import ht,syg,parent_bootstrap_ht,studentized_max_t,InferenceUnknown
from world_cal.power_route import cp_lower,cost,route_from_completed_scan,PowerUnknown
from world_cal.k0_open_loop import trace_known_negative
from world_cal.k0_oracle import nearest_rank90
from world_cal.ledger import AccessMatrix,AccessDenied,check_role_read,RunRecord
from world_cal.receipt import validate,ReceiptInvalid

ROOT=pathlib.Path(__file__).resolve().parents[1]

class WorldGoldens(unittest.TestCase):
    def test_known_absorbing(self):
        w=World(tuple("ABCD"),lambda b: "".join(b)=="ABABA")
        self.assertEqual(w.reset("ABAB"),{"buffer":tuple("ABAB"),"cursor":0,
                                         "selection":None,"clipboard":(),"last_event":None})
        for _ in range(4):w.step("MOVE_RIGHT")
        _,done,success,event=w.step(("INSERT","A"))
        self.assertTrue(done and success)
        self.assertEqual((w.calls,event,"".join(w.state.buffer)),(5,"VALID","ABABA"))
        w.step(("INSERT","B"))
        self.assertEqual(w.calls,5)

    def test_fault_no_op_capacity(self):
        w=World(tuple("ABCD"))
        w.reset("A"*16)
        self.assertEqual(w.step(("INSERT","A"))[-1],"NO_OP_PRECONDITION")
        self.assertEqual(w.step("DELETE_BACK")[-1],"NO_OP_PRECONDITION")
        self.assertEqual(w.step(("INSERT","Z"))[-1],"ACTION_FAULT")
        self.assertEqual(w.calls,3)
        self.assertEqual(w.state.buffer,tuple("A"*16))

    def test_selection_capacity(self):
        w=World(tuple("ABCD"))
        w.reset("A"*16)
        w.step("SET_ANCHOR")
        w.step("EXTEND_RIGHT")
        w.step(("INSERT","B"))
        self.assertEqual(len(w.state.buffer),16)
        self.assertEqual(w.state.buffer[0],"B")
        self.assertIsNone(w.state.selection)
        self.assertEqual(w.state.cursor,1)

    def test_24_renames(self):
        a=tuple("ABCD")
        for perm in itertools.permutations(a):
            mapping=dict(zip(a,perm))
            w1=World(a);w2=World(perm)
            w1.reset("ABCD");w2.reset(tuple(mapping[c] for c in "ABCD"))
            for op in ("MOVE_RIGHT","SET_ANCHOR","EXTEND_RIGHT","COPY",("INSERT","D"),"PASTE"):
                o2=(op[0],mapping[op[1]]) if isinstance(op,tuple) else op
                w1.step(op);w2.step(o2)
                self.assertEqual(rename(w1.state,mapping),w2.state)

    def test_negative_k0_control(self):
        self.assertEqual(trace_known_negative(),((True,6,"ABABA"),(True,9,"ADADC")))

class SourceGoldens(unittest.TestCase):
    def test_exact_source_and_counts(self):
        base=ROOT/"docs"/"research"
        m,d=load_verified(base/"WORLD-CAL-GENERATOR-MANIFEST-20261111-01.json",
                          base/"WORLD-CAL-GENERATOR-DISTRIBUTION-20261111-01.json")
        self.assertEqual(abstract_quota_counts(m),{"TRAIN":24,"CAL":24,"HOLDOUT":336})
        self.assertEqual(len(d["rows"]),384)
        self.assertEqual(m["parent_cluster_split"]["H_laws_digest"],None)

    def test_modified_source_denied(self):
        from tempfile import TemporaryDirectory
        base=ROOT/"docs"/"research"
        path=base/"WORLD-CAL-GENERATOR-MANIFEST-20261111-01.json"
        with TemporaryDirectory() as tmp:
            bad=pathlib.Path(tmp)/"mutated.json"
            bad.write_bytes(path.read_bytes()+b" ")
            with self.assertRaises(SourceMismatch):
                load_verified(bad,base/"WORLD-CAL-GENERATOR-DISTRIBUTION-20261111-01.json")

class NumericGoldens(unittest.TestCase):
    def test_hmac_rfc4231(self):
        # RFC 4231 test case 1, a public test key (not an escrow seed).
        actual=hmac_sha256(bytes.fromhex("0b"*20),b"Hi There")
        self.assertEqual(actual.hex(),"b0344c61d8db38535ca8afceaf0bf12b"
                         "881dc200c9833da726e9376c2e32cff7")

    def test_prf_normal(self):
        self.assertTrue(0<uniform53(bytes(32))<1)
        self.assertTrue(0<uniform53(bytes.fromhex("ff"*32))<1)
        z0,z1=box_muller(.5,.5)
        self.assertLessEqual(abs(z0+math.sqrt(2*math.log(2))),1e-10)
        self.assertLessEqual(abs(z1),1e-10)
        self.assertEqual(phi(0),.5)
        self.assertNotEqual(encode_parts("12",3),encode_parts("1",23))

    def test_gtheta_marginal(self):
        model=load_model()
        table=marginal_table(model)
        self.assertEqual(len(table),8)
        for gate,endpoint in enumerate((.95,.85)):
            self.assertAlmostEqual(table["FULL"][gate][-1],endpoint,places=12)
        for control in ("H+","FIXED-IF","PRED-ONLY","REC","RANK-ONLY","LOOKUP","OFF"):
            diff=sum(trapezoid(table["FULL"][gate])-trapezoid(table[control][gate])
                     for gate in range(2))/2
            self.assertLessEqual(abs(diff-.20),1e-10)
        for scenario in model["binary_joint_generator"]["scenarios"]:
            self.assertEqual(binary_outcome(scenario,{x:0 for x in
                ("cluster","law","gate","arm","checkpoint","episode")},.95),1)
            self.assertEqual(ar1_path([0]*9,scenario["checkpoint_ar1"]),tuple([0.0]*9))

    def test_exact_sampford_equal(self):
        q=[Fraction(1,3)]*3
        pi=[Fraction(2,3)]*3
        law=exact_subset_law(pi)
        first,pairs=inclusion(law,3)
        self.assertEqual(first,tuple(pi))
        self.assertEqual(pairs[0][1],Fraction(1,3))
        self.assertEqual(sum(law.values()),1)
        self.assertEqual(waterfill(q,3),tuple([1.0]*3))
        self.assertEqual(exact_subset_law([Fraction(1)]*3),{(0,1,2):Fraction(1)})
        self.assertAlmostEqual(ht([0,1],q,pi,[1,1,1]),1)
        with self.assertRaises(SamplingUnknown): exact_subset_law([Fraction(1,2)]*4,max_units=3)

    def test_sampford_unequal(self):
        pi=[Fraction(4,5),Fraction(7,10),Fraction(1,2)]
        law=exact_subset_law(pi)
        first,pair=inclusion(law,3)
        self.assertEqual(first,tuple(pi))
        self.assertTrue(all(x>=0 for x in pair[0]))

    def test_bootstrap_and_max_t(self):
        sample=[0,1];q=[.5,.5];pi=[1,1];v=[.25,.75];parents=["A","B"]
        self.assertAlmostEqual(parent_bootstrap_ht(sample,q,pi,v,parents,["A","A"]),.25)
        self.assertAlmostEqual(parent_bootstrap_ht(sample,q,pi,v,parents,["A","B"]),.5)
        with self.assertRaises(InferenceUnknown):
            studentized_max_t([0]*7,[[0]*7]*3)
        self.assertAlmostEqual(syg(sample,q,pi,[[0,1],[1,0]],v),0)

    def test_curve_cp_and_calls(self):
        from world_cal.gtheta import trapezoid
        self.assertAlmostEqual(trapezoid([i/8 for i in range(9)]),.5)
        self.assertAlmostEqual(trapezoid([.5]*9),.5)
        self.assertLessEqual(abs(cp_lower(10000)-.01**(1/10000)),1e-10)
        self.assertEqual(cost(336),4_944_976)
        self.assertEqual(route_from_completed_scan({},336)["route"],"STOP_UNKNOWN")
        self.assertEqual(nearest_rank90(list(range(1,11))),9)

class AccessGoldens(unittest.TestCase):
    def test_access_and_negative(self):
        acl=AccessMatrix()
        self.assertTrue(acl.check("FULL","ATOM","NONE","TRAIN","PUB","READ"))
        for src in ("SEC","CAL_ORACLE","CAL_DESIGN_META"):
            with self.assertRaises(AccessDenied):
                acl.check("FULL","ATOM","NONE","TRAIN",src,"READ")
        with self.assertRaises(AccessDenied):
            acl.check("FULL","ATOM","NONE","CAL","PUB","READ")
        with self.assertRaises(AccessDenied):
            check_role_read("LEARNER_ARMS","private/verifier_truth")
        with self.assertRaises(AccessDenied):
            check_role_read("BLIND_DESIGN_CALCULATOR","design/split_metadata:N_eligible,q,parent_cluster")
        with self.assertRaises(ValueError):
            RunRecord("STOP_INVALID","POSITIVE")

    def test_receipt_default_deny(self):
        payload=dict(N_eligible=336,n_required=None,route="STOP_UNKNOWN",
                     power_lower_bound=None,cost_cap_check=False,
                     algorithm_digest="sha256:"+"a"*64,split_digest="sha256:"+"b"*64)
        self.assertIs(validate(payload),payload)
        with self.assertRaises(ReceiptInvalid):
            validate({**payload,"private_law_id":"forbidden"})
        with self.assertRaises(ReceiptInvalid):
            validate({**payload,"split_digest":None})
        with self.assertRaises(ReceiptInvalid):
            validate({**payload,"route":"STATISTICAL"})

    def test_reproduce_two_processes(self):
        # Public RFC4231 HMAC-only vector; no simulation or split secrets.
        script="import hashlib,hmac;print(hmac.new(bytes.fromhex('0b'*20),b'Hi There',hashlib.sha256).hexdigest())"
        results=[subprocess.check_output([sys.executable,"-c",script]) for _ in range(2)]
        self.assertEqual(*results)

if __name__=="__main__":unittest.main()

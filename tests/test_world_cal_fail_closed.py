"""Invented tiny worlds and mocked scan control flow ONLY; no K0/CAL run.

The authorization object below is inert fixture data. Every scan test patches
run_one_repetition before calling scan_authorized; no draws/key/seed are used.
"""
import unittest
from unittest.mock import patch

from world_cal import k0_b, k0_c, power_engine as engine
from world_cal.k0_oracle import OracleUnknown, k0_outcome, k0_result_outcome
from world_cal.power_route import (PowerUnknown, SCENARIOS, R_REQUIRED,
                                  route_from_completed_scan)
from world_cal.receipt import validate as validate_receipt, ReceiptInvalid
from world_cal.sampford import SamplingUnknown
from world_cal.space import Node
from world_cal.world import State

EVIDENCE=[]

def record(case,result):
    EVIDENCE.append({"case":case,"result":result})
    return result

def pair(trials=1):
    # Literal artificial goals, not registered laws, CAL data or samples.
    return tuple(k0_b.K0Hypothesis(name,(State(()),)*trials,
                 lambda t,b:b==("A",),"same-public-fixture-demo")
                 for name in ("invented-left","invented-right"))

def b_receipt():
    return {"law_pair_count":73536,"law_pairs_digest":"untrusted-fixture",
            "demo_paths_exhausted":True,"train_paths_exhausted":True,
            "eval_paths_exhausted":True}

def c_inputs():
    return dict(cells=[k0_c.AbstractCell((),lambda b:False,1.,tuple("ABCD"))],
        space_candidates=[Node("ATOM",("MOVE_LEFT",))],
        space_complete={"typed_space_exhausted":True,
            "control_curves_exhausted":True,"canonical_space_sha256":"untrusted",
            "canonical_space_count":1},
        support_complete={"law_instance_demo_support_exhausted":True,
                          "weights_audited":True},b_final=4096,
        control_curves={arm:(0.,)*9 for arm in k0_c.CONTROLS})

def k0_inputs():
    return [{"status":"OPEN_LOOP_DOES_NOT_WIN"},{"status":"CONDITIONAL_WINS"},
            {"status":"PASS"},{"status":"COMPLETE","saturated":False}]


class K0NegativeTests(unittest.TestCase):
    def test_b_train_and_eval_real_node_cap(self):
        for mode,trials in (("TRAIN",2),("EVAL",1)):
            with self.subTest(mode=mode):
                out=record("b-"+mode+"-cap1",k0_b.solve_k0b_pair(
                    *pair(trials),mode=mode,horizon=1,cap=1))
                self.assertEqual(out["status"],"UNKNOWN")
                self.assertEqual(out["nodes"],2)

    def test_b_tiny_complete_control_and_one_less_than_needed(self):
        done=k0_b.solve_k0b_pair(*pair(),mode="EVAL",horizon=1,cap=100)
        self.assertEqual(done["status"],"PASS")
        out=record("b-cap-before-positive",k0_b.solve_k0b_pair(
            *pair(),mode="EVAL",horizon=1,cap=done["nodes"]-1))
        self.assertEqual(out["status"],"UNKNOWN")

    def test_b_truncated_scan_discards_partial_fail(self):
        p=("invented-pair",*pair(2),*pair())
        with patch.object(k0_b,"solve_k0b_pair",return_value={"status":"FAIL"}):
            out=record("b-truncated-after-fail",k0_b.scan_k0b_pairs(
                [p],complete_support=b_receipt(),cap=1))
        self.assertEqual(out["status"],"UNKNOWN")
        self.assertNotIn("failed_pairs",out)

    def test_b_iterator_resource_exit_is_unknown(self):
        def broken():
            yield ("invented-pair",*pair(2),*pair())
            raise MemoryError("invented resource stop")
        with patch.object(k0_b,"solve_k0b_pair",return_value={"status":"FAIL"}):
            out=record("b-iterator-resource",k0_b.scan_k0b_pairs(
                broken(),complete_support=b_receipt(),cap=1))
        self.assertEqual(out["status"],"UNKNOWN")

    def test_b_nominal_count_and_asserted_receipt_never_certify_support(self):
        # Fake rows and stubbed solver only: not a registered K0 full search.
        for stub in ("PASS","FAIL","UNKNOWN"):
            with self.subTest(stub=stub):
                rows=(("fake-%d"%i,None,None,None,None) for i in range(73536))
                with patch.object(k0_b,"solve_k0b_pair",new=lambda *a,**kw:{"status":stub}):
                    out=record("b-forged-completeness-"+stub,k0_b.scan_k0b_pairs(
                        rows,complete_support=b_receipt(),cap=1))
                self.assertEqual(out["status"],"UNKNOWN")
                self.assertEqual(out["failed_pairs"],[])

    def test_c_real_bfs_cap_propagates_to_l90(self):
        cell=k0_c.AbstractCell((),lambda b:b==("A",),1.,tuple("ABCD"))
        out=record("c-shortest-cap1",k0_c.shortest_path_abstract(cell,cap=1,horizon=1))
        self.assertEqual(out["status"],"UNKNOWN")
        self.assertIsNone(out["length"])
        with self.assertRaisesRegex(OracleUnknown,"STOP_UNKNOWN"):
            k0_c.complete_l90([cell],support_complete=c_inputs()["support_complete"],cap=1)
        self.assertEqual(k0_c.shortest_path_abstract(cell,cap=100,horizon=1)["length"],1)

    def test_c_registered_space_cap_and_inflated_cap(self):
        for cap in (1,2_000_000,k0_c.SPACE_SYNTAX_LOWER_BOUND):
            out=record("c-registered-cap-"+str(cap),k0_c.exhaustive_k0c_curve(
                **c_inputs(),cap=cap))
            self.assertEqual(out["status"],"UNKNOWN")
            self.assertNotIn("saturated",out)
            self.assertNotIn("oracle_AULC",out)

    def test_c_inner_iterator_cap_truncation_and_resource_paths(self):
        # The real lower bound blocks these branches first. Lower ONLY that
        # guard inside this test to audit the dormant iterator fail paths.
        with patch.object(k0_c,"SPACE_SYNTAX_LOWER_BOUND",1):
            args=c_inputs()
            args["space_candidates"]*=2
            out=record("c-inner-cap1",k0_c.exhaustive_k0c_curve(**args,cap=1))
            self.assertEqual(out["reason"],"Space cap reached")
            args=c_inputs();args["space_complete"]["canonical_space_count"]=2
            out=record("c-inner-truncated",k0_c.exhaustive_k0c_curve(**args,cap=10))
            self.assertEqual(out["reason"],"Space iterator did not exhaust")
            def broken():
                yield Node("ATOM",("MOVE_LEFT",))
                raise MemoryError("invented resource stop")
            args=c_inputs();args["space_candidates"]=broken()
            out=record("c-inner-resource",k0_c.exhaustive_k0c_curve(**args,cap=10))
            self.assertEqual(out["status"],"UNKNOWN")
            self.assertNotIn("saturated",out)

    def test_k0_unknown_precedes_fail_and_saturation(self):
        for index in range(4):
            for unknown in ("UNKNOWN","STOP_UNKNOWN",None,"NOT_RUN"):
                args=k0_inputs();args[2]={"status":"FAIL"};args[3]["saturated"]=True
                args[index]={"status":unknown,"saturated":False}
                out=k0_result_outcome(*args)
                self.assertEqual(out,"STOP_UNKNOWN")
        record("k0-unknown-precedence",{"status":"STOP_UNKNOWN","slots_checked":4})

    def test_partial_c_curve_and_truthy_status_cannot_become_definitive(self):
        args=k0_inputs()
        args[3]={"status":"UNKNOWN","saturated":False,"oracle_AULC":1.}
        self.assertEqual(k0_result_outcome(*args),"STOP_UNKNOWN")
        for value in (None,"UNKNOWN","STOP_UNKNOWN",0,1,{},[]):
            self.assertEqual(k0_outcome("OPEN_LOOP_DOES_NOT_WIN","CONDITIONAL_WINS",
                                        "FAIL",value),"STOP_UNKNOWN")
        self.assertEqual(k0_result_outcome(*k0_inputs()),"K0A_WITNESS")
        record("c-partial-not-promoted",{"status":"STOP_UNKNOWN"})


class ScanNegativeTests(unittest.TestCase):
    def assert_unknown(self,out):
        self.assertEqual(out["route"],"STOP_UNKNOWN")
        self.assertIsNone(out["n_required"])
        self.assertIsNone(out["power_lower_bound"])
        self.assertIs(out["cost_cap_check"],False)

    def scan(self,**kwargs):
        # Not a real capability or seed. All callers patch the repetition.
        args=dict(q=(.25,)*4,parent_ids=("toy0","toy1","toy2","toy3"),key=None,
            authorization=engine.CALAuthorization("BLIND_DESIGN_CALCULATOR",
                "sha256:"+"0"*64,True),b_final=4096,k0_status="K0A_WITNESS")
        args.update(kwargs)
        return engine.scan_authorized(**args)

    def test_unknown_k0_blocks_both_route_entries_before_work(self):
        counts={2:{s:R_REQUIRED for s in SCENARIOS}}
        for status in (None,"UNKNOWN","STOP_UNKNOWN","STOP_K0",True,{},"PASS"):
            with self.subTest(status=status),patch.object(engine,"run_one_repetition") as run:
                out=record("scan-blocked-k0-"+str(status),self.scan(k0_status=status))
                self.assert_unknown(out);run.assert_not_called()
                self.assert_unknown(route_from_completed_scan(counts,4,k0_status=status))

    def test_actual_b_c_cap_results_flow_through_reducer_and_both_scans(self):
        b=k0_b.solve_k0b_pair(*pair(),mode="EVAL",horizon=1,cap=1)
        c=k0_c.exhaustive_k0c_curve(**c_inputs(),cap=1)
        for index,result in ((2,b),(3,c)):
            inputs=k0_inputs();inputs[index]=result
            status=k0_result_outcome(*inputs)
            with patch.object(engine,"run_one_repetition") as run:
                integrated=self.scan(k0_status=status)
                pure=route_from_completed_scan({2:{s:R_REQUIRED for s in SCENARIOS}},
                    4,k0_status=status)
                self.assert_unknown(integrated);self.assert_unknown(pure)
                run.assert_not_called()
            record("real-cap-to-downstream-"+str(index),
                {"upstream":result,"k0_status":status,"integrated":integrated,"pure":pure})

    def test_integrated_partial_counts_then_forced_stop(self):
        for exc in (PowerUnknown,SamplingUnknown,MemoryError,RecursionError,StopIteration):
            seen=[]
            def stub(**kw):
                seen.append((kw["n"],kw["scenario_id"],kw["repetition"]))
                if len(seen)==6:raise exc("invented forced stop")
                return {"and":True,"ten_components":(True,)*10}
            with self.subTest(exc=exc.__name__),patch.object(engine,"run_one_repetition",new=stub):
                out=record("scan-forced-stop-"+exc.__name__,self.scan())
                self.assert_unknown(out)
                self.assertEqual(len(seen),6)
                self.assertEqual({n for n,s,r in seen},{2})
                self.assertEqual({s for n,s,r in seen},{SCENARIOS[0]})

    def test_integrated_truthy_unknown_is_not_a_success(self):
        for result in ({"and":"UNKNOWN"},{"and":1},{"and":None},
                       {"status":"UNKNOWN","and":True,"ten_components":(True,)*10},
                       {"and":True,"ten_components":(True,)*9+("UNKNOWN",)},
                       {"and":True,"ten_components":(False,)*10}):
            with patch.object(engine,"run_one_repetition",return_value=result) as run:
                out=record("scan-nonbool-or-partial",self.scan())
                self.assert_unknown(out);self.assertEqual(run.call_count,1)

    def test_integrated_primitive_cost_cap_forced_reached(self):
        # Force the ACTUAL registered post-complete-n cap comparison to fail.
        # Repetitions are constant mock booleans; no real generator is called.
        with patch.object(engine,"run_one_repetition",
                return_value={"and":True,"ten_components":(True,)*10}) as run, \
                patch.object(engine,"cost",return_value=20_000_001):
            out=record("scan-primitive-cost-cap",self.scan(
                q=(.5,.5),parent_ids=("toy0","toy1")))
            self.assert_unknown(out)
            self.assertEqual(run.call_count,3*R_REQUIRED)

    def test_complete_mock_counts_positive_control_no_simulation(self):
        # Exercise real 10,000x3 loop/count/CP rules with constant stub data.
        with patch.object(engine,"run_one_repetition",
                return_value={"and":True,"ten_components":(True,)*10}) as run:
            out=record("scan-complete-mock-control",self.scan())
            self.assertEqual(out["route"],"STATISTICAL")
            self.assertEqual(out["n_required"],2)
            self.assertEqual(run.call_count,3*R_REQUIRED)

    def test_missing_earlier_n_or_unknown_count_cannot_select_later_n(self):
        complete={s:R_REQUIRED for s in SCENARIOS}
        cases=({3:complete},{2:{},3:complete},{2:"UNKNOWN",3:complete},
               {2:{**complete,SCENARIOS[0]:None},3:complete},
               {2:{**complete,SCENARIOS[0]:True},3:complete})
        for rows in cases:
            out=record("route-incomplete-prefix",route_from_completed_scan(
                rows,4,k0_status="K0A_WITNESS"))
            self.assert_unknown(out)
        self.assertEqual(route_from_completed_scan({2:complete},4,
            k0_status="K0A_WITNESS")["n_required"],2)

    def test_scan_denies_missing_authorization_before_any_repetition(self):
        with patch.object(engine,"run_one_repetition") as run:
            with self.assertRaisesRegex(PowerUnknown,"STOP_UNKNOWN"):
                self.scan(authorization=None)
            run.assert_not_called()

    def test_stop_receipt_cannot_include_n_or_power(self):
        payload=dict(N_eligible=None,n_required=None,route="STOP_UNKNOWN",
            power_lower_bound=None,cost_cap_check=False,
            algorithm_digest="sha256:"+"0"*64,split_digest="sha256:"+"0"*64)
        validate_receipt(payload)  # schema fixture, no signing or real digests
        for key,value in (("n_required",2),("power_lower_bound",.99)):
            with self.assertRaises(ReceiptInvalid):validate_receipt({**payload,key:value})
        record("receipt-unknown-no-n-or-power",{"route":"STOP_UNKNOWN","n_required":None})

if __name__=="__main__":unittest.main()

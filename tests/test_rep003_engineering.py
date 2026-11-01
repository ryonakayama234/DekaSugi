"""Disclosed-only tests; never import old sealed data or scorers."""
import base64
import contextlib
import io
import json
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch
from packages.rep003 import (
    ACTIONS, ARMS, BUDGETS, MODELS, STRATA, Session, World, audit,
    conditioned_opportunity, consistent, digest, evaluate, kind, load,
    make_world, opportunity, save, state_signature, step, train, use,
    validate_snapshot, validate_trace, _trace_train,
)


class Rep003EngineeringTests(unittest.TestCase):
    def test_exact_conditional_intervention_and_semantics(self):
        zero = (0,0,0,0)
        gated = (0,1,2,1)
        self.assertEqual(step(zero,("pulse",0,None),gated),zero)
        prepared = step(zero,("set",2,1),gated)
        self.assertEqual(step(prepared,("pulse",0,None),gated),(0,1,1,0))
        self.assertEqual(step(zero,("pulse",0,None),(0,1,-1,-1)),(0,1,0,0))
        self.assertEqual(len(MODELS),len(set(state_signature(m) for m in MODELS)))

    def test_paid_history_makes_two_step_necessary(self):
        result = conditioned_opportunity()
        self.assertEqual(result["paid_conditioning"],4)
        self.assertGreater(result["surviving"],1)
        self.assertEqual(result["one_step"]["status"],"NO_OPPORTUNITY")
        self.assertEqual(result["two_step"]["status"],"WITNESS")
        self.assertEqual(result["two_step"]["cost"],2)
        self.assertEqual(result["total_witness_cost"],6)
        self.assertEqual(opportunity((0,0,0,0), (None,), 2)["status"],"NO_OPPORTUNITY")
        self.assertEqual(opportunity((0,0,0,0), MODELS, 2, max_plans=0)["status"],"UNKNOWN")
        self.assertEqual(opportunity((0,0,0,0), MODELS, 1)["status"],"WITNESS")

    def test_paid_public_training_without_host_labels(self):
        inferred, actions, h = _trace_train(0)
        self.assertEqual(kind(inferred),"GATE1")
        self.assertEqual(actions,100)
        self.assertEqual(len(h),64)
        s = train(8)
        self.assertEqual(s["train_worlds"],8)
        self.assertEqual(s["paid_train_actions"],800)
        self.assertEqual(s["distinct_families"],4)
        self.assertEqual(sum(s["support"].values()),8)
        self.assertEqual(s,train(8))
        self.assertEqual(train(0)["distinct_families"],0)

    def test_typed_public_evidence_negatives(self):
        w = make_world(1,"TRAIN")
        se = Session(w)
        row = se.apply(("pulse",0,None))
        for bogus in (
            dict(row,cost=True),dict(row,cost=1.0),dict(row,step=True),
            dict(row,after=[False,0,0,0]),dict(row,action=["pulse",-1,None]),
            dict(row,secret_rules=[]),
        ):
            with self.assertRaises(ValueError):
                validate_trace([bogus])
        with self.assertRaises(ValueError):
            se.apply(("pulse",True,None))
        with self.assertRaises(ValueError):
            se.apply(("set",0,True))

    def test_public_only_undisclosed_no_gold_leak(self):
        w1 = World(((0,1,2,1),),("a","b","c","d"),9,"X")
        w2 = World(((1,0,3,1),),("a","b","c","d"),9,"X")
        snap = train(8)
        self.assertEqual(use(snap,w1,"LQ",0),use(snap,w2,"LQ",0))
        self.assertEqual(use(snap,w1,"LQ",1),use(snap,w2,"LQ",1))
        p = use(snap,w1,"LQ",1)
        self.assertNotIn("secret_rules",json.dumps(p))
        self.assertNotIn("stratum",p)
        self.assertEqual(p["commit_digest"],digest({k:v for k,v in p.items() if k!="commit_digest"}))
        broken = dict(p)
        broken["budget"]=8
        with self.assertRaises(ValueError):
            audit(w1,broken)

    def test_snapshot_roundtrip_tamper_and_all_arms(self):
        s = train(16)
        with tempfile.TemporaryDirectory() as root:
            p = Path(root)/"snap.json"
            save(s,p)
            self.assertEqual(load(p),s)
            bad = dict(s,train_worlds=999)
            with self.assertRaises(ValueError):
                validate_snapshot(bad)
            bad = dict(s,library=[])
            with self.assertRaises(ValueError):
                validate_snapshot(bad)
            w = make_world(301,"CONDITIONAL_TRANSFER")
            for arm in ARMS:
                c=use(s,w,arm,2)
                self.assertLessEqual(c["meter"]["actions"],2)
                self.assertLessEqual(c["meter"]["model_checks"],200000)
                self.assertIn(c["prediction"]["status"],("COMMITTED","ABSTAIN"))
                self.assertEqual(c, use(s,w,arm,2))
                self.assertGreaterEqual(audit(w,c),0)

    def test_lossless_archived_pilot_recovery(self):
        from scripts.read_rep003_archive import decode_archive
        archive = Path(__file__).resolve().parents[1] / (
            "experiments/EXP-REP-003/artifacts/"
            "20261102-reduced-pilot-v1_1-raw.json.zlib.b64")
        result = decode_archive(archive)
        self.assertEqual(result["record_count"], 2016)
        self.assertEqual(result["records_digest"],
                         "6792a8cff8d3e69f4b4789da80309df4d11d602bf870a39537176d116ae5e1b9")
        self.assertEqual(sum(
            entry["LQ_vs_LA_different_action_sequences"]
            for stratum in result["policy_switch"].values()
            for entry in stratum.values()),0)
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"corrupted.b64"
            p.write_text("invalid contents")
            with self.assertRaises(ValueError):
                decode_archive(p)

    def test_real_cli_and_disclosed_raw_scoring(self):
        from packages.rep003.__main__ import main
        with tempfile.TemporaryDirectory() as root:
            snap=str(Path(root)/"s.json")
            pre=str(Path(root)/"pre.json")
            tr=str(Path(root)/"u.jsonl")
            scored=str(Path(root)/"scored.json")
            cases=[
                (["rep003","preflight","--output",pre],"DISCLOSED_OPPORTUNITY_PREFLIGHT"),
                (["rep003","train","--worlds","64","--snapshot",snap],"DISCLOSED_TRAIN"),
                (["rep003","inspect","--snapshot",snap],"DISCLOSED_INSPECT"),
                (["rep003","use","--snapshot",snap,"--world-index","301","--budget","6","--trace",tr],"DISCLOSED_LOCAL_USE"),
            ]
            for args,expected in cases:
                with patch("sys.argv",args),contextlib.redirect_stdout(io.StringIO()) as buf:
                    main()
                self.assertEqual(json.loads(buf.getvalue())["status"],expected)
            with patch("sys.argv",["rep003","evaluate-disclosed","--output",scored]),contextlib.redirect_stdout(io.StringIO()) as buf:
                main()
            data=json.loads(Path(scored).read_text())
            self.assertEqual(data["status"],"DISCLOSED_REDUCED_GRAMMAR_ENGINEERING_ONLY")
            self.assertEqual(data["record_count"],48*len(ARMS)*len(BUDGETS))
            self.assertEqual(data["records_digest"],digest(data["rows"]))
            self.assertEqual(set(data["summary"]),set(STRATA))
            self.assertEqual(len(data["train_curve"]),6)
            self.assertEqual(data["opportunity"]["total_witness_cost"],6)
            print("REP003_DISCLOSED_SUMMARY="+json.dumps({k:v for k,v in data.items() if k!="rows"},separators=(",",":"),sort_keys=True))
            packed=base64.b64encode(zlib.compress(json.dumps(data,sort_keys=True,separators=(",",":")).encode(),9)).decode()
            print("REP003_ZLIB_BASE64="+packed)


if __name__ == "__main__":
    unittest.main()

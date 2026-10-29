"""Invented tuples only; never use genuine TRAIN64 or old DEV/FINAL scorer."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from packages.evaluation.opportunity_actual import public_redacted_pair
from scripts.opportunity_real_pair_engine import _canonical
from scripts import opportunity_independent_recount as m
from scripts import opportunity_one_shot_runner as runner


def fake_raw(tid, calls):
    selected = {"node_kind": "input", "type": "String"}
    return ({
        "search": {"task_id": tid, "status": "solved", "solved": True,
                   "program": selected, "tested_candidates": 10,
                   "max_nodes": 4, "max_candidates": 100,
                   "trace_sha256": "f"*64},
        "audit_correct": True, "audit_invalid_solved": False,
        "meter": {"primitive_invocations": calls, "by_op": {"trim": calls}},
        "selected_ast": selected,
    }, 10, calls, True, False, 1.2, 2.3, .4, .5)


def synthetic_evidence():
    files = {
        "STARTED.json": {"schema_version":"opportunity-once-only-start-v1",
                         "source_commit":"a"*40,
                         "original_sha256":"b"*64,
                         "planned_pairs":64,"no_retry_even_on_failure":True},
        "COMPLETED.json": {
            "schema_version":"opportunity-once-only-completion-v1",
            "paired_count":64,
            "status":"complete_redacted_private_evidence_only",
            "no_public_raw_data":True},
    }
    choices, originals, cases = [], [], []
    for i in range(64):
        tid="t-"+f"{i:064x}"
        actions={"B1":"OFF","B2":"ON","B3":"OFF"}
        decision={"task_id":tid,"choices":{name:{"action":choice,"reason":"SYNTHETIC"}
                    for name,choice in actions.items()}}
        third={"input":f"synthetic-{i}","output":f"synthetic-out-{i}"}
        off=fake_raw(tid,12)
        on=fake_raw(tid,4)
        pair=public_redacted_pair(tid,off,on,actions,sha256(_canonical(third)).hexdigest())
        files[f"pair-{i:03d}.json"]=pair
        for arm,raw in (("OFF",off),("ON",on)):
            files[f"ARM_STARTED-{i:03d}-{arm}.json"]={
                "schema_version":"opportunity-once-only-arm-start-v1",
                "task_id":tid,"arm":arm,"index":i}
            files[f"trial-{i:03d}-{arm}.json"]={
                "schema_version":"opportunity-private-raw-trial-v1",
                "task_id":tid,"arm":arm,"canonical_original_tuple":list(raw)}
        choices.append(decision)
        originals.append({"task_id":tid,"third_audit":third})
        cases.append(SimpleNamespace(task=SimpleNamespace(task_id=tid),
                                     family=f"synthetic-f{i//8}"))
    return files,choices,originals,cases


class IndependentRecountSyntheticTests(unittest.TestCase):
    def test_complete_64_records_recomputed_and_frozen_choices(self):
        files,decisions,originals,cases=synthetic_evidence()
        summary=m.recount_complete(files.__getitem__,list(files),decisions,
                                   originals,cases,"a"*40,"b"*64)
        overall=summary["overall"]
        self.assertEqual(overall["paired_valid"],64)
        self.assertEqual(overall["classifications"]["both_correct_on_cheaper"],64)
        self.assertEqual(overall["policies"]["B1"]["decision_errors"],64)
        self.assertEqual(overall["policies"]["B1"]["sum_excess_calls"],512)
        self.assertEqual(overall["policies"]["B2"]["decision_errors"],0)
        self.assertEqual(overall["choice_disagreement_tasks"],64)
        self.assertEqual(overall["choice_sensitivity_denominator"],64)
        self.assertAlmostEqual(overall["off_search_cpu_ms_sum"],76.8)
        self.assertAlmostEqual(overall["on_search_wall_ms_sum"],147.2)
        self.assertAlmostEqual(overall["off_audit_cpu_ms_sum"],25.6)
        self.assertEqual(overall["policy_inference_cost"],
                         "not_metered_by_original_pilot")
        self.assertEqual(len(summary["by_family"]),8)
        self.assertTrue(all(x["paired_valid"]==8 for x in summary["by_family"].values()))

    def test_tamper_saved_redacted_result_rejected(self):
        files,d,o,c=synthetic_evidence()
        files["pair-018.json"]["trials"]["ON"]["primitive_calls"]=7
        with self.assertRaises(ValueError):
            m.recount_complete(files.__getitem__,list(files),d,o,c,"a"*40,"b"*64)

    def test_missing_original_trial_or_extra_file_is_rejected(self):
        files,d,o,c=synthetic_evidence()
        del files["trial-031-OFF.json"]
        with self.assertRaises((KeyError,ValueError)):
            m.recount_complete(files.__getitem__,list(files),d,o,c,"a"*40,"b"*64)
        files,d,o,c=synthetic_evidence()
        files["unexpected-file.json"]={}
        with self.assertRaises(ValueError):
            m.recount_complete(files.__getitem__,list(files),d,o,c,"a"*40,"b"*64)

    def test_raw_tuple_and_start_marker_task_identity_mutation_rejected(self):
        files,d,o,c=synthetic_evidence()
        files["trial-000-ON.json"]["canonical_original_tuple"][0]["search"]["task_id"]="t-"+"e"*64
        with self.assertRaises(ValueError):
            m.recount_complete(files.__getitem__,list(files),d,o,c,"a"*40,"b"*64)
        files,d,o,c=synthetic_evidence()
        files["ARM_STARTED-008-OFF.json"]["task_id"]="t-"+"e"*64
        with self.assertRaises(ValueError):
            m.recount_complete(files.__getitem__,list(files),d,o,c,"a"*40,"b"*64)

    def test_read_only_file_check_rejects_symlink_and_permissive_acl(self):
        with TemporaryDirectory() as tmp:
            private=Path(tmp)/"owner"
            private.mkdir(mode=0o700)
            evidence=private/"STARTED.json"
            evidence.write_text('{"synthetic":true}',encoding="utf-8")
            evidence.chmod(0o600)
            with runner._private_root(private) as fd:
                self.assertEqual(m._load_privately(fd,"STARTED.json"),{"synthetic":True})
            evidence.chmod(0o644)
            with runner._private_root(private) as fd:
                with self.assertRaises(ValueError):
                    m._load_privately(fd,"STARTED.json")
            evidence.unlink()
            evidence.symlink_to(Path(tmp)/"outside")
            with runner._private_root(private) as fd:
                with self.assertRaises(ValueError):
                    m._load_privately(fd,"STARTED.json")

    def test_empty_complete_marker_not_construed_scientific_outcome(self):
        files,d,o,c=synthetic_evidence()
        files["COMPLETED.json"]["paired_count"]=0
        with self.assertRaises(ValueError):
            m.recount_complete(files.__getitem__,list(files),d,o,c,"a"*40,"b"*64)


if __name__=="__main__":
    unittest.main()

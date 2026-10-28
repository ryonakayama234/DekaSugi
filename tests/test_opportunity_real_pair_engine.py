"""Synthetic ONLY; no real fresh TRAIN64 generator, old holdout or scorer used."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from scripts import opportunity_real_pair_engine as m


TASK="t-"+"a"*64
CHOICES={"B1":"OFF","B2":"ON","B3":"OFF"}
SKILL_ID="skill_8fe1361cb5014f85"
AST={"node_kind":"input","type":"String"}


def fake_trial(task_id=TASK, calls=7, *, invalid=False):
    return ({
        "search":{"task_id":task_id,"status":"solved","solved":True,
                  "program":deepcopy(AST),"tested_candidates":10,
                  "max_nodes":4,"max_candidates":100,"trace_sha256":"f"*64},
        "audit_correct":not invalid,"audit_invalid_solved":invalid,
        "meter":{"primitive_invocations":calls,"by_op":{"trim":calls}},
        "selected_ast":deepcopy(AST),
    },10,calls,not invalid,invalid,1.0,2.0,.2,.3)


def audit():
    return SimpleNamespace(input="SYNTHETIC-IN",output="SYNTHETIC-OUT")


def ahash():
    return sha256(m._canonical({"input":audit().input,"output":audit().output})).hexdigest()


def task():
    return SimpleNamespace(task_id=TASK,examples=(object(),object()),
                           limits=SimpleNamespace(max_ast_nodes=4,max_candidates=100))


def skill():
    return SimpleNamespace(skill_id=SKILL_ID,body_hash=m.LOCKED_SKILL)


class ActualPairSyntheticOnlyTests(unittest.TestCase):
    def test_hard_off_rejects_unactivated_actual_engine(self):
        self.assertIs(m.SCORING_ACTIVATED,False)
        with self.assertRaisesRegex(ValueError,"not activated"):
            m._unactivated_real_pair(None,None,None,None,None)
        self.assertIs(m.SCORING_ACTIVATED,False)

    def test_uses_fresh_registry_per_off_on_and_only_redacts(self):
        regs=[]
        seen=[]
        def fresh():
            r=object();regs.append(r);return r
        def register(s,r):
            seen.append(("register",r,s.skill_id));return (r,"ON")
        def fake_score(t,a,r,learned):
            seen.append(("trial",r,dict(learned),a.input))
            return fake_trial(t.task_id,5 if not learned else 3)
        result=m.assemble_audited_pair(task(),audit(),skill(),CHOICES,ahash(),
                                      registry_factory=fresh,
                                      register_skill=register,
                                      validate_skill=lambda s,r: seen.append(("validate",r)),
                                      audited_trial=fake_score)
        self.assertEqual(len(regs),3)
        self.assertEqual(len({id(r) for r in regs}),3)
        self.assertEqual(result["classification"],"both_correct_on_cheaper")
        self.assertEqual(result["policies"]["B1"]["excess_calls"],2)
        self.assertEqual([x[0] for x in seen],["validate","trial","register","trial"])
        self.assertEqual(seen[1][2],{})
        self.assertEqual(seen[3][2],{SKILL_ID:skill().__dict__} if False else {SKILL_ID:seen[3][2][SKILL_ID]})
        self.assertNotIn("SYNTHETIC-IN",json.dumps(result))
        self.assertNotIn("SYNTHETIC-OUT",json.dumps(result))

    def test_false_solved_off_stops_before_on_search(self):
        invoked=[]
        def search(t,a,r,learned):
            invoked.append("ON" if learned else "OFF")
            return fake_trial(invalid=True)
        with self.assertRaisesRegex(ValueError,"false_solved"):
            m.assemble_audited_pair(task(),audit(),skill(),CHOICES,ahash(),
                                   registry_factory=object,
                                   register_skill=lambda s,r:r,
                                   validate_skill=lambda s,r:None,
                                   audited_trial=search)
        self.assertEqual(invoked,["OFF"])

    def test_invalid_third_audit_and_skill_stop_before_any_trial(self):
        for sha,sk in [("0"*64,skill()),(ahash(),SimpleNamespace(skill_id="BAD",body_hash=m.LOCKED_SKILL))]:
            got=[]
            with self.assertRaises(ValueError):
                m.assemble_audited_pair(task(),audit(),sk,CHOICES,sha,
                                       registry_factory=object,
                                       register_skill=lambda s,r:r,
                                       validate_skill=lambda s,r:None,
                                       audited_trial=lambda *args:got.append(1))
            self.assertEqual(got,[])

    def test_private_archive_rejects_wrong_digest_without_parsing(self):
        raw=b'{"private_audit":"SYNTHETIC"}'
        with self.assertRaisesRegex(ValueError,"digest invalid"):
            m.validate_private_archive(raw,"0"*64,{"decisions":[]})

    def test_private_archive_frozen_source_requires_64_full_rows(self):
        record={
            "schema_version":"opportunity-private-audit-original-v1",
            "method":m.FRESH_METHOD,
            "scope":"fresh_train64_before_any_scored_trials",
            "public_manifest_sha256":"bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85",
            "public_pretrial_original_raw_sha256":m.LOCKED_CHOICES_RAW,
            "public_pretrial_decision_sha256":"8a8625ed86e66b27bef8d09a023172d2adbc9ad0d42c155ab7f137097e2dccb2",
            "third_audit_commitments_sha256":m.LOCKED_THIRD_COMMITMENTS,
            "paired_trials_executed_at_capture":0,"records":[]}
        original={"schema_version":"opportunity-pretrial-public-decisions-v1",
                  "method":m.FRESH_METHOD,"phase":"FRESH_TRAIN_ONLY",
                  "source_manifest_sha256":record["public_manifest_sha256"],
                  "skill_body_sha256":m.LOCKED_SKILL,
                  "policy_snapshot_sha256":{},"decisions":[],
                  "paired_trials_executed":0,"dev_or_final_evaluated":False}
        raw=m._canonical(record)+b"\n"
        with self.assertRaisesRegex(ValueError,"64-row"):
            m.validate_private_archive(raw,sha256(raw).hexdigest(),original)
        record["records"]=[{"task_id":TASK,"third_audit":{"input":"x","output":"y"}}]*64
        original["decisions"]=[{"task_id":TASK}]*64
        raw=m._canonical(record)+b"\n"
        with self.assertRaises(ValueError):
            m.validate_private_archive(raw,sha256(raw).hexdigest(),original)
        record["paired_trials_executed_at_capture"]=1
        raw=m._canonical(record)+b"\n"
        with self.assertRaisesRegex(ValueError,"source or timing"):
            m.validate_private_archive(raw,sha256(raw).hexdigest(),original)


if __name__=="__main__":
    unittest.main()

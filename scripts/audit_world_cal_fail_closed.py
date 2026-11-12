#!/usr/bin/env python3
"""Repeatable synthetic negative-test receipt; never a K0/CAL/simulation run."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def audit():
    path=ROOT/"tests/test_world_cal_fail_closed.py"
    spec=importlib.util.spec_from_file_location("fail_closed_fixture_tests",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(module))
    paths=("world_cal/k0_b.py","world_cal/k0_c.py","world_cal/k0_oracle.py",
           "world_cal/power_route.py","world_cal/power_engine.py",
           "world_cal/receipt.py","tests/test_world_cal_fail_closed.py",
           "scripts/audit_world_cal_fail_closed.py")
    payload={"kind":"SYNTHETIC_FAIL_CLOSED_NEGATIVE_TESTS_NOT_K0_CAL_OR_SIMULATION",
        "source_commit":os.environ.get("WORLD_CAL_SOURCE_HEAD","SUBMISSION_HEAD_BOUND_BY_MANIFEST_AND_PR"),
        "python":platform.python_version(),"platform":platform.platform(),
        "tests_run":result.testsRun,"successful":result.wasSuccessful(),
        "failures":[str(case) for case,tb in result.failures],
        "errors":[str(case) for case,tb in result.errors],
        "cases":module.EVIDENCE,
        "raw_source_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        "CAL_EXECUTED":False,"K0_EXECUTED":False,"POWER_SIMULATION_EXECUTED":False,
        "SEALED_SPLIT_MATERIALIZED":False,"SEED_GENERATED":False,
        "algorithm_digest":None}
    return payload

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",required=True)
    args=parser.parse_args();payload=audit()
    Path(args.output).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:payload[k] for k in ("kind","source_commit","tests_run","successful")}))
    raise SystemExit(0 if payload["successful"] else 1)

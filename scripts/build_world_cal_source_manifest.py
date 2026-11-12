#!/usr/bin/env python3
"""Candidate raw-byte closure for separate independent audit, NOT algorithm lock."""
import hashlib
import json
import platform
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATHS=tuple(sorted((
    "AGENTS.md",
    "docs/INDEX.md",
    "docs/architecture/system.md",
    "docs/architecture/contracts.md",
    "docs/research/WORLD-CAL-FINAL-AUDIT-REQUEST-20261112-01.md",
    "docs/research/WORLD-CAL-FAIL-CLOSED-EVIDENCE-20261112-01.json",
    "docs/research/WORLD-CAL-GENERATOR-SOURCE-20261111-01.md",
    "docs/research/WORLD-CAL-IMPLEMENTATION-PLAN-20261111-01.md",
    "docs/research/WORLD-CAL-IMPLEMENTATION-RQ-20261111-01.md",
    "docs/research/WORLD-CAL-IMPLEMENTATION-ERRATA-20261111-01.md",
    "docs/research/WORLD-CAL-IMPLEMENTATION-CONTINUATION-20261111-02.md",
    "docs/research/WORLD-CAL-IMPLEMENTATION-COVERAGE-AUDIT-20261111-03.md",
    "docs/research/WORLD-CAL-GENERATOR-DISTRIBUTION-20261111-01.json",
    "docs/research/WORLD-CAL-GENERATOR-MANIFEST-20261111-01.json",
    "world_cal/__init__.py",
    "world_cal/world.py",
    "world_cal/generator_contract.py",
    "world_cal/space.py",
    "world_cal/k0_open_loop.py",
    "world_cal/k0_history_dp.py",
    "world_cal/k0_oracle.py",
    "world_cal/prf.py",
    "world_cal/gtheta.py",
    "world_cal/sampford.py",
    "world_cal/inference.py",
    "world_cal/power_route.py",
    "world_cal/cal_measure.py",
    "world_cal/ledger.py",
    "world_cal/sampford_grouped.py",
    "world_cal/id_only.py",
    "world_cal/abstract_support.py",
    "world_cal/power_engine.py",
    "world_cal/k0_b.py",
    "world_cal/k0_c.py",
    "world_cal/k0_coverage.py",
    "world_cal/role_boundary.py",
    "world_cal/receipt.py",
    "world_cal/normative/WORLD-CAL-GTHETA-20261111-01-model-candidates.json",
    "world_cal/normative/WORLD-CAL-ACL-20261111-01-normalized-manifest.csv",
    "world_cal/normative/WORLD-PREREG-SPEC-20261110-06.md",
    "world_cal/normative/WORLD-CAL-PROTOCOL-20261111-01.md",
    "world_cal/requirements.lock",
    "scripts/audit_world_cal_sampford_336.py",
    "scripts/profile_world_cal_integrated.py",
    "scripts/audit_world_cal_role_process.py",
    "scripts/audit_world_cal_id_only_repro.py",
    "scripts/audit_world_cal_k0_index.py",
    "scripts/audit_world_cal_fail_closed.py",
    "scripts/profile_world_cal_synthetic.py",
    "scripts/build_world_cal_source_manifest.py",
    "tests/test_world_cal_synthetic.py",
    "tests/test_world_cal_impl_completion.py",
    "tests/test_world_cal_k0_coverage.py",
    "tests/test_world_cal_fail_closed.py",
    ".github/workflows/world-cal-synthetic-implementation.yml"
)))

def candidate():
    entries=[]
    for path in PATHS:
        p=ROOT/path
        raw=p.read_bytes()
        entries.append({"path":path,"size_bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
                        "encoding":"UTF-8/LF" if not path.endswith(".csv") else "UTF-8 CSV/LF"})
    return {
        "id":"WORLD-CAL-ALGORITHM-SOURCE-MANIFEST-20261111-01-CANDIDATE",
        "status":"CANDIDATE_UNAUDITED__NOT_ALGORITHM_DIGEST",
        "source_commit":os.environ.get("WORLD_CAL_SOURCE_HEAD","EXACT_HEAD_TO_BE_BOUND_BY_INDEPENDENT_SUPERVISOR"),
        "algorithm_digest":None,
        "split_digest":None,
        "seed":None,
        "canonical_order":"path lexicographic ascending; raw sha256 of all exact stored bytes",
        "source_origin_git_blob":{
            "spec_v6":"9362065507791ced44e2a3cc218c93a0b3cef395",
            "protocol_approved":"f01471d448da42c1458b4eb38203b71dc517a663",
            "gtheta":"7df028318df0f876ffaf7b7331738620a1187e8c",
            "acl_e2":"6068b0b21808d7016e6570b8893ef18edc2a1d75"
        },
        "environment":{"python":platform.python_version(),
                       "python_implementation":platform.python_implementation(),
                       "machine":platform.machine(),"platform":platform.platform(),
                       "libc":platform.libc_ver(),
                       "pythonhashseed":os.environ.get("PYTHONHASHSEED"),
                       "openblas_num_threads":os.environ.get("OPENBLAS_NUM_THREADS"),
                       "numpy_pin":"2.2.6", "cryptography_pin":"46.0.3",
                       "rfc8785_pin":"0.1.4",
                       "ubuntu_runner_pin":"ubuntu-24.04",
                       "ci_python_pin":"3.12.16"},
        "closed_source_files":entries,
        "excluded_from_hash":"this candidate itself; future escrow/holdout/split secret files",
        "independent_audit_required":True
    }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output")
    args=p.parse_args()
    payload=json.dumps(candidate(),indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    print(payload)
    if args.output:Path(args.output).write_text(payload,encoding="utf-8")

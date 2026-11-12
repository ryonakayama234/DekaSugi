#!/usr/bin/env python3
"""Exactly one structurally complete synthetic repetition (not power simulation).

N=336 and the approved PUBLIC q multiset; parent IDs are artificial, never the
sealed allocation. Runs the full six-factor generator + exact fixed-size
Sampford + design SYG + 999 same-parent resamples + max-T + 10 AND.
This script does NOT repeat R=10000, scan n, read CAL, or create an escrow key.
"""
import argparse
import json
import os
import platform
import resource
import sys
import time

from world_cal.power_engine import run_one_repetition

Q=(1/160,)*72+(1/480,)*264
PARENTS=(tuple("SYN-HEAVY-%02d"%(i//2) for i in range(72))+
         tuple("SYN-LIGHT-%02d"%(i//6) for i in range(264)))


def profile(n=96):
    if n!=96:raise ValueError("only preregistered fixture n=96 allowed pre-CAL")
    before=resource.getrusage(resource.RUSAGE_SELF)
    w0=time.perf_counter();c0=time.process_time()
    result=run_one_repetition(q=Q,parent_ids=PARENTS,n=n,
          scenario_id="GTHETA-BASE-01",repetition=0,
          key=bytes.fromhex("0b"*32),synthetic_fixture=True)
    cpu=time.process_time()-c0
    wall=time.perf_counter()-w0
    after=resource.getrusage(resource.RUSAGE_SELF)
    model=None
    try:
        with open("/proc/cpuinfo",encoding="utf-8") as f:
            for line in f:
                if line.startswith("model name"):
                    model=line.split(":",1)[1].strip();break
    except OSError:pass
    # Counts are algebraic upper-scan quantities, NOT completed simulations.
    # Linear scaling from one n=96 instance is a scenario assumption only.
    n_weight_sum=sum(range(2,337))
    repetitions=3*10000*(336-1)
    hours=wall*repetitions*n_weight_sum/(96*(336-1))/3600
    return {
      "kind":"PRECAL_ONE_COMPLETE_SYNTHETIC_REPETITION_ONLY",
      "full_power_executed":False,"cal_executed":False,
      "k0_executed":False,"seed_generated":False,
      "sealed_split_materialized":False,"public_fixture":{
        "N":336,"n":n,"q_counts":{"1/160":72,"1/480":264},
        "parent_structure":"synthetic 36x2 + 44x6",
        "model":"GTHETA-BASE-01","bootstrap_replicates":999,
        "repetition":0,"injected_public_test_vector":"RFC4231-style static 0b x 32 (not escrow)"
      },
      "environment":{"python":platform.python_version(),
        "implementation":platform.python_implementation(),
        "platform":platform.platform(),"libc":platform.libc_ver(),
        "machine":platform.machine(),"cpu_model":model,
        "cpu_count":os.cpu_count(),
        "pythonhashseed":os.environ.get("PYTHONHASHSEED"),
        "openblas_threads":os.environ.get("OPENBLAS_NUM_THREADS")},
      "measurement":{"wall_seconds":wall,"cpu_seconds":cpu,
        "maxrss_kib":after.ru_maxrss,
        "ru_utime_delta":after.ru_utime-before.ru_utime,
        "ru_stime_delta":after.ru_stime-before.ru_stime,
        "and_result":result["and"],
        "ten_gate_values":list(result["ten_components"]),
        "observed_parent_clusters":result["observed_parent_clusters"],
        "observed_sample_size":result["sample_size"],
        "actual_bootstrap_replicates":result["bootstrap_count"]},
      "extrapolation":{"scan":"all n=2..336, 3 scenarios, R=10000",
        "hypothesis":"one-rep wall time proportional to n; ignores fixed PPS/DP "
          "and different n-dependent bootstrap costs, no stop-early savings",
        "hypothetical_all_n_wall_hours":hours,
        "real_world_feasibility":"STOP_UNKNOWN"},
      "limitations":"Not a validated real-run budget or a production power run. "
       "Per-n model, exact authentic split law-ID mapping, scenario costs and "
       "real-world resource contention require independent audit."
    }


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output");args=p.parse_args()
    report=profile()
    raw=json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if args.output:
        with open(args.output,"w",encoding="utf-8") as f:f.write(raw)
    else:print(raw)

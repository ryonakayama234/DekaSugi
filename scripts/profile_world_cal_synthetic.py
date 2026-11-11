#!/usr/bin/env python3
"""Allowed component-only microprofiler. NEVER a CAL or power-simulation run.

No secret seed/split/holdout. Public deterministic RFC HMAC test vector and
constant-factor toy data. No R=10000, no n scanning for power, no 999-bootstrap
simulation. CPU/wall/max RSS and extrapolations are instrumented, not promises.
"""
import argparse
import hashlib
import hmac
import json
import math
import os
import platform
import resource
import tempfile
import time
from fractions import Fraction
from pathlib import Path

from world_cal.gtheta import load_model,marginal_table,binary_outcome
from world_cal.sampford import exact_subset_law,inclusion,exact_inclusions
from world_cal.inference import parent_bootstrap_ht,studentized_max_t

def sample(stage,fn,items):
    before=resource.getrusage(resource.RUSAGE_SELF)
    cpu=time.process_time()
    wall=time.perf_counter()
    checksum=fn()
    seconds=time.perf_counter()-wall
    cpu_seconds=time.process_time()-cpu
    after=resource.getrusage(resource.RUSAGE_SELF)
    return dict(stage=stage,items=items,wall_seconds=seconds,cpu_seconds=cpu_seconds,
                throughput_items_wall=(items/seconds if seconds else None),
                maxrss_kib=after.ru_maxrss,ru_utime_delta=after.ru_utime-before.ru_utime,
                ru_stime_delta=after.ru_stime-before.ru_stime,checksum=checksum)

def profile():
    model=load_model()
    scenario=model["binary_joint_generator"]["scenarios"][0]
    table=marginal_table(model)
    factors=dict.fromkeys(("cluster","law","gate","arm","checkpoint","episode"),0.0)
    # Fixed public RFC4231 HMAC key, not a PRF escrow/calibration seed.
    key=bytes.fromhex("0b"*20)
    N=8;cycles=3
    draws=N*576*cycles
    def prf_gtheta():
        digest=hashlib.sha256()
        for i in range(draws):
            mac=hmac.new(key,i.to_bytes(8,"big"),hashlib.sha256).digest()
            value=binary_outcome(scenario,factors,table["FULL"][0][i%9])
            digest.update(mac[:1]+bytes([value]))
        return digest.hexdigest()
    rows=[sample("PRF_and_Gtheta_kernel",prf_gtheta,draws)]
    def pps():
        # Exactly small synthetic N=8, n=2. Not the real N=336 design.
        pi=[Fraction(1,4)]*8
        law=exact_subset_law(pi)
        first,second=inclusion(law,8)
        return str(sum(law.values()))+":"+str(second[0][1])
    rows.append(sample("Sampford_exact_pi_ll_small_N8_n2",pps,8*8))
    for N,design_n in ((32,8),(64,16)):
        def dp(N=N,design_n=design_n):
            first,joint=exact_inclusions([design_n/N]*N)
            return hashlib.sha256(repr((sum(first),joint[0][1])).encode()).hexdigest()
        rows.append(sample(f"Sampford_exact_pi_ll_DP_N{N}_n{design_n}",dp,N*N))
    def bootstrap():
        sample_ids=list(range(8))
        q=[1/8]*8;pi=[1.0]*8
        values=[i/8 for i in sample_ids]
        parent_ids=[str(i//2) for i in sample_ids]
        base=["0","1","2","3"]
        points=[]
        for i in range(48):
            draw=[base[(i+j)%4] for j in range(4)]
            points.append(parent_bootstrap_ht(sample_ids,q,pi,values,parent_ids,draw))
        # Max-T microkernel on deterministic, nondegenerate synthetic matrix.
        center=[.1*j for j in range(7)]
        replicates=[[center[j]+.001*(j+1)*math.sin(i+j) for j in range(7)] for i in range(48)]
        result=studentized_max_t(center,replicates)
        return hashlib.sha256(repr((points,result)).encode()).hexdigest()
    rows.append(sample("parent_bootstrap_and_maxT_kernel",bootstrap,48))
    def io():
        blob=(b"synthetic-IO-only\n"*4096)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"synthetic.bin"
            p.write_bytes(blob)
            raw=p.read_bytes()
            return hashlib.sha256(raw).hexdigest()
    rows.append(sample("synthetic_file_IO",io,len(b"synthetic-IO-only\n")*4096))
    counts={}
    for upper in (336,512):
        repetitions=3*10_000*(upper-1)
        outcomes=3*10_000*576*(upper*(upper+1)//2-1)
        bootstraps=repetitions*999
        prf_rate=rows[0]["throughput_items_wall"]
        bt_rate=next(x["throughput_items_wall"] for x in rows if x["stage"]=="parent_bootstrap_and_maxT_kernel")
        counts["2.."+str(upper)]={
            "candidate_n":upper-1,"MC_repetitions":repetitions,
            "binary_outcomes":outcomes,"cluster_bootstrap_replicates":bootstraps,
            "PRF_Gtheta_kernel_lower_bound_wall_days":outcomes/prf_rate/86400,
            "bootstrap_kernel_lower_bound_wall_days":bootstraps/bt_rate/86400,
            "exact_Sampford_pi_ll_real_scale":"DP N32/N64 microbench only; N336 source data & numerical stability not audited",
            "complete_simulation_feasibility":"STOP_UNKNOWN"
        }
    return {
        "kind":"PERMITTED_SYNTHETIC_COMPONENT_PROFILE_ONLY",
        "CAL_EXECUTED":False,"POWER_SIMULATION_EXECUTED":False,"K0_EXECUTED":False,
        "seed_generated":False,"split_materialized":False,
        "environment":{"python":platform.python_version(),"platform":platform.platform(),
                       "architecture":platform.machine(),"cpu_count":os.cpu_count()},
        "rows":rows,"symbolic_extrapolation":counts,
        "limitations":"Kernel-only optimistic lower bounds; no full Gaussian sharing, per-n PPS draw, "
        "999-resample max-T repeated integration or real run. Times not a calibrated simulation ETA."
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output")
    args=parser.parse_args()
    report=profile()
    body=json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    print(body)
    if args.output:
        Path(args.output).write_text(body,encoding="utf-8")

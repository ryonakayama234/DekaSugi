"""Bounded COEV F0-C engineering-only Linux resource preflight.

Never imports historical scorers or evaluator secrets. Do not treat the
public TRAIN sim as independent scientific TRAIN. Run from the repo root:
python -m scripts.run_coev_f0c_resource_preflight --mode smoke
python -m scripts.run_coev_f0c_resource_preflight --mode full
"""
from __future__ import annotations
import argparse
import json
import os
import platform
import resource
import sys
import time
from packages.concept_world import build_catalog
from packages.concept_learning import simulate_train,recommend_programs

def _vm_hwm_kib() -> int:
    try:
        with open("/proc/self/status",encoding="ascii") as fp:
            for line in fp:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except (FileNotFoundError,PermissionError,ValueError):
        pass
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

def _measure(action):
    start_wall=time.perf_counter()
    start_cpu=time.process_time()
    result=action()
    return result,{
        "wall_seconds":round(time.perf_counter()-start_wall,6),
        "cpu_seconds":round(time.process_time()-start_cpu,6),
        # Process high-water mark is GLOBAL, not a per-phase RSS delta.
        "process_vm_hwm_kib":_vm_hwm_kib(),
    }

def run(mode: str) -> dict[str,object]:
    if type(mode) is not str or mode not in ("smoke","full"):
        raise ValueError("Only PUBLIC synthetic smoke/full resource preflights")
    if platform.system() != "Linux":
        raise RuntimeError("Linux-only VmHWM measurement")
    task_count=8 if mode=="smoke" else 256
    catalog,cold=_measure(build_catalog)
    _,warm=_measure(build_catalog)
    random_train,random_timing=_measure(lambda:simulate_train(20261031,task_count,"random"))
    active_train,active_timing=_measure(lambda:simulate_train(20261031,task_count,"active"))
    episodes,snapshot=active_train
    e=episodes[0]
    possible=tuple(i for i,row in enumerate(catalog.class_signatures)
        if all(row[q]==answer for q,answer in zip(e.public_input_ids,e.public_answers)))
    repeats=4 if mode=="smoke" else 32
    ranked,rank_time=_measure(lambda:[recommend_programs(
        snapshot,catalog,e.public_input_ids,e.public_answers,possible) for _ in range(repeats)])
    if not ranked or not ranked[-1]:
        raise AssertionError("Synthetic candidate ranking invalid")
    return {
        "status":"ENGINEERING_ONLY_UNSCORED",
        "mode":mode,"data_source":"invented_same_process_seed_20261031",
        "python":sys.version.split()[0],"platform":platform.platform(),
        "cpu_count_reported":os.cpu_count(),
        "catalog_classes":len(catalog.representatives),
        "task_count_per_arm":task_count,"ranking_repeats":repeats,
        "cold_catalog":cold,"warm_cached_catalog":warm,
        "train_random":random_timing,"train_active":active_timing,
        "candidate_rank":rank_time,"rank_input_candidates":len(possible),
        "rss_warning":"VmHWM is whole-process cumulative high water, NOT per-arm incremental peak",
        "cost_warning":"Do not extrapolate 8/256 toy tasks to a verified FINAL budget",
        "scientific_source_or_score_used":False,
        "formal_train_eligible":False,
    }

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("smoke","full"),default="smoke")
    args=parser.parse_args()
    print(json.dumps(run(args.mode),sort_keys=True,separators=(",",":")))
    return 0

if __name__=="__main__":
    raise SystemExit(main())

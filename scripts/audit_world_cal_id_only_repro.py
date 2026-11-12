#!/usr/bin/env python3
"""Synthetic-only ID-only E2E reproducibility, no CAL tags, splits or seeds.

Two fresh interpreters with different hash randomization run the *entire*
four-feature / five-parent-fold / multinomial fit / 999-label-permutation
path. The emitted digest covers canonical input and complete output. The
fixture uses public literal strings and SHA256 ordering, never a secret PRF.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from world_cal.id_only import id_only_permutation_test, PERMUTATIONS

DOMAIN = "WORLD-CAL-ID-ONLY-SYNTHETIC-NONSECRET-v1"
def canonical(obj):
    return (json.dumps(obj, ensure_ascii=True, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")

def fixture():
    # Forty artificial labels distributed across ten artificial parent clusters.
    labels = [i % 4 for i in range(40)]
    parents = ["SYNTH-PARENT-%02d" % (i // 4) for i in range(40)]
    tags = [("fixture-" + hashlib.sha256(
        ("%s:TAG:%02d" % (DOMAIN, i)).encode("ascii")).hexdigest()[:20])
            for i in range(40)]
    permutations = []
    for trial in range(PERMUTATIONS):
        # Rank by independent, explicitly PUBLIC synthetic SHA256 expressions;
        # this is not a CAL tag-reissue or registered randomness simulation.
        order = sorted(range(len(labels)), key=lambda i: (
            hashlib.sha256(("%s:PERM:%04d:%02d" % (DOMAIN, trial, i))
                           .encode("ascii")).digest(), i))
        permutations.append([labels[i] for i in order])
    return tags, labels, parents, permutations

def child():
    tags, labels, parents, permutations = fixture()
    result = id_only_permutation_test(tags, labels, parents, permutations)
    payload = {
        "kind": "SYNTHETIC_ID_ONLY_E2E_NOT_CAL",
        "fixture_domain": DOMAIN,
        "input_sha256": hashlib.sha256(canonical({
            "tags": tags, "labels": labels, "parents": parents,
            "permutations": permutations})).hexdigest(),
        "observed_macro_auc_binary64": result["observed_macro_auc"].hex(),
        "null_p95_binary64": result["null_p95"].hex(),
        "null_repetitions": result["null_repetitions"],
        "id_signal_above_null": result["id_signal_above_null"],
    }
    payload["result_digest"] = "sha256:" + hashlib.sha256(canonical(payload)).hexdigest()
    sys.stdout.buffer.write(canonical(payload))

def verify(output):
    byte_results = []
    for hash_seed in ("1", "8675309"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed,
                   OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                   MKL_NUM_THREADS="1")
        completed = subprocess.run(
            [sys.executable, __file__, "--child"], capture_output=True,
            env=env, check=True)
        byte_results.append(completed.stdout)
    if byte_results[0] != byte_results[1]:
        raise SystemExit("STOP_UNKNOWN: independent ID-only child digests differ")
    result = json.loads(byte_results[0])
    if result["null_repetitions"] != 999:
        raise SystemExit("STOP_UNKNOWN: incorrect permutation count")
    if output:
        Path(output).write_bytes(byte_results[0])
    print(json.dumps({"status": "SYNTHETIC_REPRO_PASS_TWO_PROCESSES",
                      "result_digest": result["result_digest"],
                      "input_sha256": result["input_sha256"],
                      "python": sys.version.split()[0],
                      "platform": sys.platform}, sort_keys=True))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--child", action="store_true")
    p.add_argument("--output")
    args = p.parse_args()
    if args.child:
        child()
    else:
        verify(args.output)

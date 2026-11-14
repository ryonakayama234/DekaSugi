"""Run only the explicit invented stage-A/B suite and write an engineering receipt."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "packages/sentence_revision/__init__.py",
    "packages/sentence_revision/foundation.py",
    "tests/test_sentence_revision_a.py",
    "packages/sentence_revision/arms.py",
    "tests/test_sentence_revision_b.py",
    "scripts/verify_sentence_stage_b.py",
    ".github/workflows/sentence-revision-stage-b-synthetic.yml",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True))
    source_hashes = {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu = usage.ru_utime + usage.ru_stime
    suite = unittest.defaultTestLoader.loadTestsFromNames(
        ["tests.test_sentence_revision_a", "tests.test_sentence_revision_b"])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    from packages.sentence_revision import Snapshot, grammar_digest
    from packages.sentence_revision import Meter, State
    from packages.sentence_revision.arms import ARMS, Case, Example
    meter = Meter()
    arm_evidence = {}
    def ex(text, erase):
        before = State(tuple(text), 2)
        after = State(tuple(text[:2] + text[3:]), 2) if erase else before
        return Example(before, after)
    for arm in ARMS:
        first = len(meter.receipts)
        learner = Case.create(arm, "artificial-opaque", "invented initial text",
                              (ex("ABCD", False), ex("AAAA", True)), meter=meter)
        before = learner.save()
        learner.correct("invented clarification", ex("ABAC", False))
        after = learner.save()
        prediction = learner.predict(State(tuple("CDAB"), 2))
        # Saved diagnostic bytes must survive execution unchanged for every arm.
        if learner.save() != after:
            raise AssertionError("prediction mutated case")
        arm_evidence[arm] = {
            "before_sha256": sha256(before).hexdigest(),
            "after_sha256": sha256(after).hexdigest(),
            "artificial_prediction": prediction,
            "phases": meter.receipts[first:],
        }
    receipt = {
        "schema": "sentence-stage-b-artificial-check/1",
        "status": "pass" if result.wasSuccessful() else "fail",
        "source_commit": source_commit, "dirty_worktree": dirty,
        "source_sha256": source_hashes,
        "artificial_arm_evidence": arm_evidence, "shared_counts": meter.counts,
        "python": platform.python_version(), "platform": platform.platform(),
        "test_modules": ["tests.test_sentence_revision_a", "tests.test_sentence_revision_b"], "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "grammar_sha256": grammar_digest(),
        "all_candidates_snapshot_sha256": sha256(Snapshot(tuple(f"cond-{i:03d}" for i in range(78))).encode()).hexdigest(),
        "cpu_seconds_parent": time.process_time() - start_cpu,
        "cpu_seconds_children": usage.ru_utime + usage.ru_stime - child_cpu,
        "wall_seconds": time.perf_counter() - start_wall,
        "independent_supervisor_acceptance": "pending",
        "official_predictions": "not_run", "official_scoring": "not_run",
        "stage_a_acceptance": "PR214/6881127124",
        "stage_b": "implemented_artificial_only", "stage_c": "not_implemented",
        "production_table": "not_prepared",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

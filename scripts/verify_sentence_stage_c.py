"""Explicit artificial A/B/C suites and exportable C fixture artifacts only."""
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
MODULES = ("tests.test_sentence_revision_a", "tests.test_sentence_revision_b", "tests.test_sentence_revision_c")
SOURCES = tuple("packages/sentence_revision/" + f for f in (
    "__init__.py", "foundation.py", "arms.py", "artifacts.py", "runner.py", "evaluator.py", "report.py")) + (
    "tests/test_sentence_revision_a.py", "tests/test_sentence_revision_b.py", "tests/test_sentence_revision_c.py",
    "tests/sentence_revision_c_fixture.py", "scripts/verify_sentence_stage_c.py",
    ".github/workflows/sentence-revision-stage-c-synthetic.yml")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--artifacts", required=True, help="new directory for artificial fixture artifacts")
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True))
    hashes = {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    prior = resource.getrusage(resource.RUSAGE_CHILDREN)
    suite = unittest.defaultTestLoader.loadTestsFromNames(MODULES)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    from packages.sentence_revision import Meter
    from packages.sentence_revision.evaluator import run_artificial, SETTINGS
    from tests.sentence_revision_c_fixture import fixtures
    meter = Meter()
    run = run_artificial(fixtures(), Path(args.artifacts), meter=meter)
    now = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = {
        "schema": "sentence-stage-c-artificial-check/1",
        "status": "pass" if result.wasSuccessful() and run["status"] == "complete" else "fail",
        "source_commit": commit, "dirty_worktree": dirty, "source_sha256": hashes,
        "python": platform.python_version(), "platform": platform.platform(),
        "test_modules": MODULES, "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
        "cpu_seconds_parent": time.process_time() - start_cpu,
        "cpu_seconds_children": now.ru_utime + now.ru_stime - prior.ru_utime - prior.ru_stime,
        "wall_seconds": time.perf_counter() - start_wall,
        "artificial_run_status": run["status"], "settings": SETTINGS,
        "artificial_run_final_cost": run.get("final_cost"),
        "artificial_prediction_hashes": {p.name: sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(args.artifacts).iterdir()) if p.name.startswith(("row-", "snapshot-", "before-seal-")) or p.name == "report.md"},
        "all_artifact_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(Path(args.artifacts).iterdir())},
        "cost_attribution_complete": all("scope" in p for p in meter.receipts),
        "stage_a_acceptance": "PR214/6881127124", "stage_b_acceptance": "PR215/6889951868",
        "stage_c_supervisor_acceptance": "pending", "official_predictions": "not_run",
        "official_scoring": "not_run", "production_table": "not_prepared",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k:receipt[k] for k in ("status", "source_commit", "tests_run", "failures", "errors", "skipped", "cpu_seconds_parent", "cpu_seconds_children", "wall_seconds", "artificial_run_final_cost")}))
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

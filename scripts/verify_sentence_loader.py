"""Explicit invented-only A/B/C and external-loader verification receipt."""
import argparse
from hashlib import sha256
import importlib.util
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
MODULES = ('tests.test_sentence_revision_a', 'tests.test_sentence_revision_b',
           'tests.test_sentence_revision_c', 'tests.test_sentence_loader')
NEW_SOURCES = ('scripts/run_sentence_revision.py', 'scripts/verify_sentence_loader.py',
               'tests/test_sentence_loader.py', 'tests/sentence_loader_fixture.py',
               '.github/workflows/sentence-revision-loader-synthetic.yml')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location('loader_verify', ROOT / NEW_SOURCES[0])
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    lock = loader.verify_source()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True))
    prior = resource.getrusage(resource.RUSAGE_CHILDREN)
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(MODULES))
    now = resource.getrusage(resource.RUSAGE_CHILDREN)
    unchanged = loader.verify_source()['source_sha256'] == lock['source_sha256']
    receipt = {'schema': 'sentence-loader-synthetic-verification/1',
               'status': 'pass' if result.wasSuccessful() and unchanged else 'fail',
               'source_commit': commit, 'dirty_worktree_at_start': dirty,
               'python': platform.python_version(), 'platform': platform.platform(),
               'source_lock_sha256': loader.LOCK_SHA, 'accepted_commit': loader.ACCEPTED_COMMIT,
               'pinned_source_files_unchanged': unchanged, 'pinned_source_sha256': lock['source_sha256'],
               'loader_source_sha256': {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in NEW_SOURCES},
               'test_modules': list(MODULES), 'tests_run': result.testsRun,
               'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
               'cpu_seconds_parent': time.process_time() - start_cpu,
               'cpu_seconds_children': now.ru_utime + now.ru_stime - prior.ru_utime - prior.ru_stime,
               'wall_seconds': time.perf_counter() - start_wall,
               'synthetic_package': 'invented; not the production worksheet or frozen private package',
               'official_package_loaded': False, 'official_predictions': 0, 'official_scores': 0,
               'supervisor_loader_audit': 'pending', 'merge': 'not_authorized'}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k: receipt[k] for k in ('status', 'source_commit', 'tests_run', 'failures', 'errors', 'skipped',
                                            'cpu_seconds_parent', 'cpu_seconds_children', 'wall_seconds')}))
    return 0 if receipt['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())

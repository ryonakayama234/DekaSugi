"""External supervisor-VM loader; accepted sentence_revision sources are immutable.

CLI authenticates the authorized private manifest only. Internal synthetic tests
supply their own commitment to _run_package; they never load production data.
"""
import argparse
from hashlib import sha256
import importlib
import json
import math
import os
from pathlib import Path
import stat
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = 'experiments/SENTENCE-REVISION-1/preparation/source-lock-v1.json'
LOCK_SHA = '3d31660fe094cb00c83c4542aed1c8f98c222d4c5d792006d8f26f9e31813f96'
AUTHORIZED_MANIFEST_SHA = '163f11d38827af0c2908ce1d3dc250b11645ad6a509cf8768037f94be7149c06'
ACCEPTED_COMMIT = '3f60aac8de70af9e9575d25bc72009b0c30d89f6'
CASE_IDS = ('R01', 'R02', 'R03', 'R04')
PAYLOADS = ('public-initial.json', 'disclosure-corrections.json', 'evaluator-only-unseen.json')
ROLES = ('unseen_related', 'unseen_previous_application', 'unseen_near_counterexample')
MANIFEST_KEYS = {'schema', 'status', 'frozen_at', 'source_pin', 'files_sha256',
                 'choices_sha256', 'texts_sha256', 'split', 'presentation_order',
                 'structural_check', 'structural_note', 'provenance', 'custody',
                 'official_predictions', 'official_scoring', 'production_run'}
LIMIT = 65536
RENDER_PREFIX = ('# SENTENCE-REVISION-1 — artificial engineering report\n\n'
                 '人工fixtureのみ。固定renderer。独立単位は4ケース。192予定出力中、主診断は未見96出力。\n\n')


class LoaderFault(ValueError):
    """Only fixed error codes; never include private payload contents."""


def _canonical(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise LoaderFault('duplicate_json_key')
        result[key] = value
    return result


def _decode(raw):
    def reject_constant(_):
        raise LoaderFault('nonfinite_json')
    try:
        return json.loads(raw, object_pairs_hook=_unique, parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise LoaderFault('invalid_json') from exc


def _read(path):
    # No symlinks, FIFO/devices, unbounded reads or path names from manifest data.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > LIMIT:
            raise LoaderFault('input_file_type_or_size')
        raw = stream.read(LIMIT + 1)
        if len(raw) > LIMIT or len(raw) != info.st_size:
            raise LoaderFault('input_file_size_changed')
        return raw


def _keys(value, required, optional=()):
    if (type(value) is not dict or not set(required) <= set(value)
            or not set(value) <= set(required) | set(optional)):
        raise LoaderFault('input_object_shape')


def _sha(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def verify_source(root=ROOT):
    raw = _read(root / LOCK_PATH)
    if sha256(raw).hexdigest() != LOCK_SHA:
        raise LoaderFault('source_lock_mismatch')
    lock = _decode(raw)
    if lock['accepted_commit'] != ACCEPTED_COMMIT or len(lock['source_sha256']) != 13:
        raise LoaderFault('source_lock_identity')
    for name, expected in lock['source_sha256'].items():
        if sha256(_read(root / name)).hexdigest() != expected:
            raise LoaderFault('pinned_source_mismatch')
    return lock


def _runtime():
    # main() runs in an isolated fresh interpreter with an unused pycache prefix.
    # Tests may import the same trusted modules beforehand to observe boundaries.
    if sha256(_read(ROOT / 'packages/__init__.py')).hexdigest() != '22d4d6ce91d1c3f466ea15c4a9255561d79e570e978256934cf352cd1e6123eb':
        raise LoaderFault('bootstrap_package_source_mismatch')
    modules = {name: importlib.import_module('packages.sentence_revision.' + name)
               for name in ('foundation', 'arms', 'artifacts', 'runner', 'evaluator', 'report')}
    for name, module in modules.items():
        if Path(module.__file__).resolve() != ROOT / 'packages/sentence_revision' / (name + '.py'):
            raise LoaderFault('runtime_import_origin')
    return modules


def _payloads(package, expected_sha, lock):
    if not _sha(expected_sha):
        raise LoaderFault('invalid_manifest_commitment')
    manifest_raw = _read(package / 'manifest.json')
    if sha256(manifest_raw).hexdigest() != expected_sha:
        raise LoaderFault('manifest_mismatch')
    manifest = _decode(manifest_raw)
    _keys(manifest, MANIFEST_KEYS)
    pin = manifest['source_pin']
    _keys(pin, ('accepted_commit', 'source_lock_sha256', 'grammar_sha256'))
    if pin != {'accepted_commit': ACCEPTED_COMMIT, 'source_lock_sha256': LOCK_SHA,
               'grammar_sha256': lock['grammar_sha256']}:
        raise LoaderFault('manifest_source_pin_mismatch')
    _keys(manifest['files_sha256'], PAYLOADS)
    data = []
    for filename in PAYLOADS:
        raw = _read(package / filename)
        expected = manifest['files_sha256'][filename]
        if not _sha(expected) or sha256(raw).hexdigest() != expected:
            raise LoaderFault('payload_hash_mismatch')
        value = _decode(raw)
        _keys(value, CASE_IDS)
        data.append(value)
    # Hash authenticates opaque fields too; no guessed choices/text/split encoding.
    return manifest, data


def _normalize(data, runtime, meter):
    f, a, r, e = (runtime[n] for n in ('foundation', 'arms', 'runner', 'evaluator'))
    initial, corrections, unseen = data
    gold, disclosures, publics, seen = [], [], [], set()
    for case_id in CASE_IDS:
        first, correction, hidden = initial[case_id], corrections[case_id], unseen[case_id]
        _keys(first, ('intended_case_role', 'initial_text', 'initial_examples'))
        _keys(correction, ('correction_text', 'correction_example', 'custody'))
        _keys(hidden, ('unseen',), ('intended_rule_id', 'intended_rule_ast'))
        if (type(first['initial_examples']) is not list or len(first['initial_examples']) != 2
                or type(hidden['unseen']) is not list or len(hidden['unseen']) != 3):
            raise LoaderFault('example_count')
        pairs, probes, outputs = [], [], []
        rows = [*first['initial_examples'], correction['correction_example'], *hidden['unseen']]
        for p, row in enumerate(rows):
            keys = ('example_id', 'before', 'after') if p < 3 else ('example_id', 'role', 'before', 'gold_after')
            _keys(row, keys)
            if row['example_id'] != f'{case_id}-{p + 1:02d}':
                raise LoaderFault('example_id_or_probe_order')
            if p >= 3 and row['role'] != ROLES[p - 3]:
                raise LoaderFault('unseen_role_or_probe_order')
            before = f.State.parse(row['before'])
            after = f.State.parse(row['after' if p < 3 else 'gold_after'])
            pair = a.Example(before, after)
            pair.record()  # Complete permitted final states; no hypothesis fitting.
            key = _canonical(before.record())
            if key in seen:
                raise LoaderFault('duplicate_input_state')
            seen.add(key)
            pairs.append(pair)
            probes.append(before)
            outputs.append(after)
        public = r.PublicCase(case_id, first['initial_text'], tuple(pairs[:2]), probes[2], tuple(probes[3:]))
        parent = e.GoldCase(public, correction['correction_text'], outputs[2], tuple(outputs[3:]),
                            first['intended_case_role'])
        gold.append(parent.record())
        publics.append(public.record())
        disclosures.append({'text': correction['correction_text'], 'example': pairs[2].record()})
        # Exclude ignored metadata from all downstream inputs/artifacts.
        meter.checkpoint((data, gold, publics, disclosures))
    return gold, publics, disclosures


def _public(value, runtime):
    a, f, r = (runtime[n] for n in ('arms', 'foundation', 'runner'))
    return r.PublicCase(value['rule_id'], value['text'],
                        tuple(a.Example.parse(x) for x in value['initial']),
                        f.State.parse(value['correction_input']),
                        tuple(f.State.parse(x) for x in value['unseen_inputs']))


def _exclusive(path, value):
    raw = _canonical(value)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    # Persist the directory entry as well as its bytes on supervisor Linux VM.
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _collect(store, meter, runtime):
    r, a, io = (runtime[n] for n in ('runner', 'arms', 'artifacts'))
    for i in range(4):
        record = store.read(f'public-c{i}.json')
        with io.attributed(meter, f'case{i}/loader'), meter.phase('loader-public'):
            public = _public(record, runtime)
            meter.checkpoint(record)
        del record
        episode = r.Episode(public, i, meter=meter, store=store)
        del public
        episode.before()
        # Withheld correction output/text are not supplied before the before seal.
        disclosure = store.read(f'private-disclosure-c{i}.json', retained=episode.roots())
        with io.attributed(meter, f'case{i}/loader'), meter.phase('loader-disclosure'):
            example = a.Example.parse(disclosure['example'])
            meter.checkpoint(episode.roots(disclosure))
        episode.after(disclosure['text'], example)
        del disclosure, example, episode


def _finish(store, meter, runtime, freeze_sha, seal_sha, mode, manifest_sha, start_wall, prior_cpu):
    io, f = (runtime[n] for n in ('artifacts', 'foundation'))
    # Pinned entry keeps its exclusive score-started latch and gold validation.
    results = runtime['evaluator'].score_batch(store, meter=meter,
                    expected_freeze_sha=freeze_sha, expected_seal_sha=seal_sha)
    retained = (results, freeze_sha, seal_sha, mode, manifest_sha)
    fixed_report = runtime['report'].render(results, meter=meter)
    store.write('frozen-renderer.md', fixed_report, retained=retained, text=True)
    with io.attributed(meter, 'shared/loader-report'), meter.phase('loader-report'):
        if not fixed_report.startswith(RENDER_PREFIX):
            raise LoaderFault('frozen_renderer_preamble_mismatch')
        report = (f'# SENTENCE-REVISION-1 — {mode}\n\n'
                  f'Manifest SHA-256: {manifest_sha}\n\n'
                  '固定rendererの数表・本文を使用。独立単位4ケース、予定192出力、主診断は未見96出力。\n\n'
                  + fixed_report[len(RENDER_PREFIX):])
        meter.checkpoint((retained, fixed_report, report))
    del fixed_report
    store.write('report.md', report, retained=retained, text=True)
    del report
    with io.attributed(meter, 'shared/loader-results'), meter.phase('loader-results'):
        summary = {'schema': 'sentence-loader-results/1', 'mode': mode,
                   'status': 'scored_pending_completion', 'manifest_sha256': manifest_sha,
                   'source_lock_sha256': LOCK_SHA, 'freeze_sha256': freeze_sha,
                   'predictions_seal_sha256': seal_sha, 'cases': results,
                   'independent_cases': 4, 'planned_rows': 192, 'main_unseen_rows': 96,
                   'prior_cpu_seconds': prior_cpu,
                   'authoritative_status': 'completion.json required; stop.json overrides partial outputs',
                   'cost_receipts': 'cost-receipts-NNN.json shards and completion.json tail'}
        meter.checkpoint((retained, summary))
    store.write('results.json', summary, retained=retained)
    del summary
    boundary = len(meter.receipts)
    for offset in range(0, boundary, 128):
        store.write(f'cost-receipts-{offset // 128:03d}.json',
                    meter.receipts[offset:min(offset + 128, boundary)], retained=retained)
    with io.attributed(meter, 'shared/loader-completion'), meter.phase('loader-completion'):
        completion = {'status': 'complete', 'mode': mode, 'manifest_sha256': manifest_sha,
                      'source_lock_sha256': LOCK_SHA, 'artifact_index': dict(store.index),
                      'counts': meter.counts.copy(), 'phase_receipts_tail': list(meter.receipts[boundary:]),
                      'prior_cpu_seconds': prior_cpu,
                      'cpu_seconds_including_prior': time.process_time() - meter._start,
                      'wall_seconds': time.perf_counter() - start_wall}
        meter.checkpoint((retained, completion))
    store.write('completion.json', completion, retained=retained)
    # CLI never returns results, text, states or gold to stdout.
    return {'status': 'complete', 'mode': mode, 'planned_rows': 192, 'main_unseen_rows': 96,
            'manifest_sha256': manifest_sha, 'prior_cpu_seconds': prior_cpu,
            'cpu_seconds_including_prior': time.process_time() - meter._start,
            'wall_seconds': time.perf_counter() - start_wall, 'counts': meter.counts.copy()}


def _run_package(package, root, *, manifest_sha, prior_cpu_seconds, start_cpu=None):
    """Internal engine; CLI fixes manifest_sha to the authorized commitment.

    Other commitments produce synthetic_loader_check mode only. This test seam
    is not an official manifest override and cannot label such runs official.
    """
    start_cpu = time.process_time() if start_cpu is None else start_cpu
    start_wall = time.perf_counter()
    store = meter = None
    mode = 'official_supervisor_vm' if manifest_sha == AUTHORIZED_MANIFEST_SHA else 'synthetic_loader_check'
    try:
        if (type(prior_cpu_seconds) not in (int, float) or not math.isfinite(prior_cpu_seconds)
                or not 0 <= prior_cpu_seconds < 7200):
            raise LoaderFault('invalid_prior_cpu_debit')
        package, root = Path(package), Path(root)
        if package.is_symlink() or not package.is_dir():
            raise LoaderFault('package_directory')
        if (package.resolve().is_relative_to(ROOT) or root.resolve().is_relative_to(ROOT)
                or root.resolve().is_relative_to(package.resolve())):
            raise LoaderFault('private_paths_must_be_outside_checkout_and_separate')
        if root.exists() or root.is_symlink():
            raise LoaderFault('run_root_must_not_exist')
        lock = verify_source()
        runtime = _runtime()
        f, io, e, r = (runtime[n] for n in ('foundation', 'artifacts', 'evaluator', 'runner'))
        meter = f.Meter()
        # Include import, preflight and historical preparation in the same cap.
        meter._start = start_cpu - prior_cpu_seconds
        bootstrap_cpu = time.process_time() - start_cpu
        meter.receipts.append({'phase': 'loader-bootstrap', 'scope': 'shared/loader-bootstrap',
                               'status': 'complete' if bootstrap_cpu < meter.phase_cpu else 'budget_exhausted',
                               'cpu_seconds': bootstrap_cpu, 'wall_seconds': time.perf_counter() - start_wall,
                               'counts': dict.fromkeys(meter.counts, 0)})
        if bootstrap_cpu >= meter.phase_cpu:
            raise f.BudgetExceeded('loader bootstrap phase CPU cap')
        with io.attributed(meter, 'shared/loader-preflight'), meter.phase('loader-preflight'):
            if (e.SETTINGS != lock['settings'] or io.digest(e.SETTINGS) != lock['settings_sha256']
                    or f.grammar_digest(meter) != lock['grammar_sha256']):
                raise LoaderFault('runtime_settings_or_grammar_mismatch')
            manifest, data = _payloads(package, manifest_sha, lock)
            meter.checkpoint((manifest, data))
            gold, publics, disclosures = _normalize(data, runtime, meter)
            meter.checkpoint((manifest, data, gold, publics, disclosures))
        del data, lock
        # No files/root/latch created until the entire package and all sources pass.
        store = io.Artifacts(root, meter)
        latch = package / ('.sentence-revision-' + manifest_sha + '.started')
        with io.attributed(meter, 'shared/loader-activation'), meter.phase('loader-activation'):
            activation = {'schema': 'sentence-loader-started/1', 'mode': mode,
                          'manifest_sha256': manifest_sha, 'source_lock_sha256': LOCK_SHA,
                          'run_root': str(root.resolve()), 'retry_allowed': False}
            meter.checkpoint((manifest, gold, publics, disclosures, activation))
            _exclusive(latch, activation)  # Persistent even if any later step fails.
        store.write('run-started.json', activation, retained=(manifest, gold, publics, disclosures))
        del activation
        with io.attributed(meter, 'shared/loader-freeze'), meter.phase('loader-freeze'):
            planned = r.schedule()
            freeze = {'schema': 'sentence-local-freeze/1', 'mode': mode,
                      'manifest_sha256': manifest_sha, 'source_lock_sha256': LOCK_SHA,
                      'settings': e.SETTINGS, 'grammar_sha256': f.grammar_digest(meter),
                      'source_sha256': e.source_hashes(), 'gold_sha256': io.digest(gold),
                      'public_sha256': io.digest(publics), 'schedule': planned}
            meter.checkpoint((manifest, gold, publics, disclosures, planned, freeze))
        live = (manifest, gold, publics, disclosures, planned, freeze)
        store.write('input-manifest.json', manifest, retained=live)
        store.write('schedule.json', planned, retained=live)
        store.write('private-gold.json', gold, retained=live)
        for i in range(4):
            store.write(f'public-c{i}.json', publics[i], retained=live)
            store.write(f'private-disclosure-c{i}.json', disclosures[i], retained=live)
        store.write('freeze.json', freeze, retained=live)
        freeze_sha = io.digest(freeze)
        del live, manifest, gold, publics, disclosures, planned, freeze
        _collect(store, meter, runtime)
        with io.attributed(meter, 'shared/loader-seal'), meter.phase('loader-seal'):
            names = sorted(n for n in store.index if n.startswith(('row-', 'snapshot-', 'before-seal-')))
            seal = {'freeze_sha256': freeze_sha, 'artifacts': {n: store.index[n] for n in names}}
            meter.checkpoint(seal)
        store.write('predictions-seal.json', seal)
        seal_sha = io.digest(seal)
        del seal, names
        # All13 sources/lock still must agree immediately before scoring.
        with io.attributed(meter, 'shared/loader-recheck'), meter.phase('loader-recheck'):
            verify_source()
        return _finish(store, meter, runtime, freeze_sha, seal_sha, mode, manifest_sha,
                       start_wall, prior_cpu_seconds)
    except BaseException as exc:
        # Every post-activation failure consumes the latch. No rich rendering or retry.
        code = str(exc) if type(exc) is LoaderFault else type(exc).__name__
        resource_stop = meter is not None and isinstance(exc, runtime['foundation'].BudgetExceeded)
        receipt = {'status': 'resource_stop' if resource_stop else ('invalid' if store else 'preflight_rejected'),
                   'reason_code': code, 'mode': mode, 'retry_allowed': False,
                   'planned_rows': 192, 'main_unseen_rows': 96,
                   'saved_prediction_files': 0 if store is None else len(list(store.root.glob('row-*.json'))),
                   'indexed_prediction_files': 0 if store is None else sum(n.startswith('row-') for n in store.index),
                   'last_phase': meter.receipts[-1] if meter is not None and meter.receipts else None,
                   'missing_slot_rule': 'schedule minus saved rows; no zero imputation',
                   'cpu_seconds_including_prior': time.process_time() - start_cpu + prior_cpu_seconds
                       if type(prior_cpu_seconds) in (int, float) and math.isfinite(prior_cpu_seconds) else None,
                   'wall_seconds': time.perf_counter() - start_wall}
        if store is not None:
            try:
                _exclusive(store.root / 'stop.json', receipt)
            except OSError:
                receipt['stop_receipt_write_failed'] = True
        return receipt


def main(argv=None):
    start_cpu = 0.0  # Fresh CLI: include interpreter startup and all module imports.
    parser = argparse.ArgumentParser(description='One supervisor-only SENTENCE-REVISION-1 run')
    parser.add_argument('--package', required=True, help='private four-file package directory')
    parser.add_argument('--run-root', required=True, help='new, nonexistent private directory outside checkout')
    parser.add_argument('--prior-cpu-seconds', required=True, type=float,
                        help='observed cumulative CPU already spent; subtracts from existing7200s cap')
    args = parser.parse_args(argv)
    if not sys.flags.isolated:
        print('{"status":"preflight_rejected","reason_code":"invoke_python_with_-I"}')
        return 2
    # Ignore PYTHONPATH/user site/current directory and any stale compiled cache.
    sys.path.insert(0, str(ROOT))
    sys.dont_write_bytecode = True
    with tempfile.TemporaryDirectory(prefix='sentence-loader-pycache-') as cache:
        sys.pycache_prefix = cache
        result = _run_package(args.package, args.run_root, manifest_sha=AUTHORIZED_MANIFEST_SHA,
                              prior_cpu_seconds=args.prior_cpu_seconds, start_cpu=start_cpu)
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True))
    return 0 if result['status'] == 'complete' else 2


if __name__ == '__main__':
    raise SystemExit(main())

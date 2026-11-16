"""Explicit invented-package tests of external activation, not production data."""
import concurrent.futures
import copy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from packages.sentence_revision import BudgetExceeded, Meter, State
from packages.sentence_revision.artifacts import Artifacts, digest
from packages.sentence_revision.arms import Case
from packages.sentence_revision import evaluator, runner
from tests.sentence_loader_fixture import documents, encode, fixture_cases, write_package

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sentence_loader', ROOT / 'scripts/run_sentence_revision.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.package = self.base / 'package'
        self.sha = write_package(self.package)
        self.root = self.base / 'run'

    def run_package(self, **kwargs):
        return loader._run_package(self.package, self.root, manifest_sha=self.sha,
                                   prior_cpu_seconds=kwargs.pop('prior_cpu_seconds', 12.5), **kwargs)

    def resave(self, docs):
        shutil.rmtree(self.package)
        self.sha = write_package(self.package, docs)

    def assert_no_activation(self):
        self.assertFalse(self.root.exists())
        self.assertFalse(list(self.package.glob('*.started')))
        self.assertFalse(list(self.package.glob('.*.started')))

    def test_success_and_frozen_orchestrator_equivalence(self):
        before = loader.verify_source()['source_sha256']
        result = self.run_package()
        self.assertEqual(result['status'], 'complete', result)
        self.assertEqual(result['mode'], 'synthetic_loader_check')
        self.assertGreaterEqual(result['cpu_seconds_including_prior'], 12.5)
        completion = json.loads((self.root / 'completion.json').read_bytes())
        self.assertEqual(completion['manifest_sha256'], self.sha)
        self.assertEqual(len(list(self.root.glob('row-*.json'))), 192)
        self.assertEqual(len(list(self.root.glob('snapshot-*.json'))), 32)
        self.assertEqual(len(list(self.root.glob('before-seal-*.json'))), 4)
        self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
        self.assertEqual(len(list(self.package.glob('.*.started'))), 1)
        direct_root = self.base / 'direct'
        direct = evaluator.run_artificial(fixture_cases(), direct_root, meter=Meter())
        self.assertEqual(direct['status'], 'complete', direct)
        for path in self.root.glob('row-*.json'):
            self.assertEqual(path.read_bytes(), (direct_root / path.name).read_bytes())
        for path in self.root.glob('snapshot-*.json'):
            self.assertEqual(path.read_bytes(), (direct_root / path.name).read_bytes())
        actual = json.loads((self.root / 'results.json').read_bytes())
        self.assertEqual(actual['cases'], direct['results'])
        fixed = (self.root / 'frozen-renderer.md').read_text()
        report = (self.root / 'report.md').read_text()
        self.assertTrue(fixed.startswith(loader.RENDER_PREFIX))
        self.assertTrue(report.endswith(fixed[len(loader.RENDER_PREFIX):]))
        self.assertNotIn('artificial engineering report', report)
        self.assertEqual(loader.verify_source()['source_sha256'], before)

    def test_manifest_and_each_payload_tampering_never_predict(self):
        for name in ('manifest.json', *loader.PAYLOADS):
            with self.subTest(name=name):
                path = self.package / name
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                with patch.object(Case, 'create', side_effect=AssertionError('must not learn')) as create:
                    result = self.run_package()
                    self.assertEqual(result['status'], 'preflight_rejected', result)
                    create.assert_not_called()
                self.assert_no_activation()
                path.write_bytes(original)

    def test_source_and_lock_mismatch(self):
        lock = loader.verify_source()
        target = self.base / 'copied-sources'
        for name in (loader.LOCK_PATH, *lock['source_sha256']):
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
        for name in (loader.LOCK_PATH, *lock['source_sha256']):
            with self.subTest(path=name):
                path = target / name
                original = path.read_bytes()
                path.write_bytes(original + b'\n')
                with self.assertRaises(loader.LoaderFault):
                    loader.verify_source(target)
                path.write_bytes(original)
        with patch.object(loader, 'verify_source', side_effect=loader.LoaderFault('pinned_source_mismatch')):
            with patch.object(loader, '_runtime') as imported:
                self.assertEqual(self.run_package()['status'], 'preflight_rejected')
                imported.assert_not_called()
        self.assert_no_activation()

    def test_manifest_pin_and_file_mapping_mismatch(self):
        for field, value in (('source_pin', {}), ('files_sha256', {'../secret': '0' * 64})):
            shutil.rmtree(self.package)
            self.sha = write_package(self.package, edit_manifest=lambda m: m.update({field: value}))
            result = self.run_package()
            self.assertEqual(result['status'], 'preflight_rejected', result)
            self.assert_no_activation()

    def test_invalid_shapes_ids_roles_states_and_extra_case(self):
        for change in range(9):
            docs = documents()
            if change == 0:
                docs[0]['R01']['initial_examples'][0]['before']['cursor'] = True
            elif change == 1:
                docs[0]['R01']['initial_examples'][0]['example_id'] = 'R01-02'
            elif change == 2:
                docs[2]['R01']['unseen'][0]['role'] = 'unseen_previous_application'
            elif change == 3:
                docs[2]['R01']['unseen'].reverse()
            elif change == 4:
                docs[0]['R01']['initial_examples'].pop()
            elif change == 5:
                docs[0]['R05'] = docs[0]['R04']
            elif change == 6:
                docs[0]['R01']['initial_examples'][0]['after']['clipboard'] = ['A']
            elif change == 7:
                docs[1]['R01']['correction_example']['before']['selection'] = [1, 1]
            else:
                docs[0]['R01']['intended_case_role'] = 'unknown'
            self.resave(docs)
            with self.subTest(change=change), patch.object(Case, 'create') as create:
                self.assertEqual(self.run_package()['status'], 'preflight_rejected')
                create.assert_not_called()
                self.assert_no_activation()

    def test_duplicate_input_across_cases_rejected(self):
        docs = documents()
        docs[0]['R02']['initial_examples'][0].update(
            {k: v for k, v in docs[0]['R01']['initial_examples'][0].items() if k != 'example_id'})
        self.resave(docs)
        result = self.run_package()
        self.assertEqual(result['reason_code'], 'duplicate_input_state', result)
        self.assert_no_activation()

    def test_duplicate_json_nonfinite_and_oversize_rejected(self):
        for raw in (b'{"R01":{},"R01":{}}', b'{"R01":NaN}', b' ' * (loader.LIMIT + 1)):
            path = self.package / loader.PAYLOADS[0]
            path.write_bytes(raw)
            manifest = json.loads((self.package / 'manifest.json').read_bytes())
            manifest['files_sha256'][path.name] = sha256(raw).hexdigest()
            raw_manifest = encode(manifest)
            (self.package / 'manifest.json').write_bytes(raw_manifest)
            self.sha = sha256(raw_manifest).hexdigest()
            self.assertEqual(self.run_package()['status'], 'preflight_rejected')
            self.assert_no_activation()

    def test_symlink_inputs_and_existing_roots_rejected(self):
        path = self.package / loader.PAYLOADS[0]
        other = self.base / 'other.json'
        path.rename(other)
        path.symlink_to(other)
        self.assertEqual(self.run_package()['status'], 'preflight_rejected')
        self.assert_no_activation()
        path.unlink()
        other.rename(path)
        for symlink in (False, True):
            if symlink:
                self.root.symlink_to(self.package, target_is_directory=True)
            else:
                self.root.mkdir()
            self.assertEqual(self.run_package()['status'], 'preflight_rejected')
            self.root.unlink() if symlink else self.root.rmdir()
        self.assert_no_activation()

    def test_ignored_metadata_and_gold_never_influence_predictions(self):
        self.assertEqual(self.run_package()['status'], 'complete')
        previous = {p.name: p.read_bytes() for p in self.root.glob('row-*.json')}
        docs = documents()
        for first in docs[0].values():
            first['intended_case_role'] = 'confirmation'
        for hidden in docs[2].values():
            hidden['intended_rule_id'] = {'arbitrary': ['not a condition']}
            hidden['intended_rule_ast'] = None
            for row in hidden['unseen']:
                b = State.parse(row['before'])
                deleted = State(b.buffer[:b.cursor] + b.buffer[b.cursor + 1:], b.cursor).record()
                row['gold_after'] = row['before'] if row['gold_after'] == deleted else deleted
        self.resave(docs)
        self.root = self.base / 'second'
        self.assertEqual(self.run_package()['status'], 'complete')
        self.assertEqual(previous, {p.name: p.read_bytes() for p in self.root.glob('row-*.json')})
        gold = (self.root / 'private-gold.json').read_text()
        self.assertNotIn('intended_rule', gold)
        self.assertNotIn('unseen_related', gold)

    def test_public_boundary_disclosure_order_and_all_outputs_before_score(self):
        seen = []
        create, before, after, score = Case.create, runner.Episode.before, runner.Episode.after, evaluator.score_batch
        def observe_create(arm, rule_id, text, examples, *, meter):
            self.assertTrue(all(type(x) is str for x in (arm, rule_id, text)))
            self.assertEqual(len(examples), 2)
            return create(arm, rule_id, text, examples, meter=meter)
        def observe_before(episode):
            self.assertEqual(set(episode.public.record()),
                {'rule_id', 'text', 'initial', 'correction_input', 'unseen_inputs'})
            return before(episode)
        def observe_after(episode, text, example):
            self.assertTrue((self.root / f'before-seal-c{episode.case_index}.json').is_file())
            self.assertFalse((self.root / 'score-started.json').exists())
            seen.append(episode.case_index)
            return after(episode, text, example)
        def observe_score(store, **kwargs):
            self.assertEqual(seen, [0, 1, 2, 3])
            self.assertEqual(len(list(self.root.glob('row-*.json'))), 192)
            self.assertTrue((self.root / 'predictions-seal.json').is_file())
            return score(store, **kwargs)
        with patch.object(Case, 'create', side_effect=observe_create), \
             patch.object(runner.Episode, 'before', observe_before), \
             patch.object(runner.Episode, 'after', observe_after), \
             patch.object(evaluator, 'score_batch', side_effect=observe_score) as scoring:
            self.assertEqual(self.run_package()['status'], 'complete')
            self.assertEqual(scoring.call_count, 1)

    def test_activation_and_existing_scorer_once_only(self):
        self.assertEqual(self.run_package()['status'], 'complete')
        saved = {p.name: p.read_bytes() for p in self.root.iterdir()}
        self.assertEqual(self.run_package()['status'], 'preflight_rejected')
        self.assertEqual(saved, {p.name: p.read_bytes() for p in self.root.iterdir()})
        self.root = self.base / 'attempt-second-root'
        with patch.object(runner.Episode, 'before') as predict:
            self.assertEqual(self.run_package()['status'], 'invalid')
            predict.assert_not_called()
        # The untouched pinned scorer also rejects fresh-Meter/reconstructed-store entry.
        source = self.base / 'run'
        store = object.__new__(Artifacts)
        store.root, store.meter, store.index = source, Meter(), {}
        freeze = json.loads((source / 'freeze.json').read_bytes())
        seal = json.loads((source / 'predictions-seal.json').read_bytes())
        with self.assertRaises(evaluator.Fault):
            evaluator.score_batch(store, meter=store.meter,
                                  expected_freeze_sha=digest(freeze), expected_seal_sha=digest(seal))

    def test_exclusive_package_activation_race(self):
        # Separate processes, not threads (CPU clocks and pinned Meters are process-local).
        code = '''import importlib.util,sys,json
s=importlib.util.spec_from_file_location('loader',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
print(json.dumps(m._run_package(sys.argv[2],sys.argv[3],manifest_sha=sys.argv[4],prior_cpu_seconds=0)))'''
        def launch(i):
            p = subprocess.run([sys.executable, '-c', code, str(ROOT / 'scripts/run_sentence_revision.py'),
                                str(self.package), str(self.base / f'race-{i}'), self.sha],
                               cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            statuses = [x['status'] for x in pool.map(launch, (0, 1))]
        self.assertEqual(sorted(statuses), ['complete', 'invalid'])

    def test_budget_and_failure_are_terminal(self):
        for at in ('before', 'after', 'score', 'report', 'completion'):
            with self.subTest(at=at):
                self.package = self.base / f'package-{at}'
                self.sha = write_package(self.package)
                self.root = self.base / f'run-{at}'
                if at in ('before', 'after'):
                    context = patch.object(runner.Episode, at, side_effect=BudgetExceeded('invented cap'))
                elif at == 'score':
                    context = patch.object(evaluator, 'score_batch', side_effect=BudgetExceeded('invented cap'))
                else:
                    original = Artifacts.write
                    def fail(store, name, value, **kwargs):
                        if name == ('report.md' if at == 'report' else 'completion.json'):
                            raise BudgetExceeded('invented cap')
                        return original(store, name, value, **kwargs)
                    context = patch.object(Artifacts, 'write', fail)
                with context:
                    result = self.run_package()
                self.assertEqual(result['status'], 'resource_stop', result)
                self.assertTrue((self.root / 'stop.json').exists())
                self.assertFalse((self.root / 'completion.json').exists())
                self.root = self.base / f'retry-{at}'
                with patch.object(runner.Episode, 'before') as predict:
                    self.assertEqual(self.run_package()['status'], 'invalid')
                    predict.assert_not_called()

    def test_actual_exhausted_lifetime_cpu_and_invalid_debits(self):
        with patch.object(Case, 'create') as create:
            result = self.run_package(prior_cpu_seconds=7199.9, start_cpu=time.process_time() - 1)
            self.assertEqual(result['status'], 'resource_stop', result)
            create.assert_not_called()
        self.assert_no_activation()
        for debit in (-1, 7200, True, float('nan'), float('inf')):
            self.assertEqual(self.run_package(prior_cpu_seconds=debit)['status'], 'preflight_rejected')
            self.assert_no_activation()

    def test_final_retained_roots_and_genuine_serialization_caps(self):
        from packages.sentence_revision.foundation import retained_size, canonical
        original = Artifacts.write
        for target in (None, 'results.json', 'cost-receipts-000.json', 'completion.json'):
            self.package = self.base / ('package-cap-' + str(target))
            self.sha = write_package(self.package)
            self.root = self.base / ('run-cap-' + str(target))
            observed = []
            def contains(value, wanted):
                if value is wanted:
                    return True
                if type(value) in (list, tuple):
                    return any(contains(x, wanted) for x in value)
                if type(value) is dict:
                    return any(contains(x, wanted) for x in value.values())
                return False
            def write(store, name, value, **kwargs):
                if name in ('frozen-renderer.md', 'report.md', 'results.json', 'completion.json') or name.startswith('cost-receipts-'):
                    import inspect
                    caller = inspect.currentframe().f_back
                    results = caller.f_locals['results']
                    self.assertTrue(contains(kwargs['retained'], results), name)
                    for dead in ('gold', 'publics', 'disclosures', 'planned', 'freeze', 'seal'):
                        self.assertNotIn(dead, caller.f_locals)
                    if name.startswith('cost-receipts-') or name == 'completion.json':
                        self.assertNotIn('summary', caller.f_locals)
                        self.assertNotIn('report', caller.f_locals)
                        self.assertNotIn('fixed_report', caller.f_locals)
                    del caller
                    observed.append(name)
                if name == target:
                    full = retained_size((kwargs['retained'], store.index, value, canonical(value)))
                    store.meter.max_bytes = min(1048576, full - 1)
                    self.assertGreater(full, store.meter.max_bytes)
                return original(store, name, value, **kwargs)
            with self.subTest(target=target), patch.object(Artifacts, 'write', write):
                result = self.run_package()
            self.assertTrue(observed)
            self.assertEqual(result['status'], 'complete' if target is None else 'resource_stop', result)
            if target is not None:
                self.assertFalse((self.root / target).exists())
                self.assertFalse((self.root / 'completion.json').exists())
                self.assertTrue((self.root / 'stop.json').exists())
                self.assertEqual(result['saved_prediction_files'], 192)

    def test_cli_cannot_override_official_commitment_or_leak_data(self):
        script = str(ROOT / 'scripts/run_sentence_revision.py')
        args = ['--package', str(self.package), '--run-root', str(self.root), '--prior-cpu-seconds', '0']
        p = subprocess.run([sys.executable, '-I', script, *args], capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)['reason_code'], 'manifest_mismatch')
        self.assertNotIn('SYNTHETIC', p.stdout + p.stderr)
        self.assert_no_activation()
        p = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, timeout=20)
        self.assertEqual(json.loads(p.stdout)['reason_code'], 'invoke_python_with_-I')
        p = subprocess.run([sys.executable, '-I', script, *args, '--manifest-sha256', self.sha],
                           capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 2)
        self.assert_no_activation()


if __name__ == '__main__':
    unittest.main()

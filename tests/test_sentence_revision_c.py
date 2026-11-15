"""Artificial boundary/ordering/completeness/budget checks, not a scientific trial."""
from dataclasses import replace
from hashlib import sha256
import inspect
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from packages.sentence_revision import BudgetExceeded, Fault, Meter, State, canonical
from packages.sentence_revision.arms import ARMS, Case
from packages.sentence_revision.artifacts import Artifacts, digest
from packages.sentence_revision.evaluator import (
    _validate_row, run_artificial, run_official, score_batch, SETTINGS,
)
from packages.sentence_revision.foundation import retained_size
from packages.sentence_revision.report import render
from packages.sentence_revision.runner import Episode, schedule
from tests.sentence_revision_c_fixture import fixtures


def load(root, name):
    return json.loads((Path(root) / name).read_bytes())


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()
        cls.root = Path(cls.temp.name) / "baseline"
        cls.meter = Meter()
        cls.result = run_artificial(fixtures(), cls.root, meter=cls.meter)
        if cls.result["status"] != "complete":
            raise AssertionError(cls.result)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def copied_store(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name) / "copy"
        shutil.copytree(self.root, root)
        store = object.__new__(Artifacts)
        store.root, store.meter = root, Meter()
        store.index = load(root, "completion.json")["artifact_index"]
        # Reconstruct an invented pre-score boundary, not a resumed real run.
        (root / "score-started.json").unlink()
        store.index.pop("score-started.json")
        return store

    def score(self, store):
        return score_batch(store, meter=store.meter,
                           expected_freeze_sha=self.result["freeze_sha256"],
                           expected_seal_sha=self.result["predictions_seal_sha256"])

    def test_full_192_rows_96_principal_and_32_snapshots(self):
        self.assertEqual(len(schedule()), 192)
        rows = [row for case in self.result["results"] for row in case["rows"]]
        self.assertEqual(len(rows), 192)
        self.assertEqual(len({r["slot"] for r in rows}), 192)
        self.assertEqual(sum(r["probe"] >= 3 for r in rows), 96)
        self.assertEqual(len(list(self.root.glob("snapshot-*.json"))), 32)
        self.assertEqual(load(self.root, "schedule.json"), schedule())
        self.assertEqual([c["intended_role"] for c in self.result["results"]], ["revise"] * 3 + ["confirmation"])
        for c in self.result["results"]:
            self.assertEqual(len(c["rows"]), 48)
            self.assertEqual(c["arms"]["FROZEN"]["before"], c["arms"]["FROZEN"]["after"])
            self.assertEqual(c["arms"]["MEMORY"]["unseen_before"], 0)
            self.assertEqual(c["arms"]["MEMORY"]["unseen_after"], 0)

    def test_independent_all_fields_score_recomputation_and_metrics(self):
        gold = load(self.root, "private-gold.json")
        for c in self.result["results"]:
            for row in c["rows"]:
                p = row["probe"]
                expected = (gold[c["case"]]["public"]["initial"][p]["after"] if p < 2
                            else gold[c["case"]]["correction_output"] if p == 2
                            else gold[c["case"]]["unseen_outputs"][p - 3])
                actual = row["output"]
                correct = row["status"] == "predicted" and all(actual[k] == expected[k] for k in ("buffer", "cursor", "selection", "clipboard"))
                self.assertEqual(row["correct"], correct)
            for a in ARMS:
                subset = [r for r in c["rows"] if r["arm"] == a]
                summary = c["arms"][a]
                for stage in ("before", "after"):
                    self.assertEqual(summary["unseen_" + stage], sum(r["correct"] for r in subset if r["stage"] == stage and r["probe"] >= 3))
                self.assertEqual(summary["delta"], summary["unseen_after"] - summary["unseen_before"])
        self.assertEqual([c["arms"]["REVISE"]["delta"] for c in self.result["results"]], [2, 2, 2, 0])

    def test_gold_only_change_cannot_change_prediction_bytes(self):
        changed = []
        for c in fixtures():
            opposite = []
            for before, after in zip(c.public.unseen_inputs, c.unseen_outputs):
                opposite.append(State(before.buffer[:2] + before.buffer[3:], 2) if after == before else before)
            changed.append(replace(c, unseen_outputs=tuple(opposite)))
        with TemporaryDirectory() as d:
            root = Path(d) / "altered-gold"
            result = run_artificial(tuple(changed), root, meter=Meter())
            self.assertEqual(result["status"], "complete", result)
            for path in self.root.iterdir():
                if path.name.startswith(("row-", "snapshot-", "before-seal-")):
                    self.assertEqual(path.read_bytes(), (root / path.name).read_bytes())
            self.assertNotEqual(result["results"][0]["arms"]["REVISE"]["unseen_after"], self.result["results"][0]["arms"]["REVISE"]["unseen_after"])

    def test_public_only_calls_one_meter_and_no_intermediate_scoring(self):
        import packages.sentence_revision.evaluator as ev
        events, identities = [], []
        original_predict, original_correct, original_score = Case.predict, Case.correct, ev.score_batch
        def predict(instance, value):
            self.assertIs(type(value), State)
            identities.append(instance._meter)
            events.append(("predict", len(instance._data["pairs"])))
            return original_predict(instance, value)
        def correct(instance, text, example):
            identities.append(instance._meter)
            events.append(("correct", instance._data["rule_id"]))
            return original_correct(instance, text, example)
        def score(*args, **kwargs):
            events.append(("score", len(list(args[0].root.glob("row-*.json")))))
            self.assertTrue((args[0].root / "predictions-seal.json").is_file())
            identities.append(kwargs["meter"])
            return original_score(*args, **kwargs)
        with TemporaryDirectory() as d, patch.object(Case, "predict", predict), patch.object(Case, "correct", correct), patch.object(ev, "score_batch", score):
            m = Meter()
            result = run_artificial(fixtures(), Path(d) / "spy", meter=m)
            self.assertEqual(result["status"], "complete", result)
            self.assertTrue(all(x is m for x in identities))
        self.assertEqual([e for e in events if e[0] == "score"], [("score", 192)])
        self.assertEqual(sum(e[0] == "predict" for e in events), 192)
        self.assertEqual(sum(e[0] == "correct" for e in events), 16)
        # Each four-arm correction follows24 saved pre-disclosure predictions for its case.
        self.assertEqual(events[:24], [("predict", 2)] * 24)
        self.assertEqual(events[24][0], "correct")

    def test_disclosure_requires_persisted_complete_untampered_seal(self):
        with TemporaryDirectory() as d:
            m = Meter(); store = Artifacts(Path(d) / "episode", m)
            episode = Episode(fixtures()[0].public, 0, meter=m, store=store)
            c = fixtures()[0]
            from packages.sentence_revision.arms import Example
            correction = Example(c.public.correction_input, c.correction_output)
            with self.assertRaises(Fault):
                episode.after(c.correction_text, correction)
            episode.before()
            name = "row-c0-REVISE-before-p2.json"
            (store.root / name).write_bytes(b'{}\n')
            with self.assertRaises(Fault):
                episode.after(c.correction_text, correction)
            self.assertEqual(len(episode.cases["REVISE"]._data["pairs"]), 2)
            with self.assertRaises(Fault):
                episode.before()

    def test_missing_extra_tampered_files_freeze_and_seal_rejected(self):
        for name, mutation in (("row-c0-REVISE-before-p0.json", "missing"),
                               ("snapshot-c0-REVISE-after.json", "bytes"),
                               ("private-gold.json", "bytes"),
                               ("freeze.json", "bytes"), ("schedule.json", "bytes"),
                               ("predictions-seal.json", "bytes")):
            with self.subTest(name=name):
                store = self.copied_store()
                if mutation == "missing":
                    (store.root / name).unlink()
                else:
                    (store.root / name).write_bytes(b'{}\n')
                with self.assertRaises(Fault):
                    self.score(store)
        store = self.copied_store()
        (store.root / "row-unindexed-extra.json").write_bytes(b'{}\n')
        with self.assertRaises(Fault):
            self.score(store)
        for change in ("extra", "missing"):
            store = self.copied_store()
            seal = load(store.root, "predictions-seal.json")
            if change == "extra":
                seal["artifacts"]["row-duplicate.json"] = {"sha256": "0" * 64, "bytes": 0}
            else:
                del seal["artifacts"][next(iter(seal["artifacts"]))]
            raw = canonical(seal)
            (store.root / "predictions-seal.json").write_bytes(raw)
            store.index["predictions-seal.json"] = {"sha256": sha256(raw).hexdigest(), "bytes": len(raw)}
            with self.assertRaises(Fault):
                score_batch(store, meter=store.meter, expected_freeze_sha=self.result["freeze_sha256"], expected_seal_sha=digest(seal))

    def test_source_settings_and_expected_hash_drift_block_score(self):
        from packages.sentence_revision import evaluator
        for field in ("source", "settings"):
            store = self.copied_store()
            if field == "source":
                context = patch.object(evaluator, "source_hashes", return_value={})
            else:
                context = patch.dict(SETTINGS, {"renderer": "different"})
            with context, self.assertRaises(Fault):
                self.score(store)
        store = self.copied_store()
        with self.assertRaises(Fault):
            score_batch(store, meter=store.meter, expected_freeze_sha="0" * 64, expected_seal_sha=self.result["predictions_seal_sha256"])

    def test_row_schedule_types_full_state_and_status_rejection(self):
        planned = schedule()[0]
        good = load(self.root, "row-" + planned["slot"] + ".json")
        public = load(self.root, "private-gold.json")[0]["public"]
        _validate_row(good, planned, public)
        for field, value in (("case", False), ("probe", True), ("slot", "other"), ("extra", None),
                             ("input_sha256", "0" * 64), ("status", "not_run"),
                             ("selected_id", "unknown"), ("output", None)):
            with self.subTest(field=field), self.assertRaises(Fault):
                _validate_row(dict(good, **{field: value}), planned, public)
        for field, value in (("cursor", True), ("clipboard", ""), ("selection", [0, 1])):
            bad = dict(good, output=dict(good["output"], **{field: value}))
            with self.assertRaises(Fault):
                _validate_row(bad, planned, public)

    def test_cost_attribution_nonzero_preparation_shared_total_and_report(self):
        receipts = self.meter.receipts
        self.assertTrue(all("scope" in r for r in receipts))
        self.assertEqual({a for a in ARMS if any('/' + a + '/' in r['scope'] for r in receipts)}, set(ARMS))
        self.assertTrue(any(r["phase"] == "prepare" and r["counts"]["candidate_enumerations"] == 78 for r in receipts))
        self.assertTrue(any(r["phase"] == "report" for r in receipts))
        self.assertTrue(any(r["phase"] == "persist/completion.json" for r in receipts))
        totals = {k: sum(r["counts"][k] for r in receipts) for k in self.meter.counts}
        self.assertEqual(totals, self.meter.counts)
        self.assertGreaterEqual(self.result["final_cost"]["cpu_seconds"], sum(r["cpu_seconds"] for r in receipts))
        text = (self.root / "report.md").read_text()
        for token in ("Case 0", "Case 3", "残存仮説", "除外仮説", "費用", "abstain", "clipboard", "192"):
            self.assertIn(token, text)
        for case in self.result["results"]:
            for row in case["rows"]:
                self.assertIn(row["slot"], text)
        with self.assertRaises(Fault):
            render(self.result["results"][:3], meter=Meter())

    def test_genuine_checkpoint_stops_across_pipeline_and_no_score_after_cap(self):
        # Inject at actual checkpoints under named phases, preserving Meter failure receipts.
        phases = ("prepare", "persist/row-c0-REVISE-before-p0.json", "pre-disclosure-seal",
                  "disclosure", "prediction-seal", "batch-score", "report", "completion")
        original = Meter.checkpoint
        for target in phases:
            def stop(m, retained=None):
                original(m, retained)
                if m._phase is not None and target == active_phase[0]:
                    raise BudgetExceeded("artificial named checkpoint stop")
            # phase name isn't stored by foundation Meter: track via a small context wrapper.
            original_phase = Meter.phase
            active_phase = [None]
            from contextlib import contextmanager
            @contextmanager
            def phase(m, name):
                active_phase[0] = name
                try:
                    with original_phase(m, name) as value:
                        yield value
                finally:
                    active_phase[0] = None
            with self.subTest(target=target), TemporaryDirectory() as d, patch.object(Meter, "phase", phase), patch.object(Meter, "checkpoint", stop):
                m = Meter(); root = Path(d) / "stopped"
                result = run_artificial(fixtures(), root, meter=m)
                self.assertEqual(result["status"], "resource_stop", result)
                self.assertEqual(m.receipts[-1]["status"], "budget_exhausted")
                self.assertEqual(m.receipts[-1]["phase"], target)
                self.assertTrue((root / "stop.json").is_file())
                self.assertEqual(result["planned_rows"], 192)
                self.assertFalse(result["retry_allowed"])
                if target in phases[:5]:
                    self.assertFalse(any(r["phase"] in ("batch-score", "report") for r in m.receipts))
                if (root / "results.json").exists():
                    self.assertEqual(load(root, "results.json")["status"], "scored_pending_completion")
                    self.assertIn("stop.json", load(root, "results.json")["authoritative_status"])
                self.assertIn("final_cost", result)
                if (root / "schedule.json").exists():
                    planned = load(root, "schedule.json")
                    files = list(root.glob("row-*.json"))
                    self.assertEqual(len(planned), 192)
                    self.assertEqual(len(files), result["completed_prediction_files"])

    def test_actual_shared_cpu_and_retained_caps_stop_without_reset(self):
        with TemporaryDirectory() as d:
            m = Meter(total_cpu=1e-9)
            result = run_artificial(fixtures(), Path(d) / "cpu", meter=m)
            self.assertEqual(result["status"], "resource_stop")
            self.assertEqual(result["completed_prediction_files"], 0)
            self.assertEqual(m.receipts[-1]["status"], "budget_exhausted")
            m = Meter(max_bytes=1000)
            result = run_artificial(fixtures(), Path(d) / "bytes", meter=m)
            self.assertEqual(result["status"], "resource_stop")
            self.assertEqual(result["completed_prediction_files"], 0)
            self.assertFalse(any(r["phase"] == "batch-score" for r in m.receipts))

    def test_score_entry_is_once_only_and_actual_report_size_stop_cannot_rescore(self):
        # A complete run also cannot be scored twice, even with a fresh Meter.
        store = self.copied_store()
        self.score(store)
        for meter in (store.meter, Meter()):
            store.meter = meter
            with self.assertRaises(Fault):
                self.score(store)
        import packages.sentence_revision.evaluator as ev
        import packages.sentence_revision.report as report
        from packages.sentence_revision.artifacts import attributed
        original = ev.score_batch
        captured = {}
        def capture(store, **kwargs):
            captured.update(store=store, kwargs=kwargs)
            return original(store, **kwargs)
        def real_size_stop(results, *, meter):
            with attributed(meter, "shared/report"), meter.phase("report"):
                meter.checkpoint(b"x" * meter.max_bytes)
        with TemporaryDirectory() as d, patch.object(ev, "score_batch", capture), patch.object(report, "render", real_size_stop):
            meter = Meter()
            outcome = run_artificial(fixtures(), Path(d) / "size-stop", meter=meter)
            self.assertEqual(outcome["status"], "resource_stop", outcome)
            self.assertEqual(meter.receipts[-1]["phase"], "report")
            self.assertTrue((captured["store"].root / "stop.json").exists())
            reads = []
            read = Artifacts.read
            def spy(instance, name, **kwargs):
                reads.append(name)
                return read(instance, name, **kwargs)
            with patch.object(Artifacts, "read", spy), self.assertRaises(Fault):
                original(captured["store"], **captured["kwargs"])
            self.assertNotIn("private-gold.json", reads)
            # The persistent latch still blocks after removal of only the stop marker
            # and replacement of the in-memory Meter (no OS-authenticity claim).
            (captured["store"].root / "stop.json").unlink()
            captured["store"].meter = Meter()
            args = dict(captured["kwargs"], meter=captured["store"].meter)
            with self.assertRaises(Fault):
                original(captured["store"], **args)

    def test_final_writes_cover_live_data_and_release_redundant_copies(self):
        # Inspect actual caller roots, not only the retained argument under test.
        root_names = ("gold", "planned", "freeze", "seal", "results", "report",
                      "summary", "names", "settings", "completion", "retained")
        writes, sizes = [], {}
        original_write, original_checkpoint = Artifacts.write, Meter.checkpoint
        active = [None]
        def ids(value):
            found = set()
            def visit(obj):
                if id(obj) in found:
                    return
                found.add(id(obj))
                if type(obj) in (tuple, list):
                    for item in obj:
                        visit(item)
                elif type(obj) is dict:
                    for key, item in obj.items():
                        visit(key); visit(item)
            visit(value)
            return found
        def write(store, name, value, **kwargs):
            if name in ("report.md", "results.json", "completion.json") or name.startswith("cost-receipts-"):
                caller = inspect.currentframe().f_back
                live = {k: caller.f_locals[k] for k in root_names if k in caller.f_locals}
                del caller
                if name != "report.md":
                    self.assertFalse(set(live) & {"gold", "planned", "freeze", "seal", "report", "names", "settings"})
                if name.startswith("cost-receipts-") or name == "completion.json":
                    self.assertNotIn("summary", live)
                active[0] = (name, live)
                writes.append(name)
                try:
                    return original_write(store, name, value, **kwargs)
                finally:
                    active[0] = None
            return original_write(store, name, value, **kwargs)
        def checkpoint(meter, retained=None):
            if active[0] is not None and retained is not None:
                name, live = active[0]
                checked_ids = ids(retained)
                for key, value in live.items():
                    self.assertIn(id(value), checked_ids, (name, key))
                sizes[name] = max(sizes.get(name, 0), retained_size(retained))
            return original_checkpoint(meter, retained)
        with TemporaryDirectory() as d, patch.object(Artifacts, "write", write), patch.object(Meter, "checkpoint", checkpoint):
            result = run_artificial(fixtures(), Path(d) / "live-roots", meter=Meter())
            self.assertEqual(result["status"], "complete", result)
        self.assertEqual(writes[0:2], ["report.md", "results.json"])
        self.assertEqual(writes[-1], "completion.json")
        self.assertTrue(any(n.startswith("cost-receipts-") for n in writes))
        self.assertTrue(all(0 < size <= 1048576 for size in sizes.values()), sizes)

    def test_actual_final_serialization_caps_stop_and_do_not_resume(self):
        # Tighten the real Meter immediately before each named write. The cap is
        # independently derived from caller roots plus index/value/real JSON bytes.
        # No BudgetExceeded injection: Meter.checkpoint must detect the excess.
        root_names = ("gold", "planned", "freeze", "seal", "results", "report",
                      "summary", "names", "settings", "completion")
        original = Artifacts.write
        for target in ("results.json", "cost-receipts-000.json", "completion.json"):
            observed = {}
            def write(store, name, value, **kwargs):
                if name == target:
                    caller = inspect.currentframe().f_back
                    live = tuple(caller.f_locals[k] for k in root_names if k in caller.f_locals)
                    del caller
                    raw = canonical(value)
                    # Reserve room for wrapper containers, but ensure the actual
                    # payload exceeds the cap at its buffered checkpoint.
                    full = retained_size((live, store.index, value, raw))
                    payload_only = full - sys.getsizeof(live) - sys.getsizeof((live, store.index, value, raw))
                    unchecked = retained_size((None, store.index, value, raw))
                    cap = min(1048576, payload_only - 1, unchecked - 1) if target == "results.json" else min(1048576, payload_only - 1)
                    self.assertGreater(full, cap)
                    if target != "results.json":
                        self.assertLess(unchecked, cap, (target, unchecked, cap))
                    store.meter.max_bytes = cap
                    observed.update(full=full, unchecked=unchecked, cap=cap)
                return original(store, name, value, **kwargs)
            with self.subTest(target=target), TemporaryDirectory() as d, patch.object(Artifacts, "write", write):
                root = Path(d) / "actual-cap"
                meter = Meter()
                result = run_artificial(fixtures(), root, meter=meter)
                self.assertTrue(observed)
                self.assertEqual(result["status"], "resource_stop", result)
                self.assertEqual(meter.receipts[-1]["phase"], "persist/" + target)
                self.assertEqual(meter.receipts[-1]["status"], "budget_exhausted")
                self.assertEqual(result["reason"], "retained case bytes cap")
                self.assertFalse((root / target).exists())
                self.assertFalse((root / "completion.json").exists())
                self.assertTrue((root / "stop.json").exists())
                self.assertEqual(result["completed_prediction_files"], 192)
                self.assertFalse(result["retry_allowed"])
                if target != "results.json":
                    self.assertEqual(load(root, "results.json")["status"], "scored_pending_completion")

    def test_existing_root_no_overwrite_or_official_activation(self):
        with TemporaryDirectory() as d:
            meter = Meter()
            store = Artifacts(Path(d) / "missing-parent" / "nested-run", meter)
            store.write("probe.json", {"artificial": True})
            self.assertEqual(store.read("probe.json"), {"artificial": True})
            self.assertEqual(meter.receipts[0]["scope"], "shared/artifact-setup")
        before = (self.root / "results.json").read_bytes()
        result = run_artificial(fixtures(), self.root, meter=Meter())
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(before, (self.root / "results.json").read_bytes())
        for kwargs in ({}, {"owner_approval": True}, {"mode": "official"}):
            with self.assertRaises(Fault):
                run_official(fixtures(), **kwargs)

    def test_runner_import_closure_and_hash_seed_artifact_determinism(self):
        program = '''from pathlib import Path
from tempfile import TemporaryDirectory
import sys
from packages.sentence_revision import Meter
from packages.sentence_revision.runner import Episode
assert 'packages.sentence_revision.evaluator' not in sys.modules
assert 'packages.sentence_revision.report' not in sys.modules
from packages.sentence_revision.evaluator import run_artificial
from tests.sentence_revision_c_fixture import fixtures
from hashlib import sha256
with TemporaryDirectory() as d:
 r=run_artificial(fixtures(),Path(d)/'run',meter=Meter())
 assert r['status']=='complete', r
 root=Path(d)/'run'
 print([(p.name,sha256(p.read_bytes()).hexdigest()) for p in sorted(root.iterdir()) if p.name.startswith(('row-','snapshot-','before-seal-')) or p.name=='report.md'])
assert not any(n.startswith(('packages.world_lean','world_lean_evaluator','packages.evaluation','packages.kernel','packages.exp0003a')) for n in sys.modules)
'''
        outputs = [subprocess.check_output([sys.executable, "-c", program], env=dict(os.environ, PYTHONHASHSEED=seed)) for seed in ("0", "17")]
        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()

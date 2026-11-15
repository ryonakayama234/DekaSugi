"""Parent-only artificial orchestration and one batch scorer. Official route is shut."""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import time

from .arms import ARMS, Case, Example, _text
from .artifacts import Artifacts, attributed, digest
from .foundation import BudgetExceeded, Fault, Meter, State, canonical, catalog, grammar_digest
from .runner import Episode, PublicCase, STAGES, schedule, slot

SOURCE_FILES = tuple("packages/sentence_revision/" + f for f in (
    "__init__.py", "foundation.py", "arms.py", "artifacts.py", "runner.py", "evaluator.py", "report.py"))
SETTINGS = {"schema": "sentence-evaluation/1", "arms": list(ARMS), "cases": 4,
            "stages": list(STAGES), "probes_per_stage": 6, "main_probe_indices": [3, 4, 5],
            "near_counterexample_probe": 5, "candidate_checks_cap": 100000,
            "phase_cpu_cap": 60, "total_cpu_cap": 7200, "case_bytes_cap": 1048576,
            "scoring": "all-state-fields-exact", "renderer": "fixed-condition-renderer/1"}


@dataclass(frozen=True, slots=True)
class GoldCase:
    public: PublicCase
    correction_text: str
    correction_output: State
    unseen_outputs: tuple[State, State, State]
    intended_role: str

    def record(self):
        if type(self) is not GoldCase or type(self.public) is not PublicCase:
            raise Fault("exact parent GoldCase required")
        public = self.public.record()
        _text(self.correction_text, 4096)
        if (type(self.intended_role) is not str or self.intended_role not in ("revise", "confirmation")
                or type(self.unseen_outputs) is not tuple or len(self.unseen_outputs) != 3):
            raise Fault("gold shape/role")
        pairs = [Example(self.public.correction_input, self.correction_output),
                 *[Example(b, a) for b, a in zip(self.public.unseen_inputs, self.unseen_outputs)]]
        # Validates permitted complete final states, not whether a grammar can fit them.
        for pair in pairs:
            pair.record()
        return {"public": public, "correction_text": self.correction_text,
                "correction_output": self.correction_output.record(),
                "unseen_outputs": [s.record() for s in self.unseen_outputs],
                "intended_role": self.intended_role}


def source_hashes():
    root = Path(__file__).resolve().parents[2]
    return {name: sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def run_official(*args, **kwargs):
    raise Fault("official prediction/scoring is not authorized at stage C")


def _expected(row, gold):
    p = row["probe"]
    if p < 2:
        return gold["public"]["initial"][p]["after"]
    if p == 2:
        return gold["correction_output"]
    return gold["unseen_outputs"][p - 3]


def _validate_row(row, planned, public):
    keys = {"slot", "case", "arm", "stage", "probe", "input", "input_sha256", "status", "output", "selected_id"}
    if type(row) is not dict or set(row) != keys:
        raise Fault("invalid prediction row shape")
    for key in ("slot", "case", "arm", "stage", "probe"):
        if type(row[key]) is not type(planned[key]) or row[key] != planned[key]:
            raise Fault("prediction schedule mismatch")
    inputs = [*[ex["before"] for ex in public["initial"]],
              public["correction_input"], *public["unseen_inputs"]]
    State.parse(row["input"])
    if (row["input"] != inputs[row["probe"]] or row["input_sha256"] != digest(inputs[row["probe"]])
            or digest(row["input"]) != row["input_sha256"]):
        raise Fault("prediction input mismatch")
    if row["status"] not in ("predicted", "abstain", "no_consistent_candidate"):
        raise Fault("missing/nonterminal prediction")
    if row["status"] == "predicted":
        State.parse(row["output"])
    elif row["output"] is not None:
        raise Fault("nonprediction carries output")
    selected = row["selected_id"]
    if row["arm"] == "MEMORY":
        if selected is not None or row["status"] == "no_consistent_candidate":
            raise Fault("invalid MEMORY prediction")
    elif (row["status"] == "abstain"
          or (row["status"] == "predicted" and selected not in tuple(f"cond-{i:03d}" for i in range(78)))
          or (row["status"] == "no_consistent_candidate" and selected is not None)):
        raise Fault("invalid symbolic prediction")


def _hypotheses(snapshot, rules):
    if snapshot is None:
        return None
    return [{"id": key, "ast": rules[int(key[5:])].ast(),
             "explanation": rules[int(key[5:])].explain()} for key in snapshot["candidate_ids"]]


def score_batch(store, *, meter, expected_freeze_sha, expected_seal_sha):
    """Verify complete artifacts before accessing parent gold; no learner callback."""
    if type(meter) is not Meter or store.meter is not meter:
        raise Fault("batch score requires the run Meter")
    freeze = store.read("freeze.json")
    seal = store.read("predictions-seal.json")
    saved_schedule = store.read("schedule.json")
    if digest(freeze) != expected_freeze_sha or digest(seal) != expected_seal_sha:
        raise Fault("wrong external local seal expectation")
    with attributed(meter, "shared/pre-score-validation"), meter.phase("pre-score-validation"):
        if (freeze["settings"] != SETTINGS or freeze["source_sha256"] != source_hashes()
                or freeze["grammar_sha256"] != grammar_digest(meter)):
            raise Fault("source/settings changed since preparation")
        planned = schedule()
        if freeze["schedule"] != planned or saved_schedule != planned or seal["freeze_sha256"] != expected_freeze_sha:
            raise Fault("schedule/freeze link mismatch")
        expected_names = {"row-" + r["slot"] + ".json" for r in planned}
        expected_names |= {f"snapshot-c{c}-{a}-{s}.json" for c in range(4) for a in ARMS for s in STAGES}
        expected_names |= {f"before-seal-c{c}.json" for c in range(4)}
        actual_names = {p.name for p in store.root.iterdir() if p.name.startswith(("row-", "snapshot-", "before-seal-"))}
        if set(seal["artifacts"]) != expected_names or actual_names != expected_names:
            raise Fault("missing/extra/duplicate scheduled artifacts")
        meter.checkpoint((freeze, seal, planned))
    # Verify every prediction/snapshot/seal byte before using any withheld expected value.
    for name, meta in seal["artifacts"].items():
        if store.index.get(name) != meta:
            raise Fault("changed prediction index")
        store.read(name)
    gold = store.read("private-gold.json")
    if digest(gold) != freeze["gold_sha256"]:
        raise Fault("gold changed since preparation")
    results = []
    for c in range(4):
        rows, snapshots = [], {}
        for a in ARMS:
            for s in STAGES:
                snapshots[(a, s)] = store.read(f"snapshot-c{c}-{a}-{s}.json")
                with attributed(meter, f"case{c}/{a}/{s}/restore-audit"):
                    Case.restore(canonical(snapshots[(a, s)]), meter=meter)
                for p in range(6):
                    rows.append(store.read("row-" + slot(c, a, s, p) + ".json"))
        with attributed(meter, f"case{c}/batch-score"), meter.phase("batch-score"):
            rules = catalog(meter)
            public = gold[c]["public"]
            case_plan = [r for r in planned if r["case"] == c]
            for row, plan in zip(rows, case_plan):
                _validate_row(row, plan, public)
                row["expected"] = _expected(row, gold[c])
                row["correct"] = row["status"] == "predicted" and row["output"] == row["expected"]
            arms = {}
            for a in ARMS:
                before, after = snapshots[(a, "before")], snapshots[(a, "after")]
                if (before["arm"] != a or after["arm"] != a
                        or before["rule_id"] != public["rule_id"] or after["rule_id"] != public["rule_id"]
                        or before["examples"] != public["initial"]
                        or before["texts"] != [public["text"]]
                        or after["examples"] != [*public["initial"], {"before": public["correction_input"], "after": gold[c]["correction_output"]}]
                        or after["texts"] != [public["text"], gold[c]["correction_text"]]):
                    raise Fault("snapshot/public disclosure history mismatch")
                b, d = before["current"], after["current"]
                if a == "FROZEN" and b != d:
                    raise Fault("FROZEN executable changed")
                def selected(view):
                    return None if view is None else view["selected_id"]
                def scored(stage, probes):
                    return sum(r["correct"] for r in rows if r["arm"] == a and r["stage"] == stage and r["probe"] in probes)
                pre, post = scored("before", (3, 4, 5)), scored("after", (3, 4, 5))
                initial_before = [r["correct"] for r in rows if r["arm"] == a and r["stage"] == "before" and r["probe"] < 2]
                initial_after = [r["correct"] for r in rows if r["arm"] == a and r["stage"] == "after" and r["probe"] < 2]
                arms[a] = {"unseen_before": pre, "unseen_after": post, "delta": post - pre,
                           "initial_before": initial_before, "initial_after": initial_after,
                           "lost_initial_correct": sum(x and not y for x, y in zip(initial_before, initial_after)),
                           "correction_before": scored("before", (2,)), "correction_after": scored("after", (2,)),
                           "near_before": scored("before", (5,)), "near_after": scored("after", (5,)),
                           "selection_changed": selected(b) != selected(d),
                           "observation": "no_observed_improvement_opportunity" if pre == 3 else "below_observed_ceiling",
                           "empty_after": d is not None and not d["candidate_ids"],
                           "before": b, "after": d,
                           "remaining": _hypotheses(d, rules),
                           "removed": None if b is None else _hypotheses({"candidate_ids": [x for x in b["candidate_ids"] if x not in d["candidate_ids"]]}, rules)}
                meter.checkpoint((gold[c], rows, snapshots, rules, arms))
            result = {"case": c, "rule_id": public["rule_id"], "intended_role": gold[c]["intended_role"],
                      "initial_text": public["text"], "correction_text": gold[c]["correction_text"],
                      "correction_expected": gold[c]["correction_output"], "arms": arms, "rows": rows}
            meter.checkpoint((gold[c], rows, snapshots, rules, result))
        results.append(result)
    return results


def run_artificial(cases, root, *, meter):
    """Engineering-only orchestration; never called by an official loader/CLI."""
    if type(meter) is not Meter:
        raise Fault("one mandatory run Meter")
    start_wall = time.perf_counter()
    store = None
    try:
        store = Artifacts(root, meter)
        with attributed(meter, "shared/preparation"), meter.phase("prepare"):
            if type(cases) is not tuple or len(cases) != 4 or any(type(c) is not GoldCase for c in cases):
                raise Fault("exactly four artificial cases required")
            gold = [c.record() for c in cases]
            if len({c.public.rule_id for c in cases}) != 4:
                raise Fault("duplicate case ID")
            planned = schedule()
            settings = dict(SETTINGS, grammar_sha256=grammar_digest(meter))
            freeze = {"schema": "sentence-local-freeze/1", "mode": "artificial_only",
                      "settings": SETTINGS, "grammar_sha256": settings["grammar_sha256"],
                      "source_sha256": source_hashes(), "gold_sha256": digest(gold),
                      "public_sha256": digest([g["public"] for g in gold]), "schedule": planned}
            meter.checkpoint((gold, planned, freeze))
        store.write("schedule.json", planned)
        store.write("private-gold.json", gold)
        store.write("freeze.json", freeze)
        freeze_sha = digest(freeze)
        for i, case in enumerate(cases):
            episode = Episode(case.public, i, meter=meter, store=store)
            episode.before()
            # Only this pair/text crosses the boundary after the verified before seal.
            episode.after(case.correction_text, Example(case.public.correction_input, case.correction_output))
        with attributed(meter, "shared/prediction-seal"), meter.phase("prediction-seal"):
            names = [n for n in store.index if n.startswith(("row-", "snapshot-", "before-seal-"))]
            seal = {"freeze_sha256": freeze_sha, "artifacts": {n: store.index[n] for n in sorted(names)}}
            meter.checkpoint(seal)
        store.write("predictions-seal.json", seal)
        results = score_batch(store, meter=meter, expected_freeze_sha=freeze_sha, expected_seal_sha=digest(seal))
        from .report import render
        report = render(results, meter=meter)
        store.write("report.md", report, text=True)
        with attributed(meter, "shared/result-generation"), meter.phase("result-generation"):
            summary = {"schema": "sentence-results/1", "mode": "artificial_only", "status": "scored_pending_completion",
                       "authoritative_status": "completion.json required; stop.json overrides every partial artifact",
                       "independent_cases": 4, "planned_rows": 192, "main_unseen_rows": 96,
                       "freeze_sha256": freeze_sha, "predictions_seal_sha256": digest(seal),
                       "cases": results, "counts": meter.counts.copy(),
                       "cost_receipts": "cost-receipts-NNN.json shards; completion.json tail",
                       "cpu_seconds_including_preparation": time.process_time() - meter._start,
                       "wall_seconds": time.perf_counter() - start_wall,
                       "cost_note": "phase receipts plus raw whole-run total; report/persistence finalization recorded in completion.json"}
            # Results are serialized per case in report; guard aggregate JSON buffers too.
            meter.checkpoint(summary)
        store.write("results.json", summary)
        # Shard growing run metadata; each active serialization stays within the same1MiB guard.
        boundary = len(meter.receipts)
        for offset in range(0, boundary, 128):
            store.write(f"cost-receipts-{offset // 128:03d}.json", meter.receipts[offset:min(offset + 128, boundary)])
        with attributed(meter, "shared/completion"), meter.phase("completion"):
            completion = {"status": "complete", "artifact_index": dict(store.index),
                          "counts": meter.counts.copy(), "phase_receipts_tail": list(meter.receipts[boundary:]),
                          "cpu_seconds": time.process_time() - meter._start,
                          "wall_seconds": time.perf_counter() - start_wall}
            meter.checkpoint(completion)
        store.write("completion.json", completion)
        return {"status": "complete", "root": str(store.root), "results": results,
                "freeze_sha256": freeze_sha, "predictions_seal_sha256": digest(seal),
                "final_cost": {"cpu_seconds": time.process_time() - meter._start,
                               "wall_seconds": time.perf_counter() - start_wall,
                               "counts": meter.counts.copy(), "phase_count": len(meter.receipts)}}
    except (BudgetExceeded, Fault, OSError) as exc:
        # Equivalent to Meter.phase's bounded failure receipt, never a study retry.
        # Planned schedule + exclusive per-row files retain completed/not-run slots.
        receipt = {"status": "resource_stop" if isinstance(exc, BudgetExceeded) else "invalid",
                   "reason": str(exc)[:300], "planned_rows": 192, "main_unseen_rows": 96,
                   "completed_prediction_files": 0 if store is None else len(list(store.root.glob("row-*.json"))),
                   "indexed_prediction_files": 0 if store is None else sum(n.startswith("row-") for n in store.index),
                   "schedule_status": "saved" if store is not None and "schedule.json" in store.index else "not_prepared_all_slots_not_run",
                   "missing_slot_rule": "fixed schedule() minus saved row files; no zero imputation",
                   "last_phase": meter.receipts[-1] if meter.receipts else None,
                   "cpu_observed_before_stop_write": time.process_time() - meter._start,
                   "wall_seconds": time.perf_counter() - start_wall,
                   "score_or_report_may_be_partial": True, "retry_allowed": False}
        path = Path(root)
        if path.is_dir() and store is not None:
            # No overwrite, bounded <=2KiB terminal metadata, no rich rendering after cap.
            raw = canonical(receipt)
            if len(raw) <= 2048:
                with (path / "stop.json").open("xb") as stream:
                    stream.write(raw)
        receipt["final_cost"] = {"cpu_seconds": time.process_time() - meter._start,
                                 "wall_seconds": time.perf_counter() - start_wall,
                                 "counts": meter.counts.copy(), "phase_count": len(meter.receipts)}
        return receipt

"""Invented B fixtures; no production24 cases, targets or evaluator imports."""
from dataclasses import replace
from itertools import product
import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from packages.sentence_revision import BudgetExceeded, Fault, Meter, State, canonical, catalog
from packages.sentence_revision.arms import ARMS, Case, Example
from packages.sentence_revision.foundation import retained_size


def state(text, cursor=2):
    return State(tuple(text), cursor)


def example(text, erase, cursor=2):
    before = state(text, cursor)
    after = State(before.buffer[:cursor] + before.buffer[cursor + 1:], cursor) if erase else before
    return Example(before, after)


INITIAL = (example("ABCD", False), example("AAAA", True))
CORRECTION = example("ABAC", False)


def case(arm, meter=None, initial=INITIAL):
    return Case.create(arm, "opaque-17", "initial description", initial,
                       meter=meter if meter is not None else Meter())


def oracle(pairs):
    # Independent read/predicate/output interpreter; does not call evaluate/execute.
    surviving = []
    for i, condition in enumerate(catalog()):
        ok = True
        for ex in pairs:
            s = ex.before
            reads = {"first": s.buffer[0], "prev": s.buffer[s.cursor - 1],
                     "cursor": s.buffer[s.cursor], "last": s.buffer[-1]}
            bits = [(reads[a] == reads[b]) == (op == "EQ") for op, a, b in condition.atoms]
            out = list(s.buffer)
            if all(bits):
                out.pop(s.cursor)
            if State(tuple(out), s.cursor) != ex.after:
                ok = False
                break
        if ok:
            surviving.append(f"cond-{i:03d}")
    return surviving


class ArmsTests(unittest.TestCase):
    def test_initial_agreement_same_input_and_correction_receipts(self):
        m = Meter()
        cases = [case(arm, m) for arm in ARMS]
        initial_ids = []
        inputs = []
        for learner in cases:
            before = json.loads(learner.save())
            inputs.append((before["rule_id"], before["texts"], before["examples"]))
            if before["initial"] is not None:
                initial_ids.append(before["initial"]["selected_id"])
                self.assertEqual(before["initial"]["candidate_ids"], oracle(INITIAL))
            learner.correct("clarification", CORRECTION)
            after = json.loads(learner.save())
            self.assertEqual(after["texts"], ["initial description", "clarification"])
            self.assertEqual(after["examples"], [x.record() for x in (*INITIAL, CORRECTION)])
        self.assertTrue(all(x == inputs[0] for x in inputs))
        self.assertEqual(initial_ids, ["cond-000"] * 3)
        self.assertEqual(sum(r["phase"] == "build" for r in m.receipts), 4)
        self.assertTrue(all(r["status"] == "complete" for r in m.receipts))

    def test_revise_filters_frozen_holds_and_fresh_agrees(self):
        for arm in ("REVISE", "FROZEN", "FRESH"):
            c = case(arm)
            before = json.loads(c.save())
            c.correct("clarification", CORRECTION)
            after = json.loads(c.save())
            self.assertEqual(after["initial"], before["initial"])
            wanted = oracle(INITIAL if arm == "FROZEN" else (*INITIAL, CORRECTION))
            self.assertEqual(after["current"]["candidate_ids"], wanted)
            self.assertEqual(c.predict(CORRECTION.before)["output"],
                             (example("ABAC", True).after if arm == "FROZEN"
                              else CORRECTION.after).record())

    def test_revise_fresh_fixed_order_oracle_on_many_invented_updates(self):
        # Not a production table: sixteen binary strings, arbitrary keep/delete labels.
        for letters in product("AB", repeat=4):
            ex = example("".join(letters), False)
            if any(ex.before == old.before and ex.after != old.after for old in INITIAL):
                continue
            for arm in ("REVISE", "FRESH"):
                c = case(arm)
                c.correct("clarification", ex)
                self.assertEqual(json.loads(c.save())["current"]["candidate_ids"],
                                 oracle((*INITIAL, ex)))

    def test_memory_exact_full_state_key_and_abstention_cost(self):
        m = Meter()
        c = case("MEMORY", m)
        for ex in INITIAL:
            self.assertEqual(c.predict(ex.before)["output"], ex.after.record())
        self.assertEqual(c.predict(state("ABAC"))["status"], "abstain")
        # Same buffer, different cursor must not match.
        self.assertEqual(c.predict(state("AAAA", 1))["status"], "abstain")
        c.correct("clarification", CORRECTION)
        self.assertEqual(c.predict(CORRECTION.before)["output"], CORRECTION.after.record())
        self.assertEqual(m.counts["submissions"], 3)
        self.assertEqual(m.counts["candidate_enumerations"], 0)
        self.assertEqual(len(m.receipts), 7)
        self.assertGreaterEqual(m.receipts[-1]["cpu_seconds"], 0)

    def test_conflicts_not_overwritten_and_only_one_correction(self):
        for arm in ARMS:
            c = case(arm)
            raw = c.save()
            with self.assertRaises(Fault):
                c.correct("bad clarification", example("AAAA", False))
            self.assertEqual(c.save(), raw)
            c.correct("clarification", CORRECTION)
            with self.assertRaises(Fault):
                c.correct("extra", CORRECTION)
            with self.assertRaises(Fault):
                case(arm, initial=(INITIAL[0], example("ABCD", True)))

    def test_fresh_rebuilds_each_prediction_and_never_updates_case(self):
        m = Meter()
        c = case("FRESH", m)
        for updated in (False, True):
            if updated:
                c.correct("clarification", CORRECTION)
            raw = c.save()
            outputs = []
            deltas = []
            for _ in range(2):
                outputs.append(c.predict(state("DDDC")))
                deltas.append(m.receipts[-1]["counts"])
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(deltas[0], deltas[1])
            self.assertEqual(deltas[0]["candidate_enumerations"], 156)
            self.assertGreaterEqual(deltas[0]["candidate_checks"], 78)
            self.assertEqual(c.save(), raw)

    def test_inconsistent_candidate_set_is_distinct_from_resource_stop(self):
        # ABAC and CDCA have identical equality patterns; no condition can give opposite outputs.
        initial = (example("ABAC", True), example("CDCA", False))
        for arm in ("REVISE", "FROZEN", "FRESH"):
            c = case(arm, initial=initial)
            self.assertEqual(json.loads(c.save())["current"]["candidate_ids"], [])
            self.assertEqual(c.predict(state("BBBB")), {
                "status": "no_consistent_candidate", "output": None, "selected_id": None})
        self.assertEqual(case("MEMORY", initial=initial).predict(state("BBBB"))["status"], "abstain")

    def test_confirmation_ceiling_and_independent_case_reset(self):
        a, b = case("REVISE"), case("REVISE")
        initial = json.loads(a.save())["current"]
        a.correct("confirmation", example("BBBD", True))
        self.assertEqual(json.loads(a.save())["current"]["selected_id"], initial["selected_id"])
        self.assertEqual(json.loads(b.save())["texts"], ["initial description"])
        a.predict(state("CDAB"))
        self.assertEqual(json.loads(b.save())["current"], initial)

    def test_save_restore_replay_is_charged_and_tampering_rejected(self):
        for arm in ARMS:
            c = case(arm)
            for updated in (False, True):
                if updated:
                    c.correct("clarification", CORRECTION)
                raw = c.save()
                m = Meter()
                copy = Case.restore(raw, meter=m)
                self.assertEqual(copy.save(), raw)
                self.assertEqual(copy.predict(state("BDDA")), c.predict(state("BDDA")))
                receipt = m.receipts[0]
                self.assertEqual(receipt["phase"], "restore")
                if arm != "MEMORY":
                    self.assertGreaterEqual(receipt["counts"]["candidate_checks"], 78)
                self.assertGreaterEqual(receipt["counts"]["candidate_enumerations"], 156)
                value = json.loads(raw)
                changes = [("schema", "other"), ("grammar_sha256", "0" * 64),
                           ("extra", 1), ("arm", "OTHER"), ("texts", []), ("current", None),
                           ("examples", []), ("rule_id", True)]
                for field, content in changes:
                    if value.get(field) == content:
                        continue
                    with self.subTest(arm=arm, field=field), self.assertRaises(Fault):
                        Case.restore(canonical(dict(value, **{field: content})), meter=Meter())
                if arm != "MEMORY":
                    forged = json.loads(raw)
                    forged["current"]["candidate_ids"] = ["cond-077"]
                    with self.assertRaises(Fault):
                        Case.restore(canonical(forged), meter=Meter())
                with self.assertRaises(Fault):
                    Case.restore(b' ' + raw, meter=Meter())
        for raw in (b'{"schema":1,"schema":2}', b'NaN', b'\xff', b'[]', b'{}'):
            with self.assertRaises(Fault):
                Case.restore(raw, meter=Meter())

    def test_strict_inputs_no_parser_or_hidden_extra_fields(self):
        class FakeExample(Example):
            pass
        class FakeText(str):
            pass
        for arm in ARMS:
            for examples in ([*INITIAL], (FakeExample(INITIAL[0].before, INITIAL[0].after), INITIAL[1]),
                             (replace(INITIAL[0], after=state("ABCD", 1)), INITIAL[1])):
                with self.assertRaises(Fault):
                    case(arm, initial=examples)
            with self.assertRaises(Fault):
                Case.create(arm, FakeText("id"), "text", INITIAL, meter=Meter())
            with self.assertRaises(Fault):
                Case.create(arm, "id", "text", INITIAL, meter=None)
            with self.assertRaises(TypeError):
                Case.create(arm, "id", "text", INITIAL, target="cond-000", meter=Meter())
            c = case(arm)
            with self.assertRaises(Fault):
                c.predict(state("ABC", 1))
            # Text content is deliberately ignored by the symbolic algorithm.
            d = Case.create(arm, "other", "EQ cursor last: arbitrary words", INITIAL, meter=Meter())
            self.assertEqual(c.predict(state("ABAC")), d.predict(state("ABAC")))

    def test_candidate_caps_include_build_update_restore_and_fresh_predict(self):
        for arm in ("REVISE", "FROZEN", "FRESH"):
            m = Meter(max_checks=0)
            with self.assertRaises(BudgetExceeded):
                case(arm, m)
            self.assertEqual(m.receipts[-1]["status"], "budget_exhausted")
            raw = case(arm).save()
            with self.assertRaises(BudgetExceeded):
                Case.restore(raw, meter=m)
        for arm in ("REVISE", "FRESH"):
            m = Meter()
            c = case(arm, m)
            m.max_checks = 0  # tighten only for this negative fixture
            with self.assertRaises(BudgetExceeded):
                c.correct("clarification", CORRECTION)
            self.assertEqual(m.receipts[-1]["status"], "budget_exhausted")
            with self.assertRaises(BudgetExceeded):
                c.save()
        m = Meter()
        c = case("FRESH", m)
        m.max_checks = 0
        with self.assertRaises(BudgetExceeded):
            c.predict(state("ABAC"))
        self.assertEqual(m.receipts[-1]["status"], "budget_exhausted")

    def test_cpu_total_and_retained_caps_cover_every_operation_every_arm(self):
        for arm in ARMS:
            raw = case(arm).save()
            for op in ("build", "update", "predict", "save", "restore"):
                for cap in ("phase", "total", "bytes"):
                    with self.subTest(arm=arm, op=op, cap=cap):
                        m = Meter(phase_cpu=1, total_cpu=10)
                        c = case(arm, m)
                        if cap == "bytes":
                            m.max_bytes = 1
                            context = patch("packages.sentence_revision.foundation.time.process_time",
                                            wraps=__import__("time").process_time)
                        elif cap == "total":
                            context = patch("packages.sentence_revision.foundation.time.process_time",
                                            return_value=m._start + 11)
                        else:
                            # Advance after the phase starts, including pure MEMORY operations.
                            t = m._start
                            context = patch("packages.sentence_revision.foundation.time.process_time",
                                            side_effect=[t, t + 2] + [t + 2] * 100)
                        with context, self.assertRaises(BudgetExceeded):
                            if op == "build":
                                case(arm, m)
                            elif op == "restore":
                                Case.restore(raw, meter=m)
                            elif op == "update":
                                c.correct("clarification", CORRECTION)
                            elif op == "predict":
                                c.predict(state("CDAB"))
                            else:
                                c.save()
                        self.assertEqual(m.receipts[-1]["phase"], op)
                        self.assertEqual(m.receipts[-1]["status"], "budget_exhausted")
                        if op not in ("build", "restore"):
                            with self.assertRaises(BudgetExceeded):
                                c.predict(state("AAAA"))

    def test_memory_limit_checks_entire_case_and_serialized_peak(self):
        m = Meter()
        c = Case.create("MEMORY", "id", "x" * 4000, INITIAL, meter=m)
        small = retained_size(c._data)
        m.max_bytes = small + 1000
        with self.assertRaises(BudgetExceeded):
            c.correct("y" * 4000, CORRECTION)
        self.assertEqual(m.receipts[-1]["status"], "budget_exhausted")
        with self.assertRaises(BudgetExceeded):
            Case.restore(b' ' * 1048576, meter=Meter())

    def test_hash_seed_fresh_process_determinism_and_import_closure(self):
        program = '''from packages.sentence_revision import Meter, State
from packages.sentence_revision.arms import Case, Example, ARMS
import sys
s=lambda x: State(tuple(x),2)
e=lambda x,y: Example(s(x),s(y))
m=Meter()
for arm in ARMS:
 c=Case.create(arm,'opaque','text',(e('ABCD','ABCD'),e('AAAA','AAA')),meter=m)
 c.correct('clarification',e('ABAC','ABAC'))
 print(c.save().hex())
 print(c.predict(s('CDAB')))
assert not any(n.startswith(('packages.world_lean','world_lean_evaluator',
 'packages.evaluation','packages.kernel','packages.exp0003a')) for n in sys.modules)
'''
        outputs = [subprocess.check_output([sys.executable, "-c", program],
                   env=dict(os.environ, PYTHONHASHSEED=seed)) for seed in ("0", "1", "17")]
        self.assertEqual(len(set(outputs)), 1)


if __name__ == "__main__":
    unittest.main()

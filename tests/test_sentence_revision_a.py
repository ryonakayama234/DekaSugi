"""Invented fixtures only; never imports any historical experiment or evaluator."""
from dataclasses import FrozenInstanceError
from itertools import product, combinations
import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from packages.sentence_revision import (
    BudgetExceeded, Condition, Fault, Meter, Snapshot, State, canonical,
    catalog, delete_right, execute, grammar_digest, keep, validate_input,
)
from packages.sentence_revision.foundation import retained_size


def artificial(text="ABCD", cursor=2):
    return State(tuple(text), cursor)


class FoundationTests(unittest.TestCase):
    def test_all_small_deletions_against_independent_list_oracle(self):
        for n in (4, 5, 6):
            for letters in product("ABCD", repeat=n):
                for cursor in range(1, n):
                    state = State(letters, cursor)
                    validate_input(state)
                    expected = list(letters)
                    del expected[cursor]
                    self.assertEqual(delete_right(state).record(), {
                        "buffer": expected, "cursor": cursor,
                        "selection": None, "clipboard": []})
                    self.assertIs(keep(state), state)

    def test_read_meaning_not_numeric_cursor(self):
        s = artificial("ABAC", 2)
        self.assertTrue(Condition((("EQ", "cursor", "first"),)).evaluate(s))
        self.assertFalse(Condition((("EQ", "cursor", "prev"),)).evaluate(s))
        self.assertEqual(execute(Condition((("EQ", "cursor", "first"),)), s), artificial("ABC", 2))

    def test_complete_equality_partitions_and_independent_ast_interpreter(self):
        # Four *distinct locations*: right2, prev1, first0, last3.
        patterns = set()
        for letters in product("ABCD", repeat=4):
            signature = tuple(letters[i] == letters[j] for i, j in combinations(range(4), 2))
            patterns.add(signature)
            state = State(letters, 2)
            values = dict(zip(("first", "prev", "cursor", "last"), letters))
            for condition in catalog():
                node = condition.ast()
                children = node[1:] if node[0] == "AND" else [node]
                truths = [(values[a] == values[b]) == (op == "EQ") for op, a, b in children]
                self.assertEqual(condition.evaluate(state), all(truths))
                self.assertEqual(execute(condition, state), delete_right(state) if all(truths) else state)
        self.assertEqual(len(patterns), 15)

    def test_canonical_78_order_roundtrip_and_renderer(self):
        rules = catalog()
        self.assertEqual(grammar_digest(), "ebf86948879d0dc27d66467ce4ff710bc7befbdb25ab899db15553c13eb92758")
        self.assertEqual(len(rules), 78)
        self.assertEqual(len({canonical(r.ast()) for r in rules}), 78)
        self.assertEqual([len(r.atoms) for r in rules], [1] * 12 + [2] * 66)
        for group in (rules[:12], rules[12:]):
            raw = [canonical(r.ast()) for r in group]
            self.assertEqual(raw, sorted(raw))
        for rule in rules:
            self.assertEqual(Condition.parse(json.loads(canonical(rule.ast()))), rule)
            self.assertTrue(rule.explain())
        # Contradiction retained, no semantic deduplication.
        contradiction = Condition((("EQ", "cursor", "first"), ("NE", "cursor", "first")))
        self.assertIn(contradiction, rules)
        self.assertFalse(contradiction.evaluate(artificial()))

    def test_full_state_json_immutability_and_subset_boundary(self):
        s = State(tuple("ABCD"), 2, (1, 2), tuple("CD"))
        self.assertEqual(State.parse(s.record()), s)
        self.assertIs(keep(s), s)
        with self.assertRaises(FrozenInstanceError):
            s.cursor = 1
        with self.assertRaises(Fault):
            validate_input(s)
        with self.assertRaises(Fault):
            delete_right(s)
        output = delete_right(State(tuple("ABCD"), 1, None, tuple("DD")))
        self.assertEqual(output.clipboard, tuple("DD"))
        self.assertEqual(delete_right(State((), 0)), State((), 0))
        self.assertEqual(delete_right(State(tuple("AB"), 2)), State(tuple("AB"), 2))
        for state in (State((), 0), artificial("ABC", 1), artificial("ABCD", 0),
                      artificial("ABCD", 4), artificial("ABCDABCDD", 2)):
            with self.assertRaises(Fault):
                catalog()[0].evaluate(state)

    def test_invalid_types_states_and_json(self):
        class S(str):
            pass
        class T(tuple):
            pass
        invalid = [(["A"] * 4, 2, None, ()), (tuple("ABCD"), True, None, ()),
                   (tuple("ABCD"), 5, None, ()), (tuple("ABCD"), 2, (0, 1), ()),
                   (tuple("ABCD"), 2, (False, 2), ()), (tuple("ABCD"), 2, [0, 2], ()),
                   ((S("A"),) * 4, 2, None, ()), (T("ABCD"), 2, None, ()),
                   (tuple("ABCD"), 2, None, []), (("E",) * 4, 2, None, ())]
        for args in invalid:
            with self.subTest(args=args), self.assertRaises(Fault):
                State(*args)
        for field, value in (("extra", 1), ("cursor", False), ("buffer", "ABCD"),
                             ("clipboard", {}), ("selection", [1])):
            data = artificial().record()
            data[field] = value
            with self.assertRaises(Fault):
                State.parse(data)

    def test_invalid_condition_ast_and_behavioral_subtypes(self):
        for node in (["EQ", "prev", "cursor"], ["EQ", "cursor", "cursor"],
                     ["OR", "cursor", "first"], ["NE", "next", "prev"],
                     ["AND", ["EQ", "cursor", "first"], ["EQ", "cursor", "first"]],
                     ["AND", ["NE", "cursor", "first"], ["EQ", "cursor", "first"]],
                     ["AND", "bad", []], ["EQ", True, "last"], None, {}):
            with self.subTest(node=node), self.assertRaises(Fault):
                Condition.parse(node)
        class Fake(Condition):
            def evaluate(self, *args):
                return True
        with self.assertRaises(Fault):
            execute(Fake((("EQ", "cursor", "first"),)), artificial())

    def test_snapshots_save_restore_and_reject_drift(self):
        for ids in ((), ("cond-000",), ("cond-012", "cond-077")):
            s = Snapshot(ids)
            self.assertEqual(Snapshot.decode(s.encode()), s)
            self.assertEqual(s.selected_id, ids[0] if ids else None)
        baseline = json.loads(Snapshot(("cond-000", "cond-077")).encode())
        for key, value in (("schema", "other"), ("grammar_sha256", "0" * 64),
                           ("candidate_ids", ["cond-077", "cond-000"]),
                           ("candidate_ids", ["cond-000", "cond-000"]),
                           ("candidate_ids", ["cond-078"]), ("candidate_ids", [True]),
                           ("candidate_ids", "cond-000"), ("selected_id", "cond-077"),
                           ("unexpected", True)):
            data = dict(baseline, **{key: value})
            with self.subTest(key=key, value=value), self.assertRaises(Fault):
                Snapshot.decode(canonical(data))
        for data in (b'{"schema":1,"schema":2}', b'NaN', b'\xff', b'[]', b'{}', b' ' * 1048577):
            with self.assertRaises(Fault):
                Snapshot.decode(data)

    def test_fresh_process_determinism_and_no_historical_imports(self):
        program = '''from packages.sentence_revision import *
import sys
assert not any(n.startswith(('packages.world_lean', 'world_lean_evaluator',
 'packages.evaluation', 'packages.kernel', 'packages.exp0003a')) for n in sys.modules)
print(grammar_digest())
print(Snapshot(tuple('cond-%03d' % i for i in range(78))).encode().hex())'''
        results = [subprocess.check_output([sys.executable, "-c", program],
                    env=dict(os.environ, PYTHONHASHSEED=seed)) for seed in ("0", "1", "17")]
        self.assertEqual(len(set(results)), 1)

    def test_costs_include_both_and_atoms_and_keep(self):
        m = Meter()
        with m.phase("shared-preparation"):
            rules = catalog(m)
        with m.phase("artificial-execution"):
            m.tick("candidate_checks")
            execute(Condition((("EQ", "cursor", "first"), ("NE", "cursor", "first"))), artificial(), m)
            delete_right(artificial(), m)
            keep(artificial(), m)
        self.assertEqual(m.counts, dict(candidate_enumerations=78, candidate_checks=1,
                                       condition_evaluations=2, atomic_transitions=1, submissions=3))
        self.assertEqual(m.receipts[0]["counts"]["candidate_enumerations"], 78)
        self.assertEqual(m.receipts[1]["status"], "complete")
        self.assertGreaterEqual(m.receipts[1]["cpu_seconds"], 0)
        self.assertEqual(len(rules), 78)

    def test_candidate_cap_stops_before_overrun_and_resets_per_phase(self):
        m = Meter(max_checks=1)
        with self.assertRaises(BudgetExceeded):
            with m.phase("build"):
                m.tick("candidate_checks")
                m.tick("candidate_checks")
        self.assertEqual(m.counts["candidate_checks"], 1)
        self.assertEqual(m.receipts[0]["status"], "budget_exhausted")
        with m.phase("update"):
            m.tick("candidate_checks")
        with self.assertRaises(Fault):
            m.tick("candidate_checks")

    def test_snapshot_validation_enumeration_is_not_free(self):
        m = Meter()
        with m.phase("snapshot-save"):
            data = Snapshot(("cond-000",)).encode(m)
        with m.phase("snapshot-restore"):
            Snapshot.decode(data, m)
        self.assertEqual(m.receipts[0]["counts"]["candidate_enumerations"], 78)
        self.assertEqual(m.receipts[1]["counts"]["candidate_enumerations"], 156)

    def test_cpu_and_memory_guards_and_failure_receipts(self):
        with patch("packages.sentence_revision.foundation.time.process_time", return_value=10):
            m = Meter(phase_cpu=1, total_cpu=5)
            with self.assertRaises(BudgetExceeded):
                with m.phase("CPU"):
                    with patch("packages.sentence_revision.foundation.time.process_time", return_value=11):
                        m.checkpoint()
            self.assertEqual(m.receipts[0]["status"], "budget_exhausted")
            with patch("packages.sentence_revision.foundation.time.process_time", return_value=15):
                with self.assertRaises(BudgetExceeded):
                    m.checkpoint()
        with self.assertRaises(BudgetExceeded):
            Meter().checkpoint(b'x' * 1048576)
        s = artificial()
        self.assertLess(retained_size((s, s)), retained_size((s, artificial())))
        self.assertGreater(retained_size(Snapshot(("cond-000",))), 0)
        with self.assertRaises(Fault):
            retained_size(object())
        m = Meter()
        with self.assertRaises(Fault):
            with m.phase("failure"):
                raise Fault("artificial failure")
        self.assertEqual(m.receipts[-1]["status"], "failed")
        for kw in ({"max_checks": True}, {"max_checks": 100001}, {"phase_cpu": 61},
                   {"total_cpu": 7201}, {"max_bytes": 1048577}, {"phase_cpu": float('nan')}):
            with self.assertRaises(Fault):
                Meter(**kw)


if __name__ == "__main__":
    unittest.main()

"""Deterministic exhaustive search and independent semantics checks."""
import unittest
from packages.protocol import Call, Input, parse_task, program_hash
from packages.synthesis import enumerate_candidates, synthesize
from packages.runtime import evaluate
from packages.verification import verify
from packages.cli.__main__ import run_suite


def task(name, examples, *, max_nodes=4, max_candidates=5000):
    return parse_task({"schema_version": "0.1", "task_id": name,
                       "domain": "string_to_string", "examples": [
                           {"input": x, "output": y} for x, y in examples],
                       "limits": {"max_ast_nodes": max_nodes, "max_candidates": max_candidates}})


class SynthesisTests(unittest.TestCase):
    def test_enumerator_order_and_uniqueness(self):
        programs = list(enumerate_candidates(max_nodes=4))
        self.assertEqual(len(programs), 1 + 3 + 9 + 27)
        self.assertEqual(programs[:4], [Input(), Call("trim", Input()),
                                       Call("lower", Input()), Call("upper", Input())])
        self.assertEqual(len({program_hash(p) for p in programs}), 40)

    def test_expected_programs(self):
        for name, pairs, expected in (
            ("id", [("abc", "abc"), ("z", "z")], Input()),
            ("trim", [(" x ", "x"), ("  y", "y")], Call("trim", Input())),
            ("lower", [("HI", "hi"), ("Z", "z")], Call("lower", Input())),
            ("compose", [(" RED ", "red"), (" Blue ", "blue")],
             Call("lower", Call("trim", Input()))),
        ):
            with self.subTest(name=name):
                result = synthesize(task(name, pairs))
                self.assertEqual(result.status, "solved")
                self.assertEqual(result.program, expected)
                self.assertTrue(verify(result.program, task(name, pairs).examples).matched)

    def test_correct_failure_and_boundary(self):
        no_solution = synthesize(task("reverse", [("ab", "ba")]))
        self.assertEqual(no_solution.status, "not_found")
        self.assertEqual(no_solution.tested_candidates, 40)
        cutoff = synthesize(task("budget", [(" RED ", "red")], max_candidates=1))
        self.assertEqual(cutoff.status, "budget_exhausted")
        self.assertEqual(cutoff.tested_candidates, 1)
        exact = synthesize(task("exact-limit", [(" x ", "x")], max_nodes=2, max_candidates=2))
        self.assertEqual(exact.status, "solved")
        self.assertEqual(exact.tested_candidates, 2)

    def test_repeatability_and_trace(self):
        t = task("compose", [(" RED ", "red"), (" Blue ", "blue")])
        first, second = synthesize(t), synthesize(t)
        self.assertEqual((first.status, first.program, first.tested_candidates, first.trace_sha256),
                         (second.status, second.program, second.tested_candidates, second.trace_sha256))
        self.assertNotEqual(first.trace_sha256, synthesize(task("other", [("x", "x")])).trace_sha256)

    def test_independent_holdout_outputs(self):
        t = task("compose", [(" RED ", "red"), (" Blue ", "blue")])
        solution = synthesize(t).program
        self.assertIsNotNone(solution)
        for x, expected in [("  ALPHA  ", "alpha"), (" z ", "z"), ("ABC", "abc"), ("", "")]:
            with self.subTest(x=x):
                self.assertEqual(evaluate(solution, x), expected)

    def test_preregistered_suite(self):
        report = run_suite()
        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(report["cases"]), 7)
        self.assertTrue(all(case["passed"] for case in report["cases"]))


if __name__ == "__main__":
    unittest.main()

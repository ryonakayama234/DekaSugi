"""EXP-0002B: observed runtime primitive calls, including macro expansion."""
import unittest
from dataclasses import replace
from unittest.mock import patch

from packages.evaluation import (
    DEV, TRAIN, PrimitiveCallMeter, _task, bounded_synthesize,
)
from packages.library import DEFAULT_PRIMITIVES, DEFAULT_REGISTRY, Registry
from packages.learning import discover_skills, registry_with_skill
from packages.protocol import Call, Input


class PrimitiveCallMeterTests(unittest.TestCase):
    def test_primitive_only_counts_actual_verifier_calls(self):
        task = _task("meter-lower", (("ABC", "abc"), ("DEF", "def")))
        plain = bounded_synthesize(task, DEFAULT_REGISTRY)
        meter = PrimitiveCallMeter()
        observed = bounded_synthesize(task, DEFAULT_REGISTRY, meter=meter)
        self.assertEqual(observed.status, "solved")
        self.assertEqual(observed.tested_candidates, 3)
        self.assertEqual((observed.program, observed.trace_sha256),
                         (plain.program, plain.trace_sha256))
        self.assertEqual(meter.to_dict(), {
            "primitive_invocations": 4, "by_op": {"lower": 2, "trim": 2}
        })

    def test_macro_counts_primitive_body_not_one_macro_call(self):
        skill = discover_skills(TRAIN)[0]
        extended = registry_with_skill(skill)
        meter = PrimitiveCallMeter()
        measured = bounded_synthesize(
            DEV[0], extended, {skill.skill_id: skill}, meter=meter
        )
        unmeasured = bounded_synthesize(
            DEV[0], extended, {skill.skill_id: skill}
        )
        self.assertEqual(measured.status, "solved")
        self.assertEqual(measured.tested_candidates, 5)
        self.assertEqual((measured.program, measured.trace_sha256),
                         (unmeasured.program, unmeasured.trace_sha256))
        # 2 examples each: trim/lower/upper candidates = 6 calls;
        # lower(trim(input)) macro candidate = 4 more primitive calls.
        self.assertEqual(meter.to_dict(), {
            "primitive_invocations": 10,
            "by_op": {"lower": 4, "trim": 4, "upper": 2},
        })
        self.assertEqual(tuple(p.op_id for p in DEFAULT_REGISTRY.primitives),
                         ("trim", "lower", "upper"))

    def test_identity_zero_calls_even_with_meter(self):
        task = _task("meter-identity", (("x", "x"), ("Ab", "Ab")))
        meter = PrimitiveCallMeter()
        result = bounded_synthesize(task, DEFAULT_REGISTRY, meter=meter)
        self.assertEqual(result.tested_candidates, 1)
        self.assertEqual(meter.total, 0)
        self.assertEqual(meter.by_op, {})

    def test_each_arm_uses_independent_counter(self):
        task = _task("meter-trim", ((" x ", "x"),))
        first = PrimitiveCallMeter()
        second = PrimitiveCallMeter()
        bounded_synthesize(task, DEFAULT_REGISTRY, meter=first)
        bounded_synthesize(task, DEFAULT_REGISTRY, meter=second)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.total, 1)


    def test_rejects_forged_primitive_before_execution_or_metering(self):
        def poison(_value: str) -> str:
            raise AssertionError("Caller primitive must not execute")
        forged = Registry((
            replace(DEFAULT_PRIMITIVES[0], implementation=poison),
            *DEFAULT_PRIMITIVES[1:],
        ))
        meter = PrimitiveCallMeter()
        with self.assertRaisesRegex(ValueError, "Unapproved primitive"):
            bounded_synthesize(TRAIN[0], forged, meter=meter)
        self.assertEqual(meter.total, 0)

    def test_poisoned_default_and_caller_lookup_never_execute(self):
        def poison(_value: str) -> str:
            raise AssertionError("Poisoned lookup executed")
        task = DEV[0]
        skill = discover_skills(TRAIN)[0]
        canonical = Registry()
        extended = registry_with_skill(skill, canonical)
        learned = {skill.skill_id: skill}

        def stable(result):
            return (result.status, result.program,
                    result.tested_candidates, result.trace_sha256)

        expected_off = stable(bounded_synthesize(task, canonical))
        expected_on = stable(bounded_synthesize(task, extended, learned))
        bad_lookup = dict(DEFAULT_REGISTRY.by_name)
        bad_lookup["trim"] = replace(DEFAULT_PRIMITIVES[0], implementation=poison)
        with (patch.object(DEFAULT_REGISTRY, "by_name", bad_lookup),
              patch.object(DEFAULT_REGISTRY, "signatures", {}),
              patch.object(DEFAULT_REGISTRY, "primitives", (
                  replace(DEFAULT_PRIMITIVES[0], implementation=poison),
                  *DEFAULT_PRIMITIVES[1:],
              ))):
            canonical.by_name = bad_lookup
            canonical.signatures = {}
            extended.by_name = {**extended.by_name,
                                skill.skill_id: replace(
                                    extended.primitives[-1], implementation=poison)}
            extended.signatures = {}
            for registry, skills, expected in (
                (canonical, None, expected_off),
                (extended, learned, expected_on),
            ):
                counter = PrimitiveCallMeter()
                self.assertEqual(stable(bounded_synthesize(
                    task, registry, skills, meter=counter)), expected)
                self.assertGreater(counter.total, 0)

    def test_poisoned_macro_callable_is_rebuilt_from_canonical_ast(self):
        skill = discover_skills(TRAIN)[0]
        registry = registry_with_skill(skill)
        def poison(_value: str) -> str:
            raise AssertionError("Injected macro implementation executed")
        poisoned = Registry(registry.primitives[:-1] + (
            replace(registry.primitives[-1], implementation=poison),))
        expected = bounded_synthesize(DEV[0], registry, {skill.skill_id: skill})
        meter = PrimitiveCallMeter()
        result = bounded_synthesize(
            DEV[0], poisoned, {skill.skill_id: skill}, meter=meter)
        self.assertEqual((result.status, result.program,
                          result.tested_candidates, result.trace_sha256),
                         (expected.status, expected.program,
                          expected.tested_candidates, expected.trace_sha256))
        self.assertEqual(meter.total, 10)

    def test_rejects_forged_macro_or_budget_before_counting(self):
        skill = discover_skills(TRAIN)[0]
        extended = registry_with_skill(skill)
        bad = replace(skill, body_hash="f" * 64)
        meter = PrimitiveCallMeter()
        with self.assertRaisesRegex(ValueError, "body hash mismatch"):
            bounded_synthesize(
                DEV[0], extended, {skill.skill_id: bad}, meter=meter)
        self.assertEqual(meter.total, 0)
        # Nested macro shapes must not silently bypass expanded AST budget.
        self.assertEqual(
            bounded_synthesize(DEV[0], extended, {skill.skill_id: skill},
                               meter=meter).tested_candidates, 5)
        self.assertEqual(meter.total, 10)

    def test_meter_report_is_diagnostic_not_new_policy_result(self):
        from packages.evaluation import run_experiment
        report = run_experiment()
        self.assertEqual(report["primitive_measurement_version"], "runtime-canonical-v1")
        self.assertEqual(report["promotion_status"], "pending_independent_review")
        samples = {entry["task_id"]: entry for entry in report["comparisons"]}
        for task_id, off, on in (
            ("dev-01", 14, 10),
            ("holdout-01", 14, 10),
            ("holdout-02", 14, 10),
            ("negative-reverse", 102, 122),
            ("negative-identity", 0, 0),
        ):
            self.assertEqual(samples[task_id]["primitive_measurements"]["off"]
                             ["primitive_invocations"], off)
            self.assertEqual(samples[task_id]["primitive_measurements"]["on"]
                             ["primitive_invocations"], on)


if __name__ == "__main__":
    unittest.main()

"""EXP-0002B: observed runtime primitive calls, including macro expansion."""
import unittest

from packages.evaluation import (
    DEV, TRAIN, PrimitiveCallMeter, _task, bounded_synthesize,
)
from packages.library import DEFAULT_REGISTRY
from packages.learning import discover_skills, registry_with_skill


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


if __name__ == "__main__":
    unittest.main()

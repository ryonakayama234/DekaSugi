"""Independent safety, discovery, determinism and evaluation gates for EXP-0002."""
import unittest
from dataclasses import replace

from packages.learning import SkillCandidate
from packages.protocol import program_hash

from packages.evaluation import (
    DEV, TRAIN, HOLDOUT, bounded_synthesize, expanded_nodes, run_experiment,
)
from packages.learning import (
    discover_skills, registry_with_skill, validate_skill,
)
from packages.library import DEFAULT_REGISTRY, Primitive, Registry
from packages.protocol import Call, Input, DSLValidationError
from packages.runtime import evaluate
from packages.synthesis import synthesize


class LearningTests(unittest.TestCase):
    def test_discovery_uses_two_distinct_training_episodes(self):
        self.assertEqual(discover_skills(TRAIN[:1]), ())
        candidates = discover_skills(TRAIN)
        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c.body_ast, Call("lower", Call("trim", Input())))
        self.assertEqual(c.provenance, ("train-01", "train-02"))
        self.assertEqual(c.dependencies, ("lower", "trim"))
        self.assertEqual(c.occurrences, 2)

    def test_macro_is_safe_isolated_and_semantically_equivalent(self):
        c = discover_skills(TRAIN)[0]
        r = registry_with_skill(c)
        self.assertEqual(tuple(p.op_id for p in DEFAULT_REGISTRY.primitives),
                         ("trim", "lower", "upper"))
        self.assertEqual(len(r.primitives), 4)
        for value in ("  RED ", "", " ÅBC ", "\tHi\n", "MiXeD"):
            self.assertEqual(evaluate(Call(c.skill_id, Input()), value, r),
                             evaluate(c.body_ast, value))
        for damaged in (
            replace(c, body_hash="0" * 64),
            replace(c, dependencies=("os.system",)),
            replace(c, body_ast=Call("not_allowlisted", Input())),
            replace(c, provenance=("train-01",)),
        ):
            with self.subTest(damaged=damaged), self.assertRaises(DSLValidationError):
                validate_skill(damaged)

    def test_nested_macros_rejected_and_expansion_cost_is_recursive(self):
        base = discover_skills(TRAIN)[0]
        extended = registry_with_skill(base)
        # This used to be accepted as two calls; the true physical cost is 5.
        nested_body = Call(base.skill_id, Call(base.skill_id, Input()))
        digest = program_hash(nested_body)
        nested = SkillCandidate(
            skill_id="skill_" + digest[:16], body_ast=nested_body,
            body_hash=digest, dependencies=(base.skill_id,),
            provenance=("train-01", "train-02"), occurrences=2,
        )
        with self.assertRaisesRegex(DSLValidationError, "Nested learned macros"):
            registry_with_skill(nested, extended)
        self.assertEqual(expanded_nodes(nested_body, {base.skill_id: base}), 5)
        with self.assertRaisesRegex(ValueError, "Registry and learned-skill"):
            bounded_synthesize(HOLDOUT[0], extended)
        cyclic_body = Call(base.skill_id, Input())
        cyclic = replace(base, body_ast=cyclic_body,
                         body_hash=program_hash(cyclic_body))
        with self.assertRaisesRegex(ValueError, "Cyclic macro"):
            expanded_nodes(Call(base.skill_id, Input()), {base.skill_id: cyclic})

    def test_forged_macro_metadata_cannot_underreport_cost(self):
        skill = discover_skills(TRAIN)[0]
        registry = registry_with_skill(skill)
        forged_body = replace(skill, body_ast=Input())
        with self.assertRaisesRegex(ValueError, "body hash mismatch"):
            bounded_synthesize(TRAIN[0], registry, {skill.skill_id: forged_body})
        with self.assertRaisesRegex(ValueError, "body hash mismatch"):
            expanded_nodes(Call(skill.skill_id, Input()), {skill.skill_id: forged_body})
        # Forging a self-consistent hash still must not change the registered body.
        forged_hash = replace(forged_body, body_hash=program_hash(Input()))
        with self.assertRaisesRegex(ValueError, "Registered skill body hash"):
            bounded_synthesize(TRAIN[0], registry, {skill.skill_id: forged_hash})

    def test_disguised_macro_and_unapproved_primitives_fail_closed(self):
        skill = discover_skills(TRAIN)[0]
        approved_registry = registry_with_skill(skill)

        def poison(_value: str) -> str:
            raise AssertionError("Untrusted registry function must not execute")

        # P1 regression: re-label the macro as a non-derived primitive.
        # Previously this passed with learned=None and undercounted its body.
        disguised = replace(approved_registry.primitives[-1],
                            semantics_version="python-str-lower-v1")
        forged = Registry(approved_registry.primitives[:-1] + (disguised,))
        with self.assertRaisesRegex(ValueError, "Registry and learned-skill"):
            bounded_synthesize(TRAIN[0], forged)

        # Forging an allowlisted name/version must not authorize a new callable.
        forged_lower = replace(DEFAULT_REGISTRY.primitives[1], implementation=poison)
        forged = Registry((DEFAULT_REGISTRY.primitives[0], forged_lower,
                           DEFAULT_REGISTRY.primitives[2]))
        with self.assertRaisesRegex(ValueError, "Unapproved primitive"):
            bounded_synthesize(TRAIN[0], forged)

        # Primitive order is part of deterministic search; reject reordering.
        reordered = Registry(tuple(reversed(DEFAULT_REGISTRY.primitives)))
        with self.assertRaisesRegex(ValueError, "Unapproved primitive"):
            bounded_synthesize(TRAIN[0], reordered)

        unknown = Primitive("unknown", "String", "String",
                            "python-str-lower-v1", poison)
        with self.assertRaisesRegex(ValueError, "Registry and learned-skill"):
            bounded_synthesize(TRAIN[0],
                               Registry(DEFAULT_REGISTRY.primitives + (unknown,)))

        # Even a forged macro callable with a matching derived-version label
        # is never executed: the evaluator rebuilds it from canonical AST.
        poisoned_macro = replace(approved_registry.primitives[-1],
                                 implementation=poison)
        poisoned_registry = Registry(approved_registry.primitives[:-1]
                                     + (poisoned_macro,))
        expected = bounded_synthesize(
            TRAIN[0], approved_registry, {skill.skill_id: skill})
        actual = bounded_synthesize(
            TRAIN[0], poisoned_registry, {skill.skill_id: skill})
        self.assertEqual((actual.status, actual.program, actual.tested_candidates,
                          actual.trace_sha256),
                         (expected.status, expected.program, expected.tested_candidates,
                          expected.trace_sha256))

    def test_expanded_budget_and_baseline_equivalence(self):
        c = discover_skills(TRAIN)[0]
        r = registry_with_skill(c)
        self.assertEqual(expanded_nodes(Call(c.skill_id, Input()), {c.skill_id: c}), 3)
        self.assertEqual(expanded_nodes(Call("trim", Call(c.skill_id, Input())),
                                        {c.skill_id: c}), 4)
        for task in HOLDOUT + DEV:
            first = bounded_synthesize(task, DEFAULT_REGISTRY)
            original = synthesize(task)
            self.assertEqual((first.status, first.program, first.tested_candidates,
                              first.trace_sha256),
                             (original.status, original.program, original.tested_candidates,
                              original.trace_sha256))
            second = bounded_synthesize(task, r, {c.skill_id: c})
            self.assertLessEqual(second.tested_candidates, task.limits.max_candidates)
            if second.program:
                self.assertLessEqual(expanded_nodes(second.program, {c.skill_id: c}),
                                     task.limits.max_ast_nodes)

    def test_comparison_is_repeatable_and_holdout_is_not_training(self):
        first, second = run_experiment(), run_experiment()
        self.assertEqual(first["train_task_ids"], ["train-01", "train-02"])
        self.assertEqual(first["final_task_ids"],
                         ["holdout-01", "holdout-02", "negative-reverse", "negative-identity"])
        self.assertEqual(first["status"], "functional_pass")
        self.assertEqual(first["search_benefit_same_task_family"], True)
        self.assertEqual(first["promotion_status"], "pending_independent_review")
        def stable_rows(report):
            return [(row["task_id"], row["baseline"]["status"],
                     row["baseline"]["tested_candidates"],
                     row["baseline"]["trace_sha256"], row["learned"]["status"],
                     row["learned"]["tested_candidates"],
                     row["learned"]["trace_sha256"]) for row in report["comparisons"]]
        self.assertEqual(stable_rows(first), stable_rows(second))
        positives = [row for row in first["comparisons"]
                     if row["task_id"].startswith("holdout")]
        self.assertTrue(all(row["candidate_delta"] >= 1 for row in positives))


if __name__ == "__main__":
    unittest.main()

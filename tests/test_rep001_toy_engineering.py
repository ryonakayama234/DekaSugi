"""EXP-REP-001 toy-only contract tests; NOT a research score."""
import unittest
from dataclasses import replace
from packages.relational_world import Action, InventedWorld, Observation, Relation, step
from packages.world_model import candidates, consistent_models, choose_discriminating_probe, diagnose
from packages.rep_evaluation import run_toy
from packages.representation import (induce_train_snapshot, validate_snapshot,
                                     induce_rank_only_snapshot, rank_only_prediction,
                                     learned_model_preference, digest, relational_prediction)


class RelationalWorldToyTests(unittest.TestCase):
    def setUp(self):
        self.objects = ("a", "b", "c", "d")

    def test_pulse_direct_and_gate(self):
        zeros = (False,) * 4
        direct = (Relation("a", "c"),)
        gated = (Relation("a", "c", "b", True),)
        self.assertEqual(step(self.objects, zeros, Action("pulse", "a"), direct), (False, False, True, False))
        self.assertEqual(step(self.objects, zeros, Action("pulse", "a"), gated), zeros)
        self.assertEqual(step(self.objects, (False, True, False, False), Action("pulse", "a"), gated),
                         (False, True, True, False))
        self.assertEqual(step(self.objects, zeros, Action("set_state", "b", True), gated),
                         (False, True, False, False))

    def test_boolean_strict_and_fail_closed(self):
        with self.assertRaises(ValueError):
            step(self.objects, (0, False, False, False), Action("pulse", "a"), ())
        for bad in (Action("run_shell", "a"), Action("pulse", "invalid"), Action("pulse", "a", False),
                    Action("set_state", "a", 1)):
            with self.subTest(action=bad), self.assertRaises(ValueError):
                step(self.objects, (False,) * 4, bad, ())
        with self.assertRaises(ValueError):
            step(self.objects, (False,) * 4, Action("pulse", "a"), (Relation("a", "a"),))

    def test_public_observation_excludes_hidden_relation(self):
        world = InventedWorld("train-1", self.objects, (Relation("a", "c", "b"),))
        obs = world.probe((False, True, False, False), Action("pulse", "a"))
        self.assertIsInstance(obs, Observation)
        self.assertFalse(hasattr(obs, "rules"))
        self.assertFalse(hasattr(obs, "_rules"))
        self.assertEqual(obs.after, (False, True, True, False))

    def test_counterexample_triggers_representation_refinement(self):
        world = InventedWorld("w", self.objects, (Relation("a", "c", "b", True),))
        observations = (
            world.probe((False, True, False, False), Action("pulse", "a")),
            world.probe((False, False, False, False), Action("pulse", "a")),
        )
        status = diagnose(self.objects, observations)
        self.assertEqual(status.direct_survivors, 0)
        self.assertGreater(status.expressive_survivors, 0)
        self.assertIn(status.status, ("representation_refinement_identified", "representation_refinement_ambiguous"))

    def test_deterministic_disagreement_query(self):
        models = candidates(self.objects, expressive=False)
        one = choose_discriminating_probe(self.objects, models)
        self.assertEqual(one, choose_discriminating_probe(self.objects, models))
        self.assertEqual(one[1].kind, "pulse")
        self.assertEqual(len(one[0]), 4)

    def test_unique_training_evidence_generates_role_concept(self):
        training = {}
        for index in range(3):
            ids = tuple(f"w{index}_{k}" for k in range(4))
            world = InventedWorld(f"w{index}", ids, (Relation(ids[0], ids[2], ids[1], True),))
            observations = []
            for before in ((False, False, False, False), (False, True, False, False)):
                for source in ids:
                    observations.append(world.probe(before, Action("pulse", source)))
            training[f"w{index}"] = tuple(observations)
        snapshot = induce_train_snapshot(training)
        validate_snapshot(snapshot)
        self.assertEqual(len(snapshot.concepts), 1)
        self.assertEqual(snapshot.concepts[0].role_pattern, "gated_true")
        self.assertEqual(snapshot.concepts[0].support_count, 3)
        self.assertEqual(len(snapshot.world_receipt), 64)
        self.assertEqual(snapshot, induce_train_snapshot(training))
        with self.assertRaises(ValueError):
            validate_snapshot(replace(snapshot, world_receipt="x" * 64))
        with self.assertRaises(ValueError):
            validate_snapshot(replace(snapshot, snapshot_digest="0" * 64))
        with self.assertRaises(ValueError):
            induce_train_snapshot({"w1": (training["w0"][0],)})

    def test_invented_pipeline_never_claims_formal_score(self):
        report = run_toy()
        self.assertEqual(report.source_kind, "INVENTED_TOY_ENGINEERING_ONLY")
        self.assertEqual(report.train_worlds, 3)
        self.assertEqual(report.toy_eval_worlds, 4)
        self.assertEqual(report.audit_count, 8)
        self.assertIn("gated_true", report.concept_names)
        self.assertGreaterEqual(report.r3_correct, report.r2_correct)

    def test_renaming_keeps_relational_shape(self):
        for ids in (self.objects, ("u", "v", "x", "y")):
            rule = (Relation(ids[0], ids[2], ids[1], True),)
            world = InventedWorld("w", ids, rule)
            trials = tuple(world.probe(bits, Action("pulse", src)) for bits in
                           ((False, False, False, False), (False, True, False, False)) for src in ids)
            models = consistent_models(ids, trials, True)
            self.assertEqual(models, (rule,))


    def test_behavioral_string_fields_rejected_before_action_or_rule_comparison(self):
        class BehavioralStr(str):
            def __eq__(self, other):
                return other in ("pulse", "set_state", "a", "b", "c", "d")
            __hash__ = str.__hash__

        zeros = (False,) * 4
        bad_actions = (Action(BehavioralStr("run_shell"), "a", True),
                       Action("pulse", BehavioralStr("a")),
                       Action("set_state", "a", True))
        for action in bad_actions[:2]:
            with self.subTest(action=action), self.assertRaises(ValueError):
                step(self.objects, zeros, action, ())
        for rule in (Relation(BehavioralStr("a"), "c"),
                     Relation("a", BehavioralStr("c")),
                     Relation("a", "c", BehavioralStr("b"))):
            with self.subTest(rule=rule), self.assertRaises(ValueError):
                step(self.objects, zeros, Action("pulse", "a"), (rule,))

    def test_all_observations_rejected_if_malformed_even_after_no_survivors(self):
        zero = (False,) * 4
        act = Action("pulse", "a")
        # No candidate can produce this changed state from this action.
        impossible = Observation("w", self.objects, zero, act,
                                 (True, True, True, True))
        bad_after = Observation("w", self.objects, zero, act,
                                (False, False, 1, False))
        bad_short = Observation("w", self.objects, zero, act,
                                (False, False, False))
        bad_action = Observation("w", self.objects, zero, Action("pulse", "bad"), zero)
        for bad in (bad_after, bad_short, bad_action):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                consistent_models(self.objects, (impossible, bad), True)
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                diagnose(self.objects, (bad,))

    def test_snapshot_rejects_behavioral_keys_and_bool_counts(self):
        class BehavioralStr(str):
            def __eq__(self, other):
                return other in ("gated_true", "direct")
            __hash__ = str.__hash__

        from packages.rep_evaluation import training_fixture
        snapshot = induce_train_snapshot(training_fixture())
        original = snapshot.concepts[0]
        for malformed in (
            replace(original, role_pattern=BehavioralStr("gated_true")),
            replace(original, support_count=True),
            replace(original, support_worlds=tuple([BehavioralStr(original.support_worlds[0]),
                                                      *original.support_worlds[1:]])),
        ):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                validate_snapshot(replace(snapshot, concepts=(malformed,)))

    def test_rank_only_control_shows_policy_confound_in_favorable_toy(self):
        from packages.rep_evaluation import training_fixture
        memory = training_fixture()
        concepts = induce_train_snapshot(memory)
        rank = induce_rank_only_snapshot(memory)
        self.assertEqual(concepts.world_receipt, rank.world_receipt)
        self.assertEqual(rank.preferences, (("gated_true", 3),))
        world = InventedWorld("new", self.objects, (Relation("a", "c", "b", True),))
        evidence = (world.probe((False, True, False, False), Action("pulse", "a")),)
        test_state, test_action = ((False, False, True, False), Action("pulse", "a"))
        self.assertEqual(rank_only_prediction(rank, self.objects, evidence, test_state, test_action),
                         relational_prediction(concepts, self.objects, evidence, test_state, test_action))
        with self.assertRaises(ValueError):
            rank_only_prediction(replace(rank, snapshot_digest="0" * 64),
                                 self.objects, evidence, test_state, test_action)
        toy = run_toy()
        self.assertEqual(toy.r2p_correct, toy.r3_correct)
        self.assertEqual(toy.r2p_correct, toy.audit_count)

if __name__ == "__main__":
    unittest.main()

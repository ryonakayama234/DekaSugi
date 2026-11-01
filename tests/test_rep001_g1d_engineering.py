"""G1-D synthetic-only engineering tests. NO sealed datasets or formal scorer."""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest

from packages.relational_world import Action, InventedWorld, Observation, Relation
from packages.rep_lab import (ToySession, canonical_body, canonical_hash,
    diagnose_one_edge, disclosed_training_worlds, disclosed_world, eval_audit,
    evaluate_disclosed, full_public_episode, learn_snapshot, load_snapshot,
    active_public_episode, choose_cost_aware_query, passive_public_episode,
    instantiate_template, predict, run_pilot, save_snapshot, search_two_edges,
    validate_snapshot)


class G1DTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ids = ("a", "b", "c", "d")

    def _world(self, rules, alias="test"):
        return InventedWorld(alias, self.ids, tuple(rules))

    def test_complete_one_edge_mismatch_and_repair(self):
        w = self._world((Relation("a", "b"), Relation("a", "c")))
        obs, charged = full_public_episode(w)
        self.assertGreater(charged, 64)  # paid setup + 64 pulses
        diag = diagnose_one_edge(self.ids, obs)
        self.assertEqual(diag.status, "MODEL_CLASS_MISMATCH")
        self.assertTrue(diag.search_complete)
        found = search_two_edges(self.ids, obs)
        self.assertEqual(found.status, "IDENTIFIED")
        self.assertEqual(found.total_matches, 1)
        self.assertEqual(set(found.candidates[0].model),
                         {Relation("a", "b"), Relation("a", "c")})
        self.assertEqual(found.candidates[0].body_hash,
                         canonical_hash(found.candidates[0].body))

    def test_no_false_mismatch_when_insufficient(self):
        w = self._world((Relation("a", "b"),))
        session = ToySession(w)
        self.assertEqual(diagnose_one_edge(self.ids, ()).status, "UNDERIDENTIFIED")
        session.act(Action("pulse", "d"))
        self.assertEqual(diagnose_one_edge(self.ids, tuple(session.observations)).status,
                         "UNDERIDENTIFIED")

    def test_search_exhaustion_is_distinct(self):
        w = self._world((Relation("a", "b"), Relation("a", "c")))
        obs, _ = full_public_episode(w)
        self.assertEqual(diagnose_one_edge(self.ids, obs, max_candidates=10).status,
                         "SEARCH_EXHAUSTED")
        incomplete = search_two_edges(self.ids, obs, max_pairs=10)
        self.assertFalse(incomplete.search_complete)
        self.assertEqual(incomplete.status, "SEARCH_EXHAUSTED")

    def test_full_evidence_validation_before_search(self):
        w = self._world((Relation("a", "b"), Relation("a", "c")))
        obs, _ = full_public_episode(w)
        o = obs[-1]
        bad = Observation(o.world_alias, o.object_ids, o.before,
                          o.action, (1, False, False, False))
        self.assertEqual(diagnose_one_edge(self.ids, obs + (bad,)).status, "INVALID_EVIDENCE")
        with self.assertRaises(ValueError):
            search_two_edges(self.ids, obs + (bad,))

    def test_inconsistent_replays(self):
        w = self._world((Relation("a", "b"),))
        first = w.probe((False,)*4, Action("pulse", "a"))
        conflicting = Observation(first.world_alias, first.object_ids, first.before,
                                  first.action, (False,)*4)
        self.assertEqual(diagnose_one_edge(self.ids, (first, conflicting)).status,
                         "INCONSISTENT_REPLAYS")

    def test_set_state_forgery_rejected(self):
        fabricated = Observation("test", self.ids, (False,)*4,
                                 Action("set_state", "a", True), (False,)*4)
        self.assertEqual(diagnose_one_edge(self.ids, (fabricated,)).status, "INVALID_EVIDENCE")

    def test_role_renaming_and_edge_order_invariant(self):
        one = (Relation("a", "b"), Relation("a", "c"))
        two = (Relation("w", "z"), Relation("w", "k"))
        self.assertEqual(canonical_body(one), canonical_body(two))
        self.assertEqual(canonical_body(one), canonical_body(tuple(reversed(one))))
        three = (Relation("a", "b"), Relation("c", "d"))
        self.assertNotEqual(canonical_body(one), canonical_body(three))

    def test_metered_reachable_actions(self):
        w = self._world((Relation("a", "b"),))
        s = ToySession(w)
        s.configure((True, False, True, False))
        self.assertEqual(s.actions_charged, 2)
        self.assertEqual(s.state, (True, False, True, False))
        s.act(Action("pulse", "a"))
        self.assertEqual(s.actions_charged, 3)
        s.reset()
        self.assertEqual(s.resets_charged, 1)
        self.assertEqual(s.state, (False,)*4)

    def test_snapshot_and_idempotent_source(self):
        self.assertEqual(learn_snapshot({}).train_count, 0)
        train = disclosed_training_worlds(3)
        s = learn_snapshot(train)
        self.assertEqual(s.train_count, 3)
        self.assertEqual(len(s.templates), 1)
        self.assertEqual(s.templates[0].support_worlds, tuple(sorted(train)))
        self.assertEqual(s.digest, learn_snapshot(train).digest)

    def test_snapshot_reload_and_tamper(self):
        s = learn_snapshot(disclosed_training_worlds(3))
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "snapshot.json"
            save_snapshot(s, p)
            self.assertEqual(s, load_snapshot(p))
            mutated = json.loads(p.read_text(encoding="utf8"))
            mutated["templates"][0]["support_worlds"][0] = "fake"
            p.write_text(json.dumps(mutated), encoding="utf8")
            with self.assertRaises(ValueError):
                load_snapshot(p)

    def test_invalid_types_in_snapshot(self):
        s = learn_snapshot(disclosed_training_worlds(3))
        fake = type(s)(s.schema, s.grammar, s.train_receipt, True,
                       s.templates, s.atom_rank, s.digest)
        with self.assertRaises(ValueError):
            validate_snapshot(fake)

    def test_gated_model_and_unmodeled_repair(self):
        w = self._world((Relation("a", "b", "d", True), Relation("a", "c")))
        obs, _ = full_public_episode(w)
        self.assertEqual(diagnose_one_edge(self.ids, obs).status, "MODEL_CLASS_MISMATCH")
        result = search_two_edges(self.ids, obs)
        self.assertTrue(result.search_complete)
        self.assertGreater(result.total_matches, 0)

    def test_repair_predicts_unobserved_state(self):
        training = disclosed_training_worlds(3)
        snapshot = learn_snapshot(training)
        world = disclosed_world(101, "toy-eval", "fork")
        evidence, _ = passive_public_episode(world)
        before = (True, False, True, False)
        action = Action("pulse", world.object_ids[1])
        output = predict(world.object_ids, evidence, before, action, "B3", snapshot)
        self.assertIn(output.status, ("PREDICTED", "ABSTAIN"))
        if output.after is not None:
            self.assertEqual(len(output.after), 4)

    def test_b5_active_actions_reachable_and_costed(self):
        w = self._world((Relation("a", "b", "d", True), Relation("a", "c")))
        transcript, cost = active_public_episode(w, budget=4)
        self.assertLessEqual(cost, 4)
        self.assertEqual(cost, len(transcript))
        self.assertGreater(cost, 0)
        self.assertEqual(transcript[0].before, (False,)*4)
        self.assertTrue(all(x.action.kind in ("pulse", "set_state") for x in transcript))
        self.assertIsNone(choose_cost_aware_query(self.ids, (False,)*4, (), remaining=0))

    def test_cli_train_inspect_use_with_snapshot(self):
        import contextlib
        from io import StringIO
        from unittest.mock import patch
        from packages.rep_lab.__main__ import main
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "trained.json"
            for args, status in (
                (["rep_lab", "train", "--worlds", "3", "--snapshot", str(path)],
                 "DISCLOSED_TOY_TRAIN"),
                (["rep_lab", "inspect", "--snapshot", str(path)],
                 "rep-g1d-toy-snapshot/1"),
                (["rep_lab", "use", "--snapshot", str(path)],
                 "DISCLOSED_TOY_USE_NOT_FORMAL"),
            ):
                output = StringIO()
                with patch("sys.argv", args), contextlib.redirect_stdout(output):
                    main()
                self.assertIn(status, output.getvalue())
                self.assertTrue(path.is_file())

    def test_executable_template_instantiates_novel_renamed_roles(self):
        memory = disclosed_training_worlds(3)
        snap = learn_snapshot(memory)
        target = disclosed_world(100, "toy-eval")
        instantiated = instantiate_template(snap.templates[0].body, target.object_ids)
        self.assertGreater(len(instantiated), 0)
        self.assertTrue(all(canonical_body(m) == snap.templates[0].body
                            for m in instantiated))
        obs, _ = passive_public_episode(target)
        before = (True, False, True, False)
        action = Action("pulse", target.object_ids[0])
        fixed = predict(target.object_ids, obs, before, action, "B1", snap)
        learned = predict(target.object_ids, obs, before, action, "B3", snap)
        self.assertEqual(fixed.after, learned.after)
        self.assertEqual(learned.status, "TEMPLATE_PRIOR_PREDICTION")
        self.assertLess(learned.checked, fixed.checked)

    def test_constructor_strict_and_bounded(self):
        snap = learn_snapshot(disclosed_training_worlds(3))
        with self.assertRaises(ValueError):
            instantiate_template(snap.templates[0].body, self.ids, max_bindings=2)
        with self.assertRaises(ValueError):
            instantiate_template("[[0,0,-1,true],[0,2,-1,true]]", self.ids)
        with self.assertRaises(ValueError):
            instantiate_template(snap.templates[0].body, self.ids, max_bindings=True)

    def test_paired_disclosed_scoring_and_learning_curve(self):
        result = run_pilot()
        self.assertEqual(result["status"], "DISCLOSED_ENGINEERING_ONLY_NOT_FORMAL")
        self.assertEqual([r["unique_train_worlds"] for r in result["curve"]],
                         [0, 1, 2, 3, 4, 8, 16, 32])
        self.assertTrue(result["replay_idempotent"])
        self.assertEqual(result["final"]["total_per_arm"], 6 * 64)
        self.assertEqual(set(result["final"]["correct"]),
                         {"B0", "B1", "B2", "B3", "B3x", "B4", "B5"})
        print("G1D_TOY_RESULT=" + json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()

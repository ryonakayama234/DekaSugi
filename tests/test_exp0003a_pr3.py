"""EXP-0003A PR3: preregistered TRAIN/DREAM policy, no DEV/FINAL."""
from dataclasses import replace
import json
import unittest
from unittest.mock import patch

from packages.exp0003a import FAMILIES, generate_train, opaque_id, wake, _issue_wake_receipt, sleep
from packages.exp0003a.pr3 import (
    ArmSnapshot, DREAM_POOL_SIZE, PairedObservation, choose, generate_dream_pool,
    paired_trial, positive_train, run_train_dream, select_dream, _distance,
)
from packages.library import DEFAULT_PRIMITIVES, Registry
from packages.learning import registry_with_skill
from packages.protocol import Example


class DreamPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = generate_train()
        cls.pool = generate_dream_pool(cls.train)

    def test_dream_pool_exact_seed_and_public_id(self):
        self.assertEqual(len(self.pool), DREAM_POOL_SIZE)
        self.assertEqual(len({x.task.task_id for x in self.pool}), 512)
        self.assertEqual(len({x.source_record_id for x in self.pool}), 512)
        self.assertEqual(len({x for item in self.pool for x in item.seeds}), 1536)
        self.assertFalse(set(x.task.task_id for x in self.train) &
                         set(x.task.task_id for x in self.pool))
        for index, case in enumerate(self.pool):
            family_idx, task_idx = divmod(index, 64)
            self.assertEqual(case.family, FAMILIES[family_idx])
            self.assertEqual(case.source_record_id,
                             f"dream-f{family_idx:02d}-i{task_idx:03d}")
            self.assertEqual(case.seeds, tuple(
                410000000 + 100000 * family_idx + 10 * task_idx + j for j in range(3)
            ))
            self.assertEqual(case.task.task_id, opaque_id(case.task.examples))
            self.assertEqual(len(case.task.examples), 2)
            self.assertNotIn(case.family, case.task.task_id)
        self.assertEqual(self.pool, generate_dream_pool(self.train))

    def test_random_96_stratified_order_exactly_seeded(self):
        import random
        cases = select_dream(self.pool, "random")
        self.assertEqual(len(cases), 96)
        for family_idx in range(8):
            indices = list(range(64))
            random.Random(510000000 + family_idx).shuffle(indices)
            expected = [f"dream-f{family_idx:02d}-i{j:03d}" for j in indices[:12]]
            self.assertEqual([x.source_record_id for x in cases[
                family_idx * 12:(family_idx + 1) * 12
            ]], expected)
        self.assertEqual(
            [c.source_record_id for c in cases],
            [c.source_record_id for c in select_dream(tuple(reversed(self.pool)), "random")],
        )
        with self.assertRaisesRegex(ValueError, "Duplicate DREAM"):
            select_dream((*self.pool[:-1], self.pool[0]), "random")

    def test_positive_requirement_and_counterfactual_ranking(self):
        case = self.train[80]
        episode = wake(case.task, private_audit=case.private_audit)
        skill = sleep((episode,), trusted_receipts=(_issue_wake_receipt(episode),))
        # Single episode cannot prove a reused skill.
        self.assertEqual(skill, ())
        examples = self.train[80:100]
        episodes = tuple(wake(c.task, private_audit=c.private_audit) for c in examples)
        proposal = sleep(episodes, trusted_receipts=tuple(
            _issue_wake_receipt(e) for e in episodes))
        self.assertGreater(len(proposal), 0)
        trials = tuple(paired_trial(c, proposal[0].candidate) for c in self.train)
        positives = positive_train(trials)
        self.assertGreater(len(positives), 0)
        b3 = select_dream(self.pool, "counterfactual", positives=positives)
        self.assertEqual(len(b3), 96)
        self.assertEqual(
            [x.source_record_id for x in b3],
            [x.source_record_id for x in select_dream(
                tuple(reversed(self.pool)), "counterfactual",
                positives=tuple(reversed(positives)))],
        )
        for idx in range(8):
            ranked = sorted(self.pool[idx * 64:(idx + 1) * 64], key=lambda x: (
                min(_distance(
                    __import__("packages.kernel", fromlist=["features"]).features(x.task),
                    p.vector) for p in positives),
                x.source_record_id,
            ))
            self.assertEqual(
                [x.source_record_id for x in b3[idx * 12:(idx + 1) * 12]],
                [x.source_record_id for x in ranked[:12]],
            )
        with self.assertRaisesRegex(ValueError, "No audited positive"):
            select_dream(self.pool, "counterfactual", positives=())
        fake = replace(positives[0], on_calls=positives[0].off_calls)
        # The zero-positive fail-closed gate precedes other validation.
        with self.assertRaisesRegex(ValueError, "No audited positive"):
            select_dream(self.pool, "counterfactual", positives=(fake,))
        # With a real positive also present, malformed refs are rejected.
        with self.assertRaisesRegex(ValueError, "Invalid positive"):
            select_dream(self.pool, "counterfactual",
                         positives=(positives[1], fake))

    def test_paired_trial_public_search_is_audited_separately(self):
        cases = self.train[80:100]
        episodes = tuple(wake(c.task, private_audit=c.private_audit) for c in cases)
        skill = sleep(episodes, trusted_receipts=tuple(
            _issue_wake_receipt(e) for e in episodes))[0].candidate
        trial = paired_trial(cases[0], skill)
        self.assertEqual(trial.observation.task_id, cases[0].task.task_id)
        self.assertTrue(trial.observation.on_correct)
        self.assertGreater(trial.observation.off_calls,
                           trial.observation.on_calls)
        self.assertEqual(trial.on_evidence["search"]["max_candidates"], 100)
        self.assertEqual(trial.off_evidence["search"]["max_nodes"], 4)
        self.assertNotIn("private_audit", trial.observation.to_dict())
        self.assertNotIn("family", trial.observation.to_dict())
        altered_case = replace(cases[0], private_audit=Example(
            cases[0].private_audit.input, "intentionally-wrong"))
        altered = paired_trial(altered_case, skill)
        self.assertEqual(trial.off_evidence["search"], altered.off_evidence["search"])
        self.assertEqual(trial.on_evidence["search"], altered.on_evidence["search"])
        self.assertFalse(altered.observation.on_correct)
        self.assertTrue(altered.observation.on_audit_invalid)
        bad = replace(cases[0].task, task_id="dream-leak-label")
        with self.assertRaisesRegex(ValueError, "public hash"):
            paired_trial(replace(cases[0], task=bad), skill)
        # Registry remains strictly canonical.
        self.assertEqual(tuple(x.op_id for x in Registry(DEFAULT_PRIMITIVES).primitives),
                         ("trim", "lower", "upper"))

    def test_strict_policy_and_train_dream_bundle(self):
        report, private = run_train_dream()
        self.assertEqual(report["phase"], "TRAIN_DREAM_ENGINEERING")
        self.assertFalse(report["dev_or_final_evaluated"])
        self.assertEqual(report["train_task_count"], 160)
        self.assertEqual(report["dream_pool_count"], 512)
        self.assertEqual(report["dream_selected_per_arm"], 96)
        self.assertGreater(report["wake_positive_count"], 0)
        self.assertEqual(report["wake_status"]["success"], 120)
        self.assertEqual(report["wake_status"]["not_found"], 40)
        self.assertEqual(set(report["snapshot_hashes"]), {"B1", "B2", "B3"})
        self.assertEqual(len(private["train_rows"]), 160)
        self.assertEqual(len(private["dream_rows"]), 512)
        self.assertEqual(len(private["wake_receipts"]), 160)
        from packages.exp0003a import digest
        self.assertEqual(
            digest(private["train_rows"] + private["dream_rows"]),
            report["source_manifest_sha256"],
        )
        self.assertEqual(report["source_manifest_sha256"],
                         private["source_manifest_sha256"])
        self.assertEqual(
            digest([row["public_task"]["task_id"][2:] for row in private["dream_rows"]]),
            report["pool_public_input_sha256"],
        )
        self.assertEqual(len(private["train_paired_trials"]), 160)
        self.assertEqual(len(private["dream_paired_trials"]),
                         report["selected_distinct_total"])
        for arm, expected in (("B1", 160), ("B2", 256), ("B3", 256)):
            raw = report["snapshots"][arm]
            parsed = ArmSnapshot.from_dict(raw)
            self.assertEqual(len(parsed.observations), expected)
            self.assertEqual(parsed.skill_body_sha256,
                             report["top_skill"]["body_hash"])
            self.assertEqual(parsed.to_dict(), raw)
            self.assertEqual(len(parsed.ordered_selected_pool_ids),
                             0 if arm == "B1" else 96)
            self.assertEqual(len(parsed.wake_episode_ids), 160)
            self.assertEqual(len(parsed.dream_case_ids),
                             0 if arm == "B1" else 96)
            if arm != "B1":
                self.assertEqual(list(parsed.dream_case_ids),
                                 report["selection"][arm]["ordered_dream_case_ids"])
                self.assertEqual(list(parsed.ordered_selected_pool_ids),
                                 report["selection"][arm]["ordered_selected_pool_ids"])
                self.assertEqual(list(parsed.ordered_selected_task_ids),
                                 report["selection"][arm]["ordered_selected_task_ids"])
            for i in range(3):
                decision = choose(self.train[i].task, parsed)
                self.assertIn(decision.action, ("ON", "OFF"))
                self.assertEqual(len(decision.neighbors), 5)
        b1 = ArmSnapshot.from_dict(report["snapshots"]["B1"])
        swapped = list(reversed(b1.observations))
        # KNN must not depend on training row order.
        alternate = replace(b1, observations=tuple(swapped))
        self.assertEqual(choose(self.train[90].task, b1),
                         choose(self.train[90].task, alternate))
        raw = json.loads(json.dumps(report["snapshots"]["B3"]))
        raw["max_distance"] = .99
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            ArmSnapshot.from_dict(raw)
        fake_policy = replace(b1, k=4)
        with self.assertRaisesRegex(ValueError, "Altered KNN"):
            fake_policy.to_dict()
        with self.assertRaisesRegex(ValueError, "WAKE source"):
            replace(b1, wake_episode_ids=("wake:forged",)).to_dict()
        b3 = ArmSnapshot.from_dict(report["snapshots"]["B3"])
        with self.assertRaisesRegex(ValueError, "DREAM case provenance"):
            replace(b3, dream_case_ids=tuple(reversed(b3.dream_case_ids))).to_dict()
        for value in report["cost_ms"].values():
            self.assertGreaterEqual(value, 0)
        self.assertEqual(report["registry_promotion"], "not_authorized")
        self.assertIn("pr3_source_file_sha256", report["source"])

if __name__ == "__main__":
    unittest.main()

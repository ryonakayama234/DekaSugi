"""Independent EXP-0002B train-only generator and policy contract tests."""
import unittest
from dataclasses import replace
from unittest.mock import patch

from packages.evaluation import _task
from packages.kernel import (
    ALGORITHM_VERSION, FEATURE_VERSION, SKILL_HASH, ExperimentTask,
    PolicySnapshot, TrainingObservation, _seed, choose, dataset_manifest,
    features, generate_partition, train,
)
from packages.protocol import Example, parse_task
from packages.library import DEFAULT_PRIMITIVES, DEFAULT_REGISTRY


class GeneratorTests(unittest.TestCase):
    def test_full_partition_counts_and_rng_domains_without_scoring_final(self):
        meta = dataset_manifest()  # hashes only, no search or FINAL metrics
        self.assertEqual(meta["partition_counts"], {"train": 144, "dev": 48, "final": 112})
        self.assertEqual(meta["unique_rng_seeds"], 912)
        self.assertEqual(len(meta["dataset_sha256"]), 64)
        self.assertEqual(meta, dataset_manifest())
        t = generate_partition("train")
        d = generate_partition("dev")
        self.assertEqual(len(t), 144)
        self.assertEqual(len(d), 48)
        self.assertTrue(all(len(x.task.examples) == 2 for x in t + d))
        self.assertTrue(all(x.task.limits.max_ast_nodes == 4
                            and x.task.limits.max_candidates == 100 for x in t+d))
        seeds = {s for item in t+d for s in item.seeds}
        final_seeds = {_seed("final", k, i, j)
                       for k in range(7) for i in range(16) for j in range(3)}
        self.assertTrue(seeds.isdisjoint(final_seeds))
        self.assertEqual(len(final_seeds), 336)
        self.assertEqual(t[0].task.task_id, "train-identity-000")
        self.assertEqual(d[0].task.task_id, "dev-identity-000")

    def test_generator_examples_and_independent_third_audit(self):
        train_tasks = generate_partition("train")
        for item in train_tasks:
            self.assertNotIn(item.audit, item.task.examples)
            self.assertEqual(len(item.seeds), 3)
            for sample in item.task.examples + (item.audit,):
                inp, out = sample.input, sample.output
                if item.family == "identity":
                    self.assertEqual(out, inp)
                elif item.family == "trim":
                    self.assertEqual(out, inp.strip())
                elif item.family == "lower":
                    self.assertEqual(out, inp.lower())
                elif item.family == "upper":
                    self.assertEqual(out, inp.upper())
                elif item.family == "normalize":
                    self.assertEqual(out, inp.strip().lower())
                elif item.family == "reverse":
                    self.assertEqual(out, inp[::-1])
                    self.assertNotEqual(out, inp)
        self.assertNotEqual(train_tasks[0].audit, train_tasks[0].task.examples[0])
        # Each example uses its own RNG instance and declared whitespace cycle.
        norm = next(x for x in train_tasks if x.family == "normalize")
        self.assertTrue(norm.task.examples[0].input.startswith(" "))
        self.assertEqual(norm.task.examples[0].output,
                         norm.task.examples[0].input.strip().lower())

    def test_features_read_only_public_examples_and_not_family_id(self):
        group = generate_partition("train")
        task = group[0].task
        rename = replace(task, task_id="final-replace_first-999")
        self.assertEqual(features(task), features(rename))
        self.assertEqual(len(features(task)), 8)
        identity = _task("any", (("ABC", "ABC"), ("DEF", "DEF")))
        self.assertEqual(features(identity),
                         (3/16, 3/16, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0))
        self.assertEqual(features(identity), features(replace(identity, task_id="other")))
        with self.assertRaises(ValueError):
            features(_task("one", (("X", "X"),)))
        # Not passing ExperimentTask avoids exposing family / audit / seeds.
        self.assertFalse(hasattr(task, "audit"))
        self.assertFalse(hasattr(task, "family"))
        self.assertFalse(hasattr(task, "seeds"))


class PolicyTests(unittest.TestCase):
    @staticmethod
    def _snapshot(task, *, prefer=True, far=False, gain=4, veto=False):
        v = (1.0,)*8 if far else features(task)
        rows = tuple(TrainingObservation(
            task_id=f"train-fixture-{i}", vector=v, prefer_on=prefer,
            off_calls=10 + gain, on_calls=10,
            off_candidates=6, on_candidates=5,
            off_correct=True, on_correct=not veto,
            on_audit_invalid=veto)
            for i in range(5))
        return PolicySnapshot(rows, "d"*64, "e"*64, SKILL_HASH)

    def test_nearest_neighbor_cost_threshold_and_off_fallback(self):
        task = _task("probe", ((" A ", "a"), (" B ", "b")))
        snapshot = self._snapshot(task)
        pred = choose(task, snapshot)
        self.assertEqual(pred.action, "ON")
        self.assertEqual(pred.reason, "cost_supported")
        self.assertEqual(pred.on_support, 5)
        self.assertEqual(pred.close_support, 5)
        self.assertEqual(pred.mean_call_saving, 4)
        self.assertEqual(choose(task, self._snapshot(task, prefer=False)).action, "OFF")
        self.assertEqual(choose(task, self._snapshot(task, gain=1)).reason,
                         "insufficient_call_saving")
        self.assertEqual(choose(task, self._snapshot(task, veto=True)).reason,
                         "audit_safety_veto")
        self.assertEqual(choose(task, self._snapshot(task, far=True)).reason,
                         "insufficient_support")
        # ID encodes family in the frozen dataset but inference reads ONLY examples.
        self.assertEqual(choose(replace(task, task_id="final-replace_first-999"),
                                snapshot).action, pred.action)
        tampered = replace(snapshot, k=4)
        with self.assertRaises(ValueError):
            choose(task, tampered)

    def test_training_snapshot_is_hash_verifiable(self):
        task = _task("probe", ((" A ", "a"), (" B ", "b")))
        snapshot = self._snapshot(task)
        obj = snapshot.to_dict()
        self.assertEqual(len(obj["policy_sha256"]), 64)
        self.assertEqual(obj["feature_version"], FEATURE_VERSION)
        self.assertEqual(obj["algorithm_version"], ALGORITHM_VERSION)
        self.assertEqual(PolicySnapshot.from_dict(obj).to_dict(), obj)
        obj["observations"][0]["on_calls"] += 20
        with self.assertRaisesRegex(ValueError, "content hash mismatch"):
            PolicySnapshot.from_dict(obj)

    def test_snapshot_rejects_forged_training_ids_and_derived_hash(self):
        task = _task("probe", ((" A ", "a"), (" B ", "b")))
        source = self._snapshot(task).to_dict()
        bad_ids = {**source, "training_ids": ["final-forged-000"]}
        with self.assertRaisesRegex(ValueError, "content hash mismatch"):
            PolicySnapshot.from_dict(bad_ids)
        bad_digest = {**source, "training_observations_sha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "content hash mismatch"):
            PolicySnapshot.from_dict(bad_digest)

    def test_frozen_training_only_no_final_or_dev_outcomes(self):
        evidence = train()
        self.assertEqual(evidence["training_task_count"], 144)
        self.assertEqual(len(evidence["training_trial_evidence"]), 144)
        self.assertEqual(len(evidence["training_trial_evidence_sha256"]), 64)
        for record in evidence["training_trial_evidence"]:
            self.assertEqual(record["partition"], "train")
            self.assertEqual(record["off"]["search"]["task_id"], record["task_id"])
            self.assertEqual(record["on"]["search"]["task_id"], record["task_id"])
            self.assertEqual(len(record["off"]["search"]["trace_sha256"]), 64)
            self.assertIn("elapsed_ms", record["off"]["search"])
            self.assertIn("status", record["on"]["search"])
            self.assertIn("audit_correct", record["on"])
        self.assertEqual(evidence["phase"], "TRAIN_ONLY")
        self.assertEqual(evidence["state"], "policy_trained_no_dev_or_final_outcome")
        self.assertGreater(evidence["training_primitive_invocations"], 0)
        self.assertEqual(evidence["manifest"]["partition_counts"]["final"], 112)
        snap = PolicySnapshot.from_dict(evidence["snapshot"])
        self.assertEqual(snap.skill_body_sha256, SKILL_HASH)
        self.assertEqual(len(snap.observations), 144)
        self.assertTrue(all(x.task_id.startswith("train-") for x in snap.observations))
        self.assertTrue(all(len(x.vector) == 8 for x in snap.observations))
        self.assertFalse(any(k.startswith("final_") for k in evidence))
        self.assertNotIn("final_outcomes", str(evidence).lower())
        # Training observations do not contain generator-side family or audit input strings.
        self.assertNotIn("audit", snap.to_dict()["observations"][0])
        self.assertNotIn("family", snap.to_dict()["observations"][0])

    def test_poisoned_default_registry_cannot_execute_in_skill_discovery(self):
        def poison(_value: str) -> str:
            raise AssertionError("Poisoned mutable DEFAULT_REGISTRY callback executed")
        forged = replace(DEFAULT_PRIMITIVES[0], implementation=poison)
        poisoned = dict(DEFAULT_REGISTRY.by_name)
        poisoned["trim"] = forged
        with (patch.object(DEFAULT_REGISTRY, "by_name", poisoned),
              patch.object(DEFAULT_REGISTRY, "signatures", {}),
              patch.object(DEFAULT_REGISTRY, "primitives",
                           (forged, *DEFAULT_PRIMITIVES[1:]))):
            evidence = train()
        self.assertEqual(evidence["training_task_count"], 144)
        self.assertEqual(evidence["snapshot"]["skill_body_sha256"], SKILL_HASH)


if __name__ == "__main__":
    unittest.main()

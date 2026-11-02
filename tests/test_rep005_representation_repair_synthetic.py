"""Invented public-trace-only REP005/G2 engineering tests; no scorer or private world imports."""
import subprocess
import sys
import unittest

from packages.representation_repair import (
    PublicStep, Feature, learn, load_snapshot, visible_state_predictions,
)

PULSE0 = ("pulse", 0, -1)
PULSE2 = ("pulse", 2, -1)
SET00 = ("set", 0, 0)
SET10 = ("set", 1, 0)
SET20 = ("set", 2, 0)


def invented_public_episode(actions, delayed=True):
    """Disclosed deterministic fake fixture; source logic remains TEST-ONLY."""
    before, history = 0, ()
    out = []
    for action in actions:
        after = before
        if action[0] == "set":
            after = (after & ~(1 << action[1])) | (action[2] << action[1])
        if delayed and history and history[-1] == PULSE0:
            after ^= 1 << 1
        out.append(PublicStep(before, history, action, after))
        before, history = after, (history + (action,))[-2:]
    return tuple(out)


def public_training_episodes():
    return (
        invented_public_episode((PULSE0, SET10)),
        invented_public_episode((SET00, SET10)),
        invented_public_episode((SET20, SET10)),
        invented_public_episode((PULSE2, SET10)),
    )


class PublicRepresentationRepairSyntheticTests(unittest.TestCase):
    def test_counterexample_and_unique_executable_typed_feature(self):
        corpus = public_training_episodes()
        baseline = visible_state_predictions(corpus)
        self.assertIsNone(baseline[(0, SET10)])  # same public state/action, different future
        result = learn(corpus)
        self.assertEqual(result["status"], "LEARNED_CANDIDATE")
        self.assertEqual(result["typed_body"], {"lag": 1, "action": PULSE0})
        self.assertEqual(result["candidate_count"], 1)
        self.assertGreaterEqual(result["witness_count"], 1)
        self.assertEqual(result["paid_actions"], 8)
        fresh = load_snapshot(result["snapshot"])
        self.assertEqual(fresh.predict(0, (PULSE0,), SET10), 2)
        self.assertEqual(fresh.predict(0, (SET00,), SET10), 0)
        self.assertEqual(fresh.predict(0, (SET20,), SET10), 0)
        self.assertIsNone(fresh.predict(15, (), SET10))  # abstain off-support
        self.assertEqual(fresh.evidence_sha256, result["evidence_sha256"])

    def test_fresh_process_loads_only_public_snapshot_and_dispatches_body(self):
        result = learn(public_training_episodes())
        script = ("import sys; from packages.representation_repair import load_snapshot;"
                  "s=load_snapshot(sys.stdin.read());"
                  "print(s.predict(0, (('pulse',0,-1),), ('set',1,0)))")
        completed = subprocess.run(
            [sys.executable, "-c", script],
            input=result["snapshot"], text=True, capture_output=True, timeout=10,
            check=True,
        )
        self.assertEqual(completed.stdout.strip(), "2")

    def test_identical_public_experience_cannot_invent_a_fix(self):
        corpus = (invented_public_episode((SET00, SET10), delayed=False),
                  invented_public_episode((SET20, SET10), delayed=False))
        no_repair = learn(corpus)
        self.assertEqual(no_repair["status"], "NO_REPAIR_NEEDED")
        self.assertEqual(no_repair["witness_count"], 0)
        self.assertNotIn("snapshot", no_repair)

    def test_unrepairable_conflict_is_not_reported_as_invention(self):
        # Identical public action & history returning two outcomes violates
        # a stationary deterministic premise; no history predicate can fix it.
        good = (PublicStep(0, (), SET00, 0),)
        impossible = (PublicStep(0, (), SET00, 1),)
        result = learn((good, impossible))
        self.assertEqual(result["status"], "NOT_CERTIFIED")
        self.assertEqual(result["reason"], "NO_SINGLE_HISTORY_EQUALITY_FEATURE_FITS")
        self.assertNotIn("snapshot", result)

    def test_false_history_or_forged_types_fail_closed(self):
        valid = invented_public_episode((PULSE0, SET10))
        forged = PublicStep(0, (), SET10, 0)
        with self.assertRaises(ValueError):
            learn(((valid[0], forged),))
        with self.assertRaises(ValueError):
            PublicStep(True, (), SET00, 0)
        with self.assertRaises(ValueError):
            PublicStep(0, (), ("set", True, 0), 0)
        with self.assertRaises(ValueError):
            Feature(0, PULSE0)
        with self.assertRaises(ValueError):
            learn((valid,) * 65)
        with self.assertRaises(ValueError):
            learn(tuple())

    def test_canonical_digest_and_tamper_rejection(self):
        result = learn(public_training_episodes())
        self.assertEqual(result["snapshot"], learn(public_training_episodes())["snapshot"])
        raw = result["snapshot"]
        with self.assertRaises(ValueError):
            load_snapshot(raw.replace('"witness_count":1', '"witness_count":2'))
        with self.assertRaises(ValueError):
            load_snapshot(raw + " ")
        with self.assertRaises(ValueError):
            load_snapshot("{}")
        self.assertGreater(load_snapshot(raw).paid_actions, 0)

    def test_installed_same_capacity_static_feature_is_a_valid_competitor(self):
        # This fixture cannot prove superiority over a STATIC-Hplus agent
        # with the SAME lag-1 pulse0 predicate preinstalled.
        body = load_snapshot(learn(public_training_episodes())["snapshot"])
        for history, expected in (((PULSE0,), 2), ((SET00,), 0),
                                  ((SET20,), 0), ((PULSE2,), 0)):
            static_hplus = 2 if history[-1] == PULSE0 else 0
            self.assertEqual(static_hplus, expected)
            self.assertEqual(body.predict(0, history, SET10), static_hplus)


if __name__ == "__main__":
    unittest.main()

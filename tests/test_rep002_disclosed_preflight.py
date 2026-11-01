"""New EXP-REP-002 invented-only engineering calibration; no old or sealed source."""
import json
import tempfile
import unittest
from pathlib import Path
from packages.rep002 import (ROLES, ARMS, STRATA, Session, audit, behavior_signature,
    digest, evaluate, load, reveal_outgoing, save, step, structure_signature, train,
    use, validate, world)


class Rep002PreflightTests(unittest.TestCase):
    def test_train_diverse_structures_not_renamings(self):
        self.assertEqual(train(0)["distinct_structures"], 0)
        s = train(3)
        self.assertGreaterEqual(s["distinct_structures"], 3)
        self.assertEqual(len(s["motif"]), 2)
        self.assertEqual(s["metered_train_actions"], 15)
        self.assertEqual(train(3), s)

    def test_semantic_signatures_and_pulse(self):
        a = ((0, 1), (0, 2))
        b = ((2, 0), (2, 1))
        self.assertEqual(structure_signature(a), structure_signature(b))
        self.assertEqual(behavior_signature(a), behavior_signature(b))
        self.assertEqual(step((False,) * 5, 0, a), (True, True, True, False, False))

    def test_strata_structure_not_equal_train(self):
        known = {structure_signature(world(i, "TRAIN").hidden_edges) for i in range(3)}
        for i in range(12):
            w = world(i + 300, "COMPOSITION")
            self.assertNotIn(structure_signature(w.hidden_edges), known)
            self.assertEqual(len(w.hidden_edges), 4)

    def test_canonical_snapshot_and_in_memory_tamper(self):
        s = train(64)
        validate(s)
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "concept.json"
            save(s, p)
            self.assertEqual(load(p), s)
            fake = dict(s)
            fake["motif"] = ((True, "x"),)
            with self.assertRaises(ValueError):
                validate(fake)
            raw = json.loads(p.read_text())
            raw["train_count"] = 999
            p.write_text(json.dumps(raw))
            with self.assertRaises(ValueError):
                load(p)

    def test_budget_and_no_audit_feedback(self):
        s = train(3)
        w = world(301, "COMPOSITION")
        a = use(s, w, "LQ", 2)
        b = use(s, w, "LA", 2)
        self.assertLessEqual(a["actions"], 2)
        self.assertLessEqual(b["actions"], 2)
        self.assertEqual(a["status"], "COMMITTED")
        self.assertLessEqual(len(a["edges"]), 4)
        self.assertLessEqual(len(b["edges"]), 4)
        self.assertGreaterEqual(audit(w, a["edges"], a["status"]), 0)
        self.assertNotIn("correct", a)
        self.assertNotIn("hidden_edges", a)

    def test_public_trace_validation(self):
        w = world(1, "TRAIN")
        session = Session(w)
        row = session.pulse(0)
        self.assertIsInstance(reveal_outgoing(row), tuple)
        invalid = dict(row)
        invalid["after"] = (1, False, False, False, False)
        with self.assertRaises(ValueError):
            reveal_outgoing(invalid)

    def test_fixed_fa_predictor_is_snapshot_independent(self):
        w = world(301, "COMPOSITION")
        # An untrained FA has the same fixed role-rule and same inquiry
        # selection as FA given a learned motif. This must hold at budget=0.
        for budget in (0, 2, 4, 8):
            self.assertEqual(use(train(0), w, "FA", budget),
                             use(train(3), w, "FA", budget))

    def test_public_pulse_strict_source_and_cost(self):
        w = world(3, "TRAIN")
        row = Session(w).pulse(0)
        for forged in (dict(row, source=-1), dict(row, source=5),
                       dict(row, cost=True), dict(row, cost=1.0)):
            with self.assertRaises(ValueError):
                reveal_outgoing(forged)

    def test_disclosed_end_to_end_scoring(self):
        result = evaluate()
        self.assertEqual(result["status"], "DISCLOSED_PREFLIGHT_ONLY_NOT_FORMAL")
        self.assertEqual(result["worlds"], 48)
        self.assertEqual(result["audits_per_world"], 32)
        self.assertEqual(len(result["composition_world_differences"]), 12)
        self.assertEqual(set(result["strata"]), set(STRATA))
        self.assertEqual(set(result["strata"]["COMPOSITION"]), set(ARMS))
        self.assertGreater(result["total_actions"], 0)
        self.assertEqual(len(result["records"]), 48 * 4 * 4)
        self.assertEqual(result["records_digest"], digest(result["records"]))
        summary = {k: v for k, v in result.items() if k != "records"}
        print("REP002_DISCLOSED_RESULT=" + json.dumps(summary, sort_keys=True, separators=(",", ":")))
        for start in range(0, len(result["records"]), 32):
            print("REP002_RECORD_PART=" + str(start // 32) + ":" +
                  json.dumps(result["records"][start:start+32], sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()

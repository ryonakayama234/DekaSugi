"""Source-blind Wake/Sleep/USE tests; disclosed engineering only."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.rep005_v4_g2_disclosed_pilot import (
    LEARNER, disclosed_training, evaluator_probes, learner_request,
    run_disclosed_g2, run_use, training_episode,
)
from packages.rep005_g0b_v4 import Edge, law


class TestDisclosedG2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot, cls.paid, cls.training = disclosed_training()

    def test_snapshot_from_actual_paid_public_experiences(self):
        self.assertEqual(self.paid, 48)
        self.assertEqual(len(self.training), 6)
        self.assertEqual(self.snapshot["payload"]["body"]["lag"], 1)
        self.assertEqual(self.snapshot["payload"]["training_world_sessions"], 3)
        self.assertEqual(self.snapshot["payload"]["training_paid_steps"], 48)
        self.assertEqual(self.snapshot["payload"]["body"]["effect"], "xor_one_target_bit")
        self.assertFalse(any(k in json.dumps(self.snapshot).lower()
                             for k in ('source_root', 'private_law', 'source_motif')))

    def test_fresh_process_snapshot_dispatch(self):
        panel, _ = evaluator_probes(law(Edge(2, 3, 1)))
        obj = learner_request({
            "mode": "predict", "steps": [], "snapshot": self.snapshot,
            "body_off": False, "probes": panel,
        })
        self.assertEqual(obj["status"], "OK")
        self.assertTrue(obj["actual_body_dispatch_count"] > 0)
        self.assertEqual(len(obj["predictions"]), 16)

    def test_tampering_rejected_by_untrusted_fresh_process(self):
        broken = json.loads(json.dumps(self.snapshot))
        broken["payload"]["body"]["lag"] = 2
        with self.assertRaises(RuntimeError):
            learner_request({
                "mode": "plan", "steps": [],
                "snapshot": broken, "body_off": False,
            })

    def test_private_fields_and_paid_forgery_rejected(self):
        with self.assertRaises(RuntimeError):
            learner_request({
                "mode": "train",
                "episodes": [{"world_session_id": "s0", "steps": [],
                              "true_Law": "forbidden"}],
            })
        with self.assertRaises(RuntimeError):
            learner_request({
                "mode": "plan", "snapshot": self.snapshot, "body_off": False,
                "steps": [{"before": 0, "history": [],
                           "action": ["pulse", 0, -1], "after": 0,
                           "paid_cost": 0}],
            })
        with self.assertRaises(RuntimeError):
            learner_request({
                "mode": "predict", "snapshot": self.snapshot, "body_off": False,
                "steps": [], "probes": [{"before": 0, "history": [],
                                        "action": ["pulse", 0, -1],
                                        "source_root": "leak"}],
            })

    def test_learner_source_file_forbidden_private_import(self):
        body = LEARNER.read_text(encoding="utf-8")
        imports = re.findall(r"^\s*(?:from|import)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)",
                             body, flags=re.MULTILINE)
        self.assertFalse(any(s.startswith("packages") or s.startswith("scripts")
                             for s in imports))
        self.assertTrue(Path(LEARNER).is_file())

    def test_real_fresh_world_use_eight_paid_actions_and_common_panel(self):
        model = law(Edge(2, 3, 1))
        a, panel_a, truth_a = run_use(model, self.snapshot, "LEARNED")
        b, panel_b, truth_b = run_use(model, None, "STATIC")
        self.assertEqual(panel_a, panel_b)
        self.assertEqual(truth_a, truth_b)
        for x in (a, b):
            self.assertEqual(x["paid_use_steps"], 8)
            self.assertEqual(len(x["interactions"]), 8)
            self.assertEqual(x["correct"] + x["wrong"] + x["abstained"], 16)
            self.assertTrue(all(q["charged_cost"] == 1 for q in x["interactions"]))
            self.assertTrue(all(q["action_selected_before_truth"] in [
                ["pulse", i, -1] for i in range(5)
            ] + [["set", i, bit] for i in range(5) for bit in (0, 1)]
                for q in x["interactions"]))

    def test_full_disclosed_pilot_including_body_off_comparator(self):
        out = run_disclosed_g2()
        self.assertEqual(out["actual_training_paid_steps"], 48)
        self.assertEqual(out["new_use_world_instances"], 3)
        self.assertEqual(out["panel_probes_per_instance"], 16)
        self.assertFalse(out["source_family_ancestry_independent"])
        self.assertEqual(out["sealed_G3_score"], "NOT_RUN")
        self.assertEqual(out["science_eligibility"], "STOP_SOURCE_ANCESTRY_AND_POWER_NOT_CERTIFIED")
        self.assertEqual(set(out["arm_summary"]), {"STATIC", "LEARNED", "BODY_OFF"})
        self.assertEqual(out["total_actual_paid_train_and_use"], 120)
        for v in out["arm_summary"].values():
            self.assertEqual(v["paid_use_steps_total"], 24)
            self.assertEqual(v["correct_total"] + v["wrong_total"] +
                             v["abstained_total"], 48)


if __name__ == "__main__":
    unittest.main()

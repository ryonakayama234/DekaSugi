"""Archive diagnostic verification: synthetic data only, no holdout access."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "analyze_policy_diag_archives.py"
spec = importlib.util.spec_from_file_location("policy_diag_archives", MODULE_PATH)
analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer)


class PolicyDiagArchiveTests(unittest.TestCase):
    def test_sha_fail_closed(self):
        payload = b"public synthetic"
        good = hashlib.sha256(payload).hexdigest()
        analyzer.require_digest(payload, good, "fixture")
        with self.assertRaises(ValueError):
            analyzer.require_digest(payload + b"!", good, "fixture")

    def fixture(self):
        def make_arm(arm, n):
            return {"observations": [{
                "task_id": "train-"+str(i),
                "vector": [0.0] * 8,
                "prefer_on": False,
                "off_calls": 0,
                "on_calls": 0,
                "off_correct": True,
                "on_audit_invalid": False,
            } for i in range(n)]}
        dreams = {"snapshots": {
            "B1": make_arm("B1", 160),
            "B2": make_arm("B2", 256),
            "B3": make_arm("B3", 256),
        }}
        def arm_record(name):
            return {"policy_snapshot_sha256": analyzer.SNAPSHOT_SHA[name],
                "neighbors": ["train-"+str(i) for i in range(5)],
                "decision":"OFF", "decision_reason":"insufficient_on_votes",
                "primitive_invocations":2}
        records = [{
            "task_id": "synthetic-query-"+str(i),
            "arms":{"B0":{"primitive_invocations":2},
                    "B1":{"primitive_invocations":2},
                    "B2":arm_record("B2"),
                    "B3":arm_record("B3")}
        } for i in range(64)]
        dev={"trial_rows":records,
             "summary":{"arm_totals":{a:{"primitive_invocations":128} for a in ("B0","B1","B2","B3")}}}
        freeze={"policy":{
            "b2_ordered_selected_pool_ids":["synthetic-dream-"+str(i) for i in range(96)],
            "b3_ordered_selected_pool_ids":["synthetic-dream-"+str(i) for i in range(72,168)],
        }}
        return dev,dreams,freeze

    def test_synthetic_summary_no_task_identifiers(self):
        data=analyzer.summarize(*self.fixture())
        self.assertEqual(data["archived_query_5NN"]["tasks"],64)
        self.assertEqual(data["archived_query_5NN"]["different_action"],0)
        self.assertEqual(data["dream_selection"]["overlap"],24)
        self.assertEqual(data["archived_query_5NN"]["overlap_histogram"],{"5":64})
        self.assertEqual(data["unobserved"]["query_public_TaskSpec"],True)
        self.assertNotIn("synthetic-query-",str(data))

    def test_duplicate_public_task_rejected(self):
        dev,dream,freeze=self.fixture()
        dev["trial_rows"][0]["task_id"]=dev["trial_rows"][1]["task_id"]
        with self.assertRaises(ValueError):
            analyzer.summarize(dev,dream,freeze)

    def test_forged_neighbor_rejected(self):
        dev,dream,freeze=self.fixture()
        dev["trial_rows"][0]["arms"]["B2"]["neighbors"][0]="unknown"
        with self.assertRaises(ValueError):
            analyzer.summarize(dev,dream,freeze)

    def test_inconsistent_archived_gate_rejected(self):
        dev,dream,freeze=self.fixture()
        dev["trial_rows"][0]["arms"]["B2"]["decision_reason"]="cost_supported"
        with self.assertRaises(ValueError):
            analyzer.summarize(dev,dream,freeze)

if __name__=="__main__":
    unittest.main()

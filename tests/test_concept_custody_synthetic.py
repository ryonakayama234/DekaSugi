"""Fixed public invented process IPC. No real source, Oracle or scored test."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from packages.concept_world import split_inputs

ROOT=Path(__file__).resolve().parents[1]
QUERY_IDS=split_inputs(2501).query_ids
AUDIT_IDS=split_inputs(2501).audit_ids

def wire(*frames):
    payload="".join(json.dumps(x,sort_keys=True)+"\n" for x in frames)
    proc=subprocess.run([sys.executable,"-m","packages.concept_custody.toy_worker"],
        input=payload,text=True,capture_output=True,timeout=10,cwd=ROOT,check=True)
    return [json.loads(row) for row in proc.stdout.splitlines()]

def raw_wire(payload: str):
    # Construct raw ambiguous JSON frames (not representable by Python dict).
    proc=subprocess.run([sys.executable,"-m","packages.concept_custody.toy_worker"],
        input=payload,text=True,capture_output=True,timeout=10,cwd=ROOT,check=True)
    return [json.loads(row) for row in proc.stdout.splitlines()]

class ToyQueryWireTests(unittest.TestCase):
    def test_only_selected_two_answers(self):
        answer=wire({"op":"open"},{"op":"query","input_id":QUERY_IDS[0]},
                    {"op":"query","input_id":QUERY_IDS[1]},{"op":"close"})
        self.assertEqual([x["op"] for x in answer],["opened","answer","answer","closed"])
        self.assertEqual(len(answer[0]["public"]),2)
        self.assertEqual(answer[0]["query_limit"],2)
        self.assertEqual(answer[-1]["questions_answered"],2)
        for x in answer:
            self.assertNotIn("target",x)
            self.assertNotIn("audit",x)
            self.assertNotIn("seed",x)
            self.assertNotIn("score",x)
    def test_audit_ids_and_query_replay_rejected(self):
        a=wire({"op":"open"},{"op":"query","input_id":AUDIT_IDS[0]},
               {"op":"query","input_id":QUERY_IDS[0]},
               {"op":"query","input_id":QUERY_IDS[0]},
               {"op":"query","input_id":QUERY_IDS[1]},
               {"op":"query","input_id":QUERY_IDS[2]},{"op":"close"})
        self.assertEqual(a[1],{"error":"REJECTED"})
        self.assertEqual(a[3],{"error":"REJECTED"})
        self.assertEqual(a[5],{"error":"REJECTED"})
        self.assertEqual(a[6]["questions_answered"],2)
    def test_state_machine_denies_unauthorized_phase(self):
        a=wire({"op":"query","input_id":QUERY_IDS[0]},{"op":"open"},
               {"op":"open"},{"op":"score"},{"op":"close"},
               {"op":"query","input_id":QUERY_IDS[0]})
        self.assertEqual(a[0],{"error":"REJECTED"})
        self.assertEqual(a[2],{"error":"REJECTED"})
        self.assertEqual(a[3],{"error":"REJECTED"})
        self.assertEqual(a[5],{"error":"REJECTED"})
    def test_exact_schema_and_boolean_id_denial(self):
        a=wire({"op":"open","secret":"please"},{"op":"open"},
               {"op":"query","input_id":True},
               {"op":"query","input_id":QUERY_IDS[0],"target":"leak"},
               {"op":"query","input_id":QUERY_IDS[0]},{"op":"close"})
        self.assertEqual([x.get("error") for x in a[:4]],
                         ["REJECTED",None,"REJECTED","REJECTED"])
        self.assertEqual(a[4]["op"],"answer")
    def test_duplicate_raw_json_keys_denied_before_authorization(self):
        # Audit ID in first occurrence cannot be silently overwritten by a query ID.
        q=QUERY_IDS[0]
        audit=AUDIT_IDS[0]
        frames=(
            '{"op":"score","op":"open"}\n'
            '{"op":"open"}\n'
            '{"op":"query","input_id":'+str(audit)+',"input_id":'+str(q)+'}\n'
            '{"op":"query","input_id":'+str(q)+'}\n'
            '{"op":"close"}\n'
        )
        replies=raw_wire(frames)
        self.assertEqual(replies[0],{"error":"REJECTED"})
        self.assertEqual(replies[1]["op"],"opened")
        self.assertEqual(replies[2],{"error":"REJECTED"})
        self.assertEqual(replies[3]["op"],"answer")
        self.assertEqual(replies[3]["input_id"],q)
        self.assertEqual(replies[4]["questions_answered"],1)

    def test_oversize_frame_fails_closed(self):
        self.assertEqual(wire({"op":"open","padding":"x"*2000}),
                         [{"error":"REJECTED"}])

if __name__=="__main__":
    unittest.main()

"""Invented-only same-process capability/HMAC toy. NEVER independent Oracle."""
from dataclasses import replace
import json
import secrets
import unittest
from packages.concept_world import split_inputs
from packages.concept_custody.toy_capability_gate import (
    PublicToyCapabilityGate, WIRE)

QUERY_IDS=split_inputs(2501).query_ids
AUDIT_IDS=split_inputs(2501).audit_ids

def frame(gate: PublicToyCapabilityGate, query_id: int | None,
          *, op: str = "query", sequence: int = 0,
          nonce: str | None = None, **changes: object) -> bytes:
    req={"wire":WIRE,"op":op,"phase":"TRAIN","arm":gate.arm,
         "session":gate.session,"capability":gate.public_invitation()["capability"],
         "sequence":sequence,"nonce":nonce or secrets.token_hex(16)}
    if op=="query":
        req["input_id"]=query_id
    req.update(changes)
    return json.dumps(req,separators=(",",":"),sort_keys=True).encode()+b"\n"

class PublicToyCapabilityTests(unittest.TestCase):
    def test_signed_answer_chain_close_and_no_private_truth(self):
        gate=PublicToyCapabilityGate()
        initial=gate.previous_digest
        a=gate.handle(frame(gate,QUERY_IDS[0]))
        self.assertEqual(a["op"],"answer")
        self.assertEqual(a["previous_digest"],initial)
        self.assertTrue(gate.verify_toy_receipt(a,expected_previous=initial))
        b=gate.handle(frame(gate,QUERY_IDS[1],sequence=1))
        self.assertTrue(gate.verify_toy_receipt(b,expected_previous=a["receipt_digest"]))
        final=gate.handle(frame(gate,None,op="close",sequence=2))
        self.assertEqual(final["op"],"closed")
        self.assertEqual(final["questions_answered"],2)
        self.assertTrue(gate.verify_toy_receipt(final,expected_previous=b["receipt_digest"]))
        self.assertEqual(gate.handle(frame(gate,QUERY_IDS[2],sequence=3)),{"error":"REJECTED"})
        for record in (a,b,final):
            self.assertNotIn("target",record)
            self.assertNotIn("class",record)
            self.assertNotIn("audit",record)
            self.assertNotIn("capability",record)
            self.assertNotIn("score",record)
        self.assertEqual(gate.previous_digest,final["receipt_digest"])

    def test_cross_arm_phase_session_and_capability_denied(self):
        gate=PublicToyCapabilityGate()
        bad=[
            {"arm":"random"},{"phase":"DEV"},{"phase":"FINAL"},
            {"session":"0"*32},{"capability":"0"*64},
            {"input_id":AUDIT_IDS[0]},{"input_id":True},
            {"input_id":-1},{"sequence":1},
        ]
        for patch in bad:
            self.assertEqual(gate.handle(frame(gate,QUERY_IDS[0],**patch)),
                             {"error":"REJECTED"},patch)
            self.assertEqual(gate.previous_digest,"0"*64)
        a=gate.handle(frame(gate,QUERY_IDS[0]))
        self.assertEqual(a["op"],"answer")

    def test_replay_out_of_order_and_nonce_reuse_denied(self):
        gate=PublicToyCapabilityGate()
        nonce="f"*32
        q0=frame(gate,QUERY_IDS[0],nonce=nonce)
        self.assertEqual(gate.handle(q0)["op"],"answer")
        state=gate.previous_digest
        for payload in (q0,frame(gate,QUERY_IDS[1],nonce=nonce,sequence=1),
                        frame(gate,QUERY_IDS[0],sequence=1),
                        frame(gate,QUERY_IDS[1],sequence=2)):
            self.assertEqual(gate.handle(payload),{"error":"REJECTED"})
            self.assertEqual(gate.previous_digest,state)
        self.assertEqual(gate.handle(frame(gate,QUERY_IDS[1],sequence=1))["op"],"answer")

    def test_query_cap_and_close_phase(self):
        gate=PublicToyCapabilityGate()
        self.assertEqual(gate.handle(frame(gate,None,op="close"))["op"],"closed")
        self.assertEqual(gate.handle(frame(gate,QUERY_IDS[0],sequence=1)),{"error":"REJECTED"})
        second=PublicToyCapabilityGate()
        for k in (0,1):
            self.assertEqual(second.handle(frame(second,QUERY_IDS[k],sequence=k))["op"],"answer")
        self.assertEqual(second.handle(frame(second,QUERY_IDS[2],sequence=2)),{"error":"REJECTED"})
        self.assertEqual(second.handle(frame(second,None,op="close",sequence=2))["op"],"closed")

    def test_duplicate_raw_json_extra_keys_bools_and_size_denied(self):
        gate=PublicToyCapabilityGate()
        base=frame(gate,QUERY_IDS[0])
        raw=base.rstrip(b"\n")[:-1]+b',"op":"close"}\n'
        variants=(raw,base.replace(b'"query"',b'"score"'),base.replace(b'"input_id":',b'"extra":0,"input_id":'),
                  base.replace(b'"sequence":0',b'"sequence":true'),b"x"*1025+b"\n",
                  base+b"{}\n",b'{"op":NaN}\n',b'[]\n',b'{}')
        for malformed in variants:
            self.assertEqual(gate.handle(malformed),{"error":"REJECTED"})
        self.assertEqual(gate.handle(base)["op"],"answer")

    def test_toy_hmac_detects_modified_answer_receipt_chain_and_mac(self):
        gate=PublicToyCapabilityGate()
        original=gate.handle(frame(gate,QUERY_IDS[0]))
        predecessor="0"*64
        self.assertTrue(gate.verify_toy_receipt(original,expected_previous=predecessor))
        examples=[
            dict(original,answer="FORGED"),
            dict(original,previous_digest="1"*64),
            dict(original,receipt_digest="0"*64),
            dict(original,receipt_mac="0"*64),
            dict(original,extra_field=0),
            dict(original,sequence=True),
        ]
        for tampered in examples:
            self.assertFalse(gate.verify_toy_receipt(tampered,expected_previous=predecessor))
        self.assertFalse(gate.verify_toy_receipt(original,expected_previous="f"*64))
        self.assertFalse(gate.verify_toy_receipt({"receipt_digest":"0"*64},
                                                 expected_previous=predecessor))

    def test_bad_utf8_and_nested_duplicate_keys_denied(self):
        gate=PublicToyCapabilityGate()
        b=frame(gate,QUERY_IDS[0])
        # Appending an extra field with duplicate inner keys is forbidden.
        nested=b[:-2]+b',"bad":{"k":1,"k":2}}\n'
        self.assertEqual(gate.handle(nested),{"error":"REJECTED"})
        self.assertEqual(gate.handle(b'\xff\n'),{"error":"REJECTED"})
        self.assertEqual(gate.handle(b)["op"],"answer")

if __name__=="__main__":
    unittest.main()

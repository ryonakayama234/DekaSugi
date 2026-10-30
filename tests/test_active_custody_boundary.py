"""ACTIVE-001 E0: invented-only strict public wire schema and leak denials."""
import json
import unittest
from dataclasses import asdict, replace

from packages.active_custody_boundary import (
    PUBLIC_SCHEMA, QUERY_SCHEMA, ANSWER_SCHEMA, FINAL_SCHEMA, PublicTaskView,
    encode_public_task, parse_public_task, parse_question, parse_answer,
    parse_final, challenge_digest,
)
from packages.inquiry_world import input_split


class E0PublicWireTests(unittest.TestCase):
    def setUp(self):
        split = input_split(20261030)  # INVENTED; never future study seed
        self.private_mock = {
            "target_id": "INVENTED-CUSTODIAN-ONLY",
            "audit_labels": ["SECRET_FAKE"] * 64,
            "seed_root": "SECRET_FAKE_ROOT",
            "future_answers": ["SECRET_FAKE"],
        }
        self.view = PublicTaskView(
            PUBLIC_SCHEMA, "ab"*16, split.public_ids, split.query_ids,
            ((split.public_ids[0], "PUBLIC-FAKE-A"),
             (split.public_ids[1], "PUBLIC-FAKE-B")), split.split_digest, 2,
        )
        self.json = encode_public_task(self.view)

    def _q(self, q, step=0, **added):
        return json.dumps(dict(
            schema=QUERY_SCHEMA, session_id=self.view.session_id,
            challenge_digest=challenge_digest(self.view),
            step=step, input_id=q, **added))

    def _a(self, q, step=0, **added):
        return json.dumps(dict(
            schema=ANSWER_SCHEMA, session_id=self.view.session_id,
            challenge_digest=challenge_digest(self.view),
            step=step, input_id=q, output="INVENTED_ANSWER", **added))

    def test_strict_public_roundtrip_excludes_all_secret_fields(self):
        v = parse_public_task(self.json)
        self.assertEqual(v, self.view)
        self.assertEqual(encode_public_task(v), self.json)
        fields = set(json.loads(self.json))
        self.assertEqual(fields, {"schema", "session_id", "public_examples",
                                  "public_pool_ids", "query_input_ids",
                                  "split_digest", "max_questions"})
        for name, value in self.private_mock.items():
            self.assertNotIn(name, self.json)
            payload = json.loads(self.json)
            payload[name] = value
            with self.subTest(secret=name), self.assertRaises(ValueError):
                parse_public_task(json.dumps(payload))
        self.assertNotIn("audit_ids", self.json)
        self.assertNotIn("audit_inputs", self.json)

    def test_public_rejects_invalid_pools_examples_and_duplicate_json_keys(self):
        base = json.loads(self.json)
        corrupt = (
            dict(base, public_pool_ids=[1]*28),
            dict(base, query_input_ids=[True] + base["query_input_ids"][1:]),
            dict(base, query_input_ids=base["public_pool_ids"][:1] +
                 base["query_input_ids"][1:]),
            dict(base, public_examples=[[base["public_pool_ids"][0], "a"],
                                        [base["public_pool_ids"][0], "a"]]),
            dict(base, public_examples=[[base["query_input_ids"][0], "x"],
                                        [base["public_pool_ids"][1], "y"]]),
            dict(base, max_questions=True),
            dict(base, session_id="not-opaque"),
            dict(base, split_digest="bad-digest"),
        )
        for item in corrupt:
            with self.subTest(corruption=item), self.assertRaises(ValueError):
                parse_public_task(json.dumps(item))
        raw = self.json[:-1] + ',"schema":"overridden"}'
        with self.assertRaises(ValueError):
            parse_public_task(raw)

    def test_question_and_answer_reject_wrong_turn_replay_and_leaks(self):
        q1, q2 = self.view.query_input_ids[:2]
        first = parse_question(self._q(q1), self.view, asked_ids=())
        self.assertEqual(first.input_id, q1)
        ans = parse_answer(self._a(q1), self.view, question=first)
        self.assertEqual(ans.output, "INVENTED_ANSWER")
        second = parse_question(self._q(q2, step=1), self.view,
                                asked_ids=(q1,))
        self.assertEqual(second.step, 1)
        for raw, asked in (
            (self._q(q1), (q1,)),  # duplicate
            (self._q(q2, step=0), (q1,)),  # stale step
            (self._q(q2, step=2), (q1,q2)),  # over 2 question cap
            (self._q(self.view.public_pool_ids[0]), ()),  # not query
            (self._q(True), ()),  # booleans not integer IDs
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_question(raw, self.view, asked_ids=asked)
        q_payload = json.loads(self._q(q1))
        a_payload = json.loads(self._a(q1))
        for secret in self.private_mock:
            for payload, parse in ((q_payload, lambda s: parse_question(s, self.view, asked_ids=())),
                                   (a_payload, lambda s: parse_answer(s, self.view, question=first))):
                corrupted = dict(payload, **{secret: self.private_mock[secret]})
                with self.subTest(secret=secret), self.assertRaises(ValueError):
                    parse(json.dumps(corrupted))
        with self.assertRaises(ValueError):
            parse_answer(self._a(q2), self.view, question=first)
        with self.assertRaises(ValueError):
            parse_question(json.dumps(dict(q_payload, challenge_digest="0"*64)),
                           self.view, asked_ids=())

    def test_final_submission_never_contains_audit_predictions(self):
        raw = json.dumps(dict(
            schema=FINAL_SCHEMA, session_id=self.view.session_id,
            challenge_digest=challenge_digest(self.view),
            program=["trim", "lower"]))
        valid = parse_final(raw, self.view)
        self.assertEqual(valid.program, ("trim", "lower"))
        for key in ("target_id", "audit_labels", "audit_predictions",
                    "heldout_accuracy", "seed_root", "score", "future_answers"):
            payload = json.loads(raw)
            payload[key] = "LEAK"
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_final(json.dumps(payload), self.view)
        with self.assertRaises(ValueError):
            parse_final(json.dumps(dict(json.loads(raw), program=["not_op"])), self.view)

    def test_schema_only_not_real_process_or_answer_authentication(self):
        # An arbitrary malicious peer able to calculate the public hash could
        # fabricate a valid-looking answer. That is WHY E1 requires a real
        # separated custodian and authenticated channel; E0 does not assert it.
        q = self.view.query_input_ids[0]
        pending = parse_question(self._q(q), self.view, asked_ids=())
        fake = parse_answer(self._a(q), self.view, question=pending)
        self.assertEqual(fake.output, "INVENTED_ANSWER")


if __name__ == "__main__":
    unittest.main()

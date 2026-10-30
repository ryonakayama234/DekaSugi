"""ACTIVE-001 invented-fixture-only P1 session boundary and prefix-replay regressions.

No network, old scorers, private data, or source-locked experiment imports.
"""
from dataclasses import replace
import unittest

from packages.inquiry_world import INPUTS, build_catalog, digest, input_split
from packages.active_learning import (
    final_program, make_answer, partitions, propose_disagreement, propose_random,
    start, update,
)


class QueryHistoryBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.split = input_split(20261030)
        x, y = cls.split.public_ids[:2]
        cls.public = ((x, INPUTS[x]), (y, INPUTS[y]))

    def begin(self, *, max_questions=2):
        session = start("synthetic-P1", self.public, self.split, self.catalog,
                        max_questions=max_questions)
        if max_questions:
            self.assertEqual(session.status, "ambiguous")
        return session

    def test_audit_pool_swapped_and_linked_hash_recomputed(self):
        s = self.begin()
        # This was the 2026-10-30 Codex P1 reproduction: both query pool and
        # pool_digest are changed, but the ORIGINAL split commitment remains.
        forged_pool = self.split.audit_ids
        forged_hash = digest({"split": s.split_digest,
                              "public": s.public_pool_ids, "query": forged_pool})
        forged = replace(s, available_query_ids=forged_pool,
                         pool_digest=forged_hash)
        with self.assertRaises(ValueError):
            propose_disagreement(forged, self.catalog)
        with self.assertRaises(ValueError):
            partitions(forged, self.catalog, forged_pool[0])

    def test_public_question_swap_without_original_split_authority(self):
        s = self.begin()
        public = tuple(sorted((s.public_pool_ids[0],) + s.public_pool_ids[2:] +
                              (s.available_query_ids[0],)))
        query = tuple(sorted((s.public_pool_ids[1],) + s.available_query_ids[1:]))
        forged_hash = digest({"split": s.split_digest,
                              "public": public, "query": query})
        with self.assertRaises(ValueError):
            final_program(replace(s, public_pool_ids=public,
                                  available_query_ids=query,
                                  pool_digest=forged_hash), self.catalog)

    def test_zero_receipt_after_valid_first_answer_is_rejected(self):
        s = self.begin()
        p = propose_disagreement(s, self.catalog)
        target = self.catalog.by_id[s.class_ids[-1]]
        updated = update(s, p, make_answer(p, target.output_signature[p.input_id]),
                         self.catalog)
        self.assertEqual(len(updated.trace), 1)
        old_proposal, old_answer = updated.trace[0]
        fake_answer = replace(old_answer, receipt_digest="0" * 64)
        forged = replace(updated,
                         trace=((old_proposal, fake_answer),),
                         answers=((old_proposal.input_id, old_answer.output,
                                   "0" * 64),))
        with self.assertRaises(ValueError):
            final_program(forged, self.catalog)
        with self.assertRaises(ValueError):
            propose_disagreement(forged, self.catalog)

    def test_historical_choice_must_replay_policy(self):
        s = self.begin()
        p = propose_random(s, self.catalog, seed=17)
        self.assertIsNotNone(p)
        target = self.catalog.by_id[s.class_ids[-1]]
        updated = update(s, p, make_answer(p, target.output_signature[p.input_id]),
                         self.catalog)
        old_p, old_a = updated.trace[0]
        forged_p = replace(old_p, random_seed=18)
        forged_a = make_answer(forged_p, old_a.output)
        forged = replace(updated, trace=((forged_p, forged_a),),
                         answers=((forged_p.input_id, forged_a.output,
                                   forged_a.receipt_digest),))
        with self.assertRaises(ValueError):
            final_program(forged, self.catalog)

    def test_dangling_answers_and_skipped_trace_rejected(self):
        s = self.begin()
        p = propose_disagreement(s, self.catalog)
        target = self.catalog.by_id[s.class_ids[-1]]
        updated = update(s, p, make_answer(p, target.output_signature[p.input_id]),
                         self.catalog)
        with self.assertRaises(ValueError):
            final_program(replace(updated, trace=()), self.catalog)
        with self.assertRaises(ValueError):
            final_program(replace(updated, answers=()), self.catalog)
        with self.assertRaises(ValueError):
            final_program(replace(updated, class_ids=updated.class_ids * 2),
                          self.catalog)

    def test_terminal_state_cannot_be_extended_with_second_question(self):
        # Force a legitimate terminal state after the first question.
        s = self.begin(max_questions=1)
        p = propose_disagreement(s, self.catalog)
        target = self.catalog.by_id[s.class_ids[-1]]
        terminal = update(s, p,
                          make_answer(p, target.output_signature[p.input_id]),
                          self.catalog)
        self.assertIn(terminal.status,
                      ("identified", "budget_exhausted", "model_inconsistent"))
        # Even a syntactically valid second proposal/receipt must not be accepted.
        fake_p = replace(p, step=1)
        fake_a = make_answer(fake_p, "a")
        forged = replace(terminal,
                         max_questions=2,
                         trace=terminal.trace + ((fake_p, fake_a),),
                         answers=terminal.answers + ((fake_p.input_id, "a",
                                                      fake_a.receipt_digest),))
        with self.assertRaises(ValueError):
            final_program(forged, self.catalog)

    def test_identified_after_one_question_must_be_terminal(self):
        s = self.begin(max_questions=2)
        p = propose_disagreement(s, self.catalog)
        # Select an actual singleton posterior, not a merely exhausted budget.
        singleton_output = next(y for y, count in p.predictive_partition if count == 1)
        identified = update(s, p, make_answer(p, singleton_output), self.catalog)
        self.assertEqual(identified.status, "identified")
        self.assertEqual(len(identified.class_ids), 1)
        self.assertEqual(len(identified.trace), 1)
        # A fabricated second step preserves the final single-class vote, so
        # aggregate-only class validation would incorrectly accept it.
        other = next(i for i in s.available_query_ids if i != p.input_id)
        fake_p = replace(p, step=1, input_id=other)
        fake_a = make_answer(fake_p, "unmatched-output")
        forged = replace(identified, trace=identified.trace + ((fake_p, fake_a),),
                         answers=identified.answers + ((other, "unmatched-output",
                                                       fake_a.receipt_digest),))
        with self.assertRaises(ValueError):
            final_program(forged, self.catalog)

    def test_finite_state_machine_preserves_target(self):
        s = self.begin()
        for cid in s.class_ids[:25]:
            target = self.catalog.by_id[cid]
            for policy in ("B1", "B2"):
                x = s
                for step in range(2):
                    p = (propose_random(x, self.catalog, seed=13 + step)
                         if policy == "B1" else
                         propose_disagreement(x, self.catalog))
                    if p is None:
                        break
                    x = update(x, p,
                               make_answer(p, target.output_signature[p.input_id]),
                               self.catalog)
                    self.assertIn(cid, x.class_ids)
                    self.assertEqual(len(x.trace), len(x.answers))
                    final_program(x, self.catalog)
                self.assertLessEqual(len(x.answers), 2)


if __name__ == "__main__":
    unittest.main()

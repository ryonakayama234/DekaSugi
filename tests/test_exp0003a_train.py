"""EXP-0003A preregistered TRAIN-only contract and trust boundary tests."""
from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch

from packages.exp0003a import (
    FAMILIES, ID_VERSION, TRAIN_TOTAL, digest, generate_train, opaque_id,
    private_train_manifest, sleep, train_bundle, train_report,
    _issue_wake_receipt, stable_episode_payload, wake,
)
from packages.library import DEFAULT_PRIMITIVES, DEFAULT_REGISTRY
from packages.protocol import Example, parse_task, program_hash


class Exp0003ATrainTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = generate_train()

    def test_exact_train_families_and_isolated_private_audit(self):
        self.assertEqual(len(self.cases), TRAIN_TOTAL)
        self.assertEqual([c.family for c in self.cases[::20]], list(FAMILIES))
        self.assertEqual(len({c.task.task_id for c in self.cases}), 160)
        self.assertEqual(len({x for c in self.cases for x in c.seeds}), 480)
        self.assertEqual(self.cases[0].source_record_id, "train-f00-i000")
        self.assertEqual(self.cases[-1].source_record_id, "train-f07-i019")
        for c in self.cases:
            self.assertEqual(c.task.task_id, opaque_id(c.task.examples))
            self.assertEqual(len(c.task.task_id), 66)
            self.assertEqual(len(c.task.examples), 2)
            self.assertEqual((c.task.limits.max_ast_nodes, c.task.limits.max_candidates), (4, 100))
            self.assertNotIn(c.source_record_id, repr(c.task))
            self.assertNotIn(c.family, c.task.task_id)
            self.assertEqual(len(c.seeds), 3)
        private_manifest = private_train_manifest(self.cases)
        self.assertEqual(private_manifest["partition"], "TRAIN")
        self.assertEqual(private_manifest["id_version"], ID_VERSION)
        self.assertEqual(private_manifest["count"], TRAIN_TOTAL)
        self.assertNotIn("audit", str(private_manifest))
        self.assertEqual(self.cases, generate_train())
        self.assertEqual(private_manifest, private_train_manifest(generate_train()))

    def test_reference_transformations_and_nontriviality(self):
        for case in self.cases:
            samples = case.task.examples + (case.private_audit,)
            for example in samples:
                value, output = example.input, example.output
                if case.family == "identity":
                    self.assertEqual(output, value)
                    self.assertEqual(value, value.strip())
                elif case.family == "trim":
                    self.assertEqual(output, value.strip())
                    self.assertNotEqual(output, value)
                elif case.family == "lower":
                    self.assertEqual(output, value.lower())
                    self.assertNotEqual(output, value)
                elif case.family == "upper":
                    self.assertEqual(output, value.upper())
                    self.assertNotEqual(output, value)
                elif case.family == "normalize_lower":
                    self.assertEqual(output, value.strip().lower())
                    self.assertNotEqual(output, value)
                elif case.family == "normalize_upper":
                    self.assertEqual(output, value.strip().upper())
                    self.assertNotEqual(output, value)
                elif case.family == "reverse_ood":
                    self.assertEqual(output, value[::-1])
                    self.assertNotEqual(output, value)
                else:
                    self.assertEqual(output, "Z" + value[1:])
                    self.assertNotEqual(output, value)

    def test_opaque_id_ignores_source_labels_and_protects_example_order(self):
        examples = self.cases[0].task.examples
        self.assertNotEqual(opaque_id(examples), opaque_id(examples[::-1]))
        self.assertEqual(opaque_id(examples), "t-" + digest({
            "domain": "string_to_string", "schema_version": "0.1",
            "limits": {"max_ast_nodes": 4, "max_candidates": 100},
            "examples": [{"input": e.input, "output": e.output} for e in examples],
        }))
        self.assertRaises(ValueError, opaque_id, examples[:1])
        forged = replace(self.cases[0].task, task_id="train-f00-i000")
        with self.assertRaisesRegex(ValueError, "Untrusted public"):
            wake(forged, private_audit=self.cases[0].private_audit)

    def test_wake_audit_is_independent_and_cannot_retrain_search(self):
        case = self.cases[20]  # trim requires at least one real primitive
        good = wake(case.task, private_audit=case.private_audit)
        self.assertEqual(good.status, "success")
        self.assertEqual(good.public_search_status, "solved")
        self.assertGreater(good.primitive_invocations, 0)
        self.assertGreater(good.audit_primitive_invocations, 0)
        self.assertEqual(good.public_task_sha256, case.task.task_id[2:])
        self.assertEqual(good.program_ast is not None, True)
        bad = wake(case.task, private_audit=Example(case.private_audit.input, "invalid-audit"))
        self.assertEqual(bad.status, "audit_rejected")
        self.assertEqual(bad.program_ast, good.program_ast)
        self.assertEqual((bad.trace_sha256, bad.tested_candidates, bad.primitive_invocations),
                         (good.trace_sha256, good.tested_candidates, good.primitive_invocations))
        self.assertEqual(bad.audit_correct, False)
        self.assertNotEqual(bad.audit_evidence_ref, good.audit_evidence_ref)
        receipt = _issue_wake_receipt(bad)
        self.assertEqual(len(sleep((bad,), trusted_receipts=(receipt,))), 0)
        with self.assertRaisesRegex(ValueError, "receipt mismatch"):
            sleep((replace(bad, status="success"),), trusted_receipts=(receipt,))

    def test_sleep_extracts_from_recorded_ast_not_oracle_or_resynthesis(self):
        selected = self.cases[80:120]  # both normalize families
        episodes = tuple(wake(c.task, private_audit=c.private_audit) for c in selected)
        receipts = tuple(_issue_wake_receipt(e) for e in episodes)
        with patch("packages.synthesis.synthesize", side_effect=AssertionError("must not search")):
            proposals = sleep(episodes, trusted_receipts=receipts)
        self.assertGreater(len(proposals), 0)
        self.assertEqual(
            [(p.candidate.occurrences, p.candidate.skill_id) for p in proposals],
            sorted([(p.candidate.occurrences, p.candidate.skill_id) for p in proposals],
                   key=lambda v: (-v[0], v[1])),
        )
        successes = {e.task_id: e for e in episodes if e.status == "success"}
        self.assertEqual([p.status for p in proposals],
                         ["candidate"] + ["withheld"] * (len(proposals) - 1))
        for p in proposals:
            self.assertGreaterEqual(p.candidate.occurrences, 2)
            self.assertEqual(p.candidate.body_hash, program_hash(p.candidate.body_ast))
            self.assertEqual(p.candidate.occurrences, len(p.candidate.provenance))
            self.assertTrue(set(p.candidate.provenance).issubset(successes))
            self.assertEqual(p.source_episode_ids,
                             tuple("wake:" + x for x in p.candidate.provenance))
        self.assertEqual(tuple(p.op_id for p in DEFAULT_REGISTRY.primitives),
                         tuple(p.op_id for p in DEFAULT_PRIMITIVES))

    def test_evaluator_receipts_reject_ast_status_and_trace_tampering(self):
        from packages.protocol import Call, Input
        cases = (self.cases[0], self.cases[1])
        episodes = tuple(wake(c.task, private_audit=c.private_audit) for c in cases)
        receipts = tuple(_issue_wake_receipt(e) for e in episodes)
        alternative = Call("upper", Call("trim", Input()))
        for field, modified in (
            ("program_ast", replace(episodes[0], program_ast=alternative)),
            ("status", replace(episodes[0], status="audit_rejected")),
            ("audit", replace(episodes[0], audit_evidence_ref="audit-sha256:" + "0" * 64)),
            ("trace", replace(episodes[0], trace_sha256="0" * 64)),
            ("count", replace(episodes[0], tested_candidates=999)),
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "receipt mismatch"):
                    sleep((modified, episodes[1]), trusted_receipts=receipts)
        with self.assertRaisesRegex(ValueError, "Missing or extra"):
            sleep(episodes, trusted_receipts=receipts[:1])
        with self.assertRaisesRegex(ValueError, "Duplicate trusted"):
            sleep(episodes, trusted_receipts=(receipts[0], receipts[0]))
        # Timestamp noise can change but never authenticates a different AST.
        noisy = replace(episodes[0], search_cpu_ms=episodes[0].search_cpu_ms + 100)
        self.assertEqual(stable_episode_payload(noisy),
                         stable_episode_payload(episodes[0]))
        self.assertEqual(len(sleep((noisy, episodes[1]), trusted_receipts=receipts)), 0)

    def test_private_replay_evidence_and_cost_separation(self):
        public, private = train_bundle()
        self.assertEqual(len(private["rows"]), 160)
        self.assertEqual(len(private["wake_receipts"]), 160)
        self.assertEqual(digest(private["rows"]), private["private_rows_sha256"])
        self.assertEqual(private["private_rows_sha256"],
                         public["private_manifest"]["private_rows_sha256"])
        self.assertEqual(digest(private["wake_receipts"]),
                         public["trusted_receipts_sha256"])
        self.assertEqual(private["wake_receipts_sha256"],
                         public["trusted_receipts_sha256"])
        for row, episode, receipt in zip(
            private["rows"], public["episodes"], private["wake_receipts"]
        ):
            self.assertEqual(row["task_id"], episode["task_id"])
            self.assertEqual(row["audit_evidence_ref"], episode["audit_evidence_ref"])
            self.assertEqual(receipt["episode_sha256"],
                             digest({k: v for k, v in episode.items()
                                     if not k.endswith("_ms")}))
            self.assertEqual(len(row["public_task"]["examples"]), 2)
            self.assertIn("input", row["audit"])
            self.assertIn("output", row["audit"])
            self.assertEqual(row["seeds"].__len__(), 3)
        self.assertNotIn("private_example", str(public))
        self.assertNotIn("seeds", str(public))
        self.assertIn("generator_cpu", public["train_cost_ms"])
        self.assertIn("generator_wall", public["train_cost_ms"])
        self.assertIn("sleep_cpu", public["train_cost_ms"])
        self.assertIn("sleep_wall", public["train_cost_ms"])
        for value in public["train_cost_ms"].values():
            self.assertGreaterEqual(value, 0)
        # Altering public task or raw audit must break the private manifest hash.
        altered = list(private["rows"])
        altered[0] = {**altered[0], "audit": {"input": "bad", "output": "bad"}}
        self.assertNotEqual(digest(altered), public["private_manifest"]["private_rows_sha256"])

    def test_evidence_and_replay_are_train_only(self):
        report = train_report()
        self.assertEqual(report["experiment_id"], "EXP-0003A")
        self.assertEqual(report["phase"], "TRAIN")
        self.assertEqual(report["partition_counts"], {"TRAIN": 160})
        self.assertEqual(sum(report["wake_status"].values()), 160)
        self.assertEqual(len(report["episodes"]), 160)
        self.assertEqual(report["registry_promotion"], "not_authorized")
        self.assertEqual(report["preregistered_final_evaluated"], False)
        self.assertGreater(len(report["proposals"]), 0)
        self.assertEqual(report["functional_gate"], "candidate_found")
        self.assertEqual(report["episodes_sha256"], digest([
            {k: v for k, v in row.items() if not k.endswith("_ms")}
            for row in report["episodes"]
        ]))
        first = wake(self.cases[20].task, private_audit=self.cases[20].private_audit)
        second = wake(self.cases[20].task, private_audit=self.cases[20].private_audit)
        self.assertEqual((first.trace_sha256, first.status,
                          first.primitive_invocations, first.tested_candidates),
                         (second.trace_sha256, second.status,
                          second.primitive_invocations, second.tested_candidates))

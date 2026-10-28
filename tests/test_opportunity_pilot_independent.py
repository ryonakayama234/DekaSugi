"""Independent pure-stdlib PILOT-V1 manifest verification, no scoring."""
from __future__ import annotations

import inspect
import json
from hashlib import sha256
import unittest

from scripts import audit_opportunity_pilot_public as independent
from packages.evaluation.opportunity_pilot import public_preflight, generate_train_pilot


class IndependentPilotManifestTests(unittest.TestCase):
    def test_independent_public_hash_matches_committed_expected(self):
        recalculated = independent.verify_public()
        existing = public_preflight()
        self.assertEqual(recalculated["public_count"], 64)
        self.assertEqual(recalculated["public_manifest_sha256"],
                         independent.EXPECTED_PUBLIC_SHA256)
        self.assertEqual(recalculated["public_manifest_sha256"],
                         existing["public_manifest_sha256"])
        self.assertEqual(len(recalculated["third_audit_commitments_sha256"]), 64)
        self.assertFalse(recalculated["private_audit_bytes_published"])
        self.assertEqual(recalculated["paired_trials_executed"], 0)
        self.assertFalse(recalculated["dev_or_final_evaluated"])
        self.assertTrue(recalculated["independent_from_project_generator_imports"])

    def test_independent_third_audit_commitment_matches_project_bytes(self):
        # Check private third records in memory only; publish digest, never bytes.
        commitments = []
        for case in generate_train_pilot():
            third = {"input": case.private_audit.input,
                     "output": case.private_audit.output}
            third_sha = sha256(json.dumps(
                third, sort_keys=True, separators=(",", ":"),
                ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
            commitments.append({
                "task_id": case.task.task_id,
                "third_audit_sha256": third_sha,
            })
        def digest(rows):
            return sha256(json.dumps(
                rows, sort_keys=True, separators=(",", ":"),
                ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
        expected = independent.verify_public()["third_audit_commitments_sha256"]
        self.assertEqual(digest(commitments), expected)
        commitments[0]["third_audit_sha256"] = "0" * 64
        self.assertNotEqual(digest(commitments), expected)

    def test_different_alphabet_mismatches_public_source(self):
        alternate = independent.derive_hashes(alphabet="uvwxYQ04")
        self.assertNotEqual(alternate["public_manifest_sha256"],
                            independent.EXPECTED_PUBLIC_SHA256)

    def test_invalid_alphabet_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "token exhausted"):
            independent.derive_hashes(alphabet="u")

    def test_independent_auditor_has_no_project_or_scorer_imports(self):
        source = inspect.getsource(independent)
        for prohibited in ("from packages.", "import packages.",
                           "bounded_synthesize(", "run_dev(",
                           "generate_train_pilot(", "run_train_dream("):
            self.assertNotIn(prohibited, source)


if __name__ == "__main__":
    unittest.main()

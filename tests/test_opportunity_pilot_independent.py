"""Independent pure-stdlib PILOT-V1 manifest verification, no scoring."""
from __future__ import annotations

import inspect
import unittest

from scripts import audit_opportunity_pilot_public as independent
from packages.evaluation.opportunity_pilot import public_preflight


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

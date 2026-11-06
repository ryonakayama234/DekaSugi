"""G3-1 pure contract tests: synthetic design only, NO 448 child execution."""
from __future__ import annotations

from hashlib import sha256
from itertools import product
from pathlib import Path
import tempfile
import unittest

from packages.r2_m_eng.records import digest
from packages.r2_m_a.contracts import (
    ARMS, EXPECTED_SLOTS, G2_MAIN_SHA, G2_PREREG_SHA256, LAW_IDS,
    RSS_BOUNDARY_UPPER_BYTES, RSS_BYTES_CAP, SCIENTIFIC_EXECUTION_AUTHORIZED,
    USE_POINTS, ChildRequest, Slot, expected_slot_set, rss_boundary_status,
    validate_g5_order_manifest, verify_child_payload, verify_g2_anchor,
)


class G31ContractTests(unittest.TestCase):
    def test_frozen_values_and_unordered_448_design(self):
        self.assertFalse(SCIENTIFIC_EXECUTION_AUTHORIZED)
        self.assertEqual((len(LAW_IDS), len(ARMS), len(USE_POINTS)), (16, 7, 4))
        self.assertEqual(EXPECTED_SLOTS, 448)
        self.assertEqual(set(LAW_IDS), {"".join(map(str, v))
                                        for v in product((0, 1), repeat=4)})
        self.assertEqual(tuple(USE_POINTS), ((0, 1, 1), (1, 0, 1),
                                             (1, 1, 0), (1, 1, 1)))
        slots = expected_slot_set()
        self.assertIs(type(slots), frozenset)
        self.assertEqual(len(slots), 448)
        for law in LAW_IDS:
            self.assertEqual(sum(s.law_id == law for s in slots), 28)
        for arm in ARMS:
            self.assertEqual(sum(s.arm == arm for s in slots), 64)
        self.assertNotIn("F01", ARMS)
        self.assertNotIn("F11", ARMS)
        self.assertNotIn("ORACLE-REF", ARMS)

    def test_reject_missing_duplicate_or_unapproved_slots(self):
        with self.assertRaisesRegex(ValueError, "INVALID"):
            Slot("not-a-law", USE_POINTS[0], "F00")
        with self.assertRaisesRegex(ValueError, "INVALID"):
            Slot("0000", (0, 0, 1), "F00")
        with self.assertRaisesRegex(ValueError, "INVALID"):
            Slot("0000", USE_POINTS[0], "F01")
        with self.assertRaisesRegex(ValueError, "INVALID"):
            Slot("0000", USE_POINTS[0], "ORACLE-REF")
        # Pure in-memory fictitious ordering; NOT a G5 run order or source.
        fixture = tuple(sorted(expected_slot_set(), key=lambda s: (s.law_id, s.point, s.arm)))
        digest_fixture = digest([s.as_dict() for s in fixture])
        self.assertEqual(validate_g5_order_manifest(
            fixture, expected_digest=digest_fixture), fixture)
        for wrong in (fixture[:-1], fixture[:-1] + (fixture[0],), list(fixture)):
            with self.assertRaisesRegex(ValueError, "RUN_BLOCK"):
                validate_g5_order_manifest(wrong, expected_digest=digest_fixture)
        with self.assertRaisesRegex(ValueError, "RUN_BLOCK"):
            validate_g5_order_manifest(fixture, expected_digest="0"*64)

    def test_exact_prereg_sha_and_byte_check(self):
        verify_g2_anchor(main_sha=G2_MAIN_SHA, document_sha256=G2_PREREG_SHA256)
        with self.assertRaisesRegex(ValueError, "RUN_BLOCK"):
            verify_g2_anchor(main_sha="0"*40, document_sha256=G2_PREREG_SHA256)
        with self.assertRaisesRegex(ValueError, "RUN_BLOCK"):
            verify_g2_anchor(main_sha=G2_MAIN_SHA, document_sha256="f"*64)
        with self.assertRaisesRegex(ValueError, "RUN_BLOCK"):
            verify_g2_anchor(main_sha=G2_MAIN_SHA, document_sha256=G2_PREREG_SHA256,
                             document_bytes=b"wrong bytes")

    def test_si_rss_boundary_is_visible_and_raw_values_are_not_lost(self):
        self.assertEqual(RSS_BYTES_CAP, 512_000_000)
        self.assertEqual(RSS_BOUNDARY_UPPER_BYTES, 536_870_912)
        self.assertEqual(rss_boundary_status(RSS_BYTES_CAP - 1), "WITHIN_SI_CAP")
        for value in (RSS_BYTES_CAP, RSS_BYTES_CAP + 1, 532_000_000,
                      RSS_BOUNDARY_UPPER_BYTES):
            self.assertEqual(rss_boundary_status(value), "BOUNDARY_REVIEW")
        self.assertEqual(rss_boundary_status(RSS_BOUNDARY_UPPER_BYTES + 1),
                         "RESOURCE_STOP")
        for bad in (None, -1, True, 1.5):
            with self.assertRaises(ValueError):
                rss_boundary_status(bad)

    def test_child_payload_only_five_fields_and_public_use_coordinate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            request = ChildRequest(str(root / "snapshot.json"),
                                   "a"*64, "FIXED-MACRO", USE_POINTS[0],
                                   str(root / "trace.json"))
            payload = request.as_dict()
            self.assertEqual(len(payload), 5)
            self.assertEqual(verify_child_payload(payload), request)
            for secret in ("law_id", "seed", "true_label", "score", "oracle"):
                with self.subTest(secret=secret), self.assertRaisesRegex(ValueError, "INVALID"):
                    verify_child_payload({**payload, secret: "0000"})
            for wrong in ("F11", "ORACLE-REF", "F01"):
                with self.assertRaisesRegex(ValueError, "INVALID"):
                    verify_child_payload({**payload, "arm": wrong})
            with self.assertRaisesRegex(ValueError, "INVALID"):
                verify_child_payload({**payload, "point": [0, 0, 1]})
            with self.assertRaisesRegex(ValueError, "INVALID"):
                verify_child_payload({**payload, "point": [True, 1, 1]})
            with self.assertRaisesRegex(ValueError, "INVALID"):
                verify_child_payload({**payload, "snapshot_path": "relative.json"})
            with self.assertRaisesRegex(ValueError, "INVALID"):
                verify_child_payload({**payload, "trace_path": payload["snapshot_path"]})


if __name__ == "__main__":
    unittest.main()

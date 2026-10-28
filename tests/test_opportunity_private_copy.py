"""Synthetic-only negative controls; no real TRAIN64/DEV/FINAL or third audits."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
from hashlib import sha256
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest
from unittest.mock import patch

from scripts import verify_opportunity_private_copy as m


class PrivateCopyReceiptTests(unittest.TestCase):
    def test_distinct_fake_copies_only_attest_byte_equality(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            a, b = Path(tmp) / "first", Path(tmp) / "second"
            secret = b"synthetic_fake_audit_bytes_not_research"
            a.write_bytes(secret)
            b.write_bytes(secret)
            got = m.verify_private_copies(a, b, sha256(secret).hexdigest(), root=root)
            self.assertEqual(got["copy_count"], 2)
            self.assertFalse(got["independent_private_raw_custody_verified"])
            self.assertFalse(got["scoring_authorized"])
            self.assertFalse(got["acl_encryption_retention_restore_verified"])
            self.assertNotIn("synthetic_fake", str(got))
            self.assertNotIn(str(a), str(got))

    def test_missing_mismatch_and_tampered_copy_hard_stop(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)/"repo"; root.mkdir()
            a, b = Path(tmp)/"a", Path(tmp)/"b"
            a.write_bytes(b"fixture")
            b.write_bytes(b"fixture")
            expected = sha256(b"fixture").hexdigest()
            for wrong in ("F"*64, "0"*64, "secret", ""):
                with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                    m.verify_private_copies(a, b, wrong, root=root)
            b.write_bytes(b"fixture-tampered")
            with self.assertRaises(ValueError):
                m.verify_private_copies(a, b, expected, root=root)
            b.unlink()
            with self.assertRaises(ValueError):
                m.verify_private_copies(a, b, expected, root=root)

    def test_same_file_hardlink_symlink_public_repo_and_size(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)/"repo"; root.mkdir()
            a, b = Path(tmp)/"first", Path(tmp)/"second"
            a.write_bytes(b"synthetic")
            digest = sha256(b"synthetic").hexdigest()
            with self.assertRaises(ValueError):
                m.verify_private_copies(a, a, digest, root=root)
            os.link(a,b)
            with self.assertRaises(ValueError):
                m.verify_private_copies(a, b, digest, root=root)
            b.unlink(); b.symlink_to(a)
            with self.assertRaises(ValueError):
                m.verify_private_copies(a, b, digest, root=root)
            b.unlink(); b.write_bytes(b"synthetic")
            (root/"copied_private").write_bytes(b"synthetic")
            with self.assertRaises(ValueError):
                m.verify_private_copies(a, root/"copied_private", digest, root=root)
            b.write_bytes(b"")
            with self.assertRaises(ValueError):
                m.verify_private_copies(a, b, digest, root=root)
            b.write_bytes(b"synthetic")
            with patch.object(m, "MAX_BYTES", 3), self.assertRaises(ValueError):
                m.verify_private_copies(a, b, digest, root=root)

    def test_cli_does_not_print_secret_path_or_content(self):
        with TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"PRIVATE_SECRET_FILENAME", Path(tmp)/"other"
            a.write_bytes(b"fixture")
            b.write_bytes(b"fixture")
            with redirect_stdout(StringIO()) as out, redirect_stderr(StringIO()) as err:
                rc=m.main(["--primary",str(a),"--secondary",str(b),"--expected-sha256","0"*64])
            self.assertEqual(rc,2)
            self.assertEqual(out.getvalue(),"")
            self.assertNotIn("PRIVATE_SECRET",err.getvalue())
            self.assertNotIn(str(a),err.getvalue())


if __name__ == "__main__":
    unittest.main()

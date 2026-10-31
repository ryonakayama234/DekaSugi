"""Synthetic bytes labelled .gpg are NOT real encryption or a real secret source."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from packages.concept_custody.vault_preflight import (
    ciphertext_receipt, verify_ciphertext_receipt, SCHEMA, STATUS)

METHOD="a"*40
ROOT=Path(__file__).resolve().parents[1]

class DriveVaultPreflightTests(unittest.TestCase):
    def test_bounded_public_ciphertext_hash_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"fake-data.gpg"
            path.write_bytes(b"FAKE-UNENCRYPTED-PUBLIC-TEST-ONLY")
            report=ciphertext_receipt(str(path),method_commit=METHOD,artifact_kind="sealed_source")
            self.assertEqual(report["schema"],SCHEMA)
            self.assertEqual(report["status"],STATUS)
            self.assertFalse(report["cryptographic_encryption_verified"])
            self.assertFalse(report["independent_custody_verified"])
            self.assertFalse(report["scientific_source_frozen"])
            verify_ciphertext_receipt(str(path),method_commit=METHOD,
                                      artifact_kind="sealed_source",receipt=report)
            path.write_bytes(b"TAMPERED-TEST-ONLY")
            with self.assertRaises(ValueError):
                verify_ciphertext_receipt(str(path),method_commit=METHOD,
                                          artifact_kind="sealed_source",receipt=report)

    def test_fake_verified_flags_and_extra_fields_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"test.gpg"
            path.write_bytes(b"x")
            report=ciphertext_receipt(str(path),method_commit=METHOD,artifact_kind="aggregate_only")
            for fake in (dict(report,scientific_source_frozen=True),
                         dict(report,cryptographic_encryption_verified=True),
                         dict(report,new_field="spoofed"),
                         {k:v for k,v in report.items() if k!="status"}):
                with self.assertRaises(ValueError):
                    verify_ciphertext_receipt(str(path),method_commit=METHOD,
                                              artifact_kind="aggregate_only",receipt=fake)

    def test_wrong_kind_or_method_or_non_gpg_file_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"sample.gpg"
            path.write_bytes(b"public dummy")
            report=ciphertext_receipt(str(path),method_commit=METHOD,artifact_kind="oracle_transcript")
            with self.assertRaises(ValueError):
                verify_ciphertext_receipt(str(path),method_commit="b"*40,
                                          artifact_kind="oracle_transcript",receipt=report)
            with self.assertRaises(ValueError):
                verify_ciphertext_receipt(str(path),method_commit=METHOD,
                                          artifact_kind="aggregate_only",receipt=report)
            with self.assertRaises(ValueError):
                ciphertext_receipt(str(path),method_commit=METHOD.upper(),
                                   artifact_kind="sealed_source")
            with self.assertRaises(ValueError):
                ciphertext_receipt(str(path),method_commit=METHOD,artifact_kind="FINAL")
            with self.assertRaises(ValueError):
                ciphertext_receipt(str(Path(tmp)/"missing.txt"),method_commit=METHOD,
                                   artifact_kind="sealed_source")

    def test_empty_and_symlink_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"empty.gpg"
            path.touch()
            with self.assertRaises(ValueError):
                ciphertext_receipt(str(path),method_commit=METHOD,artifact_kind="sealed_source")
            target=Path(tmp)/"other.gpg"
            target.write_bytes(b"not-real-encrypted")
            link=Path(tmp)/"link.gpg"
            link.symlink_to(target)
            with self.assertRaises(OSError):
                ciphertext_receipt(str(link),method_commit=METHOD,artifact_kind="sealed_source")

    def test_cli_inspect_verify_never_decrypts_or_exposes_plaintext(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact=Path(tmp)/"test.gpg"
            artifact.write_bytes(b"PUBLIC_DUMMY_TEST_ONLY")
            args=[sys.executable,"-m","packages.concept_custody.vault_preflight",
                  "--ciphertext",str(artifact),"--method-commit",METHOD,"--kind","sealed_source"]
            inspected=subprocess.run(args+["--mode","inspect"],cwd=ROOT,capture_output=True,
                                     text=True,check=True,timeout=10)
            report=json.loads(inspected.stdout)
            self.assertNotIn("PUBLIC_DUMMY",inspected.stdout)
            path=Path(tmp)/"receipt.json"
            path.write_text(inspected.stdout,encoding="utf-8")
            verified=subprocess.run(args+["--mode","verify","--receipt",str(path)],
                                    cwd=ROOT,capture_output=True,text=True,check=True,timeout=10)
            self.assertIn("PUBLIC_CIPHERTEXT_HASH_MATCH_ONLY",verified.stdout)
            path.write_text('{"status":"x","status":"y"}',encoding="utf-8")
            failed=subprocess.run(args+["--mode","verify","--receipt",str(path)],
                                  cwd=ROOT,capture_output=True,text=True,timeout=10)
            self.assertNotEqual(failed.returncode,0)

if __name__=="__main__":
    unittest.main()

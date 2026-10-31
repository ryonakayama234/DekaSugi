"""GPG symmetric cipher PUBLIC DUMMY ONLY; no secret scientific source."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class PublicGpgRehearsalTests(unittest.TestCase):
    def test_disposable_public_roundtrip_and_wrong_passphrase_denial(self):
        done=subprocess.run([sys.executable,"-m","packages.concept_custody.public_gpg_rehearsal"],
                            cwd=ROOT,text=True,capture_output=True,timeout=60)
        self.assertEqual(done.returncode,0,msg=done.stderr[-1000:])
        result=json.loads(done.stdout)
        self.assertEqual(result["status"],"PUBLIC_DUMMY_GPG_ROUNDTRIP_ONLY")
        self.assertEqual(result["cipher"],"AES256")
        self.assertTrue(result["correct_passphrase_roundtrip"])
        self.assertTrue(result["wrong_passphrase_rejected"])
        self.assertTrue(result["temporary_files_automatically_removed"])
        self.assertFalse(result["scientific_source_generated"])
        self.assertFalse(result["real_keys_or_labels_accessed"])
        self.assertFalse(result["third_party_custody_verified"])
        self.assertNotIn("passphrase",done.stdout.lower().replace("wrong_passphrase_rejected","").replace("correct_passphrase_roundtrip",""))

if __name__=="__main__":
    unittest.main()

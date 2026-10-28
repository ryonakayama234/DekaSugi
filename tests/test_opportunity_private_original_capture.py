"""Synthetic-only controls for fresh TRAIN64 private original capture.

Never calls the genuine source generator or scorer; every example is invented.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts import capture_opportunity_private_original as m


def synthetic_cases_and_choices():
    cases = []
    choices = []
    commitments = []
    for i in range(64):
        task_id = "t-" + f"{i:064x}"
        audit = SimpleNamespace(input=f"SYNTHETIC-INPUT-{i}", output=f"SYNTHETIC-OUTPUT-{i}")
        case = SimpleNamespace(task=SimpleNamespace(task_id=task_id),
                               private_audit=audit, family="SYNTHETIC",
                               source_record_id=f"synthetic-{i}", seeds=(i*3,i*3+1,i*3+2))
        cases.append(case)
        choices.append({"task_id": task_id, "choices": {
            p: {"action": "OFF"} for p in ("B1","B2","B3")}})
        commitments.append({"task_id": task_id,
                            "third_audit_sha256": m.digest({"input": audit.input, "output": audit.output})})
    public = {"source_manifest_sha256": m.PUBLIC_MANIFEST,
              "paired_trials_executed": 0, "dev_or_final_evaluated": False,
              "decisions": choices}
    return cases, public, m.digest(commitments)


class PrivateOriginCaptureSyntheticTests(unittest.TestCase):
    def test_synthetic_sixty_four_records_are_private_only(self):
        cases, choices, original_commitment = synthetic_cases_and_choices()
        with patch.object(m, "THIRD_COMMITMENT", original_commitment):
            raw = m.build_private_original(cases, choices)
        obj = json.loads(raw)
        self.assertEqual(len(obj["records"]), 64)
        self.assertEqual(obj["paired_trials_executed_at_capture"], 0)
        self.assertEqual(obj["records"][0]["third_audit"]["input"], "SYNTHETIC-INPUT-0")
        self.assertEqual(obj["third_audit_commitments_sha256"], original_commitment)
        self.assertTrue(raw.endswith(b"\n"))

    def test_duplicate_missing_out_of_order_action_and_commitment_drift(self):
        cases, choices, expected = synthetic_cases_and_choices()
        changed = [
            lambda c,p: c.pop(),
            lambda c,p: c.__setitem__(1, c[0]),
            lambda c,p: p["decisions"].reverse(),
            lambda c,p: p["decisions"][0]["choices"].pop("B2"),
            lambda c,p: p.update(paired_trials_executed=1),
            lambda c,p: p.update(source_manifest_sha256="0"*64),
            lambda c,p: c[0].private_audit.__setattr__("input", "TAMPERED"),
        ]
        for mutate in changed:
            c, p = deepcopy(cases), deepcopy(choices)
            mutate(c,p)
            with self.subTest(mutate=str(mutate)), patch.object(m, "THIRD_COMMITMENT", expected):
                with self.assertRaises(ValueError):
                    m.build_private_original(c,p)

    def test_readback_two_separate_simulated_devices_no_custody_claim(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            d1,d2=root/"first",root/"second"
            d1.mkdir(mode=0o700);d2.mkdir(mode=0o700)
            a,b=d1/"first-original.bin",d2/"second-original.bin"
            raw=b"synthetic_example_content"
            first=SimpleNamespace(st_dev=101,st_ino=1)
            second=SimpleNamespace(st_dev=202,st_ino=2)
            @contextmanager
            def synthetic_parent(path, expected):
                fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    yield fd
                finally:
                    os.close(fd)
            # The real source gate demands physically distinct volumes;
            # this synthetic test simulates that condition without real archives.
            with patch.object(m, "_private_destination", side_effect=[first,second]), \
                 patch.object(m, "_opened_parent", side_effect=synthetic_parent):
                receipt=m.save_private_original(raw,a,b)
            self.assertEqual(a.read_bytes(),raw)
            self.assertEqual(b.read_bytes(),raw)
            self.assertEqual(receipt["raw_sha256"],sha256(raw).hexdigest())
            self.assertEqual(receipt["scored_trials"],0)
            self.assertFalse(receipt["scoring_authorized"])
            self.assertFalse(receipt["independent_private_raw_custody_verified"])
            self.assertNotIn(str(a),json.dumps(receipt))
            self.assertNotIn("synthetic_example_content",json.dumps(receipt))
            with self.assertRaises(ValueError):
                m._private_destination(a)  # no overwrite/rerun

    def test_unsafe_destination_parent_acl_symlink_public_or_same_mount(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            priv=root/"private";priv.mkdir(mode=0o700)
            a=priv/"new-original.bin"
            self.assertIsNotNone(m._private_destination(a))
            priv.chmod(0o755)
            with self.assertRaises(ValueError):
                m._private_destination(a)
            priv.chmod(0o700)
            loop=root/"PRIVATE_SYMLINK_LOOP"
            loop.symlink_to(loop,target_is_directory=True)
            with self.assertRaises(ValueError):
                m._private_destination(loop/"orig")
            linked=root/"linked"
            linked.symlink_to(priv,target_is_directory=True)
            with self.assertRaises(ValueError):
                m._private_destination(linked/"orig")
            with patch.object(m,"ROOT",priv):
                with self.assertRaises(ValueError):
                    m._private_destination(a)
            a.write_bytes(b"existing")
            with self.assertRaises(ValueError):
                m._private_destination(a)
            b=priv/"another"
            with self.assertRaises(ValueError):
                m.save_private_original(b"synthetic",a,b)

    def test_intermediate_parent_symlink_swap_does_not_write_to_fake_public_repo(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            original_parent=root/"private-ancestor"
            public_parent=root/"fake-public-repo"
            original_parent.mkdir(mode=0o700)
            public_parent.mkdir(mode=0o700)
            (original_parent/"owner").mkdir(mode=0o700)
            (public_parent/"owner").mkdir(mode=0o700)
            original=original_parent/"owner"/"SYNTHETIC_ONLY.bin"
            expected=m._private_destination(original)
            # Replace an ancestor after the original private-directory stat.
            original_parent.rename(root/"private-moved")
            original_parent.symlink_to(public_parent,target_is_directory=True)
            with self.assertRaises(ValueError):
                with m._opened_parent(original,expected) as pinned:
                    m._write_exclusive(original.name,b"synthetic",pinned)
            self.assertFalse((public_parent/"owner"/original.name).exists())
            self.assertFalse((root/"private-moved"/"owner"/original.name).exists())

    def test_group_or_world_writable_ancestor_is_rejected_before_write(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            unsafe=root/"UNTRUSTED_ANCESTOR"
            unsafe.mkdir(mode=0o700)
            private=unsafe/"owner-only"
            private.mkdir(mode=0o700)
            target=private/"synthetic.bin"
            expected=m._private_destination(target)
            unsafe.chmod(0o777)
            with self.assertRaises(ValueError):
                with m._opened_parent(target,expected) as pinned:
                    m._write_exclusive(target.name,b"synthetic",pinned)
            self.assertFalse(target.exists())

    def test_direct_script_execution_can_find_scripts_without_running_generator(self):
        # No source generation: execute only module definitions in a clean
        # subprocess and test import resolution, never main() or any scorer.
        probe = (
            "import runpy,importlib.util;"
            "runpy.run_path('scripts/capture_opportunity_private_original.py',"
            "run_name='synthetic_import_probe');"
            "assert importlib.util.find_spec('scripts.verify_opportunity_legacy_sources')"
        )
        result=subprocess.run([sys.executable,"-c",probe],cwd=m.ROOT,
                              capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0)
        self.assertEqual(result.stdout,"")

    def test_cli_error_never_echoes_private_paths_or_captures(self):
        with redirect_stdout(StringIO()) as stdout, redirect_stderr(StringIO()) as stderr:
            result=m.main(["--capture-before-scoring",
                           "--primary","/tmp/PRIVATE_FILENAME_001",
                           "--secondary","/tmp/other",
                           "/PRIVATE_UNKNOWN_ARGUMENT"])
        self.assertEqual(result,2)
        self.assertEqual(stdout.getvalue(),"")
        self.assertNotIn("PRIVATE_",stderr.getvalue())
        self.assertNotIn("/tmp",stderr.getvalue())
        self.assertNotIn("Traceback",stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

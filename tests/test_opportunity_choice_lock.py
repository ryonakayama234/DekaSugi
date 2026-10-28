"""Synthetic-only negative controls for Issue #68 public pretrial original custody."""
from __future__ import annotations

from copy import deepcopy
import io
import stat
import zipfile
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import verify_opportunity_choice_lock as m


def fake_payload() -> dict:
    return {
        "schema_version": "opportunity-pretrial-public-decisions-v1",
        "method": "OPPORTUNITY-001-PILOT-V1", "phase": "FRESH_TRAIN_ONLY",
        "source_manifest_sha256": m.SOURCE_SHA256,
        "skill_body_sha256": m.SKILL_SHA256,
        "policy_snapshot_sha256": dict(m.SNAPSHOTS),
        "decisions": [
            {"task_id": "t-" + f"{i:064x}", "choices": {
                arm: {"action": "OFF", "reason": "insufficient_on_votes"}
                for arm in m.SNAPSHOTS
            }} for i in range(64)
        ],
        "paired_trials_executed": 0,
        "dev_or_final_evaluated": False,
    }


def origin() -> tuple[dict, dict, dict]:
    return (
        {"id": m.ORIGIN_RUN, "head_sha": m.ORIGIN_COMMIT, "head_branch": "main",
         "event": "push", "status": "completed", "conclusion": "success",
         "created_at": "2026-10-28T08:00:00Z",
         "updated_at": "2026-10-28T08:02:00Z"},
        {"id": m.ORIGIN_JOB, "run_id": m.ORIGIN_RUN, "head_sha": m.ORIGIN_COMMIT,
         "status": "completed", "conclusion": "success"},
        {"id": m.ORIGIN_ARTIFACT, "name": m.ORIGIN_ARTIFACT_NAME,
         "expired": False, "created_at": "2026-10-28T08:02:00Z",
         "expires_at": "2027-01-26T08:02:00Z",
         "workflow_run": {"id": m.ORIGIN_RUN, "head_sha": m.ORIGIN_COMMIT}},
    )


class ChoiceCustodyTests(unittest.TestCase):
    def check_fixture(self, obj: dict) -> None:
        raw = m.canonical(obj)
        with patch.object(m, "ORIGINAL_MEMBER_SHA256", m.sha(raw)), patch.object(
            m, "DECISION_SHA256", m.sha(m.canonical(fake_payload()))
        ):
            m.validate_payload(raw)

    def test_fixture_is_accepted_only_when_byte_and_logical_hash_agree(self):
        self.check_fixture(fake_payload())

    def test_missing_duplicate_extra_or_reordered_task(self):
        cases = [
            lambda p: p["decisions"].pop(),
            lambda p: p["decisions"].append(deepcopy(p["decisions"][0])),
            lambda p: p["decisions"].__setitem__(1, deepcopy(p["decisions"][0])),
            lambda p: p["decisions"].reverse(),
        ]
        for mutation in cases:
            obj = fake_payload()
            mutation(obj)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.check_fixture(obj)

    def test_policy_and_decision_drift(self):
        cases = [
            lambda p: p["policy_snapshot_sha256"].update(B1="f" * 64),
            lambda p: p["decisions"][0]["choices"].pop("B1"),
            lambda p: p["decisions"][0]["choices"].update(B4={"action": "OFF", "reason": "insufficient_support"}),
            lambda p: p["decisions"][0]["choices"]["B1"].update(action="UNDECIDED"),
            lambda p: p["decisions"][0]["choices"]["B1"].update(reason=""),
            lambda p: p["decisions"][0]["choices"]["B1"].update(action="ON"),
            lambda p: p["source_manifest_sha256"].__class__,
        ]
        for mutate in cases[:-1]:
            obj = fake_payload()
            mutate(obj)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                self.check_fixture(obj)
        obj = fake_payload()
        obj["source_manifest_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            self.check_fixture(obj)

    def test_private_field_injection_and_permission_mutation(self):
        for label, value in [
            ("private_audit", {"input": "secret"}),
            ("family", "secret"), ("seed", 123), ("source_record_id", "secret"),
            ("score", 1), ("on_off_outcomes", {"ON": True}),
        ]:
            obj = fake_payload()
            obj["decisions"][0]["choices"]["B2"][label] = value
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.check_fixture(obj)
        for value in (True, 1, -1):
            obj = fake_payload()
            obj["paired_trials_executed"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check_fixture(obj)
        obj = fake_payload()
        obj["dev_or_final_evaluated"] = True
        with self.assertRaises(ValueError):
            self.check_fixture(obj)

    def test_strict_json_rejects_duplicates_and_nan(self):
        for b in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'\xff',
                  b'x' * (m.MAX_PUBLIC_BYTES + 1)):
            with self.subTest(value=b[:30]), self.assertRaises(ValueError):
                m.parse_strict(b)

    def test_raw_bytes_cannot_be_replaced_by_semantic_reformat(self):
        obj = fake_payload()
        original = m.canonical(obj)
        reformatted = json.dumps(obj, indent=2).encode() + b"\n"
        self.assertEqual(m.sha(m.canonical(m.parse_strict(original))),
                         m.sha(m.canonical(m.parse_strict(reformatted))))
        self.assertNotEqual(m.sha(original), m.sha(reformatted))
        with patch.object(m, "ORIGINAL_MEMBER_SHA256", m.sha(original)), patch.object(
            m, "DECISION_SHA256", m.sha(original)
        ):
            with self.assertRaisesRegex(ValueError, "raw bytes mismatch"):
                m.validate_payload(reformatted)

    def test_origin_mismatch_and_initial_run_substitution(self):
        r, j, a = origin()
        self.assertEqual(m.validate_origin(r, j, a)["workflow_run_id"], m.ORIGIN_RUN)
        cases = [
            ("run", "id", 40649096613), ("run", "head_sha", "0" * 40),
            ("run", "head_branch", "feature"), ("run", "event", "workflow_dispatch"),
            ("job", "id", 0), ("job", "conclusion", "failure"),
            ("artifact", "id", 0), ("artifact", "expired", True),
            ("artifact", "name", "wrong"),
        ]
        for part, field, value in cases:
            data = [deepcopy(r), deepcopy(j), deepcopy(a)]
            data[{"run": 0, "job": 1, "artifact": 2}[part]][field] = value
            with self.subTest(part=part, field=field), self.assertRaises(ValueError):
                m.validate_origin(*data)

    def test_capture_byte_preservation_and_not_authorized_lock(self):
        obj = fake_payload()
        # Use fixture-derived digests only within this synthetic test.
        raw = json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False).encode() + b"\n"
        r, j, a = origin()
        with TemporaryDirectory() as td, patch.object(m, "ORIGINAL_MEMBER_SHA256", m.sha(raw)), patch.object(
            m, "DECISION_SHA256", m.sha(m.canonical(obj))
        ), patch.object(m, "PUBLIC_PATH", Path(td)/"copy.json"), patch.object(
            m, "LOCK_PATH", Path(td)/"lock.json"
        ):
            paths = []
            for name, data in [("OPPORTUNITY-001-pretrial-public.json", raw),
                               ("run.json", m.canonical(r)), ("job.json", m.canonical(j)),
                               ("artifact.json", m.canonical(a))]:
                p = Path(td)/name
                p.write_bytes(data)
                paths.append(p)
            m.capture(*paths)
            self.assertEqual(m.PUBLIC_PATH.read_bytes(), raw)
            self.assertFalse(m.verify_custody(raw, m.LOCK_PATH.read_bytes())[
                "new_train_pilot_scoring_permitted"])
            with self.assertRaises(ValueError):
                m.save_exact(m.PUBLIC_PATH, raw + b"\n")
            lock = json.loads(m.LOCK_PATH.read_bytes())
            lock["new_train_pilot_scoring_permitted"] = True
            with self.assertRaises(ValueError):
                m.verify_custody(raw, m.canonical(lock))

    def test_original_zip_member_is_unique_regular_and_bounded(self):
        obj = fake_payload()
        raw = m.canonical(obj)
        def archive(entries):
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as z:
                for name, payload, mode in entries:
                    info = zipfile.ZipInfo(name)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = mode << 16
                    z.writestr(info, payload)
            return buffer.getvalue()
        regular = stat.S_IFREG | 0o644
        with patch.object(m, "ORIGINAL_MEMBER_SHA256", m.sha(raw)), patch.object(
            m, "DECISION_SHA256", m.sha(raw)
        ):
            good = archive([(m.ORIGIN_MEMBER, raw, regular)])
            receipt = m.inspect_original_zip(good)
            self.assertEqual(receipt["member_raw_sha256"], m.sha(raw))
            invalid = [
                archive([(m.ORIGIN_MEMBER, raw, regular), ("secret-audit.json", b"hidden", regular)]),
                archive([(m.ORIGIN_MEMBER, raw, regular), (m.ORIGIN_MEMBER, raw, regular)]),
                archive([("../" + m.ORIGIN_MEMBER, raw, regular)]),
                archive([(m.ORIGIN_MEMBER, raw, stat.S_IFLNK | 0o777)]),
                archive([(m.ORIGIN_MEMBER, raw + b"x" * m.MAX_PUBLIC_BYTES, regular)]),
                b"not a zip",
            ]
            for altered in invalid:
                with self.subTest(archive_size=len(altered)), self.assertRaises(ValueError):
                    m.inspect_original_zip(altered)


    def test_real_saved_public_original_if_available(self):
        if not m.PUBLIC_PATH.exists() or not m.LOCK_PATH.exists():
            self.skipTest("Official artifact not yet retained by one-shot workflow")
        raw = m.PUBLIC_PATH.read_bytes()
        lock = m.LOCK_PATH.read_bytes()
        verified = m.verify_custody(raw, lock)
        self.assertEqual(verified["decision_count"], 192)
        self.assertEqual(m.sha(raw), m.ORIGINAL_MEMBER_SHA256)


if __name__ == "__main__":
    unittest.main()

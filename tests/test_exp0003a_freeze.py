"""EXP-0003A PR4 source/dataset/policy preflight; no DEV/FINAL scoring."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from packages.exp0003a import digest, generate_train
from packages.exp0003a.pr3 import generate_dream_pool
from packages.exp0003a.freeze import (
    ALPHABETS, COUNTS, FREEZE_FILE, MASTERS, SCHEMA, SOURCE_FILES,
    SPLIT_ORDER, dataset_hashes, freeze_payload, generate_partition,
    preflight_record, source_hashes, verify_frozen,
)


class FreezeV1Tests(unittest.TestCase):
    def test_generator_independent_train_dream_equivalence(self):
        train = generate_train()
        self.assertEqual(train, generate_partition("train"))
        self.assertEqual(generate_dream_pool(train), generate_partition("dream"))
        self.assertEqual(len(generate_partition("dev")), 64)
        self.assertEqual(len(generate_partition("final")), 128)
        self.assertEqual(ALPHABETS["dev"], "klmnoPQRST")
        self.assertEqual(ALPHABETS["final"], "uvwxyUVWXY")
        self.assertEqual(MASTERS["final"], 310000000)
        with self.assertRaisesRegex(ValueError, "Unregistered"):
            generate_partition("other")

    def test_cross_split_counts_collision_and_raw_hashes(self):
        data = dataset_hashes()
        self.assertEqual(tuple(data["split_order"]), SPLIT_ORDER)
        self.assertEqual(tuple(data["partition_counts"][p] for p in SPLIT_ORDER),
                         (160, 512, 64, 128))
        self.assertEqual(data["all_task_count"], 864)
        self.assertEqual(data["all_seed_count"], 2592)
        self.assertFalse(data["dev_or_final_scored"])
        self.assertFalse(data["raw_dev_or_final_rows_exported"])
        self.assertEqual(len(set(data["split_sha256"].values())), 4)
        self.assertTrue(all(len(x) == 64 for x in data["split_sha256"].values()))
        self.assertEqual(data, dataset_hashes())
        all_seeds = [s for split in SPLIT_ORDER for case in generate_partition(split)
                     for s in case.seeds]
        self.assertEqual(len(all_seeds), len(set(all_seeds)))
        all_ids = [c.task.task_id for split in SPLIT_ORDER
                   for c in generate_partition(split)]
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertEqual(data["dream_pool_public_input_sha256"], digest([
            c.task.task_id[2:] for c in generate_partition("dream")
        ]))

    def test_source_git_blobs_are_byte_exact(self):
        report = source_hashes()
        self.assertEqual(set(report["files"]), set(SOURCE_FILES))
        self.assertTrue(all(len(value["git_blob_sha1"]) == 40 and
                            len(value["raw_sha256"]) == 64
                            for value in report["files"].values()))
        self.assertEqual(report, source_hashes())
        self.assertEqual(len(report["git_blob_manifest_sha256"]), 64)

    def test_preflight_learns_only_train_dream_and_reproducible_snapshots(self):
        record = preflight_record()
        self.assertEqual(record["schema_version"], SCHEMA)
        self.assertEqual(record["plan"], "EXP-0003A-PLAN-V1")
        self.assertFalse(record["holdout_scoring_permitted"])
        self.assertFalse(record["registry_promotion_permitted"])
        self.assertEqual(record["status"], "SOURCE_DATA_TRAIN_DREAM_PREDEV_LOCK")
        self.assertEqual(record["split_data"]["all_task_count"], 864)
        self.assertEqual(record["policy"]["train_cost_positive_count"], 20)
        self.assertEqual(record["policy"]["snapshot_sha256"], {
            "B1": "3b4fc00f8ad0fe2f1cc0978886d7bc7a6285ed002c842ceeb0106fd51ee5afd4",
            "B2": "01d5595e1b4c32d200e2734630f38a848e77a64f356741445e011865834f5af7",
            "B3": "a6d46ab5dd697e8e90789693fdd3bd67bbca445ec07bc8b119401e1c0cf1e210",
        })
        self.assertEqual(record["freeze_payload_sha256"],
                         digest({k: v for k, v in record.items()
                                 if k != "freeze_payload_sha256"}))
        self.assertEqual(len(record["policy"]["b2_ordered_selected_pool_ids"]), 96)
        self.assertEqual(len(record["policy"]["b3_ordered_selected_pool_ids"]), 96)
        self.assertNotIn("audit", record["policy"])
        self.assertNotIn("private_example", json.dumps(record))

    def test_frozen_verifier_fails_closed_even_if_modified_is_rehashed(self):
        record = preflight_record()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "freeze.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            self.assertEqual(verify_frozen(path=path), record)
            altered = json.loads(json.dumps(record))
            altered["policy"]["b3_ordered_selected_pool_ids"][0] = "dream-f00-i999"
            altered["freeze_payload_sha256"] = digest({
                k: v for k, v in altered.items() if k != "freeze_payload_sha256"
            })
            path.write_text(json.dumps(altered), encoding="utf-8")
            with patch("packages.exp0003a.freeze.preflight_record", return_value=record):
                with self.assertRaisesRegex(ValueError, "Freeze drift"):
                    verify_frozen(path=path)
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                verify_frozen(path=path)

    def test_source_guard_precedes_any_executable_regeneration(self):
        record = preflight_record()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "freeze.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            # A changed generator, DSL, learning or freeze source MUST stop
            # before the first call to preflight_record/run_train_dream.
            with patch("packages.exp0003a.freeze.source_hashes",
                       return_value={"files": {}, "git_blob_manifest_sha256": "0" * 64}), \
                 patch("packages.exp0003a.freeze.preflight_record",
                       side_effect=AssertionError("unreviewed code executed")) as rerun:
                with self.assertRaisesRegex(ValueError,
                                            "source hash mismatch before regeneration"):
                    verify_frozen(path=path)
                rerun.assert_not_called()

            # A forged source manifest seal must be rejected without either
            # source scan or generator invocation.
            tampered = json.loads(json.dumps(record))
            tampered["policy"]["top_skill_id"] = "forged"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            with patch("packages.exp0003a.freeze.source_hashes",
                       side_effect=AssertionError("tampered manifest reached source")), \
                 patch("packages.exp0003a.freeze.preflight_record",
                       side_effect=AssertionError("tampered manifest reached generator")):
                with self.assertRaisesRegex(ValueError, "corrupt frozen manifest seal"):
                    verify_frozen(path=path)

            # Runtime guard precedes source access and scoring too.
            changed_runtime = json.loads(json.dumps(record))
            changed_runtime["python_version"] = "0.0"
            changed_runtime["freeze_payload_sha256"] = digest({
                k: v for k, v in changed_runtime.items()
                if k != "freeze_payload_sha256"
            })
            path.write_text(json.dumps(changed_runtime), encoding="utf-8")
            with patch("packages.exp0003a.freeze.source_hashes",
                       side_effect=AssertionError("wrong runtime reached source")), \
                 patch("packages.exp0003a.freeze.preflight_record",
                       side_effect=AssertionError("wrong runtime reached generator")):
                with self.assertRaisesRegex(ValueError, "Python runtime"):
                    verify_frozen(path=path)

    def test_committed_freeze_required_and_exact(self):
        self.assertTrue(FREEZE_FILE.is_file(), "Committed freeze is mandatory")
        frozen = verify_frozen()
        self.assertEqual(frozen, preflight_record())


if __name__ == "__main__":
    unittest.main()

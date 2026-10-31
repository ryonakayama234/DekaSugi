"""Opt-in smoke benchmark is allowlisted; no unknown test discovery."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]

class ResourceSmokeTests(unittest.TestCase):
    def test_bounded_synthetic_linux_preflight_subprocess(self):
        completed=subprocess.run([sys.executable,"-m","scripts.run_coev_f0c_resource_preflight",
                                  "--mode","smoke"],cwd=ROOT,text=True,capture_output=True,
                                  timeout=40,check=True)
        data=json.loads(completed.stdout)
        self.assertEqual(data["status"],"ENGINEERING_ONLY_UNSCORED")
        self.assertEqual(data["catalog_classes"],895)
        self.assertEqual(data["task_count_per_arm"],8)
        self.assertFalse(data["scientific_source_or_score_used"])
        self.assertFalse(data["formal_train_eligible"])
        for key in ("cold_catalog","warm_cached_catalog","train_random","train_active","candidate_rank"):
            self.assertGreaterEqual(data[key]["cpu_seconds"],0)
            self.assertGreater(data[key]["process_vm_hwm_kib"],0)

    def test_full_public_256_task_benchmark_is_bounded(self):
        # 256 is a public, invented-only TRAIN fixture, NOT registered science.
        # Print machine-readable metrics into exact-head safe CI logs.
        finished=subprocess.run([sys.executable,"-m","scripts.run_coev_f0c_resource_preflight",
                                 "--mode","full"],cwd=ROOT,text=True,capture_output=True,
                                 timeout=150,check=True)
        results=json.loads(finished.stdout)
        self.assertEqual(results["task_count_per_arm"],256)
        self.assertEqual(results["ranking_repeats"],32)
        self.assertFalse(results["scientific_source_or_score_used"])
        self.assertFalse(results["formal_train_eligible"])
        self.assertEqual(results["catalog_classes"],895)
        self.assertTrue(all(results[name]["wall_seconds"]>=0 for name in (
            "cold_catalog","warm_cached_catalog","train_random","train_active","candidate_rank")))
        print("F0C_FULL_PUBLIC_BENCHMARK_JSON="+json.dumps(results,sort_keys=True),flush=True)

if __name__=="__main__": unittest.main()

"""PR5 regression: exclusively synthetic or TRAIN fixtures; NEVER DEV/FINAL scoring."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from packages.exp0003a import FAMILIES, generate_train
from packages.exp0003a.pr3 import Decision
from packages.exp0003a_dev import (
    ARMS, FrozenAssets, _rehydrate_skill, evaluate_case, load_frozen_assets,
    require_reviewed_main_push, run_dev, summarize, validate_dev_cases,
    write_once,
)
from packages.protocol import Call, Input, program_hash
from packages.learning import SkillCandidate


def known_safe_train_skill():
    body = Call("lower", Call("trim", Input()))
    return SkillCandidate(
        skill_id="skill_" + program_hash(body)[:16], body_ast=body,
        body_hash=program_hash(body), dependencies=("lower", "trim"),
        provenance=("train-a", "train-b"), occurrences=2,
    )


class DevEngineeringEvaluatorTests(TestCase):
    def test_main_gate_denies_local_or_pr(self):
        for env in (
            {},
            {"GITHUB_EVENT_NAME": "pull_request", "GITHUB_REF": "refs/heads/main",
             "EXP0003A_DEV_APPROVED": "reviewed-main-only"},
            {"GITHUB_EVENT_NAME": "push", "GITHUB_REF": "refs/heads/main"},
        ):
            with self.subTest(env=env):
                with self.assertRaises(PermissionError):
                    require_reviewed_main_push(env)

    def test_load_freeze_is_first_and_fails_closed(self):
        with patch("packages.exp0003a_dev.verify_frozen",
                   side_effect=ValueError("tampered source")) as check, patch(
                   "packages.exp0003a_dev.run_train_dream") as learner:
            with self.assertRaisesRegex(ValueError, "tampered source"):
                load_frozen_assets()
            check.assert_called_once()
            learner.assert_not_called()

    def test_run_rejects_before_dev_generation(self):
        with patch("packages.exp0003a_dev.require_reviewed_main_push",
                   side_effect=PermissionError("review pending")), patch(
                   "packages.exp0003a_dev.generate_partition") as generator:
            with self.assertRaises(PermissionError):
                run_dev()
            generator.assert_not_called()

    def test_frozen_assets_validation_precedes_partition(self):
        with patch("packages.exp0003a_dev.require_reviewed_main_push"), patch(
                "packages.exp0003a_dev.load_frozen_assets",
                side_effect=ValueError("snapshot mismatch")), patch(
                "packages.exp0003a_dev.generate_partition") as generator:
            with self.assertRaisesRegex(ValueError, "snapshot mismatch"):
                run_dev()
            generator.assert_not_called()

    def test_dev_manifest_refuses_train_fixture(self):
        train = generate_train()
        with self.assertRaises(ValueError):
            validate_dev_cases(train[:64], {"split_data": {}})

    def test_invalid_skill_body_rejected(self):
        raw = known_safe_train_skill().to_dict()
        raw["body_hash"] = "0" * 64
        with self.assertRaises(ValueError):
            _rehydrate_skill(raw)

    def test_chooser_receives_public_task_only(self):
        case = generate_train()[0]  # TRAIN fixture, not DEV/FINAL
        skill = known_safe_train_skill()
        assets = FrozenAssets({}, {a: object() for a in ARMS[1:]},
                              {a: "0" * 64 for a in ARMS[1:]}, skill, {})
        decision = Decision("OFF", "test", (), 0.0, 0, 0, 0.0)
        def audited(_task, _audit, _registry, _learned):
            e = {
                "search": {"status": "not_found", "tested_candidates": 3},
                "meter": {"primitive_invocations": 2, "by_op": {}},
                "audit_correct": False,
                "audit_invalid_solved": False,
                "selected_ast": None,
            }
            return e, 3, 2, False, False, 0.1, 0.2, 0.0, 0.0
        with patch("packages.exp0003a_dev.choose", return_value=decision) as choose, patch(
                "packages.exp0003a_dev._audited_trial", side_effect=audited) as trial:
            result = evaluate_case(case, assets)
        self.assertEqual(set(result["arms"]), set(ARMS))
        self.assertEqual(choose.call_count, 3)
        self.assertEqual(trial.call_count, 4)
        for call in choose.call_args_list:
            self.assertIs(call.args[0], case.task)
            self.assertEqual(len(call.args), 2)
        for arm in ARMS:
            self.assertFalse(result["arms"][arm]["audited_correct"])
            self.assertEqual(result["arms"][arm]["primitive_invocations"], 2)

    def test_engineering_summary_paired_and_ood(self):
        # Explicit TRAIN-only synthetic aggregates with 8 rows per conceptual family.
        template = generate_train()
        cases = tuple(replace(template[i], family=FAMILIES[i // 8])
                      for i in range(64))
        rows = []
        for i, case in enumerate(cases):
            arms = {}
            for arm in ARMS:
                arms[arm] = {
                    "audited_correct": i % 2 == 0, "false_solved": False,
                    "tested_candidates": 4, "primitive_invocations":
                        (8 if arm == "B2" else 7),
                    "decision": "OFF", "search_cpu_ms": 0.1,
                    "audit_cpu_ms": 0.0, "search_wall_ms": 0.1,
                    "audit_wall_ms": 0.0,
                }
            rows.append({"task_id": case.task.task_id, "arms": arms})
        out = summarize(rows, cases)
        self.assertEqual(out["task_count"], 64)
        self.assertEqual(out["arm_totals"]["B0"]["audited_correct"], 32)
        self.assertEqual(out["paired_B2_minus_B3"]["primitive_invocations"], 64)
        self.assertEqual(out["paired_B2_minus_B3"]["primitive_improvements"], 64)
        self.assertEqual(out["paired_B2_minus_B3"]["bootstrap_rounds"], 1000)

    def test_reject_incomplete_rows(self):
        with self.assertRaisesRegex(ValueError, "unpaired/incomplete"):
            summarize([], ())

    def test_artifact_write_once(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "report.json"
            one = write_once(p, {"phase": "TRAIN_FIXTURE", "x": 1})
            self.assertEqual(len(one), 64)
            with self.assertRaises(FileExistsError):
                write_once(p, {"phase": "TRAIN_FIXTURE", "x": 2})
            self.assertIn('"x": 1', p.read_text())

"""Synthetic-only safety controls for real OPPORTUNITY activation wrapper.

Never invoke the actual source, archived original, old DEV/FINAL, or any
real bounded_synthesize / _audited_trial.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest

from scripts import opportunity_approved_activation as m
from scripts import opportunity_real_pair_engine as engine
from scripts import opportunity_one_shot_runner as runner


class ApprovedActivationSyntheticTests(unittest.TestCase):
    def test_scoped_flags_restore_false_on_success_and_failure(self):
        self.assertIs(engine.SCORING_ACTIVATED, False)
        self.assertIs(runner.ONE_SHOT_ACTIVATED, False)
        with m._scoped_engine_activation(runner, engine):
            self.assertIs(engine.SCORING_ACTIVATED, True)
            self.assertIs(runner.ONE_SHOT_ACTIVATED, True)
        self.assertIs(engine.SCORING_ACTIVATED, False)
        self.assertIs(runner.ONE_SHOT_ACTIVATED, False)
        with self.assertRaisesRegex(RuntimeError, "SYNTHETIC"):
            with m._scoped_engine_activation(runner, engine):
                raise RuntimeError("SYNTHETIC")
        self.assertIs(engine.SCORING_ACTIVATED, False)
        self.assertIs(runner.ONE_SHOT_ACTIVATED, False)

    def test_synthetic_interrupt_during_context_entry_restores_both_flags(self):
        # Synthetic flag holders only; never call the actual scorer or runner.
        # Simulate an interrupt immediately AFTER each activation assignment.
        class InterruptAfterTrue(SimpleNamespace):
            def __setattr__(self, name, value):
                super().__setattr__(name, value)
                if value is True:
                    raise KeyboardInterrupt("SYNTHETIC_ENTRY_INTERRUPT")

        for interrupted_side in ("runner", "engine"):
            with self.subTest(interrupted_side=interrupted_side):
                fake_runner = (InterruptAfterTrue(ONE_SHOT_ACTIVATED=False)
                               if interrupted_side == "runner" else
                               SimpleNamespace(ONE_SHOT_ACTIVATED=False))
                fake_engine = (InterruptAfterTrue(SCORING_ACTIVATED=False)
                               if interrupted_side == "engine" else
                               SimpleNamespace(SCORING_ACTIVATED=False))
                with self.assertRaisesRegex(
                        KeyboardInterrupt, "SYNTHETIC_ENTRY_INTERRUPT"):
                    with m._scoped_engine_activation(fake_runner, fake_engine):
                        self.fail("SYNTHETIC: context body must not run")
                self.assertIs(fake_runner.ONE_SHOT_ACTIVATED, False)
                self.assertIs(fake_engine.SCORING_ACTIVATED, False)

    def test_missing_external_approval_stops_before_project_runner(self):
        for custody, never in ((False, False), (True, False), (False, True)):
            with patch.object(runner, "_require_checkout",
                              side_effect=AssertionError("must not reach")):
                with self.assertRaises(ValueError):
                    m.start_owner_private_once(Path("/SYNTHETIC"),"0"*64,"a"*40,
                                               custody_confirmed=custody,
                                               never_retry_confirmed=never)

    def test_exact_checkout_verified_before_scoped_flags(self):
        seen=[]
        def fake_checkout(_):
            seen.append(("preflight", runner.ONE_SHOT_ACTIVATED,
                         engine.SCORING_ACTIVATED))
        def fake_run(*args):
            seen.append(("run", runner.ONE_SHOT_ACTIVATED,
                         engine.SCORING_ACTIVATED))
            return {"status":"SYNTHETIC_ONLY","paired_count":0}
        with patch.object(runner,"_require_checkout",side_effect=fake_checkout),\
             patch.object(runner,"run_private_once",side_effect=fake_run):
            result=m.start_owner_private_once(Path("/SYNTHETIC"),
                                              "0"*64,"a"*40,
                                              custody_confirmed=True,
                                              never_retry_confirmed=True)
        self.assertEqual(result["status"],"SYNTHETIC_ONLY")
        self.assertEqual(seen,[("preflight",False,False),("run",True,True)])
        self.assertIs(runner.ONE_SHOT_ACTIVATED,False)
        self.assertIs(engine.SCORING_ACTIVATED,False)

    def test_synthetic_failure_still_clears_flags(self):
        with patch.object(runner,"_require_checkout",return_value=None),\
             patch.object(runner,"run_private_once",
                          side_effect=RuntimeError("SYNTHETIC_ABORT")):
            with self.assertRaises(RuntimeError):
                m.start_owner_private_once(Path("/SYNTHETIC"),
                                           "0"*64,"a"*40,
                                           custody_confirmed=True,
                                           never_retry_confirmed=True)
        self.assertIs(runner.ONE_SHOT_ACTIVATED,False)
        self.assertIs(engine.SCORING_ACTIVATED,False)

    def test_default_both_engine_flags_are_hard_off(self):
        self.assertIs(runner.ONE_SHOT_ACTIVATED,False)
        self.assertIs(engine.SCORING_ACTIVATED,False)


if __name__ == "__main__":
    unittest.main()

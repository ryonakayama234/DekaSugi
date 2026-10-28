"""OPPORTUNITY-001: actual canonical OFF/ON pair engine, NOT activated.

The functions below implement the real call graph but there is NO approved
scoring CLI or workflow. A source-first one-shot activation requires separate
independent review and genuine restricted original custody, neither provided
by this module. Every CI test uses invented fake TaskSpec/tuples only.
NEVER import old holdout generators or score historical DEV/FINAL.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
FRESH_METHOD = "OPPORTUNITY-001-PILOT-V1"
LOCKED_THIRD_COMMITMENTS = "fd4a1afd1eae84026a526d82a75cec13107dfd394f86d166c7efca4763a52eaa"
LOCKED_CHOICES_RAW = "1d08e6c1518d6730e75bfaf3033a00884f7517a7d91c98a5dfff75192aabc433"
LOCKED_SKILL = "8fe1361cb5014f8503e4a57392e45f4fc7607e788fdd598f66668fbc11338eff"
# This remains False in source: separate reviewed activation is required.
SCORING_ACTIVATED = False


def _canonical(x: object) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _strict_pairs(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate private JSON key")
        out[key] = value
    return out


def _reject_numeric(value: str) -> None:
    raise ValueError("invalid numeric literal")


def _exact(obj: object, keys: set[str]) -> dict:
    if type(obj) is not dict or set(obj) != keys:
        raise ValueError("unexpected or missing original archive fields")
    return obj


def validate_private_archive(raw: bytes, expected_raw_sha256: str,
                             original_public_choices: dict) -> tuple[dict, ...]:
    """Validate archived original *bytes* against prior independent digest.

    This is structural/cryptographic consistency, NOT proof of external
    access restrictions or independent archival lifecycle.
    """
    if (type(raw) is not bytes or not 0 < len(raw) <= 256_000
            or type(expected_raw_sha256) is not str
            or re.fullmatch(r"[0-9a-f]{64}", expected_raw_sha256) is None
            or sha256(raw).hexdigest() != expected_raw_sha256):
        raise ValueError("original raw archive digest invalid")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_pairs,
                         parse_constant=_reject_numeric)
    except (UnicodeError, TypeError):
        raise ValueError("invalid archive encoding") from None
    _exact(obj, {"schema_version", "method", "scope",
                 "public_manifest_sha256", "public_pretrial_original_raw_sha256",
                 "public_pretrial_decision_sha256", "third_audit_commitments_sha256",
                 "paired_trials_executed_at_capture", "records"})
    if (obj["schema_version"] != "opportunity-private-audit-original-v1"
            or obj["method"] != FRESH_METHOD
            or obj["scope"] != "fresh_train64_before_any_scored_trials"
            or obj["public_manifest_sha256"] !=
                "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85"
            or obj["public_pretrial_original_raw_sha256"] != LOCKED_CHOICES_RAW
            or obj["public_pretrial_decision_sha256"] !=
                "8a8625ed86e66b27bef8d09a023172d2adbc9ad0d42c155ab7f137097e2dccb2"
            or obj["third_audit_commitments_sha256"] != LOCKED_THIRD_COMMITMENTS
            or type(obj["paired_trials_executed_at_capture"]) is not int
            or obj["paired_trials_executed_at_capture"] != 0):
        raise ValueError("untrusted private original source or timing")
    choices = _exact(original_public_choices, {
        "schema_version", "method", "phase", "source_manifest_sha256",
        "skill_body_sha256", "policy_snapshot_sha256", "decisions",
        "paired_trials_executed", "dev_or_final_evaluated"})
    items = obj["records"]
    public_rows = choices["decisions"]
    if (type(items) is not list or len(items) != 64 or
            type(public_rows) is not list or len(public_rows) != 64):
        raise ValueError("wrong original 64-row cardinality")
    commitments = []
    seen_ids, seen_sources, seen_seeds = set(), set(), set()
    for row, public in zip(items, public_rows, strict=True):
        _exact(row, {"task_id", "third_audit", "source_record_id", "family", "seeds"})
        task_id = row["task_id"]
        if (type(task_id) is not str or re.fullmatch(r"t-[0-9a-f]{64}", task_id) is None
                or task_id in seen_ids or type(public) is not dict
                or public.get("task_id") != task_id):
            raise ValueError("private archive/public ID mismatched")
        seen_ids.add(task_id)
        audit = _exact(row["third_audit"], {"input", "output"})
        if any(type(v) is not str for v in audit.values()):
            raise ValueError("third-audit type invalid")
        if (type(row["source_record_id"]) is not str
                or row["source_record_id"] in seen_sources
                or type(row["family"]) is not str
                or type(row["seeds"]) is not list or len(row["seeds"]) != 3
                or any(type(seed) is not int or seed in seen_seeds
                       for seed in row["seeds"])):
            raise ValueError("private source, family, or seed drift")
        seen_sources.add(row["source_record_id"])
        seen_seeds.update(row["seeds"])
        commitments.append({"task_id": task_id,
                            "third_audit_sha256": sha256(_canonical(audit)).hexdigest()})
    if sha256(_canonical(commitments)).hexdigest() != LOCKED_THIRD_COMMITMENTS:
        raise ValueError("independent private third commitment drift")
    return tuple(items)


def assemble_audited_pair(task, private_audit, skill, policy_actions: dict,
                          third_audit_sha256: str, *,
                          registry_factory: Callable, register_skill: Callable,
                          validate_skill: Callable, audited_trial: Callable) -> dict:
    """The actual two-arm wiring. CI injects fake functions, never real search."""
    from packages.evaluation.opportunity_actual import public_redacted_pair
    if (type(policy_actions) is not dict or set(policy_actions) != {"B1", "B2", "B3"}
            or any(type(v) is not str or v not in ("ON", "OFF")
                   for v in policy_actions.values())
            or type(third_audit_sha256) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", third_audit_sha256)):
        raise ValueError("pretrial decisions / third audit digest invalid")
    if (skill.skill_id != "skill_8fe1361cb5014f85"
            or skill.body_hash != LOCKED_SKILL):
        raise ValueError("nonfrozen skill rejected")
    if not hasattr(task, "task_id") or not hasattr(task, "examples") or len(task.examples) != 2:
        raise ValueError("noncanonical public TaskSpec")
    if task.limits.max_ast_nodes != 4 or task.limits.max_candidates != 100:
        raise ValueError("public search budgets altered")
    validate_skill(skill, registry_factory())
    # Fresh canonical trusted registry per arm: never reuse a caller-supplied
    # mutable registry or its primitive callable closures.
    off_registry = registry_factory()
    off_result = audited_trial(task, private_audit, off_registry, {})
    on_base = registry_factory()
    on_registry = register_skill(skill, on_base)
    on_result = audited_trial(task, private_audit, on_registry, {skill.skill_id: skill})
    return public_redacted_pair(task.task_id, off_result, on_result,
                               policy_actions, third_audit_sha256)


def source_first_preflight():
    """Must be called BEFORE importing any project packages on private runner."""
    if any(n == "packages" or n.startswith("packages.") for n in sys.modules):
        raise ValueError("project imported before immutable source verification")
    from scripts.verify_opportunity_legacy_sources import verify_legacy_source_bytes
    historic = verify_legacy_source_bytes(ROOT)
    if (historic["verified_source_count"] != 14
            or historic["dev_or_final_generated"] is not False):
        raise ValueError("old frozen source check failed")
    from scripts.verify_opportunity_generator_lock import verify_generator_lock
    new = verify_generator_lock(ROOT)
    if (new["source_file_count"] != 9 or
            new["status"] != "source_identity_verified_not_scoring_authorized"):
        raise ValueError("new frozen pilot source mismatch")
    from scripts.verify_opportunity_choice_lock import (
        PUBLIC_PATH, LOCK_PATH, validate_payload, verify_custody)
    raw = PUBLIC_PATH.read_bytes()
    locked = verify_custody(raw, LOCK_PATH.read_bytes())
    if (sha256(raw).hexdigest() != LOCKED_CHOICES_RAW
            or locked["decision_count"] != 192
            or locked["new_train_pilot_scoring_permitted"] is not False):
        raise ValueError("official original pretrial decision drift")
    return validate_payload(raw)


def _unactivated_real_pair(task, audit, frozen_skill, actions, audit_sha):
    """Real evaluator bound to canonical components; NOT callable as a CLI."""
    from packages.exp0003a.pr3 import _audited_trial
    from packages.library import DEFAULT_PRIMITIVES, Registry
    from packages.learning import registry_with_skill, validate_skill
    return assemble_audited_pair(
        task, audit, frozen_skill, actions, audit_sha,
        registry_factory=lambda: Registry(DEFAULT_PRIMITIVES),
        register_skill=registry_with_skill,
        validate_skill=validate_skill, audited_trial=_audited_trial)


def main() -> int:
    # A future independently reviewed activation PR will supply source-first
    # private archive restoration, externally attested custody and a one-shot
    # first-run ledger. This main NEVER scores, even if given arguments.
    print(json.dumps({
        "schema_version": "opportunity-actual-pair-engine-v1",
        "status": "real_pair_engine_implemented_not_activated",
        "scoring_activated": SCORING_ACTIVATED,
        "paired_trials_executed": 0,
        "independent_private_custody_verified": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

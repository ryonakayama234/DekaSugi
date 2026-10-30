"""OPPORTUNITY-002 PR3: isolated invented-only C-G2 evidence and reachability audit.

This module has no imports of any DekaSugi production package, scorer, policy,
generator, historical archive, or real task. It cannot activate experiments.
Every public result is a synthetic engineering calibration, never ability proof.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
import re

SCHEMA = "opportunity2-audit-normalizer/1"
SOURCE_LOCK = "synthetic-opportunity2-cg2/1"
ACTIONS = ("OFF", "ON")
PRIMITIVES = ("trim", "lower", "upper")
MACRO = "synthetic_lower_trim"
PROFILES = ("current_v1", "toy_bias_v1")
OUTCOMES = (
    "public_found_audit_correct",
    "public_found_audit_incorrect",
    "public_not_found",
    "integrity_invalid",
    "not_observed",
)
ROOT_KEYS = frozenset((
    "schema_version", "evidence_class", "fixture_id", "source_lock",
    "public_examples", "audit_example", "budget", "comparison", "arms",
))
ARM_KEYS = frozenset((
    "status", "program", "selected_ast", "tested_candidates",
    "public_verifier_passed", "audit_correct_claim", "audit_output_claim",
    "trace_sha256", "primitive_calls", "by_op", "observed_at", "budget_id",
))


class EvidenceError(ValueError):
    """A hard-stop contradiction in the synthetic evidence contract."""


def _fail(code: str) -> None:
    raise EvidenceError(code)


def _exact(obj: object, keys: frozenset[str], code: str) -> dict:
    if type(obj) is not dict or set(obj) != keys:
        _fail(code)
    return obj


def _is_digest(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def canonical_digest(value: object) -> str:
    """Content digest only. Authenticity requires an OUT-OF-BAND pinned digest."""
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _example(obj: object, label: str) -> tuple[str, str]:
    item = _exact(obj, frozenset(("input", "output")), label + "_shape")
    if any(type(item[k]) is not str or len(item[k]) > 256
           for k in ("input", "output")):
        _fail(label + "_type")
    return (item["input"], item["output"])


def expand(program: tuple[str, ...]) -> tuple[str, ...]:
    """Operator sequence in execution order, inside -> outside."""
    if type(program) is not tuple:
        _fail("program_type")
    expanded: list[str] = []
    for op in program:
        if op == MACRO:
            expanded.extend(("trim", "lower"))
        elif type(op) is str and op in PRIMITIVES:
            expanded.append(op)
        else:
            _fail("operator_unknown")
    return tuple(expanded)


def apply(program: tuple[str, ...], value: str) -> str:
    if type(value) is not str:
        _fail("input_type")
    for op in expand(program):
        if op == "trim":
            value = value.strip()
        elif op == "lower":
            value = value.lower()
        elif op == "upper":
            value = value.upper()
    return value


def canonical_ast(program: tuple[str, ...]) -> dict:
    node: dict = {"node_kind": "input", "type": "String"}
    for op in program:
        if op not in PRIMITIVES + (MACRO,):
            _fail("ast_operator")
        node = {"node_kind": "call", "type": "String",
                "op_id": op, "children": [node]}
    return node


def candidates(profile: str, arm: str) -> tuple[tuple[str, ...], ...]:
    """Independent finite enumerator; no production synthesis imports.

    current_v1 models the exact PR2 synthetic BFS under a four-expanded-node
    cap, including Input. toy_bias_v1 changes first-solution order deliberately
    and is NOT a statement about the frozen DekaSugi searcher.
    """
    if type(profile) is not str or profile not in PROFILES or arm not in ACTIONS:
        _fail("profile_or_arm")
    if profile == "toy_bias_v1":
        return ((), ("lower",)) if arm == "OFF" else (("lower",), ())
    operators = PRIMITIVES if arm == "OFF" else PRIMITIVES + (MACRO,)
    layer: tuple[tuple[str, ...], ...] = ((),)
    eligible: list[tuple[str, ...]] = []
    for depth in range(1, 5):
        following: list[tuple[str, ...]] = []
        for p in layer:
            if 1 + len(expand(p)) <= 4:
                eligible.append(p)
            if depth < 4:
                following.extend(p + (op,) for op in operators)
        layer = tuple(following)
    return tuple(eligible)


def _replay(profile: str, arm: str, public: tuple[tuple[str, str], ...],
            audit: tuple[str, str] | None, budget: int) -> dict:
    """Reproduce FIRST public match, complete public-call meter and trace."""
    tested = 0
    by_op: dict[str, int] = {}
    trace = sha256()
    for program in candidates(profile, arm):
        if tested >= budget:
            return {"status": "budget_exhausted", "program": None,
                    "tested_candidates": tested, "trace_sha256": trace.hexdigest(),
                    "primitive_calls": sum(by_op.values()), "by_op": by_op,
                    "audit_correct_claim": None, "audit_output_claim": None}
        tested += 1
        trace.update(json.dumps(list(program), separators=(",", ":")).encode("ascii") + b"\n")
        primitive_ops = expand(program)
        for op in primitive_ops:
            by_op[op] = by_op.get(op, 0) + len(public)
        if all(apply(program, x) == y for x, y in public):
            output = None if audit is None else apply(program, audit[0])
            return {"status": "solved", "program": list(program),
                    "tested_candidates": tested, "trace_sha256": trace.hexdigest(),
                    "primitive_calls": sum(by_op.values()), "by_op": by_op,
                    "audit_correct_claim": None if audit is None else output == audit[1],
                    "audit_output_claim": output}
    return {"status": "not_found", "program": None, "tested_candidates": tested,
            "trace_sha256": trace.hexdigest(), "primitive_calls": sum(by_op.values()),
            "by_op": by_op, "audit_correct_claim": None, "audit_output_claim": None}


def _validate_arm(raw: object, arm: str, profile: str,
                  public: tuple[tuple[str, str], ...],
                  audit: tuple[str, str] | None, budget: int,
                  decided_at: int) -> tuple[str, int, str]:
    a = _exact(raw, ARM_KEYS, "arm_shape")
    if a["status"] not in ("solved", "not_found", "budget_exhausted"):
        _fail("search_status")
    if type(a["tested_candidates"]) is not int or a["tested_candidates"] < 1:
        _fail("tested_candidates")
    if type(a["observed_at"]) is not int or a["observed_at"] <= decided_at:
        _fail("recorded_chronology")
    if not _is_digest(a["trace_sha256"]):
        _fail("trace_digest_shape")
    if type(a["primitive_calls"]) is not int or a["primitive_calls"] < 0:
        _fail("primitive_calls")
    if (type(a["by_op"]) is not dict or
            any(op not in PRIMITIVES or type(n) is not int or n < 1
                for op, n in a["by_op"].items()) or
            sum(a["by_op"].values()) != a["primitive_calls"]):
        _fail("by_op_meter")
    if type(a["budget_id"]) is not str or not a["budget_id"]:
        _fail("budget_id")
    reference = _replay(profile, arm, public, audit, budget)
    for field in ("status", "program", "tested_candidates", "trace_sha256",
                  "primitive_calls", "by_op", "audit_correct_claim", "audit_output_claim"):
        if type(a[field]) is not type(reference[field]) or a[field] != reference[field]:
            _fail("replay_" + field)
    solved = reference["status"] == "solved"
    if (type(a["public_verifier_passed"]) is not bool or
            a["public_verifier_passed"] is not solved):
        # Public flag is a claimed verdict, not an authority.
        _fail("public_verifier")
    expected_ast = canonical_ast(tuple(reference["program"])) if solved else None
    if a["selected_ast"] != expected_ast:
        _fail("selected_ast")
    if solved:
        if audit is None:
            return "not_observed", a["primitive_calls"], "third_audit_missing"
        return ("public_found_audit_correct" if reference["audit_correct_claim"]
                else "public_found_audit_incorrect"), a["primitive_calls"], ""
    return "public_not_found", a["primitive_calls"], ""


def _inspect(record: object, expected_sha256: str, expected_lock: str) -> dict:
    if not _is_digest(expected_sha256):
        _fail("expected_digest")
    if canonical_digest(record) != expected_sha256:
        _fail("fixture_digest_mismatch")
    r = _exact(record, ROOT_KEYS, "record_shape")
    if (r["schema_version"] != SCHEMA or
            r["evidence_class"] != "SYNTHETIC_INVENTED_ONLY"):
        _fail("non_synthetic_or_schema")
    if (type(r["fixture_id"]) is not str or
            re.fullmatch(r"fx-[a-z0-9-]{1,70}", r["fixture_id"]) is None):
        _fail("fixture_id")
    if (type(expected_lock) is not str or expected_lock != SOURCE_LOCK or
            r["source_lock"] != expected_lock):
        _fail("external_source_lock")
    if type(r["public_examples"]) is not list or len(r["public_examples"]) != 2:
        _fail("public_examples")
    public = tuple(_example(e, "public") for e in r["public_examples"])
    audit_raw = r["audit_example"]
    # A deliberately incomplete, well-formed synthetic audit is unobserved.
    # Extra/unknown keys are a contradiction, not a legitimate absence.
    if (type(audit_raw) is dict and
            set(audit_raw) < {"input", "output"}):
        audit = None
    else:
        audit = None if audit_raw is None else _example(audit_raw, "audit")
    b = _exact(r["budget"], frozenset(("max_expanded_nodes", "max_candidates",
                                      "budget_id")), "budget_shape")
    if (type(b["max_expanded_nodes"]) is not int or b["max_expanded_nodes"] != 4
            or type(b["max_candidates"]) is not int or not 1 <= b["max_candidates"] <= 100
            or type(b["budget_id"]) is not str or not b["budget_id"]):
        _fail("budget")
    c = _exact(r["comparison"], frozenset((
        "profile", "policy_choice", "choice_decided_at", "choice_pretrial_sealed")),
        "comparison_shape")
    if (type(c["profile"]) is not str or c["profile"] not in PROFILES
            or type(c["policy_choice"]) is not str or c["policy_choice"] not in ACTIONS
            or type(c["choice_decided_at"]) is not int or c["choice_decided_at"] < 0
            or c["choice_pretrial_sealed"] is not True):
        _fail("comparison_contract")
    arms = r["arms"]
    if (type(arms) is not dict or any(k not in ACTIONS for k in arms)
            or not arms):
        _fail("arms_shape")
    outcomes: dict[str, str] = {}
    costs: dict[str, int] = {}
    missing: list[str] = []
    mismatch = False
    for arm in ACTIONS:
        if arm not in arms or arms[arm] is None:
            missing.append(arm + "_missing")
            continue
        if type(arms[arm]) is dict and set(arms[arm]) < ARM_KEYS:
            missing.append(arm + "_truncated")
            continue
        outcome, calls, reason = _validate_arm(
            arms[arm], arm, c["profile"], public, audit,
            b["max_candidates"], c["choice_decided_at"])
        outcomes[arm] = outcome
        costs[arm] = calls
        if reason:
            missing.append(reason + "_" + arm)
        mismatch |= arms[arm]["budget_id"] != b["budget_id"]
    if missing:
        return {"status": "not_observed", "reason": ",".join(missing),
                "arm_outcomes": outcomes, "costs": costs, "choice": c["policy_choice"]}
    if mismatch:
        return {"status": "non_comparable", "reason": "budget_identity_mismatch",
                "arm_outcomes": outcomes, "costs": costs, "choice": c["policy_choice"]}
    return {"status": "valid", "reason": "",
            "arm_outcomes": outcomes, "costs": costs, "choice": c["policy_choice"]}


def normalize_pair(record: object, expected_sha256: str,
                   *, expected_lock: str = SOURCE_LOCK) -> dict:
    """Inspect invented evidence. Invalid is a hard-stop outcome, not a miss."""
    try:
        return _inspect(record, expected_sha256, expected_lock)
    except (EvidenceError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, EvidenceError) else "malformed_canonical_record"
        return {"status": "integrity_invalid", "reason": code,
                "arm_outcomes": {}, "costs": {}, "choice": None}


def aggregate_pairs(records: list[dict], pinned_digests: dict[str, str]) -> dict:
    """Fail entire estimand on ANY invalid input; never mix valid with invalid.

    The pins must be kept separately from the rows. No input task rows are
    echoed to public output. No statistical significance is claimed.
    """
    if type(records) is not list or type(pinned_digests) is not dict:
        _fail("aggregation_type")
    seen: set[str] = set()
    results: list[dict] = []
    invalid = 0
    for row in records:
        rid = row.get("fixture_id") if type(row) is dict else None
        if (type(rid) is not str or rid in seen or
                rid not in pinned_digests):
            invalid += 1
            continue
        seen.add(rid)
        result = normalize_pair(row, pinned_digests[rid])
        invalid += int(result["status"] == "integrity_invalid")
        results.append(result)
    if seen != set(pinned_digests):
        invalid += len(set(pinned_digests) - seen)
    if invalid:
        return {"schema_version": SCHEMA, "evidence_kind": "synthetic_calibration_only",
                "status": "invalid_stopped", "n_integrity_invalid": invalid,
                "estimates": None, "scoring_authorized": False}
    valid = [x for x in results if x["status"] == "valid"]
    missing = sum(x["status"] == "not_observed" for x in results)
    noncomparable = sum(x["status"] == "non_comparable" for x in results)
    both_found = discordant = not_found_pairs = not_found_arms = 0
    on_only = off_only = both_correct = neither = 0
    eligible = errors = 0
    for pair in valid:
        off = pair["arm_outcomes"]["OFF"]
        on = pair["arm_outcomes"]["ON"]
        ofound = off != "public_not_found"
        nfound = on != "public_not_found"
        not_found_arms += int(not ofound) + int(not nfound)
        not_found_pairs += int(not ofound or not nfound)
        if ofound and nfound:
            both_found += 1
            discordant += int(off != on)
        oc = off == "public_found_audit_correct"
        nc = on == "public_found_audit_correct"
        on_only += int(nc and not oc)
        off_only += int(oc and not nc)
        both_correct += int(oc and nc)
        neither += int(not oc and not nc)
        best = None
        if oc != nc:
            best = "OFF" if oc else "ON"
        elif oc and nc and pair["costs"]["OFF"] != pair["costs"]["ON"]:
            best = min(ACTIONS, key=lambda x: pair["costs"][x])
        if best is not None:
            eligible += 1
            errors += int(pair["choice"] != best)
    return {
        "schema_version": SCHEMA,
        "evidence_kind": "synthetic_calibration_only",
        "status": "calibration_observed_not_scientific_result",
        "n_input_pairs": len(records), "n_paired_valid": len(valid),
        "n_both_public_found": both_found,
        "n_third_audit_discordant_given_both_public_found": discordant,
        "third_audit_discordance_rate": (
            discordant / both_found if both_found else "not_estimable"),
        "n_public_not_found_arms": not_found_arms,
        "n_public_not_found_pairs": not_found_pairs,
        "n_integrity_invalid": 0, "n_not_observed": missing,
        "n_non_comparable": noncomparable,
        "n_on_only_correct": on_only, "n_off_only_correct": off_only,
        "n_both_correct": both_correct, "n_neither_correct": neither,
        "paired_audited_accuracy_diff": (
            (on_only - off_only) / len(valid) if valid else "not_estimable"),
        "n_eligible_policy_choices": eligible,
        "n_policy_choice_errors": errors,
        "policy_choice_error_rate": (
            errors / eligible if eligible else "not_estimable"),
        "scoring_authorized": False, "new_real_scored_tasks": 0,
    }


def finite_reachability_probe(profile: str, values: tuple[str, ...]) -> dict:
    """Find a FIRST-solution generalization witness on a finite invented set.

    Absence is INCONCLUSIVE, NEVER a proof of Unicode/DSL impossibility.
    This does not access real TaskSpec or experimental partitions.
    """
    if (type(values) is not tuple or not 1 <= len(values) <= 12 or
            any(type(x) is not str or len(x) > 64 for x in values)
            or len(set(values)) != len(values)):
        _fail("finite_domain")
    if profile not in PROFILES:
        _fail("profile_or_arm")
    for x, y in product(values, repeat=2):
        for target in candidates(profile, "OFF"):
            public = ((x, apply(target, x)), (y, apply(target, y)))
            off = _replay(profile, "OFF", public, None, 100)
            on = _replay(profile, "ON", public, None, 100)
            if off["status"] != "solved" or on["status"] != "solved":
                continue
            a, b = tuple(off["program"]), tuple(on["program"])
            for z in values:
                if apply(a, z) != apply(b, z):
                    return {"status": "IDENTIFIABLE", "evidence_kind": "synthetic_finite_witness",
                            "profile": profile, "domain_size": len(values),
                            "witness": {"public": public, "third_input": z,
                                        "off_program": off["program"], "on_program": on["program"]},
                            "universal_impossibility_proved": False,
                            "scoring_authorized": False}
    return {"status": "INCONCLUSIVE", "evidence_kind": "synthetic_finite_probe",
            "profile": profile, "domain_size": len(values), "witness": None,
            "universal_impossibility_proved": False, "scoring_authorized": False}

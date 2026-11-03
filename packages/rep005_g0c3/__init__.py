"""Evaluator-only causal-family source. Disclosed synthetic, not a learned policy or blinded family study."""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from math import isfinite
from random import Random
from time import monotonic, perf_counter
from packages.rep005_g0c import (ACTIONS, HISTORIES, N, Atom, Edge, Law, _transition,
                                 compose, guards, law, permute_law, full_semantic_orbit_equivalence)
from packages.rep005_g0c.opportunity import certify as inquiry_certify

VERSION = "CFAM-V1"
MAX_DRAWS = 48
DOMAIN_CELLS = 115680
BUDGET = 3
KEYS = tuple((h, k, n) for h in (0, 1, 2) for k in ("set", "pulse") for n in range(6))


def _seconds(v):
    if type(v) not in (int, float) or not isfinite(v) or not 0 < v <= 3600:
        raise ValueError("finite positive proof budget required")
    return float(v)


def _seed(index):
    if type(index) is not int or not 0 <= index < MAX_DRAWS:
        raise ValueError("invalid fixed-index root draw")
    return int.from_bytes(sha256(f"{VERSION}:root:{index:04d}".encode()).digest(), "big")


def _atom(rng):
    kind = rng.choice(("bit", "pulse", "set"))
    role = rng.randrange(N)
    if kind == "bit":
        return Atom("bit", role, rng.randrange(2))
    return Atom(kind, role, -1 if kind == "pulse" else rng.randrange(2), rng.choice((1, 2)))


def draw_root(index):
    """One root attempt; any invalid edge/law remains invalid, with no replacement."""
    rng = Random(_seed(index))
    edges = []
    try:
        for _ in range(rng.choice((1, 2))):
            source = rng.randrange(N)
            target = rng.choice(tuple(i for i in range(N) if i != source))
            lag = rng.randrange(3)
            guard = guards(*(_atom(rng) for _ in range(rng.choice((0, 1, 2)))))
            edges.append(Edge(source, target, lag, guard))
        model = law(*edges)
    except ValueError:
        return dict(root_id=f"root-{index:04d}", status="INVALID", reason="INVALID_TYPED_LAW",
                    model=None, variant=None, role_permutation=None)
    variant_rng = Random(_seed(index) ^ int.from_bytes(sha256(b"CFAM-V1:role").digest(), "big"))
    perm = tuple(variant_rng.sample(range(N), N))
    return dict(root_id=f"root-{index:04d}", status="VALID", reason=None, model=model,
                variant=permute_law(model, perm), role_permutation=perm)


def full_invariant(model, *, deadline_at):
    """Complete role-invariant histogram: unequal histograms PROVE nonalias.

    Simultaneous role permutations preserve history length, action kind and
    Hamming distance from same-action no-edge transition on all typed cells.
    Equal histograms are only a filter, NEVER an alias certificate.
    """
    if type(model) is not Law or type(deadline_at) not in (int, float) or not isfinite(deadline_at):
        raise ValueError("typed Law and finite absolute deadline required")
    counts = Counter()
    seen = 0
    for before in range(1 << N):
        for history in HISTORIES:
            if monotonic() >= deadline_at:
                raise TimeoutError("full-domain invariant exhausted")
            for action in ACTIONS:
                baseline = ((before & ~(1 << action[1])) | (action[2] << action[1])
                            if action[0] == "set" else before)
                after, _ = _transition(model, before, history, action)
                counts[(len(history), action[0], (after ^ baseline).bit_count())] += 1
                seen += 1
    if seen != DOMAIN_CELLS:
        raise AssertionError("incomplete semantic domain")
    return tuple(counts[key] for key in KEYS)


def orbit_census(roots, *, proof_seconds=180):
    """Exact-orbit lower/upper bounds; unknown proofs never become positives."""
    end = monotonic() + _seconds(proof_seconds)
    reps, records = [], []
    exact_pairs = invariant_nonalias_pairs = 0
    for root in roots:
        id_ = root["root_id"]
        if root["status"] != "VALID":
            records.append(dict(root_id=id_, status="INVALID", reason=root["reason"]))
            continue
        try:
            if monotonic() >= end:
                raise TimeoutError("global cap")
            invariant = full_invariant(root["model"], deadline_at=end)
            alias_of = None
            for old_id, old_law, old_invariant in reps:
                if invariant != old_invariant:
                    invariant_nonalias_pairs += 1
                    continue
                remaining = end - monotonic()
                if remaining <= 0:
                    raise TimeoutError("global cap")
                exact_pairs += 1
                certificate = full_semantic_orbit_equivalence(
                    old_law, root["model"], deadline_seconds=min(remaining, 120))
                if certificate["status"] == "NOT_CERTIFIED":
                    raise TimeoutError("exact oracle cap")
                if certificate["status"] == "ALIAS":
                    alias_of = old_id
                    break
            if alias_of is None:
                reps.append((id_, root["model"], invariant))
                records.append(dict(root_id=id_, status="CERTIFIED_NEW_ORBIT"))
            else:
                records.append(dict(root_id=id_, status="CERTIFIED_ALIAS", alias_of=alias_of))
        except TimeoutError:
            records.append(dict(root_id=id_, status="NOT_CERTIFIED", reason="PROOF_RESOURCE_CAP"))
    unknown = sum(r["status"] == "NOT_CERTIFIED" for r in records)
    return dict(status="CERTIFIED_COHORT" if not unknown else "PARTIAL_NOT_CERTIFIED",
                root_draws=len(roots), records=records,
                certified_orbits_lower_bound=len(reps), orbit_upper_bound=len(reps) + unknown,
                not_certified=unknown, invariant_nonalias_pairs=invariant_nonalias_pairs,
                full_exact_role_pairs=exact_pairs, domain_cells_per_valid_law=DOMAIN_CELLS,
                independent_scientific_family_count=None)


def panels(roots, *, panel_seconds=30):
    """Consecutive 4 draws per panel. Retain INVALID and NOT_CERTIFIED denominators."""
    _seconds(panel_seconds)
    if len(roots) % 4:
        raise ValueError("exact four-root panels required")
    records = []
    for start in range(0, len(roots), 4):
        group = roots[start:start + 4]
        row = dict(root_ids=[r["root_id"] for r in group])
        if any(r["status"] != "VALID" for r in group):
            records.append({**row, "status": "INVALID", "reason": "INVALID_ROOT_NO_REPLACEMENT"})
            continue
        laws = tuple(r["model"] for r in group)
        if len(set(laws)) != 4:
            records.append({**row, "status": "INVALID", "reason": "DUPLICATE_LAW_NO_REPLACEMENT"})
            continue
        cert = inquiry_certify(laws, BUDGET, initial_state=0, max_plans=4000,
                               max_nodes=250000, deadline_seconds=panel_seconds)
        if cert["status"] != "CERTIFIED_CLOSED_CLASS":
            records.append({**row, "status": "NOT_CERTIFIED",
                            "reason": cert.get("reason", "UNKNOWN")})
            continue
        gain = cert["adaptive_gain"]
        if not 0 <= gain <= 1:
            raise AssertionError("invalid exact adaptive gap")
        records.append({**row, "status": "CERTIFIED_POSITIVE" if gain > 0 else "CERTIFIED_ZERO",
                        "adaptive_value": cert["adaptive_value"],
                        "open_loop_value": cert["open_loop_value"], "adaptive_gain": gain,
                        "open_loop_plans": cert["evaluated_open_loop_plans"],
                        "adaptive_nodes": cert["visited_adaptive_nodes"]})
    c = Counter(r["status"] for r in records)
    n = len(records)
    return dict(records=records, attempted=n, positive=c["CERTIFIED_POSITIVE"],
                zero=c["CERTIFIED_ZERO"], invalid=c["INVALID"],
                not_certified=c["NOT_CERTIFIED"],
                opportunity_lower_bound=c["CERTIFIED_POSITIVE"] / n,
                opportunity_upper_bound=(c["CERTIFIED_POSITIVE"] + c["INVALID"] +
                                         c["NOT_CERTIFIED"]) / n,
                scope="attempted_disclosed_synthetic_panels_not_population_probability")


def run(draws=MAX_DRAWS, *, proof_seconds=180, panel_seconds=30):
    if type(draws) is not int or not 4 <= draws <= MAX_DRAWS or draws % 4:
        raise ValueError("fixed whole-panel draw size required")
    _seconds(proof_seconds)
    _seconds(panel_seconds)
    start = perf_counter()
    roots = tuple(draw_root(i) for i in range(draws))
    orbit = orbit_census(roots, proof_seconds=proof_seconds)
    inquiry = panels(roots, panel_seconds=panel_seconds)
    return dict(schema_version="g0c3-source-only-v1", experiment="EXP-REP-005-G0C3",
                distribution=VERSION, phase="DISCLOSED_SYNTHETIC_ENGINEERING_ONLY",
                root_attempts=draws, role_variant_attempt_slots=draws,
                syntax_attempt_slots=draws * 2,
                valid_roots=sum(x["status"] == "VALID" for x in roots),
                invalid_roots=sum(x["status"] == "INVALID" for x in roots),
                private_source_records=[
                    {k: (repr(v) if k in ("model", "variant") and v is not None else
                         list(v) if k == "role_permutation" and v is not None else v)
                     for k, v in root.items()} for root in roots],
                orbit=orbit, inquiry=inquiry,
                runtime=dict(wall_seconds=round(perf_counter() - start, 3)),
                real_paid_train_actions=0, learned_policy="NOT_RUN",
                scientific_family_power="NOT_CERTIFIED",
                independent_scientific_family_count=None,
                learner_access="FORBIDDEN_PRIVATE_EVALUATOR_ONLY")

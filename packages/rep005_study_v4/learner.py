"""Source-BLIND, pure-stdlib, JSON-stdin/stdout learner protocol for disclosed V4 pilot.

This file MUST NOT import packages.rep005_g0b_v4 or any private Law/certifier.
The caller executes this file in a fresh Python -I subprocess. This is not
a hardened OS sandbox against a malicious learner, only a custody boundary
against accidental import or parameter leakage.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys

N = 5
ACTIONS = (
    tuple(("set", i, b) for i in range(N) for b in (0, 1))
    + tuple(("pulse", i, -1) for i in range(N))
)
PULSE = tuple(("pulse", i, -1) for i in range(N))
MODELS = (None,) + tuple((lag, source, target)
                           for lag in (0, 1, 2)
                           for source in range(N)
                           for target in range(N) if source != target)


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def digest(data):
    return hashlib.sha256(canonical(data).encode("utf-8")).hexdigest()


def action_key(a):
    if type(a) is not list or len(a) != 3:
        raise ValueError("bad typed public action")
    key = tuple(a)
    if key not in ACTIONS or type(a[1]) is not int or type(a[2]) is not int:
        raise ValueError("invalid public action")
    return key


def history_keys(h):
    if type(h) is not list or len(h) > 2:
        raise ValueError("bad public chronology")
    return tuple(action_key(a) for a in h)


def _record(r):
    if type(r) is not dict or set(r) != {"before", "history", "action", "after", "paid_cost"}:
        raise ValueError("untrusted/extra record field")
    if type(r["before"]) is not int or type(r["after"]) is not int:
        raise ValueError("state exact-int required")
    if not (0 <= r["before"] < 32 and 0 <= r["after"] < 32):
        raise ValueError("state outside five bits")
    if type(r["paid_cost"]) is not int or r["paid_cost"] != 1:
        raise ValueError("free or forged observation")
    return r["before"], history_keys(r["history"]), action_key(r["action"]), r["after"]


def check_episode(records):
    if type(records) is not list or len(records) > 8:
        raise ValueError("illegal paid episode")
    state, hist = 0, ()
    result = []
    for r in records:
        x, h, a, after = _record(r)
        if state != x or hist != h:
            raise ValueError("forged or rearranged chronology")
        result.append((x, h, a, after))
        state, hist = after, (hist + (a,))[-2:]
    return result


def base_state(before, action):
    if action[0] == "set":
        i, bit = action[1:]
        return (before & ~(1 << i)) | (bit << i)
    return before


def interp_effect_body(model, x, hist, action):
    """Executable public typed XOR-effect rule, independent of private source."""
    after = base_state(x, action)
    if model is None:
        return after
    lag, source, target = model
    trigger = action if lag == 0 else (hist[-lag] if len(hist) >= lag else None)
    if trigger == ("pulse", source, -1):
        after ^= 1 << target
    return after


def fit_models(rows, permitted=None):
    scope = MODELS if permitted is None else permitted
    return tuple(m for m in scope if all(
        interp_effect_body(m, x, h, a) == after for x, h, a, after in rows
    ))


def count_residual_errors(model, rows):
    """Number of 5-bit residual exceptions in fully disclosed public records."""
    return sum(int(interp_effect_body(model, x, hist, action) != after)
               for x, hist, action, after in rows)


def two_part_mdl_codec(by_world):
    """Explicit fixed bit grammar (v1) for FUTURE disclosed MDL-v2 pilots.

    Model bits:
      NULL = prefix(0): 1 bit.
      EFFECT = prefix(1) + lag(2 bits) + per-world ordered source/target
               binding (5 bits for 5*4=20 possibilities): 3+5*world_count bits.
    Residual bits: 1 match/exception flag per paid public record, plus exactly
    5 bits of XOR residual for each exception. No learned length weights.
    World order is canonical sorted opaque ID. This encoder is introduced
    AFTER prior G2a diagnostic scores and cannot retroactively pre-register them.
    """
    worlds = sorted(by_world)
    rows_total = sum(len(by_world[w]) for w in worlds)
    null_errors = sum(count_residual_errors(None, by_world[w]) for w in worlds)
    entries = [{
        "kind": "NULL", "lag": None, "model_bits": 1,
        "residual_bits": rows_total + 5 * null_errors,
        "residual_exceptions": null_errors,
        "total_bits": 1 + rows_total + 5 * null_errors,
        "world_bindings": [],
    }]
    for lag in (0, 1, 2):
        bindings = []
        errors = 0
        for w in worlds:
            local = min(
                ((count_residual_errors((lag, s, t), by_world[w]), s, t)
                 for s in range(N) for t in range(N) if s != t),
                key=lambda x: (x[0], x[1], x[2]),
            )
            errors += local[0]
            bindings.append([local[1], local[2]])
        model_bits = 3 + 5 * len(worlds)
        residual_bits = rows_total + 5 * errors
        entries.append({
            "kind": "EFFECT", "lag": lag, "model_bits": model_bits,
            "residual_bits": residual_bits, "residual_exceptions": errors,
            "total_bits": model_bits + residual_bits,
            "world_bindings": bindings,
        })
    best_bits = min(x["total_bits"] for x in entries)
    winners = [x for x in entries if x["total_bits"] == best_bits]
    if len(winners) != 1 or winners[0]["kind"] != "EFFECT" or (
        winners[0]["residual_exceptions"] != 0
    ):
        raise ValueError("NOT_CERTIFIED: MDL null/tie/exception winner")
    return {
        "version": "MDL-C1-FIXED-BITS-V1-POST-G2A",
        "selection": "minimum_exact_two_part_body_plus_residual_bits",
        "null_and_lag_candidates": entries,
        "winning_kind": winners[0]["kind"],
        "winning_lag": winners[0]["lag"],
        "winning_model_bits": winners[0]["model_bits"],
        "winning_residual_bits": winners[0]["residual_bits"],
        "winning_total_bits": winners[0]["total_bits"],
    }


def make_snapshot(episodes):
    if type(episodes) is not list or len(episodes) == 0 or len(episodes) > 64:
        raise ValueError("invalid training episode count")
    by_world = {}
    public_only = []
    for item in episodes:
        if type(item) is not dict or set(item) != {"world_session_id", "steps"}:
            raise ValueError("private/extra training keys forbidden")
        world = item["world_session_id"]
        if type(world) is not str or len(world) > 64 or not world:
            raise ValueError("opaque public world ID required")
        rows = check_episode(item["steps"])
        if not rows:
            continue
        by_world.setdefault(world, []).extend(rows)
        public_only.append(item)
    if len(by_world) < 2:
        raise ValueError("reusable template requires >=2 training world sessions")
    candidate_counts = {
        world: len(fit_models(rows)) for world, rows in by_world.items()
    }
    mdl = two_part_mdl_codec(by_world)
    lag = mdl["winning_lag"]
    payload = {
        "schema": "REP005-V4-TYPED-EFFECT-C1-MDL-ENGINEERING",
        "body": {
            "trigger": "public_pulse_at_lag",
            "lag": lag,
            "effect": "xor_one_target_bit",
            "source_role": "bound_from_paid_public_use",
            "target_role": "bound_from_paid_public_use",
        },
        "evidence_sha256": digest(public_only),
        "training_world_sessions": len(by_world),
        "training_paid_steps": sum(len(rows) for rows in by_world.values()),
        "candidate_counts_by_opaque_session": candidate_counts,
        "candidate_support_lags": [lag],
        "mdl_codec": mdl,
        "selection": "minimum_exact_two_part_body_plus_residual_bits",
        "status": "ENGINEERING_V2_AFTER_DISCLOSED_PILOT_NO_CONFIRMATORY_SCIENCE",
    }
    return {"payload": payload, "sha256": digest(payload)}


def load_snapshot(raw):
    if type(raw) is not dict or set(raw) != {"payload", "sha256"}:
        raise ValueError("wrong Snapshot schema")
    if digest(raw["payload"]) != raw["sha256"]:
        raise ValueError("tampered Snapshot")
    p = raw["payload"]
    if type(p) is not dict or p.get("schema") != "REP005-V4-TYPED-EFFECT-C1-MDL-ENGINEERING":
        raise ValueError("unrecognized Snapshot version")
    b = p.get("body")
    if type(b) is not dict or set(b) != {
        "trigger", "lag", "effect", "source_role", "target_role"
    }:
        raise ValueError("bad typed Body")
    if (b["trigger"] != "public_pulse_at_lag" or b["effect"] != "xor_one_target_bit"
        or type(b["lag"]) is not int or b["lag"] not in (0, 1, 2)
        or b["source_role"] != "bound_from_paid_public_use"
        or b["target_role"] != "bound_from_paid_public_use"):
        raise ValueError("forged typed Body")
    if (p.get("status") != "ENGINEERING_V2_AFTER_DISCLOSED_PILOT_NO_CONFIRMATORY_SCIENCE"
        or p.get("mdl_codec", {}).get("version") != "MDL-C1-FIXED-BITS-V1-POST-G2A"):
        raise ValueError("unapproved Snapshot")
    return b["lag"]


def _valid_prefix(steps):
    return check_episode(steps)


def viable_models(rows, *, snapshot=None, body_off=False):
    # Same full public grammar/meta-operator envelope for STATIC and LEARNED.
    # Learned template narrows the *prior hypothesis support* via public TRAIN.
    # A pure body-only ablation MUST retain the exact same posterior support
    # after matching the same public evidence; it only disables dispatch.
    lag = load_snapshot(snapshot) if snapshot is not None else None
    models = MODELS if lag is None else ((None,) + tuple(m for m in MODELS[1:]
                                                    if m[0] == lag))
    return fit_models(rows, models)


def _entropy(outputs):
    n = len(outputs)
    if not n:
        return 0.
    counts = {}
    for x in outputs:
        counts[x] = counts.get(x, 0) + 1
    return -sum((v/n) * math.log2(v/n) for v in counts.values())


def choose_query(rows, snapshot=None, body_off=False):
    if not rows:
        state, hist = 0, ()
    else:
        state, hist = rows[-1][3], (rows[-1][1] + (rows[-1][2],))[-2:]
    candidates = viable_models(rows, snapshot=snapshot, body_off=body_off)
    if not candidates:
        return {"status": "NOT_CERTIFIED", "reason": "NO_CONSISTENT_PUBLIC_CANDIDATE"}
    pulsed = [r[2][1] for r in rows if r[2][0] == "pulse"]
    available_pulses = sorted(PULSE, key=lambda a: (pulsed.count(a[1]), a[1]))
    set_actions = [("set", i, b) for i in range(N) for b in (0, 1)]
    # No private source ID, name, hidden true Law or provenance used here.
    preferred = (set_actions + available_pulses
                 if hist and hist[-1][0] == "pulse"
                 else available_pulses + set_actions)
    best_a, best_gain = None, -1.
    for a in preferred:
        outcomes = [(base_state(state, a) if body_off else
                     interp_effect_body(m, state, hist, a)) for m in candidates]
        gain = _entropy(outcomes)
        if gain > best_gain + 1e-12:
            best_a, best_gain = a, gain
    return {
        "status": "OK", "action": list(best_a),
        "candidate_count": len(candidates),
        "predicted_outcome_entropy_bits": round(best_gain, 6),
        "trained_typed_body": snapshot is not None and not body_off,
    }


def predict(rows, probes, snapshot=None, body_off=False):
    candidates = viable_models(rows, snapshot=snapshot, body_off=body_off)
    if not candidates:
        return {"status": "NOT_CERTIFIED", "predictions": []}
    if type(probes) is not list or len(probes) > 64:
        raise ValueError("invalid probe panel size")
    pred = []
    for q in probes:
        if type(q) is not dict or set(q) != {"before", "history", "action"}:
            raise ValueError("private/extra probe field forbidden")
        x = q["before"]
        if type(x) is not int or not 0 <= x < 32:
            raise ValueError("invalid probe state")
        hist, action = history_keys(q["history"]), action_key(q["action"])
        outcomes = {(base_state(x, action) if body_off else
                     interp_effect_body(m, x, hist, action)) for m in candidates}
        pred.append(next(iter(outcomes)) if len(outcomes) == 1 else None)
    return {"status": "OK", "predictions": pred,
            "candidate_count": len(candidates),
            "actual_body_dispatch_count": (0 if body_off else len(probes) * len(candidates)),
            "trained_typed_body": snapshot is not None and not body_off}


def handle(message):
    if type(message) is not dict:
        raise ValueError("JSON object message required")
    mode = message.get("mode")
    if mode == "train":
        if set(message) != {"mode", "episodes"}:
            raise ValueError("bad train input")
        return {"status": "OK", "snapshot": make_snapshot(message["episodes"])}
    if mode in ("plan", "predict"):
        allowed = {"mode", "steps", "snapshot", "body_off"} | (
            {"probes"} if mode == "predict" else set()
        )
        if set(message) != allowed:
            raise ValueError("bad public-only use message")
        rows = _valid_prefix(message["steps"])
        if type(message["body_off"]) is not bool:
            raise ValueError("body_off not boolean")
        if mode == "plan":
            return choose_query(rows, message["snapshot"], message["body_off"])
        return predict(rows, message["probes"], message["snapshot"], message["body_off"])
    raise ValueError("unrecognized message operation")


def main():
    data = sys.stdin.read(512_000 + 1)
    if len(data) > 512_000:
        raise ValueError("input size cap")
    message = json.loads(data)
    response = handle(message)
    print(canonical(response))


if __name__ == "__main__":
    main()

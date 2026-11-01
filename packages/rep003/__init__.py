"""EXP-REP-003 G1-G4 disclosed finite conditional active-learning lab.

Synthetic worlds only; no old DEV/FINAL, no private data.
Only Session applies evaluator-held truth. All induction consumes public paid traces.
This is an intentionally reduced <=1-edge learner grammar, not V2's full two-edge
composition design. Evaluation uses out-of-grammar two-edge distractors.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from pathlib import Path
from collections import Counter

N = 4
SCHEMA = "rep003/snapshot-v3/engineering-1"
GRAMMAR = "anonymous-boolean/direct-or-gated-one-edge/xor-prestate/1"
KINDS = ("EMPTY", "DIRECT", "GATE0", "GATE1")
ARMS = ("LQ", "LA", "LR", "ER", "FA", "FX", "BODY-OFF")
STRATA = ("RENAMED", "CONDITIONAL_TRANSFER", "NOVEL", "DISTRACTOR")
BUDGETS = (0, 1, 2, 4, 6, 8)
TRAIN_SIZES = (0, 3, 8, 16, 32, 64)
MAX_CHECKS = 200000
# Model is None, or (source, target, guard, gate_value).
# guard -1 means a DIRECT edge. True worlds may have two edges (OOD only).
MODELS = (None,) + tuple(
    (i, j, -1, -1)
    for i in range(N) for j in range(N) if i != j
) + tuple(
    (i, j, k, v)
    for i in range(N) for j in range(N) if i != j
    for k in range(N) if k not in (i, j) for v in (0, 1)
)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def kind(model):
    if model is None:
        return "EMPTY"
    return "DIRECT" if model[2] == -1 else "GATE" + str(model[3])


def _strict_state(state):
    if type(state) not in (tuple, list) or len(state) != N or any(
        type(x) is not int or x not in (0, 1) for x in state
    ):
        raise ValueError("noncanonical Boolean state")
    return tuple(state)


def action_valid(action):
    if type(action) is not tuple or len(action) != 3:
        raise ValueError("invalid action tuple")
    op, i, value = action
    if type(op) is not str or type(i) is not int or not 0 <= i < N:
        raise ValueError("invalid action type or index")
    if op == "pulse":
        if value is not None:
            raise ValueError("pulse requires null value")
    elif op == "set":
        if type(value) is not int or value not in (0, 1):
            raise ValueError("set requires canonical bit")
    else:
        raise ValueError("unknown action")


def step(state, action, rules):
    """Pure finite interpreter. rules is a tuple of edges or empty tuple."""
    s = _strict_state(state)
    action_valid(action)
    op, source, value = action
    if op == "set":
        result = list(s)
        result[source] = value
        return tuple(result)
    if rules is None:
        edges = ()
    elif type(rules) is tuple and (not rules or type(rules[0]) is tuple):
        edges = rules
    else:
        edges = (rules,)
    result = list(s)
    for edge in edges:
        i, j, guard, gate = edge
        if i == source and (guard == -1 or s[guard] == gate):
            result[j] ^= 1
    return tuple(result)


def state_signature(model):
    return tuple(
        step(s, ("pulse", i, None), model)
        for s in itertools.product((0, 1), repeat=N) for i in range(N)
    )


# Each n4 canonical model has distinct full finite behavior. Assert at import.
assert len(MODELS) == len({state_signature(m) for m in MODELS})


@dataclass(frozen=True)
class World:
    """Host-only: this object MUST NOT reach any learner function."""
    secret_rules: tuple
    anonymous_ids: tuple
    seed: int
    stratum: str


def make_world(index, stratum):
    if type(index) is not int or index < 0 or stratum not in ("TRAIN",) + STRATA:
        raise ValueError("invalid disclosed world")
    rng = random.Random(19037 + index * 101 + sum(map(ord, stratum)))
    ids = list(range(N))
    rng.shuffle(ids)
    i, j, k = ids[0], ids[1], ids[2]
    if stratum == "TRAIN":
        pattern = ("GATE1", "GATE1", "GATE1", "GATE1",
                   "GATE1", "DIRECT", "GATE0", "EMPTY")[index % 8]
    elif stratum == "RENAMED":
        pattern = ("DIRECT", "GATE1")[index % 2]
    elif stratum == "CONDITIONAL_TRANSFER":
        pattern = "GATE1"
    elif stratum == "NOVEL":
        pattern = "GATE0"
    else:
        pattern = "GATE1"
    model = {"EMPTY": None, "DIRECT": (i, j, -1, -1),
             "GATE0": (i, j, k, 0), "GATE1": (i, j, k, 1)}[pattern]
    rules = () if model is None else (model,)
    if stratum == "DISTRACTOR":
        # Two-rule causal composition: intentionally outside <=1-edge grammar.
        others = [x for x in ids if x != j]
        rules = ((i, j, k, 1), (others[0], ids[3], -1, -1))
    public_ids = tuple("obj_" + format(rng.getrandbits(48), "012x") for _ in range(N))
    return World(rules, public_ids, index, stratum)


class Session:
    def __init__(self, world):
        if type(world) is not World:
            raise ValueError("host World required")
        self._world = world
        self.state = (0,) * N
        self.actions = 0
        self.trace = []

    def public(self):
        return {"ids": list(self._world.anonymous_ids),
                "state": list(self.state), "action_cost": 1, "n": N}

    def apply(self, action):
        action_valid(action)
        before = self.state
        after = step(before, action, self._world.secret_rules)
        self.state = after
        self.actions += 1
        row = {"before": list(before), "action": list(action),
               "after": list(after), "cost": 1, "step": self.actions}
        self.trace.append(row)
        return row


def validate_trace(rows):
    if type(rows) not in (tuple, list):
        raise ValueError("invalid trace")
    for idx, row in enumerate(rows, start=1):
        if type(row) is not dict or set(row) != {
            "before", "action", "after", "cost", "step"
        } or type(row["cost"]) is not int or row["cost"] != 1 or (
            type(row["step"]) is not int or row["step"] != idx
        ):
            raise ValueError("invalid public evidence envelope")
        before = _strict_state(row["before"])
        after = _strict_state(row["after"])
        if type(row["action"]) is not list or len(row["action"]) != 3:
            raise ValueError("bad action")
        a = tuple(row["action"])
        action_valid(a)
        if idx > 1 and tuple(rows[idx-2]["after"]) != before:
            raise ValueError("disconnected paid public history")
        if a[0] == "set" and step(before, a, ()) != after:
            raise ValueError("forged state-setting evidence")


def consistent(rows, models=MODELS, meter=None):
    validate_trace(rows)
    surviving = []
    for m in models:
        works = True
        for row in rows:
            if row["action"][0] != "pulse":
                continue
            if meter is not None:
                meter["model_checks"] += 1
                if meter["model_checks"] > MAX_CHECKS:
                    raise RuntimeError("shared model-check cap")
            if step(row["before"], tuple(row["action"]), m) != tuple(row["after"]):
                works = False
                break
        if works:
            surviving.append(m)
    return tuple(surviving)


def prior(models, counts, arm, snapshot):
    """Queries and predictions are separately blinded in use() below."""
    if arm in ("FA", "FX", "BODY-OFF") or snapshot["train_worlds"] == 0:
        weights = [1.0] * len(models)
    else:
        weights = [
            (counts[kind(m)] + 1) / max(1, sum(1 for x in MODELS if kind(x) == kind(m)))
            for m in models
        ]
    total = sum(weights)
    return [x / total for x in weights]


ACTIONS = tuple(("pulse", i, None) for i in range(N)) + tuple(
    ("set", i, v) for i in range(N) for v in (0, 1)
)


def _gini(outputs, weights):
    bins = {}
    for out, p in zip(outputs, weights):
        bins[out] = bins.get(out, 0.0) + p
    return 1.0 - sum(x*x for x in bins.values())


def choose_action(state, models, weights, remaining, meter, arm):
    """Exact 1/2-step nonadaptive Gini/cost proposal, execute first step only.
    All arms face identical candidate plan grammar and cap. Fixed FX deliberately
    canonical, not the strong FA comparator.
    """
    if remaining == 0 or not models:
        return None
    if arm == "FX":
        return ("pulse", meter["actions"] % N, None)
    best = (-1.0, None, None)
    for a in ACTIONS:
        if a[0] == "set" and state[a[1]] == a[2]:
            continue
        outs1 = [step(state, a, m) for m in models]
        meter["model_checks"] += len(models)
        meter["plans"] += 1
        if meter["model_checks"] > MAX_CHECKS:
            raise RuntimeError("shared model-check cap")
        value = _gini(outs1, weights)
        # Score against a plan length, not synthetic dream as new evidence.
        score = value
        key = (score, -ACTIONS.index(a), 0)
        if key > best:
            best = key
        if remaining >= 2 and a[0] == "set":
            for b in ACTIONS[:N]:
                outs2 = [(o1, step(o1, b, m)) for m, o1 in zip(models, outs1)]
                meter["model_checks"] += len(models)
                meter["plans"] += 1
                if meter["model_checks"] > MAX_CHECKS:
                    raise RuntimeError("shared model-check cap")
                score2 = _gini(outs2, weights) / 2.0
                key = (score2, -ACTIONS.index(a), -1)
                if key > best:
                    best = key
    return ACTIONS[-int(best[1])] if best[1] is not None else None


def opportunity(state, models, horizon, max_plans=10000):
    """Public finite model witness: exact exhaustive all legal action sequences.
    Returns UNKNOWN on cap; NO_OPPORTUNITY only after exhaustive enumeration.
    Caller pays its own conditioning history; oracle does not inform learner.
    """
    state = _strict_state(state)
    if type(horizon) is not int or horizon not in (0, 1, 2):
        raise ValueError("unsupported oracle horizon")
    examined = 0
    for depth in range(1, horizon+1):
        for plan in itertools.product(ACTIONS, repeat=depth):
            examined += 1
            if examined > max_plans:
                return {"status": "UNKNOWN", "examined": examined-1,
                        "complete": False}
            outputs = {}
            for model in models:
                s = state
                trace = []
                for action in plan:
                    s = step(s, action, model)
                    trace.append(s)
                key = tuple(trace)
                if outputs and key not in outputs:
                    other = next(iter(outputs))
                    return {"status": "WITNESS", "complete": True,
                            "cost": depth, "examined": examined,
                            "plan": [list(a) for a in plan],
                            "predicted_traces": [list(map(list, other)),
                                                 list(map(list, key))]}
                outputs[key] = model
    return {"status": "NO_OPPORTUNITY", "complete": True,
            "examined": examined, "cost": None}


def conditioned_opportunity():
    """4 paid all-zero pulses remove DIRECT/GATE0; 2 extra paid actions
    are necessary to expose a GATE1 vs EMPTY pair; total >= 6 actions.
    """
    w = World(((0, 1, 2, 1),), ("a", "b", "c", "d"), 9999, "PRECHECK")
    session = Session(w)
    for i in range(N):
        session.apply(("pulse", i, None))
    h = consistent(session.trace)
    short = opportunity(session.state, h, 1)
    long = opportunity(session.state, h, 2)
    return {"paid_conditioning": session.actions, "surviving": len(h),
            "one_step": short, "two_step": long,
            "total_witness_cost": session.actions + long.get("cost", 0)}


def _trace_train(index):
    # The learner sees ONLY paid observations. Host truth stays in Session.
    session = Session(make_world(index, "TRAIN"))
    for setting in ((0,0,0,0),) + tuple(
        tuple(int(j == k) for j in range(N)) for k in range(N)
    ):
        for source in range(N):
            for k, value in enumerate(setting):
                session.apply(("set", k, value))
            session.apply(("pulse", source, None))
    h = consistent(session.trace)
    if len(h) != 1:
        raise ValueError("TRAIN public evidence did not identify a semantic model")
    return h[0], session.actions, digest(session.trace)


def train(n):
    if type(n) is not int or n not in TRAIN_SIZES:
        raise ValueError("unsupported TRAIN size")
    counts = Counter({k:0 for k in KINDS})
    receipts = []
    actions = 0
    structures = set()
    for i in range(n):
        inferred, paid, trace_hash = _trace_train(i)
        # NO hidden world rule enters this learner-derived support estimate.
        counts[kind(inferred)] += 1
        structures.add(kind(inferred))
        receipts.append(trace_hash)
        actions += paid
    library = [
        {"kind": k, "body": {"effect": "toggle_target_if_source_pulsed",
                             "guard": ("always" if k == "DIRECT" else
                                       "none" if k == "EMPTY" else
                                       "observed_guard_" + k[-1])},
         "support": counts[k]}
        for k in KINDS if counts[k]
    ]
    raw = {"schema": SCHEMA, "grammar": GRAMMAR, "train_worlds": n,
           "support": {k: counts[k] for k in KINDS},
           "distinct_families": len(structures),
           "library": library, "paid_train_actions": actions,
           "public_receipts_hash": digest(receipts)}
    return {**raw, "digest": digest(raw)}


def validate_snapshot(s):
    if type(s) is not dict or set(s) != {
        "schema", "grammar", "train_worlds", "support", "distinct_families",
        "library", "paid_train_actions", "public_receipts_hash", "digest"
    } or s["schema"] != SCHEMA or s["grammar"] != GRAMMAR:
        raise ValueError("unknown SnapshotV3")
    if type(s["train_worlds"]) is not int or s["train_worlds"] not in TRAIN_SIZES:
        raise ValueError("invalid count")
    if type(s["support"]) is not dict or set(s["support"]) != set(KINDS) or any(
        type(s["support"][k]) is not int or s["support"][k] < 0 for k in KINDS
    ) or sum(s["support"].values()) != s["train_worlds"]:
        raise ValueError("invalid support")
    if type(s["paid_train_actions"]) is not int or s["paid_train_actions"] < 0:
        raise ValueError("invalid training cost")
    if type(s["distinct_families"]) is not int or (
        s["distinct_families"] != sum(s["support"][k] > 0 for k in KINDS)
    ):
        raise ValueError("invalid families")
    if type(s["library"]) is not list or s["library"] != [
        {"kind":k, "body":{"effect":"toggle_target_if_source_pulsed",
                            "guard":("always" if k=="DIRECT" else
                                     "none" if k=="EMPTY" else
                                     "observed_guard_"+k[-1])},
         "support":s["support"][k]} for k in KINDS if s["support"][k]
    ]:
        raise ValueError("invalid executable concept templates")
    if type(s["public_receipts_hash"]) is not str or len(s["public_receipts_hash"]) != 64:
        raise ValueError("invalid receipts")
    if type(s["digest"]) is not str or s["digest"] != digest({
        k:v for k,v in s.items() if k != "digest"
    }):
        raise ValueError("snapshot integrity violation")


def save(snapshot, path):
    validate_snapshot(snapshot)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(snapshot, sort_keys=True, indent=2)+"\n", encoding="utf8")


def load(path):
    s = json.loads(Path(path).read_text(encoding="utf8"))
    validate_snapshot(s)
    return s


def _predict_model(models, weights):
    if not models:
        return None
    # Order is predeclared and deterministic; no gold or audit feedback.
    return models[max(range(len(models)), key=lambda i: (weights[i], -i))]


def use(snapshot, world, arm, budget):
    validate_snapshot(snapshot)
    if type(world) is not World or arm not in ARMS or (
        type(budget) is not int or budget not in BUDGETS
    ):
        raise ValueError("bad use input")
    session = Session(world)
    meter = {"actions": 0, "model_checks": 0, "plans": 0}
    status = "COMMITTED"
    for _ in range(budget):
        h = consistent(session.trace, meter=meter)
        if not h:
            status = "ABSTAIN"
            break
        # Independent query and prediction priors: LA cannot see body-derived
        # class weights in any query path. LQ/ER and LR have learned query
        # priors; FA and BODY-OFF are wholly untrained on this world.
        query_arm = "FA" if arm == "LA" else arm
        q = prior(h, snapshot["support"], query_arm, snapshot)
        try:
            action = choose_action(session.state, h, q, budget-session.actions,
                                   meter, query_arm)
        except RuntimeError:
            status = "ABSTAIN"
            break
        if action is None:
            break
        session.apply(action)
        meter["actions"] += 1
    h = consistent(session.trace, meter=meter)
    if not h:
        status = "ABSTAIN"
    pred_arm = "FA" if arm in ("FA","FX","BODY-OFF","LR") else arm
    p = prior(h, snapshot["support"], pred_arm, snapshot)
    model = _predict_model(h, p) if status == "COMMITTED" else None
    predictor = {"status": status, "model": list(model) if model is not None else None}
    public = {"arm": arm, "budget": budget, "public_ids": session.public()["ids"],
              "trace": session.trace, "trace_digest": digest(session.trace),
              "meter": meter, "prediction": predictor,
              "snapshot_digest": snapshot["digest"]}
    public["commit_digest"] = digest(public)
    return public


def audit(world, committed, count=32):
    """Evaluator-only use of truth, and only AFTER a public commit is frozen."""
    if digest({k:v for k,v in committed.items() if k!="commit_digest"}) != committed["commit_digest"]:
        raise ValueError("uncommitted or modified prediction")
    if type(count) is not int or count != 32:
        raise ValueError("invalid audit sample count")
    rng = random.Random(8119 + world.seed*7 + sum(map(ord,world.stratum)))
    m = committed["prediction"]["model"]
    model = None if m is None else tuple(m)
    if committed["prediction"]["status"] != "COMMITTED":
        return 0
    matches = 0
    for _ in range(count):
        before = tuple(rng.randrange(2) for _ in range(N))
        a = ("pulse", rng.randrange(N), None)
        matches += step(before, a, model) == step(before, a, world.secret_rules)
    return matches


def evaluate():
    snap = train(64)
    rows = []
    for stratum in STRATA:
        for index in range(12):
            w = make_world(300+index, stratum)
            for arm in ARMS:
                for budget in BUDGETS:
                    c = use(snap, w, arm, budget)
                    result = audit(w, c)
                    rows.append({"stratum": stratum, "world_index": index,
                                 "arm": arm, "budget": budget, "correct": result,
                                 "status": c["prediction"]["status"],
                                 "actions": c["meter"]["actions"],
                                 "model_checks": c["meter"]["model_checks"],
                                 "plans": c["meter"]["plans"],
                                 "commit_digest": c["commit_digest"],
                                 "action_sequence": [row["action"] for row in c["trace"]],
                                 "predicted_model": c["prediction"]["model"]})
    summary = {}
    for st in STRATA:
        summary[st] = {}
        for arm in ARMS:
            scores = [
                sum(r["correct"]/32 for r in rows if r["stratum"]==st
                    and r["world_index"]==i and r["arm"]==arm)/len(BUDGETS)
                for i in range(12)
            ]
            summary[st][arm] = round(sum(scores)/len(scores), 6)
    deltas = {
        st: {other: round(summary[st]["LQ"]-summary[st][other], 6)
             for other in ARMS if other!="LQ"} for st in STRATA
    }
    # Post-review descriptive diagnostics, NOT preregistered positive thresholds:
    # did the learned-query body/prior actually change paid actions or commits?
    by_budget = {}
    switch = {}
    for st in STRATA:
        by_budget[st] = {}
        switch[st] = {}
        for b in BUDGETS:
            group = [r for r in rows if r["stratum"] == st and r["budget"] == b]
            by_budget[st][str(b)] = {
                arm: {"score": round(sum(r["correct"]/32 for r in group
                                           if r["arm"] == arm)/12, 6),
                      "abstentions": sum(r["status"] == "ABSTAIN" for r in group
                                           if r["arm"] == arm),
                      "mean_actions": round(sum(r["actions"] for r in group
                                                if r["arm"] == arm)/12, 3),
                      "mean_model_checks": round(sum(r["model_checks"] for r in group
                                                     if r["arm"] == arm)/12, 3)}
                for arm in ARMS
            }
            arm_rows = {arm: {r["world_index"]: r for r in group
                             if r["arm"] == arm} for arm in ARMS}
            switch[st][str(b)] = {
                "LQ_vs_LA_different_action_sequences": sum(
                    arm_rows["LQ"][i]["action_sequence"] != arm_rows["LA"][i]["action_sequence"]
                    for i in range(12)),
                "LQ_vs_FA_different_action_sequences": sum(
                    arm_rows["LQ"][i]["action_sequence"] != arm_rows["FA"][i]["action_sequence"]
                    for i in range(12)),
                "LQ_vs_LA_different_committed_models": sum(
                    arm_rows["LQ"][i]["predicted_model"] != arm_rows["LA"][i]["predicted_model"]
                    for i in range(12)),
            }
    result = {"status": "DISCLOSED_REDUCED_GRAMMAR_ENGINEERING_ONLY",
              "limitations": "one learned edge, 4 structural semantic families, same-process scorer, 2-edge OOD distractors, family pseudoreplication, no F0",
              "train_curve": [{"n":n,"snapshot":train(n)["digest"],
                               "families":train(n)["distinct_families"],
                               "actions":train(n)["paid_train_actions"]}
                              for n in TRAIN_SIZES],
              "opportunity": conditioned_opportunity(),
              "snapshot_digest": snap["digest"], "rows": rows,
              "records_digest": digest(rows),
              "record_count": len(rows),
              "summary": summary, "deltas": deltas,
              "by_budget": by_budget, "policy_switch": switch}
    return result

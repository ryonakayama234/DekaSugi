"""GTHETA-v1 marginal law and injected-factor joint evaluator; synthetic only."""
import hashlib
import json
import math
from pathlib import Path
from .prf import phi

MODEL_SHA = "31124f2df3acb7bebc9b75705aa6ac2e33f3f796a6f55dfad210863e375d077a"
WEIGHT_NAMES = ("cluster", "law", "gate", "arm", "checkpoint", "episode")

class ModelUnknown(ValueError): pass

def load_model(path=None):
    if path is None:
        path = Path(__file__).parent / "normative" / "WORLD-CAL-GTHETA-20261111-01-model-candidates.json"
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != MODEL_SHA:
        raise ModelUnknown("Gtheta model bytes changed")
    model = json.loads(raw)
    scenarios = model["binary_joint_generator"]["scenarios"]
    if len(scenarios) != 3 or {x["id"] for x in scenarios} != {
        "GTHETA-BASE-01", "GTHETA-LOWCORR-01", "GTHETA-HIGHCORR-01"}:
        raise ModelUnknown("scenario mismatch")
    for s in scenarios:
        if abs(sum(s["weight_" + key] for key in WEIGHT_NAMES) - 1.0) > 1e-10:
            raise ModelUnknown("factor weights fail")
        if not 0 <= s["checkpoint_ar1"] < 1:
            raise ModelUnknown("AR coefficient invalid")
    return model

def _sigmoid(z):
    if z >= 0: return 1 / (1 + math.exp(-z))
    a = math.exp(z)
    return a / (1+a)

def _logit(p):
    if not (0 < p < 1): raise ModelUnknown("marginal probability out of range")
    return math.log(p/(1-p))

def trapezoid(values):
    if len(values) != 9: raise ModelUnknown("requires 9 checkpoints")
    return (0.5*values[0] + sum(values[1:-1]) + 0.5*values[-1]) / 8

def full_curve(endpoint):
    return tuple(_sigmoid(_logit(endpoint) - 1.5*(8-j)/8) for j in range(9))

def control_curve(endpoint, kappa):
    return tuple(_sigmoid(_logit(endpoint) - kappa*(8-j)/8) for j in range(9))

def solve_kappa(full_g1, full_g2, control_g1, control_g2, delta=0.20):
    def difference(k):
        return (trapezoid(full_g1) - trapezoid(control_curve(control_g1,k)) +
                trapezoid(full_g2) - trapezoid(control_curve(control_g2,k))) / 2
    lo, hi = 0.0, 8.0
    if not difference(lo) <= delta <= difference(hi):
        raise ModelUnknown("slope root not bracketed")
    for _ in range(64):
        mid = (lo+hi)/2
        if difference(mid) < delta: lo = mid
        else: hi = mid
    if abs(difference(hi) - delta) > 1e-10:
        raise ModelUnknown("slope root residual")
    return hi

def marginal_table(model):
    gen = model["binary_joint_generator"]
    p = model["planning_alternative"]["fixed_candidates"]
    endpoints = (p["G1_star"], p["G2_star"])
    contrast = p["Contrast_star"]
    full = [full_curve(x) for x in endpoints]
    result = {"FULL": tuple(full)}
    for arm, deficit in zip(gen["control_strength_order"], gen["control_endpoint_deficit_additions"]):
        e1, e2 = (x - contrast - deficit for x in endpoints)
        k = solve_kappa(*full, e1, e2, p["Delta_star"])
        result[arm] = (control_curve(e1,k), control_curve(e2,k))
    return result

def ar1_path(innovations, rho: float):
    if len(innovations) != 9 or not 0 <= rho < 1:
        raise ModelUnknown("invalid AR path")
    values = [float(innovations[0])]
    for z in innovations[1:]:
        values.append(rho*values[-1]+math.sqrt(1-rho*rho)*float(z))
    return tuple(values)

def binary_outcome(scenario, factors: dict[str,float], probability: float):
    if not (0 < probability < 1): raise ModelUnknown("invalid threshold")
    if any(k not in factors or not math.isfinite(factors[k]) for k in WEIGHT_NAMES):
        raise ModelUnknown("incomplete nonfinite factors")
    latent = sum(math.sqrt(scenario["weight_"+k]) * factors[k] for k in WEIGHT_NAMES)
    return int(phi(latent) <= probability)

def aggregate_law(y):
    # y[arm][gate] = [9 rows x 4 episodes]. All same-Y contrasts.
    scores = {}
    for arm, gates in y.items():
        if len(gates) != 2: raise ModelUnknown("two gates required")
        curves = []
        endpoints = []
        for gate in gates:
            if len(gate)!=9 or any(len(v)!=4 for v in gate):
                raise ModelUnknown("9x4 outcomes required")
            values=[sum(v)/4 for v in gate]
            curves.append(trapezoid(values))
            endpoints.append(values[-1])
        scores[arm] = ((curves[0]+curves[1])/2, endpoints[0],endpoints[1])
    controls=("H+","FIXED-IF","PRED-ONLY","REC","RANK-ONLY","LOOKUP","OFF")
    return {"deltas":tuple(scores["FULL"][0]-scores[a][0] for a in controls),
            "g1":scores["FULL"][1], "g2":scores["FULL"][2],
            "contrast":scores["FULL"][1]-max(scores[a][1] for a in controls)}

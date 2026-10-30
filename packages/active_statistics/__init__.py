"""ACTIVE-001 P3: source-independent *invented* bounded-IID statistics preflight.

This is NOT a scientific scorer. No learner episode, target, Oracle answer,
heldout label, historic experiment or official seed is imported or read.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
import random
import statistics

SCHEMA = "active001-statistics-invented-only/1"
ALPHA = 0.05
DELTA = 0.05
BETA = 0.20
CONFIRMATORY_N_DRAFT = 4096
SIMULATION_SEED = 20261031


def _betacf(a: float, b: float, x: float) -> float:
    """Standard continued fraction for regularized incomplete beta."""
    floor = 1e-300
    qab, qap, qam = a + b, a + 1., a - 1.
    c, d = 1., 1. - qab*x/qap
    if abs(d) < floor:
        d = floor
    d = 1. / d
    h = d
    for m in range(1, 501):
        m2 = 2*m
        aa = m*(b-m)*x / ((qam+m2)*(a+m2))
        d = 1. + aa*d
        if abs(d) < floor:
            d = floor
        c = 1. + aa/c
        if abs(c) < floor:
            c = floor
        d = 1. / d
        h *= d*c
        aa = -(a+m)*(qab+m)*x / ((a+m2)*(qap+m2))
        d = 1. + aa*d
        if abs(d) < floor:
            d = floor
        c = 1. + aa/c
        if abs(c) < floor:
            c = floor
        d = 1. / d
        factor = d*c
        h *= factor
        if abs(factor-1.) < 2e-13:
            return h
    raise ArithmeticError("incomplete-beta continued fraction did not converge")


def _regbeta(a: float, b: float, x: float) -> float:
    if x <= 0.:
        return 0.
    if x >= 1.:
        return 1.
    factor = math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b) +
                      a*math.log(x) + b*math.log1p(-x))
    if x < (a+1.)/(a+b+2.):
        return factor*_betacf(a,b,x)/a
    return 1. - factor*_betacf(b,a,1.-x)/b


def _student_t_cdf(t: float, df: int) -> float:
    if type(df) is not int or df < 1 or not math.isfinite(t):
        raise ValueError("invalid t or degrees of freedom")
    if t == 0.:
        return 0.5
    x = df/(df+t*t)
    half_tail = 0.5*_regbeta(df/2., 0.5, x)
    return 1.-half_tail if t > 0. else half_tail


@lru_cache(maxsize=32)
def student_t_critical(df: int, *, alpha: float = ALPHA) -> float:
    """Exact numerical inverse of Student t CDF; no SciPy dependency."""
    if type(df) is not int or not 1 <= df <= 10_000:
        raise ValueError("invalid df")
    if type(alpha) is not float or not 0. < alpha < 1.:
        raise ValueError("invalid alpha")
    target = 1. - alpha/2.
    lo, hi = 0., 1.
    while _student_t_cdf(hi, df) < target:
        hi *= 2.
        if hi > 1e9:
            raise ArithmeticError("t quantile overflow")
    for _ in range(64):
        mid = (lo+hi)/2.
        if _student_t_cdf(mid, df) < target:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2.


@dataclass(frozen=True, slots=True)
class Interval:
    n: int
    mean: float
    lower: float
    upper: float
    positive_evidence: bool
    status: str


def _validate_differences(differences: tuple[float, ...]) -> None:
    if (type(differences) is not tuple or
        not 2 <= len(differences) <= 10_000 or
        any(type(d) not in (float, int) or
            not math.isfinite(d) or not -1. <= d <= 1.
            for d in differences)):
        raise ValueError("expected bounded IID task-level differences in [-1,1]")


def paired_t_interval(differences: tuple[float, ...]) -> Interval:
    """Two-sided 95% Student-t CI on ONE IID task-level difference per draw.

    Five B1 RNG replicates, if present, MUST already be averaged WITHIN the
    task before calling. Audit 64 inputs are NEVER 64 independent task units.
    """
    _validate_differences(differences)
    n = len(differences)
    mean = math.fsum(differences)/n
    # EXACT-equality constant-sample guard comes BEFORE floating-point
    # centering: fsum(values)/n can round away from the repeated input,
    # giving a spurious tiny variance and a false-positive t interval.
    is_constant = all(d == differences[0] for d in differences[1:])
    variance = (0. if is_constant else
                math.fsum((d-mean)**2 for d in differences)/(n-1))
    if is_constant or variance == 0.:
        # No Student-t uncertainty estimate is available: a constant positive
        # sample can arise from a mean-zero, rare-loss discrete IID law.
        # Return the vacuous known range of a bounded mean, not an estimated
        # t interval; NEVER claim a positive effect from this status.
        return Interval(n, mean, -1., 1., False, "zero_sample_variance")
    margin = student_t_critical(n-1)*math.sqrt(variance/n)
    return Interval(n, mean, mean-margin, mean+margin, mean-margin > 0., "computed")


def hoeffding_interval(differences: tuple[float, ...]) -> Interval:
    """Conservative two-sided 95% IID CI using known bounded range 2."""
    _validate_differences(differences)
    n = len(differences)
    mean = math.fsum(differences)/n
    margin = math.sqrt(2.*math.log(2./ALPHA)/n)
    return Interval(n, mean, mean-margin, mean+margin,
                    mean-margin > 0., "computed_conservative")


def hoeffding_sufficient_n(*, delta: float = DELTA,
                           alpha: float = ALPHA,
                           beta: float = BETA) -> int:
    """Analytic SUFFICIENT n for >=1-beta positive-claim probability.

    Uses Hoeffding twice for bounded IID D_i in [-1,1], two-sided alpha CI.
    This is neither a minimal sample size nor a rule to change N after scores.
    """
    if (any(type(x) is not float for x in (delta, alpha, beta)) or
        not 0. < delta <= 1. or
        not 0. < alpha < 1. or not 0. < beta < 1.):
        raise ValueError("invalid planned positive effect/alpha/beta")
    radius = (math.sqrt(2.*math.log(2./alpha)) +
              math.sqrt(2.*math.log(1./beta)))/delta
    return math.ceil(radius**2)


def nominal_normal_positive_power(n: int, *, delta: float = DELTA,
                                  sigma: float = 1.) -> float:
    """Planning approximation, NOT exact finite-n t power/coverage."""
    if (type(n) is not int or n < 2 or
        type(delta) is not float or type(sigma) is not float or
        not 0. <= delta <= 1. or not 0. < sigma <= 1.):
        raise ValueError("invalid planning inputs")
    zcrit = statistics.NormalDist().inv_cdf(1.-ALPHA/2.)
    z = math.sqrt(n)*delta/sigma
    return statistics.NormalDist().cdf(z-zcrit)


_SYNTHETIC_LAWS: tuple[tuple[str, float], ...] = (
    ("all_zero_null", 0.),
    ("rademacher_null", 0.),
    # Adversarial null: 99.99% tiny positive, 0.01% -1. The
    # *population* mean is exactly zero; all-positive samples are common.
    ("rare_negative_null", 0.),
    ("rademacher_positive_5pp", 0.05),
    ("sparse_positive_5pp", 0.05),
    ("point_mass_heavy_tails_5pp", 0.05),
    ("rademacher_negative_5pp", -0.05),
)


def _draw(rng: random.Random, law: str) -> float:
    u = rng.random()
    if law == "all_zero_null":
        return 0.
    if law == "rademacher_null":
        return 1. if u < .5 else -1.
    if law == "rare_negative_null":
        return 1./9999. if u < .9999 else -1.
    if law == "rademacher_positive_5pp":
        return 1. if u < .525 else -1.
    if law == "sparse_positive_5pp":
        return 1. if u < .05 else 0.
    if law == "point_mass_heavy_tails_5pp":
        return 1. if u < .125 else -1. if u < .20 else 0.
    if law == "rademacher_negative_5pp":
        return 1. if u < .475 else -1.
    raise ValueError("unknown invented law")


def simulate_invented(*, n: int, repeats: int = 100,
                      seed: int = SIMULATION_SEED) -> list[dict[str, object]]:
    """Monte Carlo ONLY on explicitly invented difference distributions."""
    if type(n) is not int or n not in (512, 4096, 8138):
        raise ValueError("only prereviewed invented n values")
    if type(repeats) is not int or not 1 <= repeats <= 200:
        raise ValueError("invented MC repeats must be 1..200")
    if type(seed) is not int or not 0 <= seed < 2**63:
        raise ValueError("invalid invented simulation seed")
    out = []
    for law, truth in _SYNTHETIC_LAWS:
        t_cover = h_cover = t_positive = h_positive = t_zero_var = 0
        for replica in range(repeats):
            rng = random.Random(f"active001-p3-INVENTED:{seed}:{n}:{law}:{replica}")
            diffs = tuple(_draw(rng, law) for _ in range(n))
            tci = paired_t_interval(diffs)
            hci = hoeffding_interval(diffs)
            t_cover += tci.lower <= truth <= tci.upper
            h_cover += hci.lower <= truth <= hci.upper
            # Only an inferentially computed CI can provide positive
            # evidence; status=zero_sample_variance is always STOP.
            t_positive += tci.status == "computed" and tci.positive_evidence
            h_positive += hci.positive_evidence
            t_zero_var += tci.status == "zero_sample_variance"
        out.append({
            "law": law, "invented_true_mean": truth, "n": n,
            "mc_repeats": repeats,
            "t_coverage_fraction": t_cover/repeats,
            "hoeffding_coverage_fraction": h_cover/repeats,
            "t_positive_fraction": t_positive/repeats,
            "hoeffding_positive_fraction": h_positive/repeats,
            "t_zero_sample_variance": t_zero_var,
        })
    return out


def invented_p3_report(*, repeats: int = 100) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "role": "invented task-differences ONLY; no official scientific outcomes",
        "seed": SIMULATION_SEED, "mc_repeats": repeats,
        "proposed_n_t": CONFIRMATORY_N_DRAFT,
        "alpha": ALPHA, "delta_planning": DELTA,
        "nominal_normal_sigma1_power_at_4096":
            nominal_normal_positive_power(CONFIRMATORY_N_DRAFT),
        "hoeffding_sufficient_n": hoeffding_sufficient_n(),
        "hoeffding_margin_at_4096": math.sqrt(2*math.log(2/ALPHA)/4096),
        "distributions": [*simulate_invented(n=512, repeats=repeats),
                          *simulate_invented(n=4096, repeats=repeats),
                          *simulate_invented(n=8138, repeats=repeats)],
        "scope_limitation": (
            "Independently invented bounded-IID difference laws; fixed split "
            "and source custody NOT confirmed; t interval not uniform finite "
            "sample coverage; MC error and sample-size selection must be "
            "separately audited; 5 B1 repeats remain ONE task unit"),
        "official_scored_active001_tasks": 0,
        "formal_source_or_seed_freeze": False,
    }


def main() -> int:
    print(json.dumps(invented_p3_report(), sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

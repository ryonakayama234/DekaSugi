"""EXP-COEV-001 F0-C prospective, score-free paired-test power design.

No target labels, no Oracle, no DEV/FINAL scoring. These calculations are
NORMAL approximations under explicitly hypothetical parameters, not results.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import erfc, log, sqrt

@dataclass(frozen=True, slots=True)
class Design:
    tasks: int = 2048
    threshold: float = 0.10
    alpha: float = 0.05

    def __post_init__(self) -> None:
        if (type(self.tasks) is not int or not 1 <= self.tasks <= 100000 or
                type(self.threshold) is not float or not 0 < self.threshold < 1 or
                type(self.alpha) is not float or not 0 < self.alpha < 1):
            raise ValueError("Unapproved paired study design")

def paired_hoeffding_radius(design: Design = Design()) -> float:
    """Two-sided 1-alpha half-width for independent D in [-1,1]."""
    if type(design) is not Design:
        raise ValueError("Invalid design")
    return sqrt(2 * log(2 / design.alpha) / design.tasks)

def approximate_joint_success_power(
        true_lift: float, discordance: float,
        design: Design = Design(), *, design_effect: float = 1.0) -> float:
    """Pr[Dbar>=tau and Dbar-Hoeffding_radius>0] under normal approximation.

    D=+1 if only learned arm correct, -1 if only baseline correct, else zero.
    E[D]=true_lift, P(|D|=1)=discordance; Var(D)=q-delta^2.
    design_effect is a *hypothetical* variance inflation, not a measured ICC.
    The resulting formula is NOT valid without independent task-level sampling
    or a justified variance estimator, especially after target-class reuse.
    """
    if type(design) is not Design or type(true_lift) is not float or type(discordance) is not float:
        raise ValueError("Invalid scenario types")
    if (not -1 <= true_lift <= 1 or not 0 <= discordance <= 1 or
            discordance < abs(true_lift) or type(design_effect) is not float or
            not 1 <= design_effect <= 1000):
        raise ValueError("Impossible paired probability / design effect")
    variance = discordance - true_lift * true_lift
    required = max(design.threshold, paired_hoeffding_radius(design))
    if variance == 0:
        return float(true_lift >= required)
    standard_error = sqrt(variance * design_effect / design.tasks)
    return 0.5 * erfc((required - true_lift) / (sqrt(2) * standard_error))

def illustrative_design_table(design: Design = Design()) -> dict[str, object]:
    """Fixed prior assumptions only; no learned or heldout outcomes."""
    if type(design) is not Design:
        raise ValueError("Invalid design")
    scenarios = []
    for lift in (0.10, 0.12, 0.15):
        for discordance in (0.20, 0.50, 0.80):
            for de in (1.0, 2.0, 4.0):
                scenarios.append({
                    "assumed_true_lift": lift, "assumed_discordance": discordance,
                    "hypothetical_design_effect": de,
                    "normal_approx_joint_pass_probability": round(
                        approximate_joint_success_power(lift,discordance,design,design_effect=de),6)
                })
    return {
        "scope":"ANALYTIC_DESIGN_ONLY_NOT_A_SCIENTIFIC_RESULT",
        "assumptions":"paired task D in {-1,0,1}; hypothetical delta,q,variance inflation",
        "tasks":design.tasks,"threshold":design.threshold,"alpha":design.alpha,
        "independent_hoeffding_halfwidth":round(paired_hoeffding_radius(design),8),
        "primary_unit":"task, never 64 correlated audit inputs",
        "class_pool_target":"fixed independently sealed semantic-class distribution, not universal novel-class inference",
        "scenarios":scenarios,
        "no_score_or_activation":True,
    }

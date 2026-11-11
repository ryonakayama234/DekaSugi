"""Integrated conditional synthetic power engine. No work occurs at import.

Production entry requires CAL_AUTHORIZED role capability supplied by the
independent launcher. An explicit, non-secret synthetic fixture can exercise
ONE complete repetition in pre-CAL CI; full scan is never run by tests/CI.
No holdout instances, scores, or seeds are read or generated here.
"""
import math
from dataclasses import dataclass

from .gtheta import MODEL_SHA, load_model, marginal_table, aggregate_law
from .inference import (InferenceUnknown, ht, syg, bootstrap_vectors,
                        studentized_max_t, one_sided_lower, ten_and_gates,
                        bootstrap_vectors_cached)
from .power_route import (R_REQUIRED, BOOTSTRAPS, SCENARIOS, PowerUnknown,
                          lower_for_completed_counts, cost)
from .prf import draw_digest, uniform53, box_muller
from .sampford import waterfill, SamplingUnknown
from .sampford_grouped import grouped_inclusions, draw_grouped

ARMS = ("FULL","OFF","PRED-ONLY","REC","RANK-ONLY","FIXED-IF","LOOKUP","H+")
CONTROLS = ("H+","FIXED-IF","PRED-ONLY","REC","RANK-ONLY","LOOKUP","OFF")
GATES = ("G1","G2")
CHECKPOINTS=9
EPISODES=4


@dataclass(frozen=True)
class CALAuthorization:
    """Verified, process-local capability; construction is NOT authorization.

    Only a separately reviewed OS-isolated launcher should create this after
    authenticating its role, approved source manifest and Owner CAL state.
    """
    role: str
    algorithm_digest: str
    approved: bool


class _CounterDraws:
    def __init__(self, key, scenario, n, repetition):
        if not isinstance(key,bytes) or len(key)!=32:
            raise PowerUnknown("STOP_UNKNOWN: injected 256-bit key required")
        if not isinstance(repetition,int) or repetition<0:
            raise PowerUnknown("STOP_UNKNOWN: invalid repetition")
        self.key,self.scenario,self.n,self.repetition=key,scenario,n,repetition
        self.next_index={}
        self.spare={}
    def uniform(self,stage):
        ix=self.next_index.get(stage,0)
        self.next_index[stage]=ix+1
        return uniform53(draw_digest(self.key,"sha256:"+MODEL_SHA,
                                     self.scenario,self.n,self.repetition,stage,ix))
    def normal(self,stage):
        if stage in self.spare:return self.spare.pop(stage)
        a,b=box_muller(self.uniform(stage),self.uniform(stage))
        self.spare[stage]=b
        return a
    def uniforms(self,stage):
        while True:yield self.uniform(stage)


def _inputs(q,parents,n,scenario):
    if scenario not in SCENARIOS or not isinstance(n,int) or not 2<=n<=len(q):
        raise PowerUnknown("STOP_UNKNOWN: invalid n/scenario")
    if len(q)!=len(parents) or any(not isinstance(p,str) or not p for p in parents):
        raise PowerUnknown("STOP_UNKNOWN: invalid parent metadata")
    if any(not isinstance(x,(float,int)) or not math.isfinite(x) or x<=0 for x in q):
        raise PowerUnknown("STOP_UNKNOWN: invalid design q")
    if abs(math.fsum(q)-1.0)>1e-10:
        raise PowerUnknown("STOP_UNKNOWN: q not normalized")
    # Private caller must have sorted canonical law IDs, checked inside role
    # boundary. This pure engine receives only aligned ordered opaque vectors.


def _synthetic_joint_scores(sample, parents, table, scenario, draws):
    """Shared latent factors, one Y array per law across all components."""
    ws={name:math.sqrt(scenario["weight_"+name]) for name in
        ("cluster","law","gate","arm","checkpoint","episode")}
    rho=scenario["checkpoint_ar1"]
    # Every independent factor is addressed by its canonical scope identifiers.
    # Drawing only selected laws must not change another law/cluster normal
    # because a preceding selected unit happened to be absent this time.
    def scoped(kind,*parts):
        return kind+"".join("|"+str(len(str(v)))+":"+str(v) for v in parts)
    cluster={c:draws.normal(scoped("cluster",c))
             for c in sorted({parents[i] for i in sample})}
    gate={(c,g):draws.normal(scoped("gate",c,g))
          for c in sorted(cluster) for g in range(2)}
    result={}
    for i in sample:
        z_l=draws.normal(scoped("law",i))
        by_arm={}
        for arm in ARMS:
            z_a=draws.normal(scoped("arm",i,arm))
            gates=[]
            for g in range(2):
                ar=[]
                for j in range(CHECKPOINTS):
                    z=draws.normal(scoped("checkpoint",i,g,arm))
                    ar.append(z if j==0 else rho*ar[-1]+math.sqrt(1-rho*rho)*z)
                rows=[]
                fixed=(ws["cluster"]*cluster[parents[i]]+ws["law"]*z_l+
                       ws["gate"]*gate[(parents[i],g)]+ws["arm"]*z_a)
                for j in range(CHECKPOINTS):
                    baseline=fixed+ws["checkpoint"]*ar[j]
                    observations=[]
                    for episode in range(EPISODES):
                        latent=baseline+ws["episode"]*draws.normal(
                            scoped("episode",i,g,arm,j))
                        # Required normative binary64 Phi=erfc; no latent
                        # substitutions or independent Contrast draw.
                        probability=.5*math.erfc(-latent/math.sqrt(2))
                        if not math.isfinite(probability):
                            raise PowerUnknown("STOP_UNKNOWN: CDF nonfinite")
                        observations.append(int(probability<=table[arm][g][j]))
                    rows.append(tuple(observations))
                gates.append(tuple(rows))
            by_arm[arm]=tuple(gates)
        result[i]=aggregate_law(by_arm)
    return result


def _ht_b(sample,q,pi,scores,gate):
    return {arm:ht(sample,q,pi,{i:scores[i]["b_by_arm"][arm][gate] for i in sample})
            for arm in ARMS}


def _draw_bootstrap_clusters(sample,parents,draws):
    clusters=tuple(sorted({parents[i] for i in sample}))
    k=len(clusters)
    if k<2:raise PowerUnknown("STOP_UNKNOWN: fewer than two observed parent clusters")
    return tuple(tuple(clusters[min(k-1,int(draws.uniform("bootstrap")*k))]
                       for _ in range(k)) for _ in range(BOOTSTRAPS))


def run_one_repetition(*, q, parent_ids, n, scenario_id, repetition, key,
                       synthetic_fixture=False, authorization=None,
                       cached_design=None):
    """All components of EXACTLY ONE power repetition; no implicit looping.

    A fixture is public and must be explicitly flagged. Production requires a
    verified calculator process capability, not an in-process learner flag.
    """
    if not synthetic_fixture and not (isinstance(authorization,CALAuthorization)
            and authorization.approved and
            authorization.role=="BLIND_DESIGN_CALCULATOR" and
            authorization.algorithm_digest.startswith("sha256:")):
        raise PowerUnknown("STOP_UNKNOWN: CAL_AUTHORIZED process capability absent")
    _inputs(q,parent_ids,n,scenario_id)
    try:
        if cached_design is None:
            pi=waterfill(q,n)
            _,pij=grouped_inclusions(pi)
        else:
            pi,pij=cached_design
            if len(pi)!=len(q) or abs(math.fsum(pi)-n)>1e-10:
                raise PowerUnknown("STOP_UNKNOWN: bad cached design")
        draws=_CounterDraws(key,scenario_id,n,repetition)
        sample=draw_grouped(pi,draws.uniforms("pps"))
        model=load_model()
        scenario=next(s for s in model["binary_joint_generator"]["scenarios"]
                      if s["id"]==scenario_id)
        scores=_synthetic_joint_scores(sample,parent_ids,marginal_table(model),
                                       scenario,draws)
        vectors={i:tuple(scores[i]["deltas"])+(scores[i]["g1"],scores[i]["g2"])
                 for i in sample}
        # Every dimension has the same PPS inclusion, design variance and
        # same cluster bootstrap draw: never iid episode/law resampling.
        for dim in range(9):
            variance=syg(sample,q,pi,pij,{i:vectors[i][dim] for i in sample})
            if variance<=0 or not math.isfinite(variance):
                raise PowerUnknown("STOP_UNKNOWN: degenerate SYG variance")
        bootstrap_draws=_draw_bootstrap_clusters(sample,parent_ids,draws)
        pts,replicates=bootstrap_vectors_cached(sample,q,pi,vectors,parent_ids,bootstrap_draws)
        ci=studentized_max_t(pts[:7],tuple(r[:7] for r in replicates),alpha=.0125)
        g1lower=one_sided_lower(pts[7],replicates,7,alpha=.00625)
        g2lower=one_sided_lower(pts[8],replicates,8,alpha=.00625)
        b1=_ht_b(sample,q,pi,scores,0)
        b2=_ht_b(sample,q,pi,scores,1)
        both={arm:(b1[arm]+b2[arm])/2 for arm in ARMS}
        contrast=both["FULL"]-max(both[arm] for arm in CONTROLS)
        family_diag=(b1["FULL"]-max(b1[a] for a in CONTROLS),
                     b2["FULL"]-max(b2[a] for a in CONTROLS))
        gates,all_success=ten_and_gates(pts[:7],ci,pts[7],pts[8],
                                        g1lower,g2lower,contrast)
        k2_ci=studentized_max_t(pts[:7],tuple(r[:7] for r in replicates),alpha=.05)[3]
        return {"and":all_success,"ten_components":gates,
                "contrast":contrast,"family_contrast_descriptive":family_diag,
                "g1":pts[7],"g2":pts[8],"main_intervals":ci,
                "k2_rec_interval_95":k2_ci,
                "k2_equivalence_descriptive":k2_ci[0]>=-.05 and k2_ci[1]<=.05,
                "sample_size":len(sample),"observed_parent_clusters":len(set(parent_ids[i] for i in sample)),
                "bootstrap_count":BOOTSTRAPS}
    except (InferenceUnknown,SamplingUnknown,ValueError,OverflowError,
            ZeroDivisionError) as exc:
        raise PowerUnknown("STOP_UNKNOWN: integrated repetition failed: "+str(exc)) from exc


def scan_authorized(*, q, parent_ids, key, authorization, b_final):
    """The future CAL-only R=10,000 x 3 x ascending-n scan; never pre-CAL.

    No simulation is called unless authorization arrives from an audited,
    OS-isolated BLIND_DESIGN_CALCULATOR launcher. No skip/fast pass/adaptive
    R or 999 substitutions. Any incomplete n fails closed.
    """
    if not (isinstance(authorization,CALAuthorization) and authorization.approved
            and authorization.role=="BLIND_DESIGN_CALCULATOR"
            and len(authorization.algorithm_digest)==71):
        raise PowerUnknown("STOP_UNKNOWN: CAL authorization missing")
    N=len(q)
    for n in range(2,min(N,512)+1):
        design=(waterfill(q,n),None)
        design=(design[0],grouped_inclusions(design[0])[1])
        counts={}
        for scenario in SCENARIOS:
            successes=0
            for r in range(R_REQUIRED):
                if run_one_repetition(q=q,parent_ids=parent_ids,n=n,
                        scenario_id=scenario,repetition=r,key=key,
                        authorization=authorization,cached_design=design)["and"]:
                    successes+=1
            counts[scenario]=successes
        lower=lower_for_completed_counts(counts)
        if lower>=.80 and cost(n,b_final)<=20_000_000:
            return {"route":"STATISTICAL","n_required":n,
                    "power_lower_bound":lower,"cost_cap_check":True}
    # A complete finite descriptive evaluation is a separately authorized
    # route; the simulation alone cannot assert it.
    return {"route":"STOP_UNKNOWN","n_required":None,
            "power_lower_bound":None,"cost_cap_check":False}

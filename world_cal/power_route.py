"""Pure mathematical gates. No power simulation is executed by this module."""
import math

R_REQUIRED = 10_000
BOOTSTRAPS = 999
SCENARIOS = ("GTHETA-BASE-01","GTHETA-LOWCORR-01","GTHETA-HIGHCORR-01")
class PowerUnknown(ValueError):pass

def cost(n,b_final=6144,t_horizon=24):
    if not isinstance(n,int) or n<2 or b_final not in (4096,6144) or t_horizon!=24:
        raise PowerUnknown("unapproved cost inputs")
    return 250_000+8*b_final+2*20*t_horizon+8*2*9*4*t_horizon*n

def _betacf(a,b,x):
    fpmin=1e-300
    qab=a+b;qap=a+1;qam=a-1
    c=1.0;d=1.0-qab*x/qap
    if abs(d)<fpmin:d=fpmin
    d=1.0/d;h=d
    for m in range(1,1001):
        m2=2*m
        aa=m*(b-m)*x/((qam+m2)*(a+m2))
        d=1+aa*d;d=fpmin if abs(d)<fpmin else d
        c=1+aa/c;c=fpmin if abs(c)<fpmin else c
        d=1/d;h*=d*c
        aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2))
        d=1+aa*d;d=fpmin if abs(d)<fpmin else d
        c=1+aa/c;c=fpmin if abs(c)<fpmin else c
        d=1/d;delta=d*c;h*=delta
        if abs(delta-1)<1e-14:return h
    raise PowerUnknown("incomplete beta did not converge")

def regularized_beta(a,b,x):
    if x<=0:return 0.0
    if x>=1:return 1.0
    bt=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
    if x<(a+1)/(a+b+2):return bt*_betacf(a,b,x)/a
    return 1-bt*_betacf(b,a,1-x)/b

def cp_lower(successes, repetitions=R_REQUIRED, alpha=0.01):
    if repetitions!=R_REQUIRED or not isinstance(successes,int) or not 0<=successes<=repetitions:
        raise PowerUnknown("MC repetition count not approved")
    if successes==0:return 0.0
    if successes==repetitions:return alpha**(1/repetitions)
    lo,hi=0.0,1.0
    for _ in range(64):
        mid=(lo+hi)/2
        if regularized_beta(successes,repetitions-successes+1,mid)<alpha:lo=mid
        else:hi=mid
    return hi

def lower_for_completed_counts(scenario_counts):
    if set(scenario_counts)!=set(SCENARIOS):raise PowerUnknown("incomplete scenarios")
    return min(cp_lower(scenario_counts[s]) for s in SCENARIOS)

def route_from_completed_scan(counts_by_n,N_eligible,b_final=6144,cost_cap=20_000_000):
    """Requires COMPLETE per-n scenario counts; never fills in missing n."""
    end=min(N_eligible,512)
    if not 2<=end: return {"route":"STOP_UNKNOWN","n_required":None}
    for n in range(2,end+1):
        if n not in counts_by_n:return {"route":"STOP_UNKNOWN","n_required":None}
        try:lower=lower_for_completed_counts(counts_by_n[n])
        except PowerUnknown:return {"route":"STOP_UNKNOWN","n_required":None}
        if lower>=.80 and cost(n,b_final)<=cost_cap:
            return {"route":"STATISTICAL","n_required":n,"power_lower_bound":lower}
    # Finite-descriptive requires real complete H evaluation; cannot be inferred here.
    return {"route":"STOP_UNKNOWN","n_required":None}

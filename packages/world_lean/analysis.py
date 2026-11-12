"""Pure deterministic statistics. No seed generation, task loading or evaluation IO."""
from fractions import Fraction
from math import comb
from random import Random

ARMS=('FULL','OFF','STATIC-RANK','LOOKUP')
B=(0,512,1024,2048,4096)
N_SEEDS=16
MAIN_QUERY_DENOMINATOR=48
BOOTSTRAP=9999

def aulc(counts: tuple[int,...]) -> Fraction:
    if type(counts) is not tuple or len(counts)!=len(B) or any(type(v) is not int or not 0<=v<=48 for v in counts):
        raise ValueError('five checkpoint success counts in 0..48 required')
    return sum((Fraction((B[i+1]-B[i])*(counts[i]+counts[i+1]),2*4096*48)
                for i in range(len(B)-1)),Fraction())

def binomial_one_sided(wins: int) -> Fraction:
    if type(wins) is not int or not 0<=wins<=N_SEEDS: raise ValueError('wins')
    return Fraction(sum(comb(N_SEEDS,j) for j in range(wins,N_SEEDS+1)),2**N_SEEDS)

def _percentile(sorted_values: list[Fraction], q_num: int, q_den: int) -> Fraction:
    # Frozen linear interpolation at (N-1)*q; exact Fraction arithmetic.
    pos=Fraction((len(sorted_values)-1)*q_num,q_den)
    lo=pos.numerator//pos.denominator
    if lo==len(sorted_values)-1:return sorted_values[lo]
    return sorted_values[lo]+(pos-lo)*(sorted_values[lo+1]-sorted_values[lo])

def paired_summary(per_seed: tuple[dict,...], bootstrap_seed: int) -> dict:
    if len(per_seed)!=N_SEEDS:raise ValueError('exactly 16 paired seeds')
    if type(bootstrap_seed) is not int:raise ValueError('fixed integer bootstrap seed')
    values={arm:tuple(aulc(tuple(p[arm])) for p in per_seed) for arm in ARMS}
    result={}
    rng=Random(bootstrap_seed)
    # Generate the same 9999 index tuples and apply to all 3 comparisons.
    draw=tuple(tuple(rng.randrange(N_SEEDS) for _ in range(N_SEEDS)) for _ in range(BOOTSTRAP))
    for control in ARMS[1:]:
        d=tuple(x-y for x,y in zip(values['FULL'],values[control]))
        mean=sum(d,Fraction())/N_SEEDS
        ordered=sorted(d)
        bs=sorted(sum((d[i] for i in ix),Fraction())/N_SEEDS for ix in draw)
        wins=sum(x>0 for x in d)
        result[control]={
            'deltas':[str(v) for v in d],
            'mean':str(mean),
            'median':str((ordered[7]+ordered[8])/2),
            'wins':wins,
            'one_sided_sign_p':str(binomial_one_sided(wins)),
            'bootstrap_95pct_ci':[str(_percentile(bs,25,1000)),str(_percentile(bs,975,1000))],
            'mean_ge_0.10':mean>=Fraction(1,10),'sign_pass':wins>=12}
    return {'checkpoint_b':list(B),'per_arm_aulc':{a:[str(v) for v in values[a]] for a in ARMS},
            'paired':result,'main_effect_gate':all(x['mean_ge_0.10'] and x['sign_pass'] for x in result.values()),
            'bootstrap_method':'9999 paired resamples, Python MT19937 Random(seed), exact linear percentile at (N-1)*q'}

def scientific_decision(per_seed: tuple[dict,...], *, groups: dict[str,tuple[int,int]],
                        ambiguous: tuple[int,int], usage_seed_count: int,
                        bootstrap_seed: int) -> dict:
    """Pure predeclared AND/STOP decision for *future authorized* completed data.

    No task/seed generation or evaluator access. Missing data raises instead of
    converting an incomplete experiment into zero-success outcomes.
    """
    expected=('true','false','with_copy','without_copy','p0','p1','p2','p3')
    if set(groups)!=set(expected):raise ValueError('all 8 secondary groups are mandatory')
    if len(per_seed)!=N_SEEDS:raise ValueError('incomplete paired seed data')
    if any(type(n) is not int or type(k) is not int or not 0<=n<=k or k==0
           for n,k in groups.values()):raise ValueError('group denominators')
    a,n=ambiguous
    if type(a) is not int or type(n) is not int or not 0<=a<=n or n==0:
        raise ValueError('ambiguous numerator/denominator')
    if type(usage_seed_count) is not int or not 0<=usage_seed_count<=N_SEEDS:
        raise ValueError('usage seeds')
    summary=paired_summary(per_seed,bootstrap_seed)
    last={arm:sum(p[arm][-1] for p in per_seed) for arm in ARMS}
    final={arm:Fraction(count,N_SEEDS*MAIN_QUERY_DENOMINATOR) for arm,count in last.items()}
    strongest=max(final[a] for a in ARMS[1:])
    group_rates={k:Fraction(*groups[k]) for k in expected}
    ambiguous_rate=Fraction(a,n)
    static_zero=Fraction(sum(p['STATIC-RANK'][0] for p in per_seed),N_SEEDS*48)
    static_aulc=Fraction(sum(Fraction(x) for x in summary['per_arm_aulc']['STATIC-RANK']),N_SEEDS)
    all_gates=(summary['main_effect_gate'] and final['FULL']>=Fraction(4,5)
        and final['FULL']-strongest>=Fraction(-1,20)
        and all(x>=Fraction(3,5) for x in group_rates.values())
        and ambiguous_rate<=Fraction(1,10) and usage_seed_count>=12)
    stops=[]
    if ambiguous_rate>Fraction(1,10):stops.append('SPEC_INSUFFICIENT')
    if usage_seed_count<12:stops.append('ACQUIRED_USAGE_INSUFFICIENT')
    if static_zero>=Fraction(9,10) and static_aulc>=Fraction(9,10):
        stops.append('STATIC_RANK_CEILING')
    for control in ('STATIC-RANK','OFF'):
        if Fraction(summary['paired'][control]['mean'])<Fraction(1,20):
            stops.append('SMALL_EFFECT_'+control)
    if final['FULL']-strongest<Fraction(-1,20) or final['FULL']<Fraction(3,5):
        stops.append('HARMFUL')
    status='LEAN_B_EFFICIENCY_CANDIDATE' if all_gates and not stops else (
        'STOP_DIAGNOSTIC' if stops else 'INCONCLUSIVE')
    return {'status':status,'all_AND_passed':all_gates and not stops,
            'stops':stops,'paired':summary,
            'final_success_fraction':{a:str(final[a]) for a in ARMS},
            'secondary_group_fraction':{k:str(group_rates[k]) for k in expected},
            'ambiguous_fraction':str(ambiguous_rate),'usage_seeds':usage_seed_count,
            'static_rank_b0_fraction':str(static_zero),
            'static_rank_aulc_mean_fraction':str(static_aulc),
            'notice':'Pure analyzer; does not certify scientific claims without independent audit/Owner decision.'}

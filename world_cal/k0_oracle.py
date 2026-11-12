"""K0-c / L90 deterministic accounting; full abstract search requires separate GO."""
import math

class OracleUnknown(ValueError):pass

def nearest_rank90(shortest_lengths):
    if not shortest_lengths or any((not isinstance(x,int) or x<0) for x in shortest_lengths):
        raise OracleUnknown("no complete shortest path lengths")
    z=sorted(shortest_lengths)
    return z[math.ceil(0.9*len(z))-1]

def saturation_upper(oracle_aulc, strongest_control_aulc, threshold=0.15):
    if not (0<=oracle_aulc<=1 and 0<=strongest_control_aulc<=1):
        raise OracleUnknown("incomplete oracle/control")
    return oracle_aulc-strongest_control_aulc<threshold

def k0_outcome(open_status,conditional_status,b_status,c_saturated):
    # Closed vocabularies: e.g. STOP_UNKNOWN or the nonempty string
    # 'UNKNOWN' in the c slot must never be interpreted as a truth value.
    if (open_status not in ("OPEN_LOOP_WINS","OPEN_LOOP_DOES_NOT_WIN") or
            conditional_status not in ("CONDITIONAL_WINS","CONDITIONAL_DOES_NOT_WIN") or
            b_status not in ("PASS","FAIL") or type(c_saturated) is not bool):
        return "STOP_UNKNOWN"
    if b_status=="FAIL" or c_saturated:
        return "STOP_K0"
    if open_status=="OPEN_LOOP_DOES_NOT_WIN" and conditional_status=="CONDITIONAL_WINS":
        return "K0A_WITNESS"
    return "K0A_NO_WITNESS"


def k0_result_outcome(open_result,conditional_result,b_result,c_result):
    """Consume status-bearing results; never read a partial oracle curve.

    This is a reducer, not a source/custody/completeness authenticator.
    Registered full K0-b/c currently cannot supply definitive results.
    """
    if any(type(r) is not dict for r in
           (open_result,conditional_result,b_result,c_result)):
        return "STOP_UNKNOWN"
    if c_result.get("status")!="COMPLETE":
        return "STOP_UNKNOWN"
    return k0_outcome(open_result.get("status"),conditional_result.get("status"),
                      b_result.get("status"),c_result.get("saturated"))

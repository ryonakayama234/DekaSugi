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
    if "UNKNOWN" in (open_status,conditional_status,b_status) or c_saturated is None:
        return "STOP_UNKNOWN"
    if b_status=="FAIL" or c_saturated:
        return "STOP_K0"
    if open_status=="OPEN_LOOP_DOES_NOT_WIN" and conditional_status=="CONDITIONAL_WINS":
        return "K0A_WITNESS"
    return "K0A_NO_WITNESS"

"""Owner-keyed PRF primitives. No secret, seed, or implicit random generation."""
import hashlib
import hmac
import math
import struct

class PRFError(ValueError): pass

def encode_parts(*parts):
    result = bytearray()
    for part in parts:
        if isinstance(part, int):
            if not 0 <= part < 2**64: raise PRFError("index out of range")
            value = struct.pack(">Q", part)
            marker = b"I"
        elif isinstance(part, str):
            value = part.encode("utf-8")
            marker = b"S"
        elif isinstance(part, bytes):
            value = part
            marker = b"B"
        else: raise PRFError("invalid domain component")
        result.extend(marker + struct.pack(">Q", len(value)) + value)
    return bytes(result)

def hmac_sha256(key: bytes, data: bytes) -> bytes:
    if not isinstance(key, bytes) or not isinstance(data, bytes):
        raise PRFError("bytes required")
    return hmac.new(key, data, hashlib.sha256).digest()

def draw_digest(key: bytes, model_digest: str, scenario: str, n: int,
                repetition: int, stage: str, draw_index: int) -> bytes:
    if len(key) != 32: raise PRFError("256-bit Owner key required")
    return hmac_sha256(key, encode_parts("WORLD-CAL-v1", model_digest, scenario,
                                         n, repetition, stage, draw_index))

def uniform53(digest: bytes) -> float:
    if len(digest) != 32: raise PRFError("expected SHA-256 digest")
    x = int.from_bytes(digest[:7], "big") >> 3
    u = (x + 0.5) / (1 << 53)
    if not math.isfinite(u) or u <= 0.0:
        raise PRFError('STOP_UNKNOWN: nonpositive/nonfinite PRF uniform')
    # Supervisor RQ-CAL-IMPL-02: binary64 rounding at the upper endpoint.
    # Only this representation boundary has a defined correction; all others STOP.
    if u >= 1.0:
        u = math.nextafter(1.0, 0.0)
    if not 0.0 < u < 1.0:
        raise PRFError('STOP_UNKNOWN: invalid corrected PRF uniform')
    return u

def box_muller(u1: float, u2: float) -> tuple[float, float]:
    if not (0 < u1 < 1 and 0 < u2 < 1): raise PRFError("uniform must be open interval")
    radius = math.sqrt(-2.0 * math.log(u1))
    return radius * math.cos(2*math.pi*u2), radius * math.sin(2*math.pi*u2)

def phi(z: float) -> float:
    if not math.isfinite(z): raise PRFError("nonfinite latent")
    return 0.5 * math.erfc(-z / math.sqrt(2))

"""RFC8785 JCS + Ed25519 receipt. No keys are created by this module."""
import hashlib
import re

KEYS=frozenset(("N_eligible","n_required","route","power_lower_bound",
                "cost_cap_check","algorithm_digest","split_digest"))
ENVELOPE_KEYS=frozenset(("signer_role","key_id","signature_algorithm","signature","payload_sha256"))
ROUTES=frozenset(("STATISTICAL","FINITE_DESCRIPTIVE","STOP_UNKNOWN"))
SHA_RE=re.compile(r"sha256:[0-9a-f]{64}\Z")
class ReceiptInvalid(ValueError):pass

def validate(payload):
    if set(payload)!=KEYS:raise ReceiptInvalid("payload must be exactly seven keys")
    if payload["route"] not in ROUTES:raise ReceiptInvalid("invalid route")
    if type(payload["cost_cap_check"]) is not bool:raise ReceiptInvalid("bad cost flag")
    if payload["N_eligible"] is not None and (type(payload["N_eligible"]) is not int or payload["N_eligible"]<0):
        raise ReceiptInvalid("invalid N")
    if payload["n_required"] is not None and (type(payload["n_required"]) is not int or payload["n_required"]<2):
        raise ReceiptInvalid("invalid n")
    if payload["power_lower_bound"] is not None:
        p=payload["power_lower_bound"]
        if type(p) is not float or not 0<=p<=1:raise ReceiptInvalid("invalid power")
    for k in ("algorithm_digest","split_digest"):
        if not isinstance(payload[k],str) or not SHA_RE.fullmatch(payload[k]):
            raise ReceiptInvalid("digest not yet audited/escrowed")
    if payload["route"]=="STOP_UNKNOWN" and (payload["n_required"] is not None or payload["power_lower_bound"] is not None):
        raise ReceiptInvalid("unknown cannot claim completed power")
    if payload["route"]=="STATISTICAL" and (payload["n_required"] is None or payload["power_lower_bound"] is None or not payload["cost_cap_check"]):
        raise ReceiptInvalid("incomplete statistical receipt")
    return payload

def canonical(payload):
    validate(payload)
    try:
        import rfc8785
        return rfc8785.dumps(payload)
    except ImportError as exc:
        raise ReceiptInvalid("pinned RFC8785 dependency missing") from exc

def make_envelope(payload, signer, key_id):
    """signer must be externally authorized Ed25519PrivateKey; never generated here."""
    raw=canonical(payload)
    sig=signer.sign(raw)
    return {"signer_role":"BLIND_DESIGN_CALCULATOR","key_id":key_id,
            "signature_algorithm":"Ed25519","signature":sig.hex(),
            "payload_sha256":"sha256:"+hashlib.sha256(raw).hexdigest()}

def verify_envelope(payload,envelope,public_key):
    if set(envelope)!=ENVELOPE_KEYS or envelope["signer_role"]!="BLIND_DESIGN_CALCULATOR" or envelope["signature_algorithm"]!="Ed25519":
        raise ReceiptInvalid("invalid envelope")
    raw=canonical(payload)
    if envelope["payload_sha256"]!="sha256:"+hashlib.sha256(raw).hexdigest():
        raise ReceiptInvalid("payload digest mismatch")
    try:
        public_key.verify(bytes.fromhex(envelope["signature"]),raw)
    except Exception as exc:
        raise ReceiptInvalid("Ed25519 verification failure") from exc
    return True

"""COEV F0-D: public-toy capability/query/transcript contract, NOT real custody.

Fixed public toy target and public query partition. Random per-process toy
capability and HMAC key exercise wire invariants but are not protected from
a same-process adversary. Never use as an official TRAIN/DEV/FINAL Oracle.
"""
from __future__ import annotations
from hashlib import sha256
import hmac
import json
import re
import secrets
from packages.concept_world import Program, execute, inputs, split_inputs

WIRE = "coev-f0d-toy-capability/1"
TOY_SEED = 2501
QUERY_LIMIT = 2
_MAX_BYTES = 1024
_HEX32 = re.compile(r"[0-9a-f]{32}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_TOY_TARGET = Program("contains_a", ("reverse",), ("upper",))
_FIELDS = frozenset(("wire","op","phase","arm","session","capability",
                    "sequence","nonce","input_id"))
_CLOSE_FIELDS = _FIELDS - frozenset(("input_id",))

def _canonical(obj: dict[str, object]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def _reject_duplicates(pairs: list[tuple[str,object]]) -> dict[str,object]:
    seen: dict[str,object] = {}
    for key,value in pairs:
        if key in seen:
            raise ValueError("duplicate key")
        seen[key]=value
    return seen

def _reject_number(value: str) -> None:
    raise ValueError("nonfinite JSON constant")

def _decode(frame: bytes) -> dict[str,object]:
    if type(frame) is not bytes or not 1 <= len(frame) <= _MAX_BYTES or not frame.endswith(b"\n"):
        raise ValueError("invalid bounded frame")
    if frame.count(b"\n") != 1:
        raise ValueError("multiple frames")
    parsed=json.loads(frame.decode("utf-8"), object_pairs_hook=_reject_duplicates,
                      parse_constant=_reject_number)
    if type(parsed) is not dict:
        raise ValueError("request must be JSON object")
    return parsed

class PublicToyCapabilityGate:
    """Local same-process toy. Not an authenticated evaluator or a key vault."""

    def __init__(self, *, arm: str = "active") -> None:
        if type(arm) is not str or arm not in ("active","random"):
            raise ValueError("invalid toy arm")
        self.arm=arm
        self.session=secrets.token_hex(16)
        self._capability=secrets.token_hex(32)
        self._signing_key=secrets.token_bytes(32)
        self._used_inputs: set[int] = set()
        self._used_nonces: set[str] = set()
        self._next_sequence=0
        self._previous="0"*64
        self._closed=False
        partition=split_inputs(TOY_SEED)
        self._allowed=frozenset(partition.query_ids)
        self._audit=frozenset(partition.audit_ids)

    def public_invitation(self) -> dict[str,object]:
        """Bearer capability is public to the toy client; never publish real ones."""
        return {"wire":WIRE,"phase":"TRAIN","arm":self.arm,
                "session":self.session,"capability":self._capability,
                "query_limit":QUERY_LIMIT}

    @property
    def previous_digest(self) -> str:
        return self._previous

    def _check_frame(self, item: dict[str,object]) -> str:
        op=item.get("op")
        if type(op) is not str or op not in ("query","close"):
            raise ValueError("invalid op")
        if set(item) != (_FIELDS if op=="query" else _CLOSE_FIELDS):
            raise ValueError("schema mismatch")
        if (type(item["wire"]) is not str or item["wire"] != WIRE or
                type(item["phase"]) is not str or item["phase"]!="TRAIN" or
                type(item["arm"]) is not str or item["arm"]!=self.arm or
                type(item["session"]) is not str or item["session"]!=self.session or
                type(item["capability"]) is not str or
                not hmac.compare_digest(item["capability"], self._capability) or
                type(item["sequence"]) is not int or
                item["sequence"]!=self._next_sequence or
                type(item["nonce"]) is not str or
                not _HEX32.fullmatch(item["nonce"]) or
                item["nonce"] in self._used_nonces or self._closed):
            raise ValueError("capability, phase or sequence denied")
        if op=="query":
            q=item["input_id"]
            if (type(q) is not int or q not in self._allowed or q in self._audit or
                    q in self._used_inputs or len(self._used_inputs)>=QUERY_LIMIT):
                raise ValueError("invalid or duplicate query")
        return op

    def _seal(self, body: dict[str,object]) -> dict[str,object]:
        payload={"wire":WIRE,"session":self.session,
                 "previous_digest":self._previous,**body}
        digest=sha256(_canonical(payload)).hexdigest()
        payload["receipt_digest"]=digest
        payload["receipt_mac"]=hmac.new(self._signing_key,_canonical(payload),sha256).hexdigest()
        self._previous=digest
        return payload

    def handle(self, frame: bytes) -> dict[str,object]:
        """Fail closed without consuming sequence, query budget or nonce."""
        try:
            item=_decode(frame)
            op=self._check_frame(item)
            if op=="query":
                q=item["input_id"]
                answer=execute(_TOY_TARGET,inputs()[q])
                body={"op":"answer","sequence":self._next_sequence,
                      "nonce":item["nonce"],"input_id":q,"answer":answer}
            else:
                body={"op":"closed","sequence":self._next_sequence,
                      "nonce":item["nonce"],"questions_answered":len(self._used_inputs)}
            # All input validation/answer computation happens before mutation.
            self._used_nonces.add(item["nonce"])
            if op=="query":
                self._used_inputs.add(item["input_id"])
            self._next_sequence+=1
            if op=="close":
                self._closed=True
            return self._seal(body)
        except (ValueError,TypeError,KeyError,IndexError,UnicodeError):
            return {"error":"REJECTED"}

    def verify_toy_receipt(self, receipt: dict[str,object],
                           *, expected_previous: str) -> bool:
        """A toy-only verifier; relies on SAME-PROCESS toy HMAC key."""
        if type(receipt) is not dict or type(expected_previous) is not str:
            return False
        fields=set(("wire","session","previous_digest","op","sequence","nonce",
                    "receipt_digest","receipt_mac"))
        if receipt.get("op")=="answer":
            fields|={"input_id","answer"}
        elif receipt.get("op")=="closed":
            fields|={"questions_answered"}
        else:
            return False
        if set(receipt)!=fields:
            return False
        if (any(type(receipt[k]) is not str for k in
                ("wire","session","previous_digest","op","nonce","receipt_digest","receipt_mac")) or
                type(receipt["sequence"]) is not int or
                (receipt["op"]=="answer" and
                 (type(receipt["input_id"]) is not int or type(receipt["answer"]) is not str)) or
                (receipt["op"]=="closed" and type(receipt["questions_answered"]) is not int) or
                receipt["wire"]!=WIRE or receipt["session"]!=self.session or
                receipt["previous_digest"]!=expected_previous or
                not _HEX64.fullmatch(receipt["receipt_digest"]) or
                not _HEX64.fullmatch(receipt["receipt_mac"])):
            return False
        unsigned={k:v for k,v in receipt.items() if k not in ("receipt_digest","receipt_mac")}
        digest=sha256(_canonical(unsigned)).hexdigest()
        signed={k:v for k,v in receipt.items() if k!="receipt_mac"}
        mac=hmac.new(self._signing_key,_canonical(signed),sha256).hexdigest()
        return (hmac.compare_digest(digest,receipt["receipt_digest"]) and
                hmac.compare_digest(mac,receipt["receipt_mac"]))

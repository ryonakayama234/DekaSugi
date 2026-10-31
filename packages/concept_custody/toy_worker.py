"""Separate-process public-fixture query worker; NOT an independent trusted Oracle.

Fixed synthetic target/source are disclosed. Strict JSONL; never eval/exec/pickle.
Does not support scoring, real confidential samples, network or official activation.
"""
from __future__ import annotations
import json
import sys
from packages.concept_world import Program, execute, inputs, split_inputs
from packages.concept_custody import TOY_WIRE_VERSION, TOY_QUERY_CAP

_TOY_SEED=2501
_TOY_PROGRAM=Program("contains_a",("reverse",),("upper",))
_MAX_LINE_BYTES=1024

def _answer(value: str) -> str:
    return execute(_TOY_PROGRAM,value)

def _frame(value: dict[str,object]) -> str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def run() -> int:
    domain=inputs()
    partition=split_inputs(_TOY_SEED)
    public=partition.public_ids[:2]
    allowed=set(partition.query_ids)
    opened=False
    finished=False
    queries: set[int]=set()
    while True:
        line=sys.stdin.buffer.readline(_MAX_LINE_BYTES+2)
        if not line: break
        if len(line)>_MAX_LINE_BYTES or not line.endswith(b"\n"):
            sys.stdout.write(_frame({"error":"REJECTED"})+"\n")
            sys.stdout.flush()
            break
        try:
            item=json.loads(line)
            if type(item) is not dict or any(type(k) is not str for k in item):
                raise ValueError("frame")
            if item=={"op":"open"} and not opened and not finished:
                opened=True
                result={"op":"opened","wire":TOY_WIRE_VERSION,"query_limit":TOY_QUERY_CAP,
                    "public":[{"input_id":i,"input":domain[i],"answer":_answer(domain[i])} for i in public]}
            elif (opened and not finished and set(item)=={"op","input_id"} and
                  item.get("op")=="query"):
                q=item["input_id"]
                if type(q) is not int or q not in allowed or q in queries or len(queries)>=TOY_QUERY_CAP:
                    raise ValueError("unauthorized question")
                queries.add(q)
                result={"op":"answer","input_id":q,"answer":_answer(domain[q])}
            elif item=={"op":"close"} and opened and not finished:
                finished=True
                result={"op":"closed","questions_answered":len(queries)}
            else:
                raise ValueError("state or payload")
        except (ValueError,TypeError,KeyError,UnicodeDecodeError):
            result={"error":"REJECTED"}
        sys.stdout.write(_frame(result)+"\n")
        sys.stdout.flush()
    return 0

if __name__=="__main__":
    raise SystemExit(run())

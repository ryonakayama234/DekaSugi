"""EXP-REP-003 local disclosed engineering CLI. No sealed evaluation access."""
import argparse
import json
import zlib
import base64
from pathlib import Path
from . import (BUDGETS, STRATA, ARMS, train, save, load, use,
               make_world, evaluate, conditioned_opportunity, digest)


def main():
    p = argparse.ArgumentParser(description="REP003 disclosed finite causal learner")
    cmd = p.add_subparsers(dest="command", required=True)
    f = cmd.add_parser("preflight")
    f.add_argument("--scope", choices=("disclosed",), default="disclosed")
    f.add_argument("--output", required=True)
    t = cmd.add_parser("train")
    t.add_argument("--worlds", type=int, default=64)
    t.add_argument("--snapshot", required=True)
    i = cmd.add_parser("inspect")
    i.add_argument("--snapshot", required=True)
    u = cmd.add_parser("use")
    u.add_argument("--snapshot", required=True)
    u.add_argument("--world-index", type=int, default=301)
    u.add_argument("--stratum", choices=STRATA, default="CONDITIONAL_TRANSFER")
    u.add_argument("--arm", choices=ARMS, default="LQ")
    u.add_argument("--budget", type=int, choices=BUDGETS, default=6)
    u.add_argument("--trace", required=True)
    e = cmd.add_parser("evaluate-disclosed")
    e.add_argument("--output", required=True)
    e.add_argument("--emit-archive-to-log", action="store_true")
    args = p.parse_args()
    if args.command == "preflight":
        result = conditioned_opportunity()
        result = {"status": "DISCLOSED_OPPORTUNITY_PREFLIGHT", **result}
        path = Path(args.output)
    elif args.command == "train":
        snap = train(args.worlds)
        save(snap, args.snapshot)
        print(json.dumps({"status":"DISCLOSED_TRAIN", "snapshot_digest":snap["digest"],
                          "worlds":snap["train_worlds"],"distinct_families":snap["distinct_families"],
                          "paid_actions":snap["paid_train_actions"]},sort_keys=True))
        return
    elif args.command == "inspect":
        snap = load(args.snapshot)
        print(json.dumps({"status":"DISCLOSED_INSPECT","snapshot":snap},sort_keys=True))
        return
    elif args.command == "use":
        snap = load(args.snapshot)
        committed = use(snap, make_world(args.world_index, args.stratum),args.arm,args.budget)
        path = Path(args.trace)
        result = {"status":"DISCLOSED_LOCAL_USE","committed":committed}
    else:
        result = evaluate()
        path = Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    if args.command == "evaluate-disclosed":
        small = {k:v for k,v in result.items() if k!="rows"}
        print("REP003_SUMMARY="+json.dumps(small,sort_keys=True,separators=(",",":")))
        if args.emit_archive_to_log:
            # Reconstruct full raw JSON in trusted connector from Actions log.
            compressed = base64.b64encode(zlib.compress(json.dumps(result,sort_keys=True,separators=(",",":")).encode(),9)).decode()
            print("REP003_ZLIB_BASE64="+compressed)
    else:
        print(json.dumps({"status":result["status"],"path":str(path),
                          "digest":digest(result)},sort_keys=True))


if __name__ == "__main__":
    main()

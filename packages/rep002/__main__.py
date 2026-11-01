"""Disclosed engineering CLI. Never loads formal DEV/FINAL data."""
import argparse
import json
from pathlib import Path
from . import SCHEMA, train, save, load, world, use, evaluate, audit


def main() -> None:
    p = argparse.ArgumentParser(description="EXP-REP-002 disclosed direct-relational preflight")
    cmd = p.add_subparsers(dest="command", required=True)
    t = cmd.add_parser("train")
    t.add_argument("--worlds", type=int, default=64)
    t.add_argument("--snapshot", required=True)
    i = cmd.add_parser("inspect")
    i.add_argument("--snapshot", required=True)
    u = cmd.add_parser("use")
    u.add_argument("--snapshot", required=True)
    u.add_argument("--world-index", type=int, default=301)
    u.add_argument("--stratum", choices=("RENAMED", "COMPOSITION", "NOVEL", "DISTRACTOR"), default="COMPOSITION")
    u.add_argument("--arm", choices=("LQ", "LA", "LR", "FA"), default="LQ")
    u.add_argument("--budget", type=int, default=4)
    e = cmd.add_parser("evaluate-disclosed")
    e.add_argument("--output", required=True)
    a = p.parse_args()
    if a.command == "train":
        s = train(a.worlds)
        save(s, Path(a.snapshot))
        result = {"status": "DISCLOSED_TRAIN", "schema": SCHEMA,
                  "worlds": s["train_count"], "structures": s["distinct_structures"],
                  "concepts": int(bool(s["motif"])), "digest": s["digest"],
                  "charged_train_actions": s["metered_train_actions"]}
    elif a.command == "inspect":
        result = {"status": "DISCLOSED_INSPECT", "snapshot": load(Path(a.snapshot))}
    elif a.command == "use":
        s = load(Path(a.snapshot))
        w = world(a.world_index, a.stratum)
        committed = use(s, w, a.arm, a.budget)
        # The auditor owns the score; the learner-facing output omits hidden labels.
        result = {"status": "DISCLOSED_LOCAL_USE", "world": w.name,
                  "public_roles": w.public_roles, "arm": a.arm,
                  "budget": a.budget, "prediction_commit": committed}
    else:
        result = evaluate()
        path = Path(a.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

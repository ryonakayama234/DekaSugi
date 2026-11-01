"""Disclosed synthetic EXP-REP-001 G1-D CLI. No formal data interfaces."""
from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import asdict
import json
from pathlib import Path
from packages.relational_world import Action
from . import (ToySession, disclosed_training_worlds, disclosed_world,
               diagnose_one_edge, learn_snapshot, load_snapshot, predict,
               run_pilot, save_snapshot)


def main() -> None:
    parser = ArgumentParser(description="G1-D toy-only Wake/Sleep, use and score")
    parser.add_argument("command", choices=("train", "inspect", "use", "evaluate-toy"))
    parser.add_argument("--snapshot", type=Path, default=Path(".run/rep-g1d/snapshot.json"))
    parser.add_argument("--worlds", type=int, choices=(0, 1, 2, 3, 4, 8, 16, 32), default=8)
    args = parser.parse_args()
    if args.command == "train":
        episodes = disclosed_training_worlds(args.worlds)
        result = learn_snapshot(episodes)
        save_snapshot(result, args.snapshot)
        print(json.dumps({"status": "DISCLOSED_TOY_TRAIN", "train_worlds": args.worlds,
                          "snapshot": str(args.snapshot), "digest": result.digest,
                          "templates": [asdict(x) for x in result.templates]},
                         ensure_ascii=False, sort_keys=True))
    elif args.command == "inspect":
        snapshot = load_snapshot(args.snapshot)
        print(json.dumps(asdict(snapshot), ensure_ascii=False, sort_keys=True))
    elif args.command == "evaluate-toy":
        print(json.dumps(run_pilot(), ensure_ascii=False, sort_keys=True))
    else:
        snapshot = load_snapshot(args.snapshot)
        host = disclosed_world(300, "user", "fork")
        session = ToySession(host)
        # Host truth and graph remain outside the inference call.
        for source in session.object_ids:
            session.act(Action("pulse", source))
        evidence = tuple(session.observations)
        before = (True, False, True, False)
        action = Action("pulse", session.object_ids[0])
        prediction = predict(session.object_ids, evidence, before, action, "B3", snapshot)
        print(json.dumps({"status": "DISCLOSED_TOY_USE_NOT_FORMAL",
                          "snapshot_digest": snapshot.digest,
                          "diagnosis": asdict(diagnose_one_edge(session.object_ids, evidence)),
                          "observed_actions": session.actions_charged,
                          "prediction": asdict(prediction),
                          "note": "Demo-only same-process host, not independent custody."},
                         ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

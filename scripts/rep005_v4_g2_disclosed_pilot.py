"""Disclosed source-controlled G1/G2 engineering-only, never historical EVAL.

PRIVATE host knows Law and holds independent scoring truth. The learner runs as a
fresh python -I subprocess, receives ONLY source-free JSON public records and
a SHA-bound typed ConceptSnapshot, and never imports the private source engine.
The three heldout use instances are role permutations of the same lag1 motif;
this is NOT independent causal-family scientific transfer.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from packages.rep005_g0b_v4 import ACTIONS, BUDGET, Edge, PrivateWorld, law
from packages.rep005_g0b_v4 import step as private_truth

LEARNER = (Path(__file__).resolve().parents[1] /
           "packages" / "rep005_study_v4" / "learner.py")


def learner_request(message):
    if not LEARNER.is_file():
        raise RuntimeError("missing isolated learner entrypoint")
    result = subprocess.run(
        [sys.executable, "-I", str(LEARNER)],
        input=json.dumps(message, ensure_ascii=False, sort_keys=True),
        encoding="utf-8", capture_output=True, timeout=12, check=False,
        cwd="/tmp",
    )
    if result.returncode != 0:
        raise RuntimeError("source-blind subprocess refused request: " +
                           result.stderr[-800:])
    return json.loads(result.stdout)


def as_public(record):
    # Explicit source-free allowlist. Source Law, motif and split never enter.
    return {
        "before": record.before,
        "history": [list(a) for a in record.history],
        "action": list(record.action),
        "after": record.after,
        "paid_cost": record.paid_cost,
    }


def training_episode(model, indices):
    world = PrivateWorld(model)
    public = []
    for i in indices:
        for action in (("pulse", i, -1), ("set", 0, 0)):
            public.append(as_public(world.observe_paid(action)))
    assert len(public) == 8
    return public


def disclosed_training():
    training_sources = (
        ("train-opaque-0", law(Edge(0, 1, 1))),
        ("train-opaque-1", law(Edge(1, 4, 1))),
        ("train-opaque-2", law(Edge(3, 2, 1))),
    )
    episodes = []
    for sid, model in training_sources:
        for ix in ((0, 1, 2, 3), (4, 0, 1, 2)):
            episodes.append({"world_session_id": sid,
                             "steps": training_episode(model, ix)})
    out = learner_request({"mode": "train", "episodes": episodes})
    assert out["status"] == "OK"
    snap = out["snapshot"]
    assert snap["payload"]["body"]["lag"] == 1
    assert snap["payload"]["training_paid_steps"] == 48
    return snap, 48, episodes


def fixed_probe_programs():
    # Declared a priori, independent of the target Law and all arm trajectories.
    instructions = []
    for i in range(5):
        instructions.append(([("pulse", i, -1)], ("set", 4, 0)))
    for i in range(5):
        instructions.append(([("pulse", i, -1)],
                             ("pulse", (i + 1) % 5, -1)))
    for i in range(5):
        instructions.append(([("pulse", i, -1), ("set", 4, 1)],
                             ("set", 3, 0)))
    instructions.append(([], ("pulse", 4, -1)))
    assert len(instructions) == 16
    return instructions


def evaluator_probes(model):
    result, answers = [], []
    for prefix, action in fixed_probe_programs():
        w = PrivateWorld(model)
        for a in prefix:
            w.observe_paid(a)
        before, history = w.x, w.hist
        answer, _ = private_truth(model, before, history, action)
        result.append({"before": before, "history": [list(x) for x in history],
                       "action": list(action)})
        answers.append(answer)
    return result, answers


def public_prefix(steps):
    if not steps:
        return 0, []
    final = steps[-1]
    return final["after"], (final["history"] + [final["action"]])[-2:]


def run_use(model, snapshot, arm):
    """A truly new WorldSession per arm; exactly 8 legally charged actions."""
    world = PrivateWorld(model)
    transcript = []
    active_snap = snapshot if arm in ("LEARNED", "BODY_OFF") else None
    body_off = arm == "BODY_OFF"
    interaction = []
    for _ in range(BUDGET):
        decision = learner_request({
            "mode": "plan", "steps": transcript,
            "snapshot": active_snap, "body_off": body_off,
        })
        if decision["status"] != "OK":
            raise RuntimeError("inquiry failed closed: " + repr(decision))
        before, hist = public_prefix(transcript)
        probe = {"before": before, "history": hist, "action": decision["action"]}
        prior = learner_request({
            "mode": "predict", "steps": transcript, "snapshot": active_snap,
            "body_off": body_off, "probes": [probe],
        })
        step = world.observe_paid(tuple(decision["action"]))
        transcript.append(as_public(step))
        interaction.append({
            "action_selected_before_truth": decision["action"],
            "inquiry_candidate_count": decision["candidate_count"],
            "inquiry_expected_entropy": decision["predicted_outcome_entropy_bits"],
            "predicted_before_truth": prior["predictions"][0],
            "observed_after": step.after,
            "before": step.before,
            "public_history": [list(a) for a in step.history],
            "charged_cost": step.paid_cost,
        })
    panel, answers = evaluator_probes(model)
    pre = learner_request({
        "mode": "predict", "steps": transcript, "snapshot": active_snap,
        "body_off": body_off, "probes": panel,
    })
    correct = wrong = abstained = 0
    for pred, truth in zip(pre["predictions"], answers):
        if pred is None:
            abstained += 1
        elif pred == truth:
            correct += 1
        else:
            wrong += 1
    result = {
        "arm": arm,
        "correct": correct, "wrong": wrong, "abstained": abstained,
        "utility": (correct - wrong) / 16,
        "coverage": (correct + wrong) / 16,
        "paid_use_steps": world.paid,
        "frozen_snapshot_used": arm != "STATIC",
        "candidate_count_after_paid_use": pre["candidate_count"],
        "effect_interpreter_dispatch_count": pre["actual_body_dispatch_count"],
        "interactions": interaction,
        "probe_predictions": pre["predictions"],
    }
    return result, panel, answers


def physical_snapshot_file_roundtrip(snapshot):
    """Actually persist bytes on disk, read them, then validate in fresh child."""
    with tempfile.TemporaryDirectory(prefix="rep005-v4-snapshot-") as tmp:
        path = Path(tmp) / "learned-concept.snapshot.json"
        path.write_text(json.dumps(snapshot, sort_keys=True, ensure_ascii=False),
                        encoding="utf-8")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        check = learner_request({"mode": "plan", "steps": [],
                                 "snapshot": loaded, "body_off": False})
        if check["status"] != "OK":
            raise RuntimeError("disk Snapshot rehydration failed")
        return loaded


def run_disclosed_g2():
    snapshot, paid_train, train_episodes = disclosed_training()
    snapshot = physical_snapshot_file_roundtrip(snapshot)
    use_laws = (
        ("use-instance-0", law(Edge(2, 3, 1))),
        ("use-instance-1", law(Edge(4, 1, 1))),
        ("use-instance-2", law(Edge(0, 4, 1))),
    )
    world_results = []
    for sid, model in use_laws:
        arms = []
        reference_panel, reference_truth = None, None
        for arm in ("STATIC", "LEARNED", "BODY_OFF"):
            result, panel, truth = run_use(model, snapshot, arm)
            if reference_panel is not None:
                assert reference_panel == panel and reference_truth == truth
            reference_panel, reference_truth = panel, truth
            arms.append(result)
        world_results.append({
            "opaque_use_id": sid, "arms": arms,
            "probe_program_sha256": hashlib.sha256(
                json.dumps(reference_panel, sort_keys=True).encode()).hexdigest(),
            "reference_panel_truth_sha256": hashlib.sha256(
                json.dumps(reference_truth).encode()).hexdigest(),
        })
    arm_summary = {}
    for arm in ("STATIC", "LEARNED", "BODY_OFF"):
        rows = [next(a for a in w["arms"] if a["arm"] == arm)
                for w in world_results]
        arm_summary[arm] = {
            "correct_total": sum(x["correct"] for x in rows),
            "wrong_total": sum(x["wrong"] for x in rows),
            "abstained_total": sum(x["abstained"] for x in rows),
            "mean_utility_over_three_correlated_world_instances":
                round(sum(x["utility"] for x in rows) / 3, 6),
            "paid_use_steps_total": sum(x["paid_use_steps"] for x in rows),
        }
    return {
        "status": "DISCLOSED_G2_ENGINEERING_ONLY_NOT_SCIENTIFIC_L3",
        "hypothesis_type": "within_single_known_lag1_motif_role_rebinding",
        "source_family_ancestry_independent": False,
        "sealed_G3_score": "NOT_RUN",
        "full_Hplus_G": "NOT_CERTIFIED",
        "process_isolation": "fresh Python -I public-only subprocess; NOT a hardened OS sandbox",
        "source_imported_in_public_learner": False,
        "learner_code_path": "packages/rep005_study_v4/learner.py",
        "snapshot": snapshot,
        "snapshot_file_roundtrip_verified": True,
        "training_public_episodes": len(train_episodes),
        "actual_training_paid_steps": paid_train,
        "new_use_world_instances": len(world_results),
        "panel_probes_per_instance": 16,
        "arm_summary": arm_summary,
        "world_results": world_results,
        "total_actual_paid_train_and_use": paid_train +
            sum(x["paid_use_steps_total"] for x in arm_summary.values()),
        "science_eligibility": "STOP_SOURCE_ANCESTRY_AND_POWER_NOT_CERTIFIED",
    }


def main():
    r = run_disclosed_g2()
    # Preserve real public-only Snapshot and evaluator receipt as CI artifacts
    # when explicitly configured; never include private Law/source files.
    artifact_dir = os.environ.get("REP005_V4_ARTIFACT_DIR")
    if artifact_dir:
        root = Path(artifact_dir)
        root.mkdir(parents=True, exist_ok=True)
        (root / "learned-concept.snapshot.json").write_text(
            json.dumps(r["snapshot"], sort_keys=True, ensure_ascii=False, indent=2),
            encoding="utf-8")
        (root / "disclosed-engineering-report.json").write_text(
            json.dumps(r, sort_keys=True, ensure_ascii=False, indent=2),
            encoding="utf-8")
    print("REP005_V4_G2_DISCLOSED_RESULT_START")
    print(json.dumps(r, ensure_ascii=False, sort_keys=True, indent=2))
    print("REP005_V4_G2_DISCLOSED_RESULT_END")


if __name__ == "__main__":
    main()

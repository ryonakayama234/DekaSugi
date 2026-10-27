"""POLICY-DIAG-001 synthetic/ TRAIN-only tests. Never open DEV or FINAL."""
import unittest
from dataclasses import replace

from packages.exp0003a import generate_train
from packages.exp0003a.pr3 import ArmSnapshot, PairedObservation
from packages.policy_diagnostics import snapshot_profile, dream_overlap, replay, compare_public_tasks

class PolicyDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = generate_train()
        cls.observations = tuple(PairedObservation(
            task_id=t.task.task_id, vector=(0.0,)*8,
            prefer_on=(i%2==0), off_calls=6, on_calls=4,
            off_candidates=10, on_candidates=9,
            off_correct=True, on_correct=True,
            on_audit_invalid=False
        ) for i,t in enumerate(cls.tasks))

    @classmethod
    def snapshot(cls, arm):
        # Synthetic Dream IDs are valid structural records, not generated or scored tasks.
        train = list(cls.observations)
        skillhash = "a"*64
        if arm in ("B2","B3"):
            # Chosen duplicate input IDs are forbidden: generate synthetic distinct opaque IDs.
            from hashlib import sha256
            extra = [replace(cls.observations[0], task_id="t-"+sha256(f"{arm}:{i}".encode()).hexdigest()) for i in range(96)]
            train += extra
            pool_ids=tuple(f"dream-f{f:02d}-i{i:03d}" for f in range(8) for i in range(12)) if arm=="B2" else tuple(f"dream-f{f:02d}-i{i+12:03d}" for f in range(8) for i in range(12))
            task_ids=tuple(x.task_id for x in extra)
        else:
            pool_ids=task_ids=()
        return ArmSnapshot(arm=arm,observations=tuple(train),
            skill_id="skill_"+skillhash[:16],skill_body_sha256=skillhash,
            source_manifest_sha256="b"*64,pool_public_input_sha256="c"*64,
            ordered_selected_pool_ids=pool_ids,ordered_selected_task_ids=task_ids,
            wake_episode_ids=tuple("wake:"+x.task_id for x in cls.observations),
            dream_case_ids=tuple(arm.lower()+":"+x for x in pool_ids))

    def test_profile_feature_collisions(self):
        a=self.snapshot("B2")
        p=snapshot_profile(a)
        self.assertEqual(p["observation_count"],256)
        self.assertEqual(p["unique_feature_vectors"],1)
        self.assertGreater(p["collision_groups_with_label_or_cost_conflict"],0)

    def test_dream_overlap(self):
        o=dream_overlap(self.snapshot("B2"),self.snapshot("B3"))
        self.assertEqual(o["overlap_count"],0)
        self.assertEqual(o["jaccard"],0)

    def test_choose_parity_and_order_invariance(self):
        a=self.snapshot("B2")
        task=self.tasks[0].task
        x=replay(task,a)
        swapped=replace(a,observations=tuple(reversed(a.observations[:160]))+a.observations[160:],
                        wake_episode_ids=tuple(reversed(a.wake_episode_ids)))
        self.assertEqual(x["action"],replay(task,swapped)["action"])
        self.assertEqual(x["neighbors"],replay(task,swapped)["neighbors"])

    def test_compare_public_train_only(self):
        q=compare_public_tasks((self.tasks[0].task,),self.snapshot("B2"),self.snapshot("B3"))
        self.assertEqual(q["task_count"],1)
        self.assertEqual(q["rows"][0]["cost_status"],"not_observed")

    def test_reject_duplicate_id(self):
        a=self.snapshot("B2")
        changed=replace(a,observations=(a.observations[1],)+a.observations[1:])
        with self.assertRaises(ValueError):
            snapshot_profile(changed)

    def test_reject_false_archived_action(self):
        task=self.tasks[0].task
        a=self.snapshot("B2");b=self.snapshot("B3")
        wrong={task.task_id:{"arms":{"B2":{"decision":"UNTRUSTED","primitive_invocations":1},
                                      "B3":{"decision":"OFF","primitive_invocations":1}}}}
        with self.assertRaises(ValueError):
            compare_public_tasks((task,),a,b,wrong)


    def test_reject_arm_mismatch(self):
        task=self.tasks[0].task
        a=self.snapshot("B2"); b=self.snapshot("B3")
        for left,right in ((a,a),(b,a),(self.snapshot("B1"),b)):
            with self.subTest(arms=(left.arm,right.arm)),self.assertRaises(ValueError):
                compare_public_tasks((task,),left,right)

    def test_all_sequential_gates_and_exact_boundaries(self):
        """Force each frozen gate with valid synthetic 8D feature vectors."""
        from packages.kernel import features
        from dataclasses import replace as r
        task=self.tasks[0].task
        base=features(task)
        a=self.snapshot("B2")
        inds=sorted(range(len(a.observations)),key=lambda i:a.observations[i].task_id)[:5]

        def vector_at_distance(distance):
            # Every coordinate remains in its validated range; one unit step
            # in dimension 3 gives mean-L1 distance 0.125. A small step of
            # 0.18 in 8D requires changing >=2 features.
            # Normalize within [0,1] in coordinates 0/1, [-1,1] at 2.
            vec=list(base)
            remain=8*distance
            for i in range(8):
                lo=-1.0 if i==2 else 0.0
                hi=1.0
                room=(hi-vec[i]) if (hi-vec[i]) >= (vec[i]-lo) else (vec[i]-lo)
                step=min(room, remain)
                sign=1 if hi-vec[i]>=vec[i]-lo else -1
                vec[i]+=sign*step
                remain-=step
            if remain>1e-9:
                raise AssertionError("Synthetic fixture distance unavailable")
            return tuple(vec)

        def build(nclose=5, votes=5, saving=2, veto=False, distance=.6):
            rows=list(a.observations)
            for i,o in enumerate(rows):
                if i in inds:
                    rank=inds.index(i)
                    vec=base if rank<nclose else vector_at_distance(distance)
                    rows[i]=r(o,vector=vec,prefer_on=rank<votes,
                              off_calls=10,on_calls=10-saving,
                              off_correct=True,on_audit_invalid=veto and rank==0)
                else:
                    rows[i]=r(o,vector=vector_at_distance(0.85))
            return r(a,observations=tuple(rows))

        cases=[
            ("on_exact_saving",build(), "cost_supported","ON"),
            ("insufficient_near",build(nclose=2), "insufficient_support","OFF"),
            ("veto_priority",build(nclose=2,veto=True),"insufficient_support","OFF"),
            ("veto",build(veto=True),"audit_safety_veto","OFF"),
            ("votes",build(votes=3),"insufficient_on_votes","OFF"),
            ("saving",build(saving=1),"insufficient_call_saving","OFF"),
            ("near_boundary",build(nclose=3,distance=.18),"cost_supported","ON"),
            ("outside_boundary",build(nclose=2,distance=.18001),"insufficient_support","OFF"),
        ]
        for name,snap,reason,action in cases:
            with self.subTest(name=name):
                result=replay(task,snap)
                self.assertEqual((result["reason"],result["action"]),(reason,action))

if __name__ == "__main__":
    unittest.main()

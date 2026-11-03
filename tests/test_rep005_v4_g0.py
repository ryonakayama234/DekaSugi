"""V4 G0 prospective source-only tests: no historical scorer or sealed source."""
import itertools
import unittest

from packages.rep005_g0b_v4 import (
    ACTIONS, Atom, BUDGET, DOMAIN_CELLS, Edge, HISTORIES, Law, PrivateWorld,
    PublicStep, certificate_catalog, canonical_semantic_orbit,
    feasible_fixed_opportunity, full_signature, guarded, law,
    legal_closed_class_id, memorylessness_witness, permute_signature,
    rename_action, rename_bitmask, step, validate_public_step,
    verify_public_chronology,
)


def independent_transition(model, x, hist, action):
    """Separately authored, branch-oriented reference evaluator (not step())."""
    state = [bool(x & (1 << k)) for k in range(5)]
    if action[0] == "set":
        state[action[1]] = bool(action[2])
    flips = [0] * 5
    for e in model.edges:
        trigger_action = action if e.lag == 0 else (
            hist[-e.lag] if len(hist) >= e.lag else None
        )
        if trigger_action != ("pulse", e.source, -1):
            continue
        valid = True
        for g in e.guard:
            if g.kind == "bit":
                if bool(x & (1 << g.role)) != bool(g.value):
                    valid = False
            elif len(hist) < g.lag or hist[-g.lag] != (g.kind, g.role, g.value):
                valid = False
        if valid:
            flips[e.target] = flips[e.target] ^ 1
    return sum((int(state[k]) ^ flips[k]) << k for k in range(5))


class V4G0SourceTest(unittest.TestCase):
    def setUp(self):
        self.none = law()
        self.direct = law(Edge(0, 1))
        self.lag1 = law(Edge(0, 1, 1))
        self.lag2 = law(Edge(0, 1, 2))
        self.guarded = law(Edge(0, 1, 0, guarded(Atom("bit", 2, 1))))
        self.double = law(Edge(0, 1), Edge(2, 1))

    def test_domain_and_exact_complete_independent_oracle(self):
        self.assertEqual(DOMAIN_CELLS, 115680)
        for m in (self.none, self.direct, self.lag1, self.lag2,
                  self.guarded, self.double):
            sig = full_signature(m)
            self.assertEqual(len(sig), DOMAIN_CELLS)
            pos = 0
            for x in range(32):
                for hist in HISTORIES:
                    for action in ACTIONS:
                        self.assertEqual(sig[pos],
                                         independent_transition(m, x, hist, action),
                                         (m, x, hist, action))
                        pos += 1

    def test_role_equivariance_all_120_renamings_and_exact_orbit(self):
        signatures = (full_signature(self.none), full_signature(self.direct),
                      full_signature(self.lag1))
        self.assertEqual(len(list(itertools.permutations(range(5)))), 120)
        for sig in signatures:
            for p in itertools.permutations(range(5)):
                altered = permute_signature(sig, p)
                self.assertEqual(len(altered), DOMAIN_CELLS)
                for x in (0, 1, 3, 7, 15, 31):
                    for h in ((), (("pulse", 0, -1),), (("set", 2, 1), ("pulse", 1, -1))):
                        for action in (("pulse", 0, -1), ("pulse", 3, -1),
                                       ("set", 4, 1)):
                            from packages.rep005_g0b_v4 import ACTION_INDEX, HIST_INDEX
                            before = (x * len(HISTORIES) + HIST_INDEX[h]) * 15 + ACTION_INDEX[action]
                            rh = tuple(rename_action(a, p) for a in h)
                            ra = rename_action(action, p)
                            after_index = (rename_bitmask(x, p) * len(HISTORIES) +
                                           HIST_INDEX[rh]) * 15 + ACTION_INDEX[ra]
                            self.assertEqual(altered[after_index],
                                             rename_bitmask(sig[before], p))
        direct_renamed = law(Edge(3, 4))
        self.assertEqual(canonical_semantic_orbit(full_signature(self.direct)),
                         canonical_semantic_orbit(full_signature(direct_renamed)))

    def test_parity_and_set_precedence(self):
        m = law(Edge(0, 1), Edge(0, 1, 0, guarded(Atom("bit", 2, 1))))
        self.assertEqual(step(m, 4, (), ("pulse", 0, -1))[0], 4)
        self.assertEqual(step(m, 0, (), ("pulse", 0, -1))[0], 2)
        m2 = law(Edge(0, 1), Edge(2, 1))
        x, _ = step(m2, 0, (), ("set", 1, 1))
        self.assertEqual(x, 2)
        x, h = step(m2, 0, (), ("pulse", 0, -1))
        self.assertEqual(x, 2)
        x, _ = step(m2, x, h, ("pulse", 2, -1))
        self.assertEqual(x, 0)

    def test_lag1_legal_public_memoryless_contradiction(self):
        witness = memorylessness_witness(self.lag1)
        self.assertIsNotNone(witness)
        self.assertNotEqual(witness["first_after"], witness["second_after"])
        self.assertIsNone(memorylessness_witness(self.none))
        first_prefix = witness["first_prefix"]
        second_prefix = witness["second_prefix"]
        for prefix, next_expected in ((first_prefix, witness["first_after"]),
                                      (second_prefix, witness["second_after"])):
            w = PrivateWorld(self.lag1)
            for a in prefix:
                w.observe_paid(tuple(a))
            r = w.observe_paid(tuple(witness["action"]))
            self.assertEqual((r.before, r.after), (witness["before"], next_expected))

    def test_two_world_complete_adaptive_identification(self):
        self.assertEqual(legal_closed_class_id((self.none, self.direct), 0)["status"],
                         "UNID")
        self.assertEqual(legal_closed_class_id((self.none, self.direct), 1)["status"],
                         "ID")
        self.assertEqual(legal_closed_class_id((self.none, self.lag1), 1)["status"],
                         "UNID")
        self.assertEqual(legal_closed_class_id((self.none, self.lag1), 2)["status"],
                         "ID")
        stopped = legal_closed_class_id((self.none, self.lag1), 2, max_nodes=0)
        self.assertEqual(stopped["status"], "NOT_CERTIFIED")
        self.assertEqual(legal_closed_class_id((self.none, self.none), 1)["status"],
                         "NOT_CERTIFIED")
        self.assertEqual(legal_closed_class_id(tuple(self.none for _ in range(65)), 1)["reason"],
                         "CLASS_SIZE_CAP")

    def test_actual_feasible_vs_nonadaptive_query(self):
        out = feasible_fixed_opportunity(self.none, self.direct,
                                         ("pulse", 0, -1), ("set", 0, 0))
        self.assertEqual(out["terminal_MAP_feasible"], 1.0)
        self.assertEqual(out["terminal_MAP_fixed"], 0.5)
        self.assertEqual(out["gap"], 0.5)

    def test_public_chronology_and_type_security(self):
        world = PrivateWorld(self.lag1)
        r1 = world.observe_paid(("pulse", 0, -1))
        r2 = world.observe_paid(("pulse", 0, -1))
        self.assertEqual(r1.paid_cost + r2.paid_cost, 2)
        verify_public_chronology((r1, r2))
        with self.assertRaises(ValueError):
            verify_public_chronology((r2, r1))
        with self.assertRaises(ValueError):
            validate_public_step(PublicStep(False, (), ACTIONS[0], 0))
        with self.assertRaises(ValueError):
            validate_public_step(PublicStep(0, (), ACTIONS[0], 0, 0))
        with self.assertRaises(ValueError):
            PrivateWorld(self.none).observe_paid(("pulse", 5, -1))
        for _ in range(BUDGET - 2):
            world.observe_paid(("set", 4, 1))
        with self.assertRaises(ValueError):
            world.observe_paid(("pulse", 0, -1))

    def test_constructor_duplicate_and_history_guards(self):
        with self.assertRaises(ValueError):
            law(Edge(0, 1), Edge(0, 1))
        with self.assertRaises(ValueError):
            Edge(0, 1, 0, guarded(Atom("bit", 2, 0), Atom("bit", 2, 1)))
        with self.assertRaises(ValueError):
            Edge(0, 1, 0, guarded(Atom("pulse", 2, -1, 1), Atom("pulse", 3, -1, 1)))
        self.assertEqual(step(self.lag2, 0, (), ("pulse", 0, -1))[0], 0)
        self.assertEqual(step(self.lag2, 0, (("pulse", 0, -1),), ("set", 2, 0))[0], 0)
        self.assertEqual(step(self.lag2, 0,
                              (("pulse", 0, -1), ("set", 2, 0)),
                              ("set", 2, 0))[0], 2)

    def test_pilot_catalog_exact_role_orbits(self):
        report = certificate_catalog()
        self.assertEqual(report["raw_named_constructor_count"], 12)
        self.assertEqual(report["full_verified_Hplus_G"] if "full_verified_Hplus_G" in report
                         else report["verified_closed_full_Hplus_G"], False)
        self.assertTrue(report["nonalias_exact_semantic_orbits"] >= 4)
        self.assertEqual(set(r["role_permutations"] for r in report["records"]), {120})
        self.assertEqual(set(r["full_signature_cells"] for r in report["records"]), {115680})


if __name__ == "__main__":
    unittest.main()

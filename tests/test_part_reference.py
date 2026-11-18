import copy
import json
from pathlib import Path
import unittest
from packages.part_reference import acquire, predict
from scripts.audit_part_reference import audit

DATA = Path(__file__).resolve().parents[1]/'experiments/PART-REFERENCE-1'


class PartReferenceTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads((DATA/'train.json').read_text())
        self.chunks, self.cost = acquire(self.rows)
        # Engineering probes use a different body from the fixed evaluation.
        self.q = dict(id='probe', left=1, right=2, text='zz')

    def test_reference_dependency(self):
        result = predict(self.chunks, self.q, 'REF', self.cost)
        self.assertEqual(result['output'], 'ABBAzzDCCD')
        self.assertEqual(result['used_references'], ['C01','C04'])
        changed = copy.deepcopy(self.chunks)
        changed[0]['text'] = 'ZZZZ'
        self.assertEqual(predict(changed,self.q,'REF',self.cost)['output'],'ZZZZzzDCCD')

    def test_mask_falls_back_and_preserves_preselection(self):
        ref = predict(self.chunks,self.q,'REF',self.cost)
        mask = predict(self.chunks,self.q,'MASK',self.cost)
        self.assertEqual(ref['candidates'],mask['candidates'])
        self.assertEqual(ref['preselection_cost'],mask['preselection_cost'])
        self.assertEqual(mask['used_references'],[])
        self.assertEqual(mask['output'],'zzDCCD')

    def test_char_retains_duplicate_slots(self):
        result = predict(self.chunks,self.q,'CHAR',self.cost)
        self.assertEqual(len(result['candidates']),9)
        self.assertEqual(result['candidates'][1]['body'],result['candidates'][2]['body'])
        self.assertFalse(result['candidates'][8]['within_limits'])
        self.assertEqual(result['candidates'][8]['stored_length'],9)

    def test_unknown_selector_rejected(self):
        with self.assertRaises(ValueError):
            predict(self.chunks,dict(self.q,left=3),'REF',self.cost)

    def test_ambiguous_training_rejected(self):
        self.rows[0]['output'] = 'uu'
        with self.assertRaises(ValueError):
            acquire(self.rows)

    def test_conflicting_support_rejected(self):
        self.rows[1]['output'] = 'BBBBv'
        with self.assertRaises(ValueError):
            acquire(self.rows)

    def test_duplicate_evidence_rejected(self):
        self.rows[1]['id'] = self.rows[0]['id']
        with self.assertRaises(ValueError):
            acquire(self.rows)

    def test_unknown_arm_rejected(self):
        with self.assertRaises(ValueError):
            predict(self.chunks,self.q,'OTHER',self.cost)

    def test_auditor_rejects_missing_arms(self):
        with self.assertRaises(ValueError):
            audit(dict(schema='part-reference/1',answers_read_before_lock=0,arms={}),{})


class EvidenceCorruptionTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((DATA/'runs/local-01/predictions.json').read_text())
        self.answers = json.loads((DATA/'answers.json').read_text())

    def test_full_recount(self):
        self.assertEqual(audit(self.record,self.answers)['verdict'],'MET')

    def test_changed_counter_rejected(self):
        self.record['arms']['MASK']['records'][0]['preselection_cost']['candidate_slots'] = 0
        with self.assertRaises(ValueError):
            audit(self.record,self.answers)

    def test_missing_candidate_rejected(self):
        self.record['arms']['REF']['records'][0]['candidates'].pop()
        with self.assertRaises(ValueError):
            audit(self.record,self.answers)

    def test_reference_claim_rejected(self):
        self.record['arms']['REF']['records'][0]['used_references'] = []
        with self.assertRaises(ValueError):
            audit(self.record,self.answers)

    def test_changed_prediction_rejected(self):
        self.record['arms']['CHAR']['records'][0]['output'] = self.answers['Q01']
        with self.assertRaises(ValueError):
            audit(self.record,self.answers)

    def test_early_answer_read_rejected(self):
        self.record['answers_read_before_lock'] = 1
        with self.assertRaises(ValueError):
            audit(self.record,self.answers)

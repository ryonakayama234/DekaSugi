"""Invented contract negatives. Do not run the diagnostic corpus in unit tests."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from packages.symbol_bootstrap import Budget, Learner, ResourceStop, digest
from packages.symbol_reformation import LIMITS, ARMS, compare, diagnose, load_input
from packages.symbol_reformation.__main__ import run


def artificial_states():
    # Eighteen distinct raw strings, not the diagnostic's original corpus.
    rows=[[f'E{i+1:03}',chr(97+i%18)+'!'] for i in range(54)]
    return {a:dict(arm=a,rows=copy.deepcopy(rows),chunks={},fragments={},rules={},memory={},ngrams={}) for a in ARMS}


class ReformationTests(unittest.TestCase):
    def test_once_pairs_deduplication_and_state_readonly(self):
        states=artificial_states(); before=digest(states)
        with patch.object(Learner,'observe',side_effect=AssertionError('observe forbidden')), patch.object(Learner,'predict',side_effect=AssertionError('predict forbidden')):
            d,trials,events=diagnose(states,Budget(LIMITS))
        self.assertEqual(before,digest(states))
        self.assertEqual(len(trials),459)  # 153 pairs, length 2, 2+1 routes
        self.assertEqual(len(events),306)
        expected=[[f'E{j+1:03}',f'E{i+1:03}'] for i in range(1,18) for j in range(i)]
        for arm in ARMS:
            self.assertEqual(d['arms'][arm]['pairs'],expected)
            self.assertEqual(d['arms'][arm]['summary']['new'],1)
        self.assertFalse(d['comparison']['full_chunk_exclusive_new'])

    def test_no_outputs_remains_zero(self):
        with patch.object(Learner,'_outputs',return_value=[]):
            d,_,events=diagnose(artificial_states(),Budget(LIMITS))
        self.assertFalse(events)
        self.assertTrue(all(d['arms'][a]['summary']['new']==0 for a in ARMS))

    def test_symbol_dependencies_and_event_retention(self):
        states=artificial_states()
        for a in ARMS:
            states[a]['rows']=[[eid,t[0]*4+'!'] for eid,t in states[a]['rows']]
        for eid,t in states['FULL']['rows'][:18]:
            expansion=t[:2]
            states['FULL']['chunks'][expansion]=dict(id='C-'+digest(expansion)[:16], expansion=expansion, created_at=eid)
        d,_,events=diagnose(states,Budget(LIMITS))
        symbol=[e for e in events if e['route']=='symbol']
        self.assertTrue(symbol)
        self.assertTrue(all(e['chunk_uses'] and e['dependencies'] for e in symbol))
        self.assertTrue(all(u['end']-u['start']==len(u['expansion']) for e in symbol for u in e['chunk_uses']))
        with patch.dict(LIMITS,events=0), self.assertRaises(ResourceStop):
            diagnose(states,Budget(LIMITS))

    def test_unique_evidence_and_no_added_observations(self):
        states=artificial_states()
        ast=dict(pattern=[['V',0]],output=[['L','!']])
        rid='R-'+digest(ast)[:16]
        for a in ARMS:states[a]['rules']={rid:dict(id=rid,**ast)}
        d,_,_=diagnose(states,Budget(LIMITS))
        c=d['arms']['FULL']['candidates'][rid]
        self.assertEqual(len(c['evidence']),18)
        self.assertEqual(c['support'],18)
        self.assertEqual(len(states['FULL']['rows']),54)

    def test_failure_and_inapplicable_preserved(self):
        states=artificial_states()
        ast=dict(pattern=[['L','a']],output=[['L','?']])
        rid='R-'+digest(ast)[:16]
        for a in ARMS:states[a]['rules']={rid:dict(id=rid,**ast)}
        d,_,_=diagnose(states,Budget(LIMITS))
        c=d['arms']['FULL']['candidates'][rid]
        self.assertEqual((c['support'],c['failure'],c['inapplicable']),(0,1,17))

    def test_exclusion_uses_both_before_and_character_after(self):
        cand=lambda routes:dict(routes=routes,support=2)
        arms={'FULL':dict(before=['old-full'],candidates={r:cand(rt) for r,rt in [('old-full',['symbol']),('old-nc',['symbol']),('nc-after',['symbol']),('char',['symbol','character']),('unique',['symbol'])]}),
              'NO-CHUNK':dict(before=['old-nc'],candidates={'nc-after':cand(['character'])})}
        self.assertEqual(compare(arms,Budget(LIMITS))['full_chunk_exclusive_supported'],['unique'])

    def test_different_ledgers_and_no_chunk_dictionary_rejected(self):
        states=artificial_states();states['NO-CHUNK']['rows'][0][1]='bad'
        with self.assertRaises(ValueError):diagnose(states,Budget(LIMITS))
        states=artificial_states();states['NO-CHUNK']['chunks']={'bad':{}}
        with self.assertRaises(ValueError):diagnose(states,Budget(LIMITS))

    def test_operations_stop_not_complete(self):
        with self.assertRaises(ResourceStop):diagnose(artificial_states(),Budget(dict(LIMITS,operations_total=0)))

    def test_cli_stops_on_resource_and_invalid_input(self):
        for exc, status in ((ResourceStop('fixture cap'),'RESOURCE_STOP'),(ValueError('fixture corruption'),'INVALID')):
            with tempfile.TemporaryDirectory() as tmp, patch('packages.symbol_reformation.__main__.load_input',side_effect=exc):
                out=Path(tmp)/'run'
                self.assertEqual(run(out),2)
                import json
                self.assertEqual(json.loads((out/'STOP.json').read_text())['status'],status)
                self.assertFalse((out/'COMPLETE.json').exists())
                self.assertFalse((out/'report.json').exists())

    def test_cli_save_failure_revokes_complete_summary(self):
        # Exercise write phase and artifact cap on invented zero-candidate data only.
        with tempfile.TemporaryDirectory() as tmp, patch('packages.symbol_reformation.__main__.load_input',return_value=artificial_states()), patch.dict(LIMITS,artifact_bytes=17000):
            out=Path(tmp)/'run'
            self.assertEqual(run(out),2)
            self.assertTrue((out/'STOP.json').exists())
            self.assertFalse((out/'report.json').exists())

    def test_state_loader_opens_only_states_member(self):
        from zipfile import ZipFile
        opened=[]; original=ZipFile.read
        def read(z,name,*args,**kw):
            opened.append(name);return original(z,name,*args,**kw)
        with patch.object(ZipFile,'read',read):states=load_input(Budget(LIMITS))
        self.assertEqual(opened,['states.json'])
        self.assertEqual(set(states),set(ARMS))


if __name__=='__main__':unittest.main()

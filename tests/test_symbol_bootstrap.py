"""Contract negatives using the fixed invented system only; no historic runners."""
import ast
import copy
from pathlib import Path
import unittest

from packages.symbol_bootstrap import Budget, Learner, ResourceStop, digest
from packages.symbol_bootstrap.__main__ import aggregate, audit_ledger, load_lock


class SymbolBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.lock=load_lock()
        self.budget=Budget(self.lock['limits'])

    def learner(self,arm='FULL'):
        return Learner(arm,self.lock['alphabet'],self.budget)

    def test_split_metadata_not_in_core(self):
        source=Path('packages/symbol_bootstrap/__init__.py').read_text()
        tree=ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node,ast.Constant) and isinstance(node.value,str):
                for word in ['dax','mip','nuv','zok','qef','wyg']:
                    self.assertNotIn(word,node.value)
        self.assertEqual(len(audit_ledger(self.lock)),14)

    def test_read_only_independent_predictions(self):
        l=self.learner()
        for i,r in enumerate(self.lock['train'][:5]):l.observe(f'E{i:03}',r['prefix']+r['expected'])
        before=digest(l.state())
        a=l.predict(self.lock['tests'][4]['prefix'],7)
        l.predict(self.lock['tests'][-1]['prefix'],7)
        self.assertEqual(a,l.predict(self.lock['tests'][4]['prefix'],7))
        self.assertEqual(before,digest(l.state()))

    def test_no_chunk_relearn_and_no_learn_empty(self):
        for arm in ('NO-CHUNK','MEMORY','NO-LEARN'):
            l=self.learner(arm)
            for i,r in enumerate(self.lock['train'][:5]):l.observe(str(i),r['prefix']+r['expected'])
            self.assertFalse(l.chunks)
            self.assertFalse(l.fragments)
            if arm!='NO-CHUNK':self.assertFalse(l.rules)
            if arm=='NO-LEARN':self.assertFalse(l.rows);self.assertFalse(l.ngrams)

    def test_exact_memory_and_fallback_are_separate(self):
        l=self.learner('MEMORY');r=self.lock['train'][0]
        l.observe('E001',r['prefix']+r['expected'])
        self.assertEqual(l.predict(r['prefix'],7)['prediction'],r['expected'])
        self.assertEqual(l.predict(self.lock['tests'][-1]['prefix'],7)['path'],'ngram')
        self.assertEqual(self.learner('NO-LEARN').predict(r['prefix'],7)['prediction'],';'*7)

    def test_repetition_not_unique_support(self):
        l=self.learner();r=self.lock['train'][0]
        for i in range(3):l.observe(str(i),r['prefix']+r['expected'])
        self.assertFalse(l.rules)
        self.assertFalse(l.chunks)

    def test_counterexample_reduces_existing_support(self):
        l=self.learner('NO-CHUNK')
        for i,r in enumerate(self.lock['train'][:5]):l.observe(str(i),r['prefix']+r['expected'])
        r=self.lock['train'][0];trace=l.predict(r['prefix'],7)
        self.assertIsNotNone(trace['selected'])
        rule=l.rules[trace['selected']['rule']]
        before=l._rank(rule)[0]
        l.observe('negative',r['prefix']+r['expected'][::-1])
        self.assertGreater(l._rank(rule)[0],before)
        self.assertTrue(any(e['episode']=='negative' and e['status']=='failure' for e in rule['evidence']))

    def test_stop_does_not_prune(self):
        limits=dict(self.lock['limits'],operations_total=0)
        with self.assertRaises(ResourceStop):Learner('FULL',self.lock['alphabet'],Budget(limits)).predict('dax|mip>',7)
        l=self.learner();l.limits=dict(l.limits,rules=0)
        with self.assertRaises(ResourceStop):
            for i,r in enumerate(self.lock['train'][:5]):l.observe(str(i),r['prefix']+r['expected'])
        self.assertEqual(l.rules,{})

    def test_bad_input_and_fixed_freeze(self):
        l=self.learner()
        for text in ('', 'a'*33, '日本語'):
            with self.assertRaises(ValueError):l.observe('bad',text)
        self.assertEqual(len(self.lock['train'])*self.lock['rounds'],54)

    def test_incomplete_or_duplicate_comparison_rejected(self):
        from packages.symbol_bootstrap.__main__ import aggregate
        rows=[dict(id=t['id'],group=t['group'],arm=a,correct=False,trace={'prediction':''}) for t in self.lock['tests'] for a in self.lock['arms']]
        with self.assertRaises(ValueError):aggregate(rows[:-1],self.lock['arms'])
        with self.assertRaises(ValueError):aggregate(rows[:-1]+rows[:1],self.lock['arms'])


if __name__=='__main__':unittest.main()

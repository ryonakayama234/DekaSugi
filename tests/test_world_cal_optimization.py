"""Only artificial primitive inputs. Full fixture comparisons use the audit runner."""
import math
import sys
import unittest
from unittest.mock import patch

from world_cal import power_engine as e
from world_cal.inference import bootstrap_vectors_cached,bootstrap_vectors_array,InferenceUnknown
from world_cal.prf import encode_parts,draw_digest,uniform53,box_muller,PRFError

try:
    from world_cal import _prf_batch
except ImportError:
    _prf_batch=None

class OptimizationGoldens(unittest.TestCase):
    @unittest.skipIf(_prf_batch is None,'explicit native build not installed')
    def test_full_prf_bytes_indexes_and_domains(self):
        key=bytes(range(32))
        for stage in ('pps','bootstrap','episode|1:0|1:1|4:FULL|1:8','日本語|😀'):
            prefix=encode_parts('WORLD-CAL-v1','sha256:'+e.MODEL_SHA,'GTHETA-BASE-01',96,7,stage)
            for start in (0,1,2**32,2**64-3):
                expected=[draw_digest(key,'sha256:'+e.MODEL_SHA,'GTHETA-BASE-01',96,7,stage,i)
                          for i in range(start,start+3)]
                self.assertEqual(_prf_batch.uniforms(key,prefix,start,3,True),b''.join(expected))
                self.assertEqual(_prf_batch.uniforms(key,prefix,start,3),list(map(uniform53,expected)))
        with self.assertRaises(ValueError):_prf_batch.uniforms(key,b'',2**64-1,2)
        with self.assertRaises(ValueError):_prf_batch.uniforms(b'x',b'',0,1)

    def test_mixed_spare_and_batch_consumption(self):
        obj=e._CounterDraws(bytes(32),'GTHETA-BASE-01',8,3)
        us=[uniform53(draw_digest(bytes(32),'sha256:'+e.MODEL_SHA,'GTHETA-BASE-01',8,3,'normal',i)) for i in range(12)]
        expected=[v for i in range(0,12,2) for v in box_muller(us[i],us[i+1])]
        actual=[obj.normal('normal')]+obj.normal_many('normal',4)
        self.assertEqual(obj.normal_many('normal',0),[])
        actual+=obj.normal_many('normal',7)
        self.assertEqual(actual,expected)
        self.assertEqual(obj.next_index,{'normal':12});self.assertEqual(obj.spare,{})
        with self.assertRaises(e.PowerUnknown):obj.normal_many('normal',-1)

    def test_python_fallback_uniform_bytes(self):
        with patch.object(e,'_batch_uniforms',None):
            obj=e._CounterDraws(bytes(32),'GTHETA-BASE-01',8,0)
            actual=obj.uniform_many('bootstrap',19)
            expected=[uniform53(draw_digest(bytes(32),'sha256:'+e.MODEL_SHA,'GTHETA-BASE-01',8,0,'bootstrap',i)) for i in range(19)]
            self.assertEqual(actual,expected)

    def test_bootstrap_native_numerical_and_fallback(self):
        sample=list(range(7));q=[1/7]*7;pi=[.4]*7
        parents=['a','a','b','c','c','d','d']
        values={i:tuple((-1)**(i+j)*(i+1)*(j+1)/77 for j in range(9)) for i in sample}
        draws=[['a','b','c','d'],['a','a','a','b'],['d','c','c','b']]
        args=(sample,q,pi,values,parents,draws)
        a=bootstrap_vectors_cached(*args);b=bootstrap_vectors_array(*args)
        self.assertEqual(a[0],b[0])
        self.assertLessEqual(max(abs(x-y) for ra,rb in zip(a[1],b[1]) for x,y in zip(ra,rb)),1e-10)
        with patch.dict(sys.modules,{'world_cal._prf_batch':None}):
            self.assertEqual(bootstrap_vectors_array(*args),a)
        with self.assertRaises(InferenceUnknown):bootstrap_vectors_array(*args[:-1],[['missing']*4])

    @unittest.skipIf(_prf_batch is None,'explicit native build not installed')
    def test_native_reduction_rejects_malformed(self):
        for counts,groups in (([[1]],[[1.]*8]),([[1,2]],[[1.]*9]),([[1.]],[[1.]*9]),([[1]],[[math.nan]*9])):
            with self.assertRaises(ValueError):_prf_batch.weighted_sums(counts,groups)

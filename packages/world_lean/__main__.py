"""Public runtime CLI; lacks formal evaluator/seed/holdout entrypoints."""
import argparse
import json
import sys
from .core import SYMS, OPS, canonical
from .analysis import aulc, binomial_one_sided
p=argparse.ArgumentParser(description='WORLD-LEAN-1 public runtime / analysis only')
p.add_argument('command',choices=['contract','aulc','sign-p'])
p.add_argument('values',nargs='*')
a=p.parse_args()
if a.command=='contract':
    output={'world':'lean-editor/1','primitive_types':list(OPS),
            'concrete_tokens':14,'sym_count':len(SYMS),
            'max_primitives':12,'finish_scoring':True,'evaluation_enabled':False}
elif a.command=='aulc':
    output={'aulc_fraction':str(aulc(tuple(int(x) for x in a.values)))}
else:
    output={'p_exact_fraction':str(binomial_one_sided(int(a.values[0])))}
sys.stdout.buffer.write(canonical(output))

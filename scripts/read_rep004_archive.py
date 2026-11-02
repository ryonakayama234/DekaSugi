"""Validate and reconstruct the full disclosed REP004 score archive, stdlib only."""
import argparse
import base64
import hashlib
import json
import zlib
from pathlib import Path

EXPECTED = '70ee6d9c531e18d1576d05649469808375678aebda804036d3ccc7d83ca8b1b3'
ARMS = ('LQ','LA','LR','ER','FA','FX','BODY-OFF','STATIC-MACRO')
BUDGETS = (0,1,2,4,8)
STRATA = ('SEEN_ROLEBLIND','UNSEEN_COMPOSITION','UNSEEN_IN_GRAMMAR','OUT_OF_GRAMMAR')


def verify(archive):
    blob=base64.b64decode(Path(archive).read_text(encoding='ascii').strip(),validate=True)
    raw=zlib.decompress(blob)
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:
        raise ValueError('RAW_SHA256_MISMATCH')
    data=json.loads(raw)
    rows=data['rows']
    keys={(r['stratum'],r['index'],r['arm'],r['budget']) for r in rows}
    expected={(s,i,a,b) for s in STRATA for i in range(12) for a in ARMS for b in BUDGETS}
    if len(rows)!=1920 or keys!=expected or data['summary']['trials']!=1920:
        raise ValueError('TRIAL_SET_MISMATCH')
    for r in rows:
        if not(0<=r['exact']<=64 and r['score']==r['exact']/64 and r['actions']<=r['budget']):
            raise ValueError('INVALID_ROW')
        if not isinstance(r['commit_digest'],str) or len(r['commit_digest'])!=64:
            raise ValueError('INVALID_COMMIT')
    for st in STRATA:
        for arm in ARMS:
            avg=round(sum(r['score'] for r in rows if r['stratum']==st and r['arm']==arm)/60,6)
            if avg!=data['summary']['summary'][st][arm]:
                raise ValueError('REAGGREGATION_MISMATCH')
    return raw,data


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--archive',required=True)
    ap.add_argument('--output')
    args=ap.parse_args()
    raw,data=verify(args.archive)
    if args.output:
        p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    print(json.dumps({'status':'ARCHIVE_VERIFIED','records':len(data['rows']),
        'raw_sha256':hashlib.sha256(raw).hexdigest()},sort_keys=True))

if __name__=='__main__':main()
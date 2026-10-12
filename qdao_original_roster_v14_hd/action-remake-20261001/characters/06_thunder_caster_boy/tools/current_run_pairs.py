"""Load only position observations whose reviewed PNG bytes are still current."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
SOURCES=['run_NE_SW_contactpairs_20261004.json','run_SE_contactpairs_20261004.json','run_S_contactpairs_20261004.json','run_EW_contactpairs_20261004.json','run_N_NW_contactpairs_20261004.json','full_limb_final_20261005.json']
def current_run_pairs():
    result={}
    for name in SOURCES:
        p=R/'review'/name
        if not p.exists():continue
        data=json.loads(p.read_text(encoding='utf-8-sig'))
        for f in data.get('frames',[]):
            rel=f.get('file',f.get('path',''))
            q=R/rel
            if not rel.startswith('runtime/run/') or not q.is_file():continue
            if hashlib.sha256(q.read_bytes()).hexdigest()!=f.get('sha256'):continue
            parts=rel.split('/')
            result[rel]={'supportLeg':f.get('supportLeg'),'pairFrames':f.get('pairFrames'),'positionPhase':f.get('positionPhase'),'sourceReview':'review/'+name,'sha256':f['sha256']}
    return result

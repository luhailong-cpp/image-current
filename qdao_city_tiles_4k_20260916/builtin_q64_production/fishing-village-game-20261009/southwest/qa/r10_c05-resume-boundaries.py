import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image
import numpy as np
Q = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
top = Q/'repair-r09_c05-v3-context-native.png'
bottom = Q/'full-tile-r10_c05-context-native.png'
a=np.array(Image.open(top).convert('RGB'))[115:4211,115:4211]
b=np.array(Image.open(bottom).convert('RGB'))[115:4211,115:4211]
combined=np.concatenate([a[-345:], b[:345]],axis=0)
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'role':'art boundary QA only; no game/runtime validation','northSources':[{'path':str(p),'sha256':sha(p)} for p in (top,bottom)],'operation':'integer crop + canonical hard cut, no resize or feather','boundaryYInCrop':345,'globalBoundaryY':36864,'qa':[]}
for i,x in enumerate([0,800,1600,2400,3196],1):
    p=Q/f'r10_c05-resume-north-{i}-100pct.png'
    pixels=combined[:,x:x+900]
    Image.fromarray(pixels).save(p)
    assert np.array_equal(np.array(Image.open(p)),pixels)
    out['qa'].append({'path':str(p),'sha256':sha(p),'globalBox':[16384+x,36864-345,16384+x+900,36864+345],'dimensions':[900,690]})
(Q/'r10_c05-resume-boundaries.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'northQaCount':5,'sourcesUnchanged':True}))

from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent.parent
rows=json.loads((root/'candidate-selection.json').read_text(encoding='utf-8-sig'))
result=[]
for e in rows:
    im=np.asarray(Image.open(root/e['file']))
    alpha=im[:,:,3]
    h,w=alpha.shape
    edges={k:int(v.max()) for k,v in {'left':alpha[:,0],'right':alpha[:,-1],'top':alpha[0,:],'bottom':alpha[-1,:]}.items()}
    ys,xs=np.where(alpha>32)
    bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    result.append({'action':e['action'],'direction':e['direction'],'frame':e['frame'],'file':e['file'],'visibleBBoxAlpha32':bbox,'edgeMaxAlpha':edges,'possibleClippedEdge':any(v>32 for v in edges.values())})
(root/'provenance/selected-edge-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([e for e in result if e['possibleClippedEdge']],ensure_ascii=False))


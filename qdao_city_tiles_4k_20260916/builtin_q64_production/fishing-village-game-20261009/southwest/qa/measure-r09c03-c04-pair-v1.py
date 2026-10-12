import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
p=Q/'pair-r09c03-c04-v1-trace.json';t=json.loads(p.read_text(encoding='utf-8-sig'))
out=[]
for i,v in enumerate(t['tiles']):
 a=np.array(Image.open(t['inputs'][i]['context']['path']).convert('RGB'));b=np.array(Image.open(v['context']['path']).convert('RGB'));d=np.any(a!=b,axis=2);ys,xs=np.where(d)
 out.append({'tile':v['tile'],'changedPixelCount':int(d.sum()),'changedContextBBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None,'coreChangedPixelCount':int(d[115:4211,115:4211].sum()),'southHaloChangedPixelCount':int(d[4211:].sum()),'northHaloChangedPixelCount':int(d[:115].sum())})
print(json.dumps(out))


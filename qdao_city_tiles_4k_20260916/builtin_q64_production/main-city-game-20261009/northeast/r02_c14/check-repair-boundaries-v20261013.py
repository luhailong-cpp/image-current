from pathlib import Path
from PIL import Image
import json,numpy as np
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
plan=json.loads((Q/'repair-plan-v1.json').read_text());result={}
for p in plan['repairs']:
 a=np.array(Image.open(p['input']).convert('RGB'),dtype=float);b=np.array(Image.open(T/'native/repairs'/(p['id']+'-local-v20261013.png')).convert('RGB'),dtype=float)
 d=np.abs(a-b).mean(2);xs=d.mean(0);ys=d.mean(1)
 roi=[int(xs[:151].argmin()),int(ys[:151].argmin()),int(1103+xs[1103:].argmin()+1),int(1103+ys[1103:].argmin()+1)]
 result[p['id']]={'suggestedCrop':roi,'meanAbsRGB':float(d.mean()),'edgeScores':[float(xs[roi[0]]),float(ys[roi[1]]),float(xs[roi[2]-1]),float(ys[roi[3]-1])]}
(Q/'boundary-crop-diagnostics-v1.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

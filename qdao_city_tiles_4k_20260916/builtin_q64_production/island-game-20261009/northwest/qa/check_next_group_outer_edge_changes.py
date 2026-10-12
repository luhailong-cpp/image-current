from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf8'))
inputs=read(Z/'qa/connected-r04-r05-c03-c04-v1.input-manifest.json')['tileMatrix']
current=read(Z/'qa/connected-r04-r05-current-v1.manifest.json')['tiles']
report=[]
for row in inputs:
 for item in row:
  tid=item['tileId'];out=next(x for x in current if x['tileId']==tid)
  a=np.array(Image.open(item['image']['path']));b=np.array(Image.open(out['image']['path']))
  edges={}
  for side,aa,bb in [('north',a[0],b[0]),('south',a[-1],b[-1]),('west',a[:,0],b[:,0]),('east',a[:,-1],b[:,-1])]:
   ix=np.flatnonzero(np.any(aa!=bb,axis=-1));edges[side]=dict(changedPixels=len(ix),minimumCoordinate=int(ix.min()) if len(ix) else None,maximumCoordinateInclusive=int(ix.max()) if len(ix) else None)
  report.append(dict(tileId=tid,input=item['image'],connected=out['image'],edges=edges))
out=Z/'qa/connected-r04-r05-v1.input-edge-differences.json'
with out.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps([dict(tileId=x['tileId'],edges=x['edges']) for x in report],indent=2))

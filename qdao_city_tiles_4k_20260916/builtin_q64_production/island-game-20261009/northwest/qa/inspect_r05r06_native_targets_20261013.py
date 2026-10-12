from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1]
M=Z/'qa/connected-r05-r06-current-v1.manifest.json'
D=json.loads(M.read_text(encoding='utf8'))
O=Z/'qa/cross_r05r06_native_targets_review_20261013_v1';O.mkdir(exist_ok=False)
info=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
jobs={'rail_west':[3470,4596,4724,5850],'paving_north':[5060,3470,6314,4724]}
items=[]
for name,box in jobs.items():
 im=Image.new('RGB',(1254,1254));parts=[]
 for i,t in enumerate(D['tiles']):
  p=Path(t['image']['path']);assert info(p)==t['image']
  ox,oy=(i%2)*4096,(i//2)*4096
  x0,y0=max(box[0],ox),max(box[1],oy);x1,y1=min(box[2],ox+4096),min(box[3],oy+4096)
  if x1<=x0 or y1<=y0:continue
  with Image.open(p) as src:im.paste(src.crop((x0-ox,y0-oy,x1-ox,y1-oy)),(x0-box[0],y0-box[1]))
  parts.append(dict(tileId=t['tileId'],source=t['image'],sourceBox=[x0-ox,y0-oy,x1-ox,y1-oy]))
 p=O/f'{name}.png';im.save(p)
 items.append(dict(name=name,clusterBox=box,output=info(p),parts=parts))
with (O/'index.json').open('x',encoding='utf8') as f:json.dump(dict(operation='diagnostic exact native crop, not final artwork',manifest=info(M),isAiGeneration=False,resizing=False,pixelSynthesis=False,items=items),f,indent=2)
print(str(O))

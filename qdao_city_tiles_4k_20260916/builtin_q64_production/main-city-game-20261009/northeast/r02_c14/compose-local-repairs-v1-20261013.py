from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(Q/'repair-plan-v1.json');base=Path(plan['baseCandidate']['file']);original=Image.open(base).convert('RGB');out=original.copy()
rois={'wall-leaves':[80,240,1104,970],'leaf-bands':[115,220,1139,800],'roof-corner':[80,80,1174,1060],'rock-corner':[115,350,1139,1139]}
layers=[]
for item in plan['repairs']:
 f=T/'native/repairs'/(item['id']+'-local-v20261013.png');rec=read(Path(str(f)+'.generation.json'));assert sha(f)==rec['sha256']
 crop=rois[item['id']];x,y=item['origin'];out.paste(Image.open(f).convert('RGB').crop(crop),(x+crop[0],y+crop[1]))
 layers.append({'id':item['id'],'file':str(f),'sha256':rec['sha256'],'origin':[x,y],'crop':crop})
dest=T/'candidates/r02_c14.local-repairs-v1-20261013.png';dest.parent.mkdir(exist_ok=True);assert not dest.exists();out.save(dest)
control=out.copy()
for layer in layers:
 x,y=layer['origin'];a,b,c,d=layer['crop'];box=(x+a,y+b,x+c,y+d);control.paste(original.crop(box),box[:2])
assert ImageChops.difference(control,original).getbbox() is None
for item in plan['repairs']:
 x,y=item['origin'];out.crop((x,y,x+1254,y+1254)).save(Q/(item['id']+'-composed-v1.png'))
binding={'baseCandidate':str(base),'baseSha256':sha(base),'candidate':str(dest),'candidateSha256':sha(dest),'layers':layers,'operation':'Integer native crop/paste only. No resampling, blurring, feathering, synthetic painting.','outsideRepairRectanglesByteIdentical':True,'status':'composed_visual_boundary_review_pending','internalPassed4kCount':0}
(Q/'composition-v1.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf-8')
print(json.dumps(binding))

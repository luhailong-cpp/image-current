from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,numpy as np
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prev=read(Q/'composition-v3.json');base=Path(prev['candidate']);assert sha(base)==prev['candidateSha256'];original=Image.open(base).convert('RGB');out=original.copy()
specs={'wall-right':([350,485],[435,565],[840,1020],[675,840]),'leaf-right':([800,960],[450,590],None,[690,880]),'rock-bottom':([0,110],[600,745],[1150,1254],[1030,1170])}
layers=[];windows=[]
for key,ranges in specs.items():
 f=T/'native/repairs'/(key+'-local-v2-20261013.png');rec=read(Path(str(f)+'.generation.json'));req=read(T/'prompts'/(key+'-local-v2-20261013.request.json'))
 assert sha(f)==rec['sha256'];x,y=req['repairTarget']['origin']
 im=Image.open(f).convert('RGB');src=Image.open(req['referenced_image_paths'][0]).convert('RGB')
 diff=np.abs(np.asarray(im).astype(float)-np.asarray(src).astype(float)).mean(axis=2)
 crop=[]
 for axis,limits in enumerate(ranges):
  if limits is None:crop.append(1254);continue
  lo,hi=limits
  values=[]
  for p in range(lo,hi):
   strip=diff[max(p-2,0):min(p+3,1254),:] if axis in [1,3] else diff[:,max(p-2,0):min(p+3,1254)]
   values.append((float(strip.mean()),p))
  crop.append(min(values)[1])
 a,b,c,d=crop;out.paste(im.crop(crop),(x+a,y+b))
 layers.append({'id':key,'file':str(f),'sha256':sha(f),'origin':[x,y],'crop':crop,'edgeSelection':'Minimum measured line difference within specified native-crop boundary windows; no pixel modification.'})
dest=T/'candidates/r02_c14.local-repairs-v4-20261013.png';assert not dest.exists();out.save(dest)
check=out.copy()
for item in layers:
 x,y=item['origin'];a,b,c,d=item['crop'];box=[x+a,y+b,x+c,y+d];check.paste(original.crop(box),box[:2])
assert ImageChops.difference(check,original).getbbox() is None
for item in layers:
 x,y=item['origin'];f=Q/(item['id']+'-composed-v4.png');out.crop([x,y,x+1254,y+1254]).save(f);windows.append(str(f))
binding={'baseCandidate':str(base),'baseSha256':sha(base),'candidate':str(dest),'candidateSha256':sha(dest),'priorComposition':str(Q/'composition-v3.json'),'layers':layers,'windows':windows,'outsideRepairRectanglesByteIdentical':True,'operation':'Integer native crop/paste only, no resampling, blur, blending, synthetic detail or color correction.','status':'local_visual_review_pending','internalPassed4kCount':0,'formalAcceptedCount':0}
(Q/'composition-v4.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf-8')
print(json.dumps(binding))


from pathlib import Path
import sys,json,hashlib,importlib.util
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent
R=W.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('hard',R/'assemble_r03_c03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def patch(sr,sc):
 p=W/'selections'/f's{sr:02d}_s{sc:02d}.json'
 return Path(read(p)['file']) if p.exists() else None
def run(sr,sc):
 p=patch(sr,sc);im=Image.open(p).convert('RGB');a=np.asarray(im);reports=[]
 for rr,cc,role in [(sr-1,sc,'north'),(sr,sc-1,'west'),(sr,sc+1,'east'),(sr+1,sc,'south')]:
  npth=Path(read(W/'plan.json')['northBoundary'][sc-1]['file']) if rr==0 else patch(rr,cc)
  if not npth:continue
  ni=Image.open(npth).convert('RGB');b=np.asarray(ni)
  if role in ('west','east'):first,second=(b,a) if role=='west' else(a,b)
  else:first,second=(b.transpose(1,0,2),a.transpose(1,0,2)) if role=='north' else(a.transpose(1,0,2),b.transpose(1,0,2))
  ids=np.ones((1254,1254),dtype=np.uint8)
  stitched,_,detail=m.append_hard(first,ids,second,ids*2,role)
  mid=np.concatenate((first[:,939:1139],second[:,115:315]),axis=1)
  crop=stitched[:,939:1339]
  if role in ('north','south'):mid=mid.transpose(1,0,2);crop=crop.transpose(1,0,2)
  prefix=W/'qa'/f'{p.stem}.{role}'
  Image.fromarray(mid).save(str(prefix)+'-midline-100pct.png');Image.fromarray(crop).save(str(prefix)+'-mincut-100pct.png')
  reports.append({'role':role,'neighbor':str(npth),'sha256':sha(npth),'seam':detail,'qaPrefix':str(prefix)})
 if sr==1:
  n=R/'tiles'/'r03_c03.candidate.png';t=Image.open(n);x=(sc-1)*1024
  out=Image.new('RGB',(1024,400));out.paste(t.crop((x,3896,x+1024,4096)),(0,0));out.paste(im.crop((115,115,1139,315)),(0,200));out.save(W/'qa'/f'{p.stem}.north-actual-tile-100pct.png')
  reports.append({'actualNorthTile':str(n),'sha256':sha(n)})
 write(W/'qa'/f'{p.stem}.mechanical-qa.json',{'source':str(p),'sha256':sha(p),'method':'native integer cuts plus exact minimum-error hard cut; no scaling or feathering','neighbors':reports})
 print(json.dumps({'source':p.name,'neighbors':[r.get('role','actual tile') for r in reports]}))
if __name__=='__main__':run(*map(int,sys.argv[1:3]))

from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent
sys.path.insert(0,str(B))
from assemble_r03_c03 import append_hard
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def patch(r,c):
 p=W/'selections'/f's{r:02d}_s{c:02d}.json';return Path(read(p)['file']) if p.exists() else None
r,c=map(int,sys.argv[1:3]);p=patch(r,c);a=np.asarray(Image.open(p).convert('RGB'));out=[]
for rr,cc,role in [(r-1,c,'north'),(r,c-1,'west'),(r,c+1,'east'),(r+1,c,'south')]:
 npth=patch(rr,cc)
 if not npth:continue
 b=np.asarray(Image.open(npth).convert('RGB'));first,second=(b,a) if role in ('north','west') else (a,b)
 if role in ('north','south'):first=first.transpose(1,0,2);second=second.transpose(1,0,2)
 stitched,_,detail=append_hard(first,np.ones((1254,1254),np.uint16),second,np.ones((1254,1254),np.uint16)*2,role)
 crop=stitched[:,939:1339]
 if role in ('north','south'):crop=crop.transpose(1,0,2)
 path=W/'qa'/f'{p.stem}.{role}-mincut-100pct.png';Image.fromarray(crop).save(path);out.append(str(path))
if r==1:
 n=Image.open(B/'delivery-2x2/stage-v4/r04_c04.png');x=(c-1)*1024;band=Image.new('RGB',(1024,400));band.paste(n.crop((x,3896,x+1024,4096)),(0,0));band.paste(Image.fromarray(a).crop((115,115,1139,315)),(0,200));q=W/'qa'/f'{p.stem}.north-actual-100pct.png';band.save(q);out.append(str(q))
if c==1:
 n=Image.open(B/'work-r05_c03/final-v1/r05_c03.candidate.png');y=(r-1)*1024;band=Image.new('RGB',(400,1024));band.paste(n.crop((3896,y,4096,y+1024)),(0,0));band.paste(Image.fromarray(a).crop((115,115,315,1139)),(200,0));q=W/'qa'/f'{p.stem}.west-actual-100pct.png';band.save(q);out.append(str(q))
print(json.dumps({'source':str(p),'crops':out}))


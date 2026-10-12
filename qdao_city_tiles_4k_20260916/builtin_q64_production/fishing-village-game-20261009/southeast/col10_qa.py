"""Native core assembly and inspection crops; no generated or resized delivery pixels."""
from pathlib import Path
import json, hashlib
from datetime import datetime,timezone
from PIL import Image
import numpy as np
import sys
T=Path(__file__).resolve().parent/sys.argv[1]
assert T.name in ['r11_c10','r12_c10','r13_c10','r14_c10']
plan=json.loads((T/'coordinate-plan.json').read_text(encoding='utf-8-sig'))
x0,y0=plan['tileOrigin']
Q=T/'qa'/'internal'
Q.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
selected=read(T/'selected-patches.json')
canvas=Image.new('RGB',(4096,4096))
parts={}
sources=[]
for pid,rel in selected['patches'].items():
 r,c=int(pid[1])-1,int(pid[2])-1
 path=T/rel;im=Image.open(path).convert('RGB');assert im.size==(1254,1254)
 core=im.crop((115,115,1139,1139));canvas.paste(core,(c*1024,r*1024))
 parts[pid]=core
 sources.append({'patch':pid,'path':str(path),'sha256':sha(path),'crop':[115,115,1139,1139],'destination':[c*1024,r*1024,(c+1)*1024,(r+1)*1024]})
records=[]
for r in range(1,5):
 for c in range(1,5):
  a=f'p{r}{c}'
  if a not in parts:continue
  for dr,dc,axis in [(0,1,'vertical'),(1,0,'horizontal')]:
   b=f'p{r+dr}{c+dc}'
   if b not in parts:continue
   if axis=='vertical':
    out=Image.new('RGB',(512,1024));out.paste(parts[a].crop((768,0,1024,1024)),(0,0));out.paste(parts[b].crop((0,0,256,1024)),(256,0))
    world=[x0+c*1024-256,y0+(r-1)*1024,x0+c*1024+256,y0+r*1024]
    aa=np.asarray(parts[a],dtype=np.int16)[:,-1];bb=np.asarray(parts[b],dtype=np.int16)[:,0]
   else:
    out=Image.new('RGB',(1024,512));out.paste(parts[a].crop((0,768,1024,1024)),(0,0));out.paste(parts[b].crop((0,0,1024,256)),(0,256))
    world=[x0+(c-1)*1024,y0+r*1024-256,x0+c*1024,y0+r*1024+256]
    aa=np.asarray(parts[a],dtype=np.int16)[-1];bb=np.asarray(parts[b],dtype=np.int16)[0]
   file=Q/f'{a}--{b}.png';out.save(file)
   record={'id':f'{a}--{b}','file':str(file),'sha256':sha(file),'axis':axis,'globalBox':world,'dimensions':list(out.size),'seamCoordinateInCrop':256,'meanRGBStep':float(np.abs(aa-bb).mean()),'resamplingApplied':False,'sources':[s for s in sources if s['patch'] in (a,b)],'visualStatus':'pending'}
   write(file.with_suffix('.png.derivation.json'),record);records.append(record)
crossings=[]
for r in range(1,4):
 for c in range(1,4):
  pids=[f'p{rr}{cc}' for rr in (r,r+1) for cc in (c,c+1)]
  if not all(pid in parts for pid in pids):continue
  box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256]
  file=Q/f'cross-r{r}-c{c}.png';canvas.crop(box).save(file)
  rec={'id':file.stem,'file':str(file),'sha256':sha(file),'globalBox':[box[0]+x0,box[1]+y0,box[2]+x0,box[3]+y0],'sources':[s for s in sources if s['patch'] in pids],'resamplingApplied':False,'visualStatus':'pending'}
  write(file.with_suffix('.png.derivation.json'),rec);crossings.append(rec)
complete=len(parts)==16
candidate=None
if complete:
 candidate=T/f'{T.name}-candidate-4096.png';canvas.save(candidate)
 assert Image.open(candidate).size==(4096,4096)
 write(candidate.with_suffix('.png.derivation.json'),{'file':str(candidate),'sha256':sha(candidate),'dimensions':[4096,4096],'globalBox':plan['tileCoreBox'],'operation':'16 unscaled native core crops, hard joined at halo midlines','coreCrop':[115,115,1139,1139],'resamplingApplied':False,'layoutPixelsUsed':False,'formalAccepted':False,'sources':sources})
preview=Q/'overview-QA-only-1024.png';canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
write(preview.with_suffix('.png.derivation.json'),{'sha256':sha(preview),'operation':'downsampled QA-only composite; black gaps are missing cores','sources':sources,'complete':complete})
summary={'tile':T.name,'createdAt':datetime.now(timezone.utc).isoformat(),'selectedCount':len(parts),'complete4kCount':int(complete),'formalAccepted':False,'candidate':str(candidate) if candidate else None,'preview':str(preview),'seams':records,'crossings':crossings,'visualStatus':'pending','externalStatus':'pending final neighbor review'}
write(Q/'manifest.json',summary)
print(json.dumps({'selectedCount':len(parts),'seams':len(records),'crossings':len(crossings),'candidate':str(candidate) if candidate else None,'preview':str(preview)}))


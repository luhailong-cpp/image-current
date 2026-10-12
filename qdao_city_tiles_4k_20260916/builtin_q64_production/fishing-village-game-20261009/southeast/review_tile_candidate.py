"""Exact native assembly and all available internal seam/cross QA crops."""
from pathlib import Path
from PIL import Image
import sys,json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;tile=sys.argv[1];T=Z/tile
selection=T/(sys.argv[2] if len(sys.argv)>2 else 'selected-patches.json')
label=sys.argv[3] if len(sys.argv)>3 else 'root-pass'
Q=T/'qa'/label;Q.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sel=json.loads(selection.read_text(encoding='utf-8-sig'));parts={};sources=[]
ox,oy=(int(tile[5:7])-1)*4096,(int(tile[1:3])-1)*4096
canvas=Image.new('RGB',(4096,4096))
for pid,rel in sel['patches'].items():
 p=T/rel;im=Image.open(p);assert im.size==(1254,1254)
 core=im.crop((115,115,1139,1139));r,c=int(pid[1])-1,int(pid[2])-1;canvas.paste(core,(c*1024,r*1024));parts[pid]=core
 sources.append({'patch':pid,'file':str(p),'sha256':sha(p),'crop':[115,115,1139,1139],'destination':[c*1024,r*1024]})
records=[]
def crop_record(name,b,pids):
 p=Q/f'{name}.png';canvas.crop(b).save(p)
 d={'file':str(p),'sha256':sha(p),'globalBox':[b[0]+ox,b[1]+oy,b[2]+ox,b[3]+oy],'sources':[s for s in sources if s['patch'] in pids],'resamplingApplied':False,'visualReview':'pending'}
 write(p.with_suffix('.png.derivation.json'),d);records.append(d)
for r in range(1,5):
 for c in range(1,5):
  a=f'p{r}{c}'
  if a not in parts:continue
  for dr,dc in [(0,1),(1,0)]:
   b=f'p{r+dr}{c+dc}'
   if b not in parts:continue
   box=[c*1024-256,(r-1)*1024,c*1024+256,r*1024] if dc else [(c-1)*1024,r*1024-256,c*1024,r*1024+256]
   crop_record(f'{a}--{b}',box,[a,b])
for r in range(1,4):
 for c in range(1,4):
  ids=[f'p{rr}{cc}' for rr in (r,r+1) for cc in (c,c+1)]
  if all(p in parts for p in ids):crop_record(f'cross-r{r}-c{c}',[c*1024-256,r*1024-256,c*1024+256,r*1024+256],ids)
candidate=None
if len(parts)==16:
 candidate=Q/'candidate-4096.png';canvas.save(candidate);write(candidate.with_suffix('.png.derivation.json'),{'sha256':sha(candidate),'operation':'16 exact native cores','sources':sources,'resamplingApplied':False,'layoutPixelsUsed':False})
preview=Q/'preview-QA-1024.png';canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
write(Q/'manifest.json',{'tile':tile,'createdAt':datetime.now(timezone.utc).isoformat(),'selection':str(selection),'selectionSha256':sha(selection),'sources':sources,'evidence':records,'candidate':str(candidate) if candidate else None,'selectedCount':len(parts),'formalAccepted':False,'internalReady':False})
print(json.dumps({'tile':tile,'selectedCount':len(parts),'QAImageCount':len(records),'directory':str(Q)}))

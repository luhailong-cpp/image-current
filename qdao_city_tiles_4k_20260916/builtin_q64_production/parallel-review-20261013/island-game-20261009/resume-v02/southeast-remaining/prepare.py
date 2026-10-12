from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
full={t['tileId']:t for t in read(R/'southeast-audit-v01/inventory.json')['tiles'] if t['fullCoverage']}
def rc(tid):return int(tid[1:3]),int(tid[5:7])
def id(r,c):return f'r{r:02d}_c{c:02d}'
existing_pairs={};existing_cross=set()
for ts in [['r09_c12','r09_c13','r10_c12','r10_c13'],['r11_c11','r11_c12','r12_c11','r12_c12']]:
 existing_cross.add(tuple(sorted(ts)))
 for a in ts:
  r,c=rc(a)
  for b in [id(r+1,c),id(r,c+1)]:
   if b in ts:existing_pairs[tuple(sorted([a,b]))]='previous source-hash-verified local group'
new=[]
for a,t in full.items():
 r,c=rc(a)
 for b,orientation in [(id(r,c+1),'vertical'),(id(r+1,c),'horizontal')]:
  if b not in full or tuple(sorted([a,b])) in existing_pairs:continue
  directory=O/f'{a}__{b}';directory.mkdir(exist_ok=True);records=[];board=Image.new('RGB',(2048,1024))
  with Image.open(t['file']) as ai,Image.open(full[b]['file']) as bi:
   for s in range(4):
    if orientation=='vertical':
     im=Image.new('RGB',(512,1024));im.paste(ai.crop((3840,s*1024,4096,(s+1)*1024)),(0,0));im.paste(bi.crop((0,s*1024,256,(s+1)*1024)),(256,0));world=[c*4096-256,(r-1)*4096+s*1024,c*4096+256,(r-1)*4096+(s+1)*1024];board.paste(im,(s*512,0))
    else:
     im=Image.new('RGB',(1024,512));im.paste(ai.crop((s*1024,3840,(s+1)*1024,4096)),(0,0));im.paste(bi.crop((s*1024,0,(s+1)*1024,256)),(0,256));world=[(c-1)*4096+s*1024,r*4096-256,(c-1)*4096+(s+1)*1024,r*4096+256];board.paste(im,((s%2)*1024,(s//2)*512))
    f=directory/f'segment-{s+1}-100pct.png';im.save(f);records.append({'file':f.as_posix(),'sha256':sha(f),'worldBox':world,'segment':s+1,'dimensions':list(im.size)});im.close()
  f=directory/'board-100pct.png';board.save(f);board.close();new.append({'tiles':[a,b],'orientation':orientation,'inputs':[{'file':full[x]['file'],'sha256':full[x]['sha256']} for x in [a,b]],'segments':records,'board':f.as_posix(),'status':'pending_visual_review','formalAccepted':False})
cross=[]
for a,t in full.items():
 r,c=rc(a);ids=[a,id(r,c+1),id(r+1,c),id(r+1,c+1)]
 if not all(x in full for x in ids) or tuple(sorted(ids)) in existing_cross:continue
 im=Image.new('RGB',(1024,1024))
 for j,x in enumerate(ids):
  with Image.open(full[x]['file']) as src:
   box=[3584 if j%2==0 else 0,3584 if j<2 else 0,4096 if j%2==0 else 512,4096 if j<2 else 512];im.paste(src.crop(box),((j%2)*512,(j//2)*512))
 f=O/f'cross-{a}-100pct.png';im.save(f);im.close();cross.append({'tiles':ids,'worldPoint':[c*4096,r*4096],'file':f.as_posix(),'sha256':sha(f),'status':'pending_visual_review','formalAccepted':False})
write(O/'summary.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceVerification':'../southeast/baseline-candidate-reuse.json','scope':'remaining full-candidate neighbor edges outside previously inspected groups; same frozen pixels','newEdgeReviews':new,'newCrossReviews':cross,'generationCalls':0,'productionWrites':False,'formalAcceptedCount':0})
print(json.dumps({'newPairs':[x['tiles'] for x in new],'newCrosses':[x['tiles'] for x in cross]}))

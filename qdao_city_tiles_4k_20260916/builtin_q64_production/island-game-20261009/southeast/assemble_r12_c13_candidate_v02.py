from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
import numpy as np
R=Path(__file__).resolve().parent;Q=R/'qa/r12_c13-resume-sol-20261012'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
vs=read(R/'progress-r12_c13.json')['selectedVersions'];assert len(vs)==16
out=R/'tiles/r12_c13.candidate-sol-20261012-v02.png';assert not out.exists()
im=Image.new('RGB',(4096,4096));sources=[]
for rc,v in sorted(vs.items()):
 p=R/'native'/f'r12_c13_p{rc}_{v}.png';a=Image.open(p).convert('RGB');assert a.size==(1254,1254);x=(int(rc[1])-1)*1024;y=(int(rc[0])-1)*1024
 im.paste(a.crop((115,115,1139,1139)),(x,y));sources.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':[115,115,1139,1139],'destination':[x,y],'role':'exact selected native core'})
im.save(out);d={'file':out.as_posix(),'sha256':sha(out),'width':4096,'height':4096,'operation':'exact 16 source-native 1024 core crop/paste; no resampling, blending or painting','sources':sources,'selectedPatchVersions':vs,'formalAccepted':False,'status':'full_coverage_pending_seam_review','createdAtUtc':datetime.now(timezone.utc).isoformat()};write(Path(str(out)+'.generation.json'),d)
actual=np.asarray(Image.open(out).convert('RGB'));mismatched=0
for s in sources:
 x,y=s['destination'];a=np.asarray(Image.open(s['file']).convert('RGB').crop(tuple(s['sourceCrop'])));n=int(np.count_nonzero(np.any(actual[y:y+1024,x:x+1024]!=a,axis=2)));s['mismatchedPixels']=n;mismatched+=n
write(Q/'candidate-v02-source-pixel-proof.json',{'file':out.as_posix(),'sha256':sha(out),'coveredPixels':4096**2,'mismatchedPixels':mismatched,'sourceCoreCount':16,'resampled':False,'blended':False,'paintedAfterGeneration':False,'sources':sources,'passed':mismatched==0})
items=[]
for r in range(4):
 for c in range(1,4):
  b=[c*1024-256,r*1024,c*1024+256,(r+1)*1024];p=Q/f'candidate-v02-seam-v-r{r+1}-c{c}.png';im.crop(tuple(b)).save(p);items.append({'id':f'v-r{r+1}-c{c}','box':b,'file':p.as_posix(),'sha256':sha(p),'status':'pending_visual'})
for r in range(1,4):
 for c in range(4):
  b=[c*1024,r*1024-256,(c+1)*1024,r*1024+256];p=Q/f'candidate-v02-seam-h-r{r}-c{c+1}.png';im.crop(tuple(b)).save(p);items.append({'id':f'h-r{r}-c{c+1}','box':b,'file':p.as_posix(),'sha256':sha(p),'status':'pending_visual'})
junctions=[]
for r in range(1,4):
 for c in range(1,4):
  b=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];p=Q/f'candidate-v02-junction-r{r}-c{c}.png';im.crop(tuple(b)).save(p);junctions.append({'id':f'junction-r{r}-c{c}','box':b,'file':p.as_posix(),'sha256':sha(p),'status':'pending_visual'})
w=R/'tiles/r12_c12.candidate-sol-20261012-v01.png';wi=Image.open(w).convert('RGB');qa=Q/'candidate-v02-west-full-seam.png';seam=Image.new('RGB',(512,4096));seam.paste(wi.crop((3840,0,4096,4096)),(0,0));seam.paste(im.crop((0,0,256,4096)),(256,0));seam.save(qa)
write(Path(str(qa)+'.trace.json'),{'operation':'exact native-derived full candidate west core hard seam','resampled':False,'sources':[{'file':w.as_posix(),'sha256':sha(w),'crop':[3840,0,4096,4096],'destination':[0,0]},{'file':out.as_posix(),'sha256':sha(out),'crop':[0,0,256,4096],'destination':[256,0]}],'file':qa.as_posix(),'sha256':sha(qa)})
for row in range(1,5):seam.crop((0,(row-1)*1024,512,row*1024)).save(Q/f'candidate-v02-west-row{row}.png')
write(Q/'candidate-v02-seam-review.json',{'candidate':out.as_posix(),'sha256':sha(out),'internalSeams':items,'junctions':junctions,'status':'pending_visual','formalAccepted':False})
print(json.dumps({'candidate':out.as_posix(),'sha256':sha(out),'proofMismatchedPixels':mismatched,'internalSeams':len(items),'junctions':len(junctions),'formalAccepted':False}))

"""Adopt the reviewed shared stairs joint as a candidate; preserve every source and old selection."""
from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent
Q=Z/'seam-qa/G3-shared-stairs-resume-20261012'
I=Q/'G3-bottom-conditioned-v3.adoption-instructions.json'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def copy_exact(a,b):
 b.parent.mkdir(parents=True,exist_ok=True)
 if b.exists(): assert sha(a)==sha(b)
 else: shutil.copy2(a,b)
 assert sha(a)==sha(b)
d=read(I); now=datetime.now(timezone.utc).isoformat()
for row in d['currentSelections']: assert sha(Path(row['canonical']))==row['canonicalSha256']
sels={}
for tile in ('r12_c09','r12_c10'):
 T=Z/tile;p=T/'selected-patches.json'
 copy_exact(p,T/'qa/G3-joint-adoption-20261012/selection-before.json')
 sels[tile]=read(p)
records=[]
for row in d['patches']:
 tile,pid=row['tile'],row['patch'];T=Z/tile;a=Path(row['file'])
 assert sha(a)==row['sha256']
 assert Image.open(a).size==(1254,1254)
 b=T/f'processed/G3-joint-resume-20261012/{pid}-G3-native-v3.png'
 copy_exact(a,b)
 old=sels[tile]['patches'].get(pid)
 record={'patch':pid,'source':str(a),'sourceSha256':sha(a),'file':str(b),'sha256':sha(b),'previousSelection':old,'operation':'Byte-exact copy of generated v2 polygon-mask and v3 native rectangle composition; see replay package','adoptionInstructions':str(I),'adoptionInstructionsSha256':sha(I),'nativeDimensions':[1254,1254],'coreCrop':[115,115,1139,1139],'resamplingApplied':False,'layoutPixelsUsed':False,'internalReady':False,'formalAccepted':False,'materialPending':True}
 write(b.with_suffix('.png.derivation.json'),record); records.append(record)
 sels[tile]['patches'][pid]=b.relative_to(T).as_posix()
for tile,sel in sels.items():
 T=Z/tile
 assert len(sel['patches'])==16
 canvas=Image.new('RGB',(4096,4096));sources=[]
 for pid,rel in sorted(sel['patches'].items()):
  a=T/rel;im=Image.open(a);assert im.size==(1254,1254)
  xy=((int(pid[2])-1)*1024,(int(pid[1])-1)*1024)
  canvas.paste(im.crop((115,115,1139,1139)),xy)
  sources.append({'patch':pid,'file':str(a),'sha256':sha(a),'crop':[115,115,1139,1139],'destination':list(xy)})
 p=T/f'candidate/{tile}-G3-joint-resume-20261012-v3-4096.png'
 p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();canvas.save(p)
 write(p.with_suffix('.png.derivation.json'),{'operation':'16 exact native 1024 cores','sources':sources,'sha256':sha(p),'dimensions':[4096,4096],'resamplingApplied':False,'layoutPixelsUsed':False})
 sel.update(candidate=str(p),candidateSha256=sha(p),status='full_native_candidate_joint_material_QA_pending',internalReady=False,formalAccepted=False,materialPending=True,wallJointAdoption=str(Q/'root-G3-joint-adoption-20261012.json'),updatedAt=now)
 write(T/'selected-patches.json',sel)
write(Q/'root-G3-joint-adoption-20261012.json',{'createdAt':now,'sourceInstructions':str(I),'sourceInstructionsSha256':sha(I),'patches':records,'geometryReview':str(Q/'root-v3-independent-geometry-review.json'),'materialPending':True,'formalAccepted':False,'candidateSelections':{t:str(Z/t/'selected-patches.json') for t in sels}})
print(json.dumps({'coordinatedPatches':len(records),'fullCandidates':list(sels),'materialPending':True}))

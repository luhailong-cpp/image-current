from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util,sys,uuid
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(p)
label,passed,remaining,note=sys.argv[1:]
passed=passed.split(',') if passed else [];remaining=remaining.split(',') if remaining else []
p=T/'repairs'/label/'composition.json';m=read(p)
spec=importlib.util.spec_from_file_location('selection',T/'selective_replay.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
replay=mod.replay(str(p));now=datetime.now(timezone.utc).isoformat()
qa={'reviewedAt':now,'status':'local_pass','scope':note,'localPassedRepairs':passed,'remainingInternal':remaining,'internalArtQA':'failed_remaining_'+','.join(remaining) if remaining else 'local_internal_repairs_pass_pending_full_review','externalNeighborSeamQA':'not_passed','formalAccepted':False,'replay':replay}
put(p.parent/'visual-review.json',qa)
m['candidate']['size']=[4096,4096];m['context']['size']=[4326,4326]
put(T/'repairs/latest-repair.json',m)
old=read(T/'candidate/latest-assembly.json')
new={'schemaVersion':2,'tile':'r14_c14','status':'partial_native_repair_remaining_QA','publishedAt':now,'candidate':m['candidate'],'context':m['context'],'manifest':{'path':str(p),'sha256':sha(p)},'initialAssembly':old.get('initialAssembly',old),'localPassedRepairs':passed,'remainingInternal':remaining,'reservedCorner':[0,0,630,630],'reservedCornerUnchanged':True,'externalNeighborSeamQA':'not_passed','formalAccepted':False}
put(T/'candidate/latest-assembly.json',new)
q=T/'review'/('published-'+label);q.mkdir(exist_ok=True)
Image.open(m['candidate']['path']).resize((1024,1024),Image.Resampling.LANCZOS).save(q/'overview-preview-only.png')
records=list((T/'native').glob('*.generation.json'))+list((T/'repairs').glob('*/generation.json'))
progress=read(T/'progress.json');progress.update(status=new['status'],updatedAt=now,activeNativeCount=16,generatedNativeCount=len(records),complete4kCandidateCount=1,internalArtQA=qa['internalArtQA'],externalNeighborSeamQA='not_passed',candidate=m['candidate']['path'],context=m['context']['path'],assemblyManifest=str(p),formalAccepted=False,currentPatch=','.join(remaining),nextStep='Continue remaining native repairs, then full internal review and current neighbor-core edge review; protect northwest630 square.')
put(T/'progress.json',progress)
for f in ['continuation-round-20261011.json','local-continuation-20261011.json']:
 c=read(T/f);c.update(updatedAt=now,currentCoordinate='r14_c14 remaining '+','.join(remaining),candidate=m['candidate'],manifest=new['manifest'],internalQA=qa['internalArtQA'],externalQA='not_passed',localPassedRepairs=passed,remainingInternal=remaining,formalAccepted=False);put(T/f,c)
print(json.dumps({'candidate':m['candidate'],'manifest':new['manifest'],'generatedNativeRecordCount':len(records),'replay':replay},indent=2))

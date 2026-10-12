from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
p=T/'repairs/i06-retained-20261011/composition.json';m=read(p)
spec=importlib.util.spec_from_file_location('selection',T/'selective_replay.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
replay=mod.replay(str(p))
now=datetime.now(timezone.utc).isoformat()
qa={'reviewedAt':now,'status':'local_pass','scope':'I06 only: dangling diagonal grout near x3006,y2705 now connects to existing left slab groove. Full1254 composition viewed, source perimeter and red paper retained. I07 lower isolated corner is explicitly excluded and remains unresolved.','internalArtQA':'failed_remaining_I01_I02_I03_I04_I05_I07','externalNeighborSeamQA':'not_passed; unchanged by this internal repair','formalAccepted':False,'replay':replay}
put(T/'repairs/i06-retained-20261011/visual-review.json',qa)
m['candidate']['size']=[4096,4096];m['context']['size']=[4326,4326]
put(T/'repairs/latest-repair.json',m)
old=read(T/'candidate/latest-assembly.json')
initial=old.get('initialAssembly',old)
new={'schemaVersion':2,'tile':'r14_c14','status':'partial_native_repair_remaining_internal_and_external_QA_failed','publishedAt':now,'candidate':m['candidate'],'context':m['context'],'manifest':{'path':str(p),'sha256':sha(p)},'initialAssembly':initial,'localPassedRepairs':['I06'],'remainingInternal':['I01','I02','I03','I04','I05','I07'],'reservedCorner':[0,0,630,630],'reservedCornerUnchanged':True,'externalNeighborSeamQA':'not_passed','formalAccepted':False}
put(T/'candidate/latest-assembly.json',new)
im=Image.open(m['candidate']['path'])
q=T/'review/i06-published-20261011';q.mkdir(exist_ok=True)
im.resize((1024,1024),Image.Resampling.LANCZOS).save(q/'overview-preview-only.png')
im.crop((2600,2380,3500,3280)).save(q/'i06-context-900-100pct.png')
records=list((T/'native').glob('*.generation.json'))+list((T/'repairs').glob('*/generation.json'))
progress=read(T/'progress.json');progress.update(status=new['status'],updatedAt=now,activeNativeCount=16,generatedNativeCount=len(records),complete4kCandidateCount=1,internalArtQA=qa['internalArtQA'],externalNeighborSeamQA=qa['externalNeighborSeamQA'],candidate=m['candidate']['path'],context=m['context']['path'],assemblyManifest=str(p),formalAccepted=False,currentPatch='internal_I01_I02',nextStep='Run existing prepared exact-endpoint repair through original builtin route once, preserve source/receipt, compose and visually check; reserved northwest630 square untouched.')
put(T/'progress.json',progress)
cont={'resumedAt':now,'currentCoordinate':'r14_c14 internal I01/I02; I06 retained and published','successfulOutputsRecovered':2,'firstRecoveredSource':read(T/'repairs/upper-left-20261011T060818-6e7f4444/generation.json')['originalOutput'],'appliedRecoveredSource':m['originalOutput'],'firstActualNewOutputAfterThisResume':None,'candidate':m['candidate'],'manifest':new['manifest'],'internalQA':qa['internalArtQA'],'externalQA':qa['externalNeighborSeamQA'],'errors':[],'networkPlan':'Original builtin image_gen route once. If network revoked, preserve exact failure and stop new network attempts; no alternate API.','reservedCorner':[0,0,630,630],'reservedCornerUnchanged':True,'formalAccepted':False}
put(T/'continuation-round-20261011.json',cont);put(T/'local-continuation-20261011.json',cont)
print(json.dumps({'candidate':m['candidate'],'context':m['context'],'manifest':new['manifest'],'generatedNativeRecordCount':len(records),'replay':replay},indent=2))


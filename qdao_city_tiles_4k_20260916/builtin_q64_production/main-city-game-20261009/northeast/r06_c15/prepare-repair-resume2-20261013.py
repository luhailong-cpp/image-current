from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
Q=T/'qa/core-baseline/31b09711d96a1bf993b7'
R=T/'qa/local-repair-resume2-20261013'
R.mkdir(exist_ok=True)
base=Q/'r06_c15-core-baseline.candidate.png'
im=Image.open(base).convert('RGB')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
items=[('panel',[140,2350,1394,3604]),('ledge',[540,2842,1794,4096]),('roof',[2580,2480,3834,3734]),('trunk',[2240,1340,3494,2594]),('wallrail',[840,1180,2094,2434]),('fascia',[1720,400,2974,1654])]
records=[]
for name,box in items:
 f=R/(name+'-target-v1.png')
 if not f.exists():im.crop(box).save(f)
 records.append({'id':name,'file':str(f),'sha256':sha(f),'crop':box,'source':str(base),'sourceSha256':sha(base),'operation':'integer crop only'})
(R/'targets-v1.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
tp=json.loads((T/'tile-progress.json').read_text(encoding='utf-8-sig'))
tp.update({'candidate':str(base),'candidateSha256':sha(base),'completeCandidateCount':1,'complete4kCandidateCount':1,'internalPassed4kCount':0,'pendingP2Count':6,'generationStopped':False,'blocker':None,'status':'complete-native-candidate-local-P2-repairs','updatedAt':datetime.now(timezone.utc).isoformat()})
(T/'tile-progress.json').write_text(json.dumps(tp,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records))

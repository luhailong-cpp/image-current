from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent;T=Z/'r08_c14'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
native=[]
for r in range(1,5):
 for c in range(1,5):
  p=f'p{r}{c}';f=T/'native'/(p+'.png');rec=Path(str(f)+'.generation.json')
  if f.exists() and rec.exists():
   d=read(rec);assert hashlib.sha256(f.read_bytes()).hexdigest()==d['sha256'];native.append({'patch':p,'file':str(f),'sha256':d['sha256']})
record={'tile':'r08_c14','status':'native_production_waiting_required_neighbor_patches','updatedAt':datetime.now(timezone.utc).isoformat(),'nativeCount':len(list((T/'native').glob('*.png'))),'selectedCoreCount':len(native),'remainingCoreCount':16-len(native),'nativeSources':native,'completeCandidateCount':0,'internalPassed4kCount':0,'formalAcceptedCount':0,'nextPatch':'p12_or_p21_when_ready','requiredNeighbors':{'p12':'r07_c14/p42','p21':'r08_c13/p24'},'inflightGeneration':None,'actualModel':None,'actualQuality':None}
(T/'tile-progress.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'savedCores':len(native),'required':record['requiredNeighbors']}))


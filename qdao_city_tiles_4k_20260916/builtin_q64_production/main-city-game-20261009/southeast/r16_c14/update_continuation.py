from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
active=read(T/'active-native-map.json')
records=[read(p) for p in sorted((T/'native').glob('*.generation.json'))]
now=datetime.now(timezone.utc).isoformat()
first=min(records,key=lambda r:r['generatedAt']) if records else None
p=T/'production-resume-20261013.json'
d=read(p) if p.exists() else {'schemaVersion':1,'resumedAt':now,'currentCoordinate':'r16_c14','formalAccepted':False,'route':'builtin','actualModel':None,'actualQuality':None}
d.update(updatedAt=now,activeNativeCount=len(active),actualNativeOutputCount=len(records),expectedNativeCount=16,missingNativeCount=16-len(active),candidate=None,internalQA='pending',externalQA='pending',nextPatches=[f'p{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5) if f'p{r:02d}_{c:02d}' not in active],status='active_native_generation',firstNewOutput=({'path':first['file'],'sha256':first['sha256'],'generatedAt':first['generatedAt'],'size':[first['width'],first['height']]} if first else None),newNetworkError=None)
save(p,d);save(T/'local-continuation-20261013.json',d)
progress=read(T/'progress.json');progress.update(actualNativeOutputCount=len(records),missingNativeCount=16-len(active),nextStep='Complete remaining actual native outputs, assemble 4K candidate, inspect six seams/nine intersections/four edges and north/west joined boundaries.');save(T/'progress.json',progress)
print(json.dumps(d,indent=2))

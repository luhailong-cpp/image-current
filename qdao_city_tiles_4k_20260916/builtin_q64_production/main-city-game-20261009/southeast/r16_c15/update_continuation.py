from pathlib import Path
from datetime import datetime,timezone
import json
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
a=read(T/'active-native-map.json');records=list((T/'native').glob('*.generation.json'));n=len(records);missing=[f'p{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5) if f'p{r:02d}_{c:02d}' not in a];now=datetime.now(timezone.utc).isoformat()
for name in ['production-resume-20261013.json','local-continuation-20261013.json']:
 c=read(T/name);c.update(updatedAt=now,activeNativeCount=len(a),actualNativeOutputCount=n,missingNativeCount=len(missing),nextPatches=missing,status='native_generation_in_progress',formalAccepted=False);save(T/name,c)
p=read(T/'progress.json');p.update(updatedAt=now,activeNativeCount=len(a),actualNativeOutputCount=n,missingNativeCount=len(missing),nextPatches=missing,status='native_generation_in_progress',formalAccepted=False);save(T/'progress.json',p)
print(json.dumps({'active':len(a),'actual':n,'next':missing[:4]}))

from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
active=read(T/'active-native-map.json');v=active.pop('p01_01');save(T/'active-native-map.json',active)
record=read(T/'native'/f'{v}.png.generation.json')
qa={'tile':'r16_c15','patch':'p01_01','version':v,'sha256':record['sha256'],'result':'rejected_before_dependency','findings':['False vertical architectural edge at x115 follows exact left-anchor boundary; inset-panel left border x145 appears without mapped reason.','New horizontal line y650 begins at x115 without west continuation.'],'retained':True,'allDependentGenerationsStarted':False}
save(T/'review/p01_01-first-rejected.json',qa)
p=read(T/'progress.json');p.update(activeNativeCount=0,missingNativeCount=16,actualNativeOutputCount=1,status='first_native_rejected_geometry_repair_pending',nextPatch='p01_01',formalAccepted=False);save(T/'progress.json',p)
c={'schemaVersion':1,'resumedAt':datetime.now(timezone.utc).isoformat(),'currentCoordinate':'r16_c15','activeNativeCount':0,'actualNativeOutputCount':1,'expectedNativeCount':16,'firstNewOutput':{'path':record['file'],'sha256':record['sha256'],'generatedAt':record['generatedAt']},'candidate':None,'status':p['status'],'rejected':qa,'actualModel':None,'actualQuality':None,'newNetworkError':None,'formalAccepted':False}
save(T/'production-resume-20261013.json',c);save(T/'local-continuation-20261013.json',c)

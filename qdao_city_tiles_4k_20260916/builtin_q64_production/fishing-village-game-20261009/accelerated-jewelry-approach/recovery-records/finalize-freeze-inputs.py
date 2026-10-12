from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach');f=b/'migration-freeze-20261011.json';v=json.loads(f.read_text(encoding='utf-8'))
items=[b.parent.parent/'parallel_20261005/daylight-only-20261009/donghai-natural-stone-clear-routes-v10.png',b.parent/'production-contract.json',b.parent.parent/'acceleration-20261010/assignments.json']
v['additionalWorkspaceInputs']=[{'file':str(p),'exists':p.exists(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None} for p in items]
v['inFlightStatus']='none_known; no running child agent or active root builtin call at freeze'
v['workerStopDelivery']='Stop instruction delivered to all3; interrupt returned pending_init for each. No worker was running a new generation turn.'
v['savedAtUtc']=datetime.now(timezone.utc).isoformat()
f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
roundfile=b/'continuation-status-20261011-evening.json'
roundfile.write_text(json.dumps({'updatedAtUtc':v['savedAtUtc'],'status':'migration_frozen','generationStopped':True,'freezeManifest':str(f),'candidateCount':6,'selectedNativeCoreCount':96,'completeRegion':False,'remainingCoreCoordinates':[],'pendingRepairs':v['pendingRepairs'],'knownInFlightRequests':[],'unsavedSuccessfulOutputPaths':[],'gitOperationsByThisTask':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'freeze':str(f),'savedAtUtc':v['savedAtUtc'],'additionalInputsExist':all(x['exists'] for x in v['additionalWorkspaceInputs']),'generationStopped':True}))


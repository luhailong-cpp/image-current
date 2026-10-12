from pathlib import Path
from datetime import datetime,timezone
import json,sys,hashlib
T=Path(__file__).resolve().parents[1]
manifest=T/sys.argv[1]
m=json.loads(manifest.read_text(encoding='utf-8-sig'))
assert m['tile']==T.name and not m['formalAccepted']
native_ids=[f'p{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5) if (T/'native'/f'p{r:02d}_{c:02d}.png.generation.json').is_file()]
blocked=[]
historical_rejections=[]
for receipt in (T/'pipeline/receipts').glob('*.rejected-receipt.json'):
    rr=json.loads(receipt.read_text(encoding='utf-8-sig'))
    rq=Path(rr['request']); request=json.loads(rq.read_text(encoding='utf-8-sig')); pid=request['coordinates']['id']
    entry={'patch':pid,'receipt':str(receipt),'request':str(rq),'rawGuide':str(T/'guides'/f'{pid}.layout-only.png'),'actualEditSeed':request['references'][0]['file'],'requestId':rr.get('requestId'),'status':rr['status'],'returnedImage':False,'bypassAttempted':False,'selectedNativeNowExists':pid in native_ids}
    if pid in native_ids:
        native=T/'native'/f'{pid}.png'
        entry['resolvedNativeEvidence']={'file':str(native),'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'generationRecord':str(T/'native'/f'{pid}.png.generation.json')}
    else:
        blocked.append(entry)
    historical_rejections.append(entry)
state={'schemaVersion':1,'savedAtUtc':datetime.now(timezone.utc).isoformat(),'worker':'sol_left_20261012','tile':T.name,'status':'active_native_production' if len(native_ids)<16 else 'candidate_pending_visual_and_external_QA','selectedNativeCount':len(native_ids),'savedNativePatchIds':native_ids,'assembledNativeCount':m['assembledNativeCount'],'latestCoverageAssembly':str(manifest),'output':m['output'],'formalAccepted':False,'actualModel':None,'actualQuality':None,'nextPatch':sys.argv[2],'openFindings':sys.argv[3:]}
state['blockedNativeRequests']=blocked
state['historicalNativeRejections']=historical_rejections
(T/'production-resume-20261012.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(state,ensure_ascii=False))

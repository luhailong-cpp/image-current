from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
now=datetime.now(timezone.utc).isoformat();read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
T=B/'r09_c01';ep=T/'migration-runtime-evidence-20261011.json';e=read(ep);g=e['lastProductionTurn']['lastImageGeneration']
rq=T/'pipeline/prompts/p03_02.v02.request.json';req=read(rq);pres=read(T/'migration-unattributed-cache-return-20261011.json')
assert e['thread']['status']['type']=='idle' and g['status']=='completed'
assert req['prompt']==g['revisedPrompt']
assert Path(g['savedPath']).resolve()==Path(pres['sourceCachePath']).resolve()
assert sha(pres['workspaceCopy'])==pres['sha256']
receipt={'tool':'image_gen.imagegen','status':'returned_image','route':'builtin','sourceOutputPath':g['savedPath'],'sourceOutputSha256':pres['sha256'],'savedNative':pres['workspaceCopy'],'request':str(rq),'requestSha256':sha(rq),'prompt':req['promptFile'],'promptSha256':req['promptSha256'],'recordedAtUtc':now,'startedAtUtc':None,'returnedAtUtc':None,'timestampCaveat':'Actual call start/return timestamps not recovered; no inference from file mtime.','actualModel':None,'actualQuality':None,'apiUsed':False,'recoveredFromRuntimeEvidence':str(ep),'runtimeEvidenceSha256':sha(ep),'runtimeToolItemId':g['id'],'runtimeStatus':'completed','requestPromptExactlyMatchesRuntimePrompt':True,'visualStatus':'not_re_reviewed_during_migration_freeze','selected':False,'formalAccepted':False}
rp=T/'pipeline/receipts/p03_02.v02.recovered-receipt.json';atomic_json(rp,receipt)
pres.update(requestAttribution='Confirmed r09_c01 p03_02 v02 by exact runtime revisedPrompt match to persisted request',recoveredReceipt=str(rp),attributionEvidence=str(ep));atomic_json(T/'migration-unattributed-cache-return-20261011.json',pres)
freeze={'schemaVersion':1,'savedAtUtc':now,'recordedBy':'/root','worker':'/root/resume_r11c06','zone':'r09_c01','generationStopped':True,'inFlightRequestCount':0,'unsavedSuccessfulOutputCount':0,'unsavedSuccessfulOutputPaths':[],'workerPersonalFinalReplyReceived':False,'confirmationSource':'Root independent runtime inspection after interrupt; not represented as a worker reply','runtimeEvidence':str(ep),'runtimeState':'idle','lastImageGenerationStatus':'completed','lastOutput':pres['workspaceCopy'],'lastOutputSha256':pres['sha256'],'lastRequest':str(rq),'lastOutputReceipt':str(rp),'selectedNativeCount':9,'selectionUnchanged':True,'pendingReturnedCoordinate':'p03_02 v02 saved but not selected or reviewed during freeze','nextMissingCoordinate':'p03_02 native selection, then p03_03','formalAccepted':False,'pendingRepairs':['One red lantern continuity edit saved but unreviewed; no production resumed.','Existing tower/roof/brown-plane seams and 7 unselected core slots remain.'],'externalPreservationManifest':str(B/'migration-preserved-external-20261011/manifest.json')}
atomic_json(T/'migration-freeze-20261011.json',freeze)
mp=B/'migration-preserved-external-20261011/manifest.json';m=read(mp)
for x in m['sourceFiles']:
    if Path(x['originalExternalPath']).name==Path(g['savedPath']).name:
        x.update(requestAttributionPending=False,request=str(rq),recoveredReceipt=str(rp))
atomic_json(mp,m)
print(json.dumps({'receipt':str(rp),'workerFreeze':str(T/'migration-freeze-20261011.json'),'inFlight':0,'unsaved':0,'selectedNativeCount':9},ensure_ascii=False))


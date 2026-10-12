from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat();source=Path('D:/work/image/AGENTS.md')
assert sha(source)=='94b3d5f54a7f2bfb41a9a5f3e06f166d2e2f4bf24845813090974e59ac5dbbcf'
copy=B/'pipeline-tools/project-root-AGENTS.received-20261013.md';assert not copy.exists();shutil.copy2(source,copy)
refs=[]
for p in [Path('D:/work/image/designs/mail-ui-v1/01-mail-event.png'),Path('D:/work/image/designs/team-ui-v2/team-ui-v2.png')]:refs.append({'file':str(p),'existsNow':p.is_file(),'sha256':sha(p),'actuallyViewedForThisMapQA':False,'role':'Current authoritative UI reference; no UI generation requested in this local map QA turn.'})
record={'recordedAtUtc':now,'source':str(source),'sourceSha256':sha(source),'fullFileActuallyReadByRoot':True,'localPreservedCopy':str(copy),'localCopySha256':sha(copy),'previousModelGate':str(B/'pipeline-tools/image-model-25-gate-20261013.json'),'newGenerationAndAiRepairAllowed':False,'reason':'No exposed tool route explicitly selects and confirms GPT Image 2.5; an old config target is not evidence.','paidApiAllowed':False,'historicalImagesNotRelabeledOrRegenerated':True,'currentUiReferences':refs,'newGenerationCallsThisTurn':0,'newAiRepairCallsThisTurn':0}
rp=B/'pipeline-tools/image-model-25-root-policy-ack-20261013.json';assert not rp.exists();atomic_json(rp,record)
p=read(B/'progress.json');p.update(updatedAtUtc=now,projectRootInstruction=str(source),projectRootInstructionSha256=sha(source),imageModelPolicyAcknowledgement=str(rp),requestedExactImageModel='GPT Image 2.5',holdNewImageGeneration=True,generationStopped=True,productionLines=0,currentStage='local_assembly_and_QA_pending_lane_reports_under_model_25_gate',networkBlocked=None,networkPermissionStatus='Not retested this turn because user model requirement forbids unverified image calls; previous permission failure preserved in historical evidence.',currentVerifiedInventory=str(B/'pipeline-tools/local-delivery-inventory-20261013/inventory.json'),missingNativeCoordinateList=str(B/'pipeline-tools/local-delivery-inventory-20261013/missing-patches.csv'),coverageQaOnlyPreview=str(B/'pipeline-tools/local-delivery-inventory-20261013/coverage-QA-only-v02.png'))
if p.get('currentWorkerNetworkPermissionErrors'):
 p['historicalWorkerNetworkPermissionErrors']=p.get('historicalWorkerNetworkPermissionErrors',[])+p.pop('currentWorkerNetworkPermissionErrors')
if p.get('missingHistoricalReference'):p['historicallyMissingReference']=p.pop('missingHistoricalReference')
p['previousVerificationCurrentStatus']=p.get('verificationCurrentStatus');p['verificationCurrentStatus']='Current adopted output/native hashes verified; formerly missing UI reference now exists; native visual defects and missing coverage remain.'
p['historicalReferencePresentNow']=True;p['currentUiReferenceFileEvidence']=refs
p['zoneDeliverySummary'].update(countsSnapshotUtc=p['countsSnapshotUtc'])
atomic_json(B/'progress.json',p)
print(json.dumps({'policyAck':str(rp),'requiredImageModel':p['requestedExactImageModel'],'newImageCalls':0,'currentUiReferenceFilesExist':all(r['existsNow'] for r in refs)},ensure_ascii=False))

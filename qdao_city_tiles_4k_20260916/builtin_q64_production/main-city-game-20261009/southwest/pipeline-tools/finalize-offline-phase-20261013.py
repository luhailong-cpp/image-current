from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib,sys,csv
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
cache={}
def sha(p):
 p=Path(p);key=str(p.resolve())
 if key not in cache:cache[key]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[key]
now=datetime.now(timezone.utc).isoformat()
lp=B/'r09_c03/pipeline/local-review-20261013-v01/left-lane-local-review-handoff.json'
rp=B/'r10_c08/pipeline/qa/right-lane-review-20261013-v01/lane-review-and-repair-queue.json'
cp=B/'pipeline-tools/col5-local-audit-20261013-v01/actual-views-and-findings.json'
cq=B/'pipeline-tools/col5-local-audit-20261013-v01/lane-repair-queue.json'
assert sha(lp)=='bd9a6dfd555a7a54e01ab82fef211be77eb9c1bfa7abfb3d29ffeea2406f3cb8'
assert sha(rp)=='d09124d9b1568c258739a3dea6e529e9799ce0bf54e4d5d4d01d2bfe855e1897'
assert sha(cp)=='b4c6981a500a99344bb1688930fdb18f83b8f26ea9c5fbac3f01f0b42c5cba9d'
assert sha(cq)=='3e3aba1df3910938445fe36fa19eecb3ecc0e2fb4bce5ab876da0853212c8675'
left,right,col5,c5queue=read(lp),read(rp),read(cp),read(cq)
assert left['newGeneratorCallsDuringThisLocalReview']==0 and right['generatorCallsAfterModelGate']==0 and col5['scope']['newImageCallsSinceModelGate']==0
assert left['formalAcceptedCount']==0 and right['formalAcceptedCount']==0 and not col5['formalAccepted']
def verify_file_hash_pairs(v):
 if isinstance(v,dict):
  if isinstance(v.get('file'),str) and isinstance(v.get('sha256'),str):assert sha(v['file'])==v['sha256'],v['file']
  for x in v.values():verify_file_hash_pairs(x)
 elif isinstance(v,list):
  for x in v:verify_file_hash_pairs(x)
for v in [col5['actuallyViewedCrops'],col5['actualPanelViews'],right['panels'],right['sourceManifest'],right['originalEvidenceIndex']]:verify_file_hash_pairs(v)
cat=read(B/'current-candidates.json');laneSummaries=[]
for t in left['tiles']:
 assert sha(t['report'])==t['reportSha256']
 for e in t['sourceOutputs']:
  assert sha(e['file'])==e['sha256']
  if t['tile'] in cat['tiles'] and e.get('pixels')==[4096,4096]:assert e['sha256']==cat['tiles'][t['tile']]['candidate']['sha256']
 if t['tile'] in cat['tiles']:cat['tiles'][t['tile']]['supplementalNativeQaReview']={'file':t['report'],'sha256':t['reportSha256']}
for tid in ['r09_c07','r09_c08','r10_c07']:cat['tiles'][tid]['supplementalNativeQaReview']={'file':str(rp),'sha256':sha(rp)}
for tid in ['r13_c05','r14_c05']:cat['tiles'][tid]['supplementalNativeQaReview']={'file':str(cp),'sha256':sha(cp),'repairQueue':str(cq),'repairQueueSha256':sha(cq)}
partials={}
for tid,aid in [('r09_c03','4e586b2c586d8ef0'),('r10_c08','d31aa999288c3f9d'),('r13_c06','e7b5e8d88639ad53')]:
 ap=B/tid/'pipeline/output'/aid/'assembly.json';a=read(ap);core=a['output'];ctx=a['contextOutput'];assert not a['complete4kCandidate']
 for e in [core,ctx]:assert sha(e['file'])==e['sha256']
 im=Image.open(core['file']).convert('RGB');context=Image.open(ctx['file']).convert('RGB');w,h=im.size
 assert np.array_equal(np.array(im),np.array(context.crop((115,115,115+w,115+h))))
 partials[tid]={'assembly':str(ap),'assemblySha256':sha(ap),'core':core,'context':ctx,'verifiedNativeSlotCount':a['verifiedNativeCount'],'missingPatchIds':a['missingPatchIds'],'sourceResampling':False,'internalPassed':False,'formalAccepted':False}
inv=B/'pipeline-tools/local-delivery-inventory-20261013/inventory.json';missing=B/'pipeline-tools/local-delivery-inventory-20261013/missing-patches.csv'
rows=list(csv.DictReader(missing.open(encoding='utf-8-sig')));assert len(rows)==766 and len({(r['tile'],r['missing_patch']) for r in rows})==766
p=read(B/'progress.json');assert p['selectedNativePatchCount']==258 and p['complete4kCandidateCount']==15 and p['remainingCorePatchCount']==766 and p['formalAcceptedCount']==0
summary={'recordedAtUtc':now,'status':'local_assembly_inventory_and_bounded_native_QA_saved_full64_objective_incomplete','targetTiles':64,'fullNativeCandidates':15,'partialTiles':3,'untouchedTiles':46,'selectedNativePatches':258,'missingNativePatches':766,'internalPassedTiles':0,'formalAcceptedTiles':0,'newGenerationCallsThisTurn':0,'newAiRepairCallsThisTurn':0,'verifiedModelRouteAvailable':False,'requestedImageModel':'GPT Image 2.5','modelPolicyAcknowledgement':str(B/'pipeline-tools/image-model-25-root-policy-ack-20261013.json'),'inventory':{'file':str(inv),'sha256':sha(inv)},'missingCoordinateCsv':{'file':str(missing),'sha256':sha(missing),'uniqueRows':766},'qaOnlyPreview':str(B/'pipeline-tools/local-delivery-inventory-20261013/coverage-QA-only-v02.png'),'laneReviews':[{'lane':'left','report':str(lp),'sha256':sha(lp),'nativePanelsBuilt':28,'nativePanelsActuallyViewed':17,'unviewedPanelsPending':11,'repairQueueCountsByTile':{t['tile']:t['repairQueueCount'] for t in left['tiles']}},{'lane':'right','report':str(rp),'sha256':sha(rp),'nativePanelsActuallyViewed':26,'externalSegmentsActuallyViewed':19,'internalSegmentsActuallyViewed':7,'unviewedGeneratedPanelsPending':12,'repairQueueItems':len(right['repairQueue'])},{'lane':'col5','report':str(cp),'sha256':sha(cp),'nativeCropsActuallyViewed':75,'nativePanelsActuallyViewed':20,'additionalSingleNativePartialEdgeViewed':1,'repairQueue':str(cq),'repairQueueSha256':sha(cq),'repairQueueItems':len(c5queue['issues'])}],'rootPartialReview':str(B/'r13_c06/pipeline/output/e7b5e8d88639ad53/root-local-qa-model-gate-20261013/root-review.json'),'currentPartials':partials,'mechanicalVerification':'Current full15 output hashes/dimensions and exact core-context crops, selected258 source/record hashes, latest3 partial core-context crops, and local QA report/evidence hashes verified. This is not visual acceptance.','verifiedFileHashesInThisFinalization':len(cache),'pending':'766 missing native patches; concrete native geometry/material repairs; unviewed seam sections; renewed whole-tile and whole-zone acceptance. All new image calls require verified explicitly selected GPT Image2.5 within user-authorized no-paid-API scope.','originalsAndVersionsPreserved':True,'paidApiUsed':False,'gitOperationsUsed':False,'uploadsPerformedByThisWindow':False,'objectiveComplete':False}
out=B/'pipeline-tools/local-qa-handoff-20261013.json';assert not out.exists();atomic_json(out,summary)
cat.update(updatedAtUtc=now,lastLocalQaHandoff=str(out),formalAcceptedCount=0);atomic_json(B/'current-candidates.json',cat)
p.update(updatedAtUtc=now,status='incomplete_awaiting_verified_GPT_Image_2_5_route',currentStage='local_inventory_assembly_and_QA_saved_new_generation_gated',productionInProgress=False,productionLines=0,generationStopped=True,holdNewImageGeneration=True,inFlightStatus='none_local_qa_phase_saved',imageGenerationInFlight=False,rootImageGenerationInFlight=False,currentPartials=partials,latestLocalQaHandoff=str(out),localQaPhaseComplete=True,finalCityComplete=False,allCrossEdgesPassed=False,activeCoordinate='r13_c06:p01_03_waiting_verified_image_2_5_route')
p['workerStatus'].update(reportedAtUtc=now,activeWorkers=[],activeGenerationWorkers=[],activeGenerationTiles=[],activeRepairTiles=[],activeReviewWorkers=[],productionLines=0,individualWorkerGenerationInFlight='none; no generator submitted under verified Image2.5 gate',supportActivities='All three bounded local QA lane reports saved, source/evidence hashes checked, partials assembled from existing native artwork. Full64 objective remains incomplete.')
atomic_json(B/'progress.json',p)
print(json.dumps({'handoff':str(out),'full':15,'missingPatches':766,'accepted':0,'newImageCalls':0,'verifiedFileHashes':len(cache),'localReports':3,'currentPartials':len(partials)},ensure_ascii=False))

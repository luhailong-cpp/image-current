from workflow import *
import re
WORKSPACE=Path('D:/work/image')
state=read(ROOT/'production-state.json');tiles=state['tiles'];covered={t['tile'] for t in tiles};plan=read(ROOT/'coordinate-plan.json')
native=list((ROOT/'native').glob('*.png'));last=max(native,key=lambda p:p.stat().st_mtime)
rootSelected={'11':'v03','12':'v02','13':'v04','14':'v04','21':'v01','22':'v01','23':'v03','31':'v02','32':'v04','33':'v01','41':'v01'}
rootBreak={'tile':'r12_c12','fullCandidateExists':False,'generatedRegularCoordinates':['11','12','13','14','21','22','23','24','31','32','33','41','42'],'workingVersions':rootSelected,'workingVersionsAreNotFullTileAcceptance':True,'ungeneratedRegularCoordinates':['34','43','44'],'pendingRepairs':[{'object':'p12/p13 long floorboard junction','base':'p12v02 + p13v04','reject':'p13v05 changes groove phases; do not adopt','savedWholeJoint':'native/r12_c12_deck_whole_joint_v01.png','tileRelativeOrigin':[1421,-115],'nextActionAfterMigration':'Inspect actual four outer joins before assigning native source ownership. Whole output already saved, do not regenerate blindly.'},{'object':'p24 lower board','savedVersions':['native/r12_c12_p24_v01.png','native/r12_c12_p24_v02.png'],'finding':'v01 has a disconnected long groove at lower-left/interior; v02 changes other grooves and creates new fading fragments. Neither whole version accepted.','rejectedProposal':'qa/r12-p24-board-ownership/proposal.png','proposalReason':'Diagonal binary source ownership trial crosses a groove and creates a triangular dark line; not accepted.'},{'object':'p41/p42 floor joint','savedVersion':'native/r12_c12_p42_v01.png','finding':'North joint with p32v04 reviewed continuous. Left p41v01/p42v01 has phase jumps in long grooves, pending complete board repair.'}],'nextMissingCoordinate':'r12_c12_p43 after reusing p33v01 and p42v01 right/top context, or p34 after p24 repaired','rootInFlightRequests':[]}
children={}
for name,f in [('coordinate_audit','migration-freeze-coordinate-audit-20261011.json'),('left_continue','migration-freeze-left-20261011.json'),('right_continue','migration-freeze-right-20261011.json')]:
 p=ROOT/f
 children[name]={'checkpoint':str(p),'exists':p.exists(),'status':'local_archive_requested_waiting_receipt' if not p.exists() else 'checkpoint_saved','sha256':sha(p) if p.exists() else None,'record':read(p) if p.exists() else None}
refs=read(ROOT/'references.json'); externalInputs=[];missing=[]
for f in (ROOT/'prompts').glob('*.request.json'):
 try:r=read(f)
 except Exception:continue
 for ref in r.get('references',[]):
  p=Path(ref.get('file',''))
  if not str(p):continue
  if p.is_absolute() and not p.is_relative_to(WORKSPACE):externalInputs.append(str(p))
for p in sorted(set(externalInputs)):
 if not Path(p).exists():missing.append(p)
rootGenerated=Path('C:/Users/luyua/.codex/generated_images/01a1216d-8b5f-7823-bf97-16e5128906cc')
nativeHashes={sha(p) for p in native};orphan=[]
for p in rootGenerated.glob('*.png'):
 if sha(p) not in nativeHashes:orphan.append(str(p))
counts=state['counts'];counts['generatedNativeCount']=len(native)
freeze={'schemaVersion':1,'zone':'Eight Immortals island southeast','savedAtUtc':now(),'generationStopRecordedAtUtc':'2026-10-12T02:33:15Z','generationStopped':True,'noNewGenerationAfterFreezeRequest':True,'reason':'User switches to committing/pushing all materials for another computer; central migration chat owns Git.','gitActionsByThisWorker':False,'rootInFlightCount':0,'childCheckpointStatus':children,'allChildCheckpointsSaved':all(v['exists'] for v in children.values()),'selectedCandidatePaths':tiles,'counts':counts,'assigned4kCount':len(plan['tiles']),'remainingWithoutFullCandidate':[t['id'] for t in plan['tiles'] if t['id'] not in covered],'activeCoordinates':['r08_c11','r12_c11','r12_c12','r12_c13'],'rootProductionBreakpoint':rootBreak,'latestSavedNative':{'file':str(last),'sha256':sha(last)},'recoveredLastRootOutput':{'file':str(ROOT/'native/r12_c12_deck_whole_joint_v01.png'),'sha256':sha(ROOT/'native/r12_c12_deck_whole_joint_v01.png'),'status':'saved_not_adopted','recoveryReceipt':str(ROOT/'prompts/r12_c12_deck_whole_joint_v01.recovery-receipt.json')},'unsavedSuccessfulOutputPaths':orphan,'rootOutputDirectoryAudit':{'directory':str(rootGenerated),'pngCount':len(list(rootGenerated.glob('*.png'))),'allSavedNativeHashMatches':not orphan},'externalReferencePaths':sorted(set(externalInputs)),'missingExternalReferencePaths':missing,'layoutAndStyleReferences':refs,'externalOriginalsPolicy':'Original imagegen outputs outside workspace are redundant when their SHA matches the archived native. Preserve originals; migrate native+generation records+prompts+guides+QA. Child checkpoints list their output directories. No deletion performed.','nativeScaleAndProvenance':'All final candidate/native pixels retained unchanged; rejected QA proposals remain unadopted. actualModel and actualQuality remain unknown.','nextStep':'Continue artwork only after migration and new user instruction. Preserve this freeze and all intermediate files.'}
if freeze['allChildCheckpointsSaved']:
 freeze.update(checkpointFinalized=True,finalizedAtUtc=now(),inFlightCount=0,allSuccessfulOutputsArchived=True,allWorkersStopped=True,subtaskRuntimeStatus={k:'completed_local_archive_no_active_imagegen' for k in children},freezeDisposition='No new art work. All child receipts saved. This is the finalized migration checkpoint.')
write(ROOT/'migration-freeze-20261011.json',freeze)
for f in ['production-state.json','progress.json','continuation-round-20261011.json','migration-production-handoff-20261011.json']:
 p=ROOT/f;d=read(p);d.update(updatedAt=now(),status='frozen_for_migration',generationStopped=True,inFlight=False,rootInFlightCount=0,freezeCheckpoint=str(ROOT/'migration-freeze-20261011.json'),nextStep=freeze['nextStep'])
 if f=='production-state.json':d['counts']=counts;d['activeWorkers']={k:'frozen; see child checkpoint' for k in ['root','coordinate_audit','left_continue','right_continue']}
 elif f in ['progress.json','continuation-round-20261011.json']:d.update(counts)
 else:d['counts']=counts
 write(p,d)
p=ROOT/'progress-r12_c12.json';d=read(p);d.update(updatedAt=now(),status='frozen_for_migration',generationStopped=True,inFlight=False,inFlightRequests=[],generatedNativeCount=len(list((ROOT/'native').glob('r12_c12*.png'))),workingVersions=rootSelected,missingPatches=['r12_c12_p34','r12_c12_p43','r12_c12_p44'],pendingRepairs=rootBreak['pendingRepairs'],nextStep=freeze['nextStep'],recoveredLastOutput=freeze['recoveredLastRootOutput']);write(p,d)
print(json.dumps({'freeze':str(ROOT/'migration-freeze-20261011.json'),'rootInFlightCount':0,'allChildCheckpointsSaved':freeze['allChildCheckpointsSaved'],'counts':counts,'remaining':len(freeze['remainingWithoutFullCandidate']),'unsavedRootOutputs':orphan,'externalInputs':sorted(set(externalInputs))}))

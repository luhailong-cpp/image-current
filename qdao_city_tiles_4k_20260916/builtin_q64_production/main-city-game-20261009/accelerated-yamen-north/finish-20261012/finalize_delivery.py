import sys,os,zipfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';R=H/'final-records';D=ROOT/'delivery-20261012-v1'
manifest=p.read(D/'delivery-manifest.json');audit=p.read(R/'source-audit.json')
manifest.update({'internalFullyPassedTileCount':4,'localChangedQAReviewedCount':44,'newSuccessfulBuiltinRawOutputsThisResume':20,'sourceAudit':str(R/'source-audit.json'),'finalBoundaryReview':str(R/'boundary-review.json'),'d4FinalRecipeClarification':str(R/'d4-final-recipe-clarification.json'),'inFlightRequests':0,'unsavedSuccessfulOutputs':0,'formalAcceptedCount':0})
tmp=H/'final-records/delivery-manifest-writing.json';p.put_json(tmp,manifest);os.replace(tmp,D/'delivery-manifest.json')
canonical=[]
for t in manifest['tiles']:
 canonical.append({'coordinate':t['tile'],'canonicalAdoptedFile':t['candidate'],'workspaceRelativePath':str(Path(t['candidate']).relative_to(Path('D:/work/image'))),'sha256':t['sha256'],'pixels':[4096,4096],'sourceCandidateAlias':t['sourceCandidate'],'assembly':t['assembly'],'review':t['review'],'internalLocalQA':'PASS','formalAccepted':False})
state=p.read(ROOT/'production-resume-20261012.json');prior=state.get('currentUniqueAdoptedCandidates',[])
state.setdefault('previousCanonicalAdoptedSets',[]).append({'replacedAtUtc':p.now(),'candidates':prior,'keptAsHistoricalAliases':True})
new=[]
for raw in audit['rawOutputs']:
 new.append({'file':raw['file'],'sha256':raw['sha256'],'pixels':raw['pixels'],'record':raw['generationRecord'],'recordSHA256':raw['generationRecordSHA256'],'saved':True})
state.update({'status':'four_assigned_tiles_locally_reviewed_and_delivered_external_acceptance_pending','updatedAtUtc':p.now(),'candidateCount':4,'coveredCoreCount':64,'missingAssignedCoordinates':[],'internalFullyPassedTileCount':4,'formalAcceptedCount':0,'currentUniqueAdoptedCandidates':canonical,'newRawOutputsThisResume':new,'newRawOutputCount':20,'rootNewRawOutputCount':16,'restoredChildNewRawOutputCount':4,'currentToolError':None,'generationCurrentlyOnHoldForActualPermissionFailure':False,'inFlightRequests':0,'unsavedSuccessfulOutputs':0,'deliveryManifest':str(D/'delivery-manifest.json'),'sourceAudit':str(R/'source-audit.json'),'nextStep':'Only formal cross-area acceptance remains:24 boundary segments across6 unavailable neighbors, plus current full adopted south neighbor verification. Do not expand production coordinates.'})
tmp=R/'resume-final-writing.json';p.put_json(tmp,state);os.replace(tmp,ROOT/'production-resume-20261012.json')
progress=p.read(ROOT/'progress.json');progress.update({'status':state['status'],'updatedAt':p.now(),'currentCoordinate':None,'nextCoordinate':None,'candidateCount':4,'deliveredCandidateCount':4,'coveredCoreCoordinates':64,'missingNativeCount':0,'internalFullyPassedTileCount':4,'formalAcceptedCount':0,'currentUniqueAdoptedCandidates':canonical,'generationStopped':True,'generationHoldReason':'Assigned artwork and local QA completed','currentToolError':None,'generationCurrentlyOnHoldForActualPermissionFailure':False,'newRawOutputCountThisResume':20,'inFlightRequests':0,'unsavedSuccessfulOutputs':0,'deliveryManifest':str(D/'delivery-manifest.json'),'sourceAudit':str(R/'source-audit.json'),'nextStep':state['nextStep'],'scopeCompletion':'Four assigned tiles locally reviewed and delivered; whole-zone/whole-map and formal outer acceptance not claimed'})
p.replace_json(ROOT/'progress.json',progress)
for t in manifest['tiles']:
 for basename,src in [(t['tile']+'-review.json',Path(t['review']))]:
  p.put_bytes(D/basename,src.read_bytes())
for name in ['source-audit.json','boundary-review.json','d4-final-recipe-clarification.json']:p.put_bytes(D/name,(R/name).read_bytes())
p.put_json(D/'local-quality-summary.json',{'candidateCount':4,'internalFullyPassedTileCount':4,'nativeChangedQAReviewed':44,'retainedPixelIdenticalQA':88,'knownOpenInternalDefects':[],'formalAcceptedCount':0,'missingOuterNeighborTiles':p.read(R/'boundary-review.json')['missingNeighborTiles'],'newSuccessfulBuiltinRawCount':20,'selectedLogicalCores':64,'inFlightRequests':0,'unsavedSuccessfulOutputs':0,'scope':'These four assigned tiles only'})
archive=D/'yamen-north-4tiles-4096-20261012.zip';assert not archive.exists()
names=[t['tile']+'.png' for t in manifest['tiles']]+['overview-preview-2048.png','delivery-manifest.json','delivery-notes.txt','prompt-records-index.json','source-audit.json','boundary-review.json','d4-final-recipe-clarification.json','local-quality-summary.json']+[t['tile']+'-review.json' for t in manifest['tiles']]
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_STORED) as z:
 for name in names:z.write(D/name,arcname=name)
with zipfile.ZipFile(archive,'r') as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==len(names)
 for t in manifest['tiles']:
  assert hashlib.sha256(z.read(t['tile']+'.png')).hexdigest()==t['sha256']
p.put_json(D/'archive-verification.json',{'file':str(archive),'sha256':p.sha(archive),'bytes':archive.stat().st_size,'entries':names,'fourOriginalPNGHashesMatchCanonical':True,'zipIntegrityVerified':True,'formalAccepted':False})
print({'archive':str(archive),'MiB':round(archive.stat().st_size/1048576,2),'canonicalCount':4,'newRawCount':20,'missingAssigned':0,'formalAccepted':0})


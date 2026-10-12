from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
b=Path(__file__).resolve().parents[1];e=b/'resume-20261012'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(e/'candidate-manifest.json');regionqa=read(e/'root-final-review.json');audit=read(e/'provenance-audit.json');resume=read(b/'production-resume-20261012.json')
assert audit['status']=='PASS' and not audit['issues'] and not audit['missing']
assert audit['selectedCoreCount']==32 and audit['totalRawCount']==117
assert regionqa['status']=='PASS_INTERNAL_QA' and regionqa['regionNativeReviewCount']==30 and not regionqa['blockingFindings']
assert regionqa['candidateSha256']==m['regionCandidate']['sha256']==sha(m['regionCandidate']['file'])
assert all(s['sha256']==sha(s['file']) and Image.open(s['file']).size==(4096,4096) for s in m['sources'])
assert all(x['exactPixelPasteVerified'] for x in m['assemblyChecks'])
assert sha(resume['historicalFreezePreserved']['file'])==resume['historicalFreezePreserved']['sha256']
south=[]
for t in ['r05_c10','r05_c11']:
 p=b/t/'qa/final-v4/findings.json';q=read(p);source=next(s for s in m['sources'] if s['tile']==t)
 assert q['candidateSha256']==source['sha256']
 coverage=q['totalCoverage'];assert coverage['required']==coverage['passed']==32 and coverage['pending']==coverage['blocking']==0
 assert not q.get('blockingFindings',[])
 for s in q['segments']:
  assert sha(s['file'])==s['sha256'] and s['status'].startswith('PASS')
 south.append({'tile':t,'file':str(p),'sha256':sha(p),'candidateSha256':q['candidateSha256'],'coverage':coverage})
now=datetime.now(timezone.utc).isoformat()
outerfile=b/'r05_c11/qa/resume-20261012/outer-neighbor-availability.json';outer=read(outerfile)
assert outer['availableCurrentFull4096Count']==outer['availableFull4096CandidateCount']==0 and outer['unavailableFull4096Count']==10
pending=[{'tile':f'r03_c{c}','edge':'north','neighbor':f'r02_c{c}'} for c in [10,11]]+[{'tile':f'r05_c{c}','edge':'south','neighbor':f'r06_c{c}'} for c in [10,11]]
pending += [{'tile':f'r{r:02}_c{c}','edge':edge,'neighbor':f'r{r:02}_c{n:02}'} for r in [3,4,5] for c,edge,n in [(10,'west',9),(11,'east',12)]]
assert len(pending)==10
counts={'selectedCoreCount':96,'requiredCoreCount':96,'extensionSelectedCoreCount':32,'priorSelectedCoreCount':64,'extensionCoreNativeVersionCount':audit['newCoreRawCount'],'extensionRepairRawCount':audit['newRepairRawCount'],'extensionRawCount':audit['newRawCount'],'priorRawCount':71,'rawGeneratedImageCount':audit['totalRawCount'],'newRawCountSinceResume':audit['newRawCountSinceResume'],'allRawNativeDimensions1254':True,'allActualModelQualityUnknown':True}
evidence=[{'file':str(p),'sha256':sha(p)} for p in [e/'root-final-review.json',e/'provenance-audit.json',b/'delivery/production-summary.json',outerfile]]+south
status='production_complete_six_candidates_external_neighbors_pending'
m.update({'updatedAt':now,'status':status,'internalAndRegionQA':'PASS','formalAcceptedCount':0,'exteriorSeamsReviewed':False,'exteriorSeamsPending':pending,'exteriorNeighborAvailability':{'file':str(outerfile),'sha256':sha(outerfile),'fullNeighborCandidatesAvailable':0,'required':10},'generationCounts':counts,'qaEvidence':evidence,'localArtProductionComplete':True,'priorFourUnchanged':True})
write(e/'candidate-manifest.json',m)
summary={'updatedAt':now,'status':status,'localArtProductionComplete':True,'coordinates':m['coordinates'],'globalPixelBox':m['globalPixelBox'],'tiles':m['sources'],'region':m['regionCandidate'],'preview':{'file':m['preview'],'sha256':sha(m['preview']),'classification':'downsampled preview only'},'generationCounts':counts,'nativeMethod':'Each4096 tile uses sixteen unscaled1024 core crops from measured1254 builtin outputs with115px halos and documented native local alpha repairs. Region is exact unscaled pixel paste.','nativePixelsResized':False,'overviewPixelsUsedInFinal':False,'paidApiUsed':False,'builtinOnly':True,'actualModel':None,'actualQuality':None,'formalAcceptedCount':0,'withinRegionSeamsReviewed':True,'regionReviewCount':30,'exteriorReviewPending':True,'exteriorSeamsPending':pending,'exteriorReviewReason':'All ten adjacent full4096 candidates were unavailable at the read-only inventory checkpoint; local assigned artwork is complete.','qaEvidence':evidence,'manifest':str(e/'candidate-manifest.json'),'priorFourPreserved':True,'historicalFreezePreserved':resume['historicalFreezePreserved'],'gitOperationsByThisTask':False,'fixedUploadSnapshotUntouched':True}
write(e/'production-summary.json',summary)
adopted=[dict(s,formalAccepted=False,stage='assigned_artwork_complete_internal_and_region_QA_passed') for s in m['sources']]
progress=read(b/'progress.json')
progress.update({'updatedAt':now,'status':status,'localArtProductionComplete':True,'candidateCount':6,'completeCandidateCount':6,'completeCandidateCountDefinition':'Six full4096 candidates with internal and within-region QA passed; external formal acceptance pending.','formalAcceptedCount':0,'selectedNativeCoreCount':96,'requiredNativeCoreCount':96,'rawGeneratedImageCount':counts['rawGeneratedImageCount'],'extensionRawGeneratedImageCount':counts['extensionRawCount'],'extensionCoreVersionCount':counts['extensionCoreNativeVersionCount'],'extensionRepairRawCount':counts['extensionRepairRawCount'],'nextCoordinate':None,'nextCoordinates':[],'withinRegionSeamsReviewed':True,'externalSeamsChecked':False,'externalRegionSeamsChecked':False,'nextAction':'Assigned six-tile artwork delivered. Review ten external boundaries when neighboring full candidates are available.','candidateManifest':str(e/'candidate-manifest.json'),'deliveryManifest':str(e/'candidate-manifest.json'),'productionSummary':str(e/'production-summary.json'),'regionCandidate':m['regionCandidate'],'generationStopped':True,'generationStopReason':'assigned_artwork_complete','pendingRepairs':[],'currentAdoptedCandidates':adopted,'selectedCandidatePaths':adopted,'exteriorNeighborPairs':pending,'exteriorNeighborAvailability':str(outerfile),'generationCounts':counts})
progress['remainingNeighborPairs']={edge:[[s['neighbor'],s['tile']] for s in pending if s['edge']==edge] for edge in ['north','south','west','east']}
for s in m['sources']:
 progress['tiles'][s['tile']].update({'candidate':s['file'],'candidateSha256':s['sha256'],'dimensions':[4096,4096],'status':'candidate_complete_internal_and_within_region_seams_reviewed','formalAccepted':False,'externalRegionSeamsChecked':False})
 if s['tile'] in ['r05_c10','r05_c11']:
  qp=b/s['tile']/'qa/final-v4/findings.json'
  progress['tiles'][s['tile']].update({'updatedAt':now,'qaReport':str(qp),'validationReport':str(qp),'qaManifest':str(qp.with_name('manifest.json')),'internalSeamsReviewed':24,'northSeamsReviewed':4,'neighborSeamsReviewed':4,'blockingFindings':0,'repairCount':2 if s['tile']=='r05_c10' else 6,'repairCountDefinition':'Selected distinct builtin raw repair sources used by this tile; shared source is counted once region-wide.','repairContributionCount':3 if s['tile']=='r05_c10' else 6})
write(b/'progress.json',progress)
resume.update({'updatedAtUtc':now,'completedAtUtc':now,'status':status,'localArtProductionComplete':True,'generationStopped':True,'generationStopReason':'assigned_artwork_complete','rawGeneratedImageCount':117,'candidateCount':6,'currentCandidates':adopted,'pendingRepairs':[],'withinRegionSeamsReviewed':True,'finalDeliveryManifest':str(e/'candidate-manifest.json'),'productionSummary':str(e/'production-summary.json'),'regionCandidate':m['regionCandidate'],'exteriorSeamsPending':pending,'formalAcceptedCount':0})
write(b/'production-resume-20261012.json',resume)
write(e/'migration-handoff.json',{'updatedAt':now,'status':status,'ownerThread':'01a11b5e-158a-77d0-8c02-e8e503b7abe4','deliveryScope':'All six assigned native candidates and complete8192x12288 region, internal QA passed, ten exterior neighbors unavailable.','selectedCandidatePaths':adopted,'sixTileManifest':str(e/'candidate-manifest.json'),'sixTileProductionSummary':str(e/'production-summary.json'),'regionCandidate':m['regionCandidate'],'generationCounts':counts,'pendingRepairs':[],'formalAcceptedCount':0,'gitOperationsByThisTask':False,'fixedUploadSnapshotUntouched':True,'historicalFreezePreserved':resume['historicalFreezePreserved']})
print(json.dumps({'status':status,'candidateCount':6,'nativeCoreCount':96,'rawCount':117,'regionSha256':m['regionCandidate']['sha256'],'exteriorNeighborsPending':10}))

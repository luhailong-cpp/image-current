from workflow import *
q=ROOT/'qa/r14_c12-sol-20261013-v01'
proof=read(q/'source-proof.json');candidate=Path(proof['candidate'])
assert sha(candidate)==proof['candidateSha256'] and proof['sourceReplayMismatch']==0
record={'tile':'r14_c12','reviewedAt':now(),'candidate':str(candidate),'sha256':sha(candidate),'internalPassed':True,'formalAccepted':False,'sourceProof':str(q/'source-proof.json'),'sourceProofSha256':sha(q/'source-proof.json'),'reviewInheritance':str(q/'review-inheritance.json'),'unchangedPreviouslyPassedSeams':18,'unchangedPreviouslyPassedJunctions':5,'newSeamsViewed':['h32','h33','h42','h43','v23','v33'],'newJunctionsViewed':['j22','j23','j32','j33'],'newContactFiles':[{'path':str(q/n),'sha256':sha(q/n)} for n in ['contact-new-h.png','contact-new-v.png','contact-new-j.png']],'visualFinding':'Continuous sea geometry, consistent water scale and color; no hard broken feature or visible rectangular mismatch at the six new seams/four junctions. 24/24 actual seams and 9/9 junctions passed, with unchanged checks reused by hash.','northActualCandidateEdge':'previously passed four actual segments; input first-row pixels unchanged','south':'world map boundary, no outside tile required','externalPassed':False,'pending':'actual west/east full neighboring candidates and complete outer-corner review'}
out=q/'root-internal-review-resume-20261013.json';assert not out.exists();write(out,record)
entry={'tile':'r14_c12','candidate':str(candidate),'sha256':sha(candidate),'fullyCovered':True,'internalPassed':True,'externalPassed':False,'localArtworkAcceptanceReady':False,'formalAccepted':False,'sourceProof':str(q/'source-proof.json'),'review':str(out),'pending':record['pending']}
resume=read(ROOT/'production-resume-20261012.json');adopt=resume['currentAdoptedCandidates'];assert not any(x['tile']=='r14_c12' for x in adopt);adopt.append(entry)
counts=resume['counts'];counts.update(fullyCovered4kCount=16,complete4kCount=16,internalPassed4kCount=15,missingNative4kCount=33,fullCandidatePendingRepairOrReviewCount=1)
resume['remainingWithoutFullCandidate']=[t for t in resume['remainingWithoutFullCandidate'] if t!='r14_c12']
resume.update(updatedAtUtc=now(),currentTile='r14_c14',status='active_builtin_native_continuation',generationStopped=False)
resume['networkInterruption']['resolvedBy']='Both missing r14_c12 p33/p43 returned successfully, saved, assembled and visually passed; old interruption remains historical.'
write(ROOT/'production-resume-20261012.json',resume)
for name in ['progress.json','production-state.json','current-zone-counts-20261013.json']:
    p=ROOT/name;d=read(p)
    if 'counts' in d:d['counts']=dict(counts)
    else:d.update(counts)
    if 'currentAdoptedCandidates' in d:d['currentAdoptedCandidates']=adopt
    if 'missingNativeTiles' in d:d['missingNativeTiles']=resume['remainingWithoutFullCandidate']
    d.update(status='active_builtin_native_continuation',generationStopped=False,updatedAt=now(),updatedAtUtc=now(),currentTile='r14_c14')
    write(p,d)
d=read(ROOT/'progress-r14_c12.json');d.update(status='internal_passed_external_pending',generatedNativeCount=16,workingVersions={f'{r}{c}':'v01' for r in range(1,5) for c in range(1,5)},currentCandidate=str(candidate),internalPassed=True,externalPassed=False,inFlight=False,inFlightRequests=[],updatedAt=now());write(ROOT/'progress-r14_c12.json',d)
print(json.dumps({'adopted':'r14_c12','counts':counts,'review':str(out)}))

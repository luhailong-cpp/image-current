from workflow import *
tid='r08_c11';q=ROOT/'qa/r08_c11-v01-sol';candidate=ROOT/'tiles/r08_c11.candidate-v01.png'
proof=read(q/'root-independent-source-replay-20261013.json');peer=read(q/'native-visual-review-sol-20261012.json')
assert sha(candidate)==proof['candidateSha256']==peer['candidateSha256'] and proof['sourceReplayMismatch']==0
assert peer['internalJoinPass'] and peer['internalSeamsDirectlyViewed']==24 and peer['junctionsDirectlyViewed']==9
review={'updatedAtUtc':now(),'candidate':str(candidate),'candidateSha256':sha(candidate),'status':'internal_accepted_after_peer_actual_review_and_root_independent_audit','peerReview':str(q/'native-visual-review-sol-20261012.json'),'peerActualSeams':24,'peerActualJunctions':9,'peerOverlayEdges':19,'peerOverlayCorners':18,'rootPixelReplayProof':str(q/'root-independent-source-replay-20261013.json'),'rootSourcePixelMismatch':0,'rootOriginalScaleSpotChecks':['overlay21-left.png','overlay21-right.png','overlay20-right.png','overlay19-top.png','overlay17-bottom.png','overlay18-bottom.png','overlay19-corner-bottom-right.png'],'finding':'Actual wall, coping, pavement and roof contours remain connected. Narrow internal coping/shadow-rim and material phase differences retained under practical object-gap criterion. Preview-only apparent steps were not used as proof of defects.','externalAccepted':False,'formalAccepted':False}
write(q/'root-internal-acceptance-20261013.json',review)
resume=read(ROOT/'production-resume-20261012.json');items=[x for x in resume['currentAdoptedCandidates'] if x['tile']!=tid]
items.append({'tile':tid,'candidate':str(candidate),'sha256':sha(candidate),'fullyCovered':True,'internalPassed':True,'externalPassed':False,'localArtworkAcceptanceReady':False,'formalAccepted':False,'sourceProof':str(q/'root-independent-source-replay-20261013.json'),'review':str(q/'root-internal-acceptance-20261013.json'),'pending':'Actual north and west neighbor production incomplete. East/south reviewed by peer; all-four external acceptance still false.'})
resume['currentAdoptedCandidates']=items;resume['pendingCandidates']=[x for x in resume.get('pendingCandidates',[]) if x['tile']!=tid]
accepted={x['tile'] for x in items if x['internalPassed']};full={x['tile'] for x in items if x['fullyCovered']}|{x['tile'] for x in resume['pendingCandidates']}
counts=resume['counts'];counts.update(generatedNativeCount=len(list((ROOT/'native').glob('*.png'))),fullyCovered4kCount=len(full),complete4kCount=len(full),internalPassed4kCount=len(accepted),missingNative4kCount=49-len(full),fullCandidatePendingRepairOrReviewCount=len(full-accepted))
agents=Path('D:/work/image/AGENTS.md');requirement=resume['generationModelRequirement'];requirement.update(projectInstructionFile=str(agents),projectInstructionSha256=sha(agents),projectInstructionReadAtUtc=now())
nextStep='Continue only local review and exact assembly of saved originals. New generation/AI repair requires an explicitly selectable verified GPT Image 2.5 route and existing no-paid-API constraints. Do not resubmit unspecified builtin requests.'
resume.update(counts=counts,updatedAtUtc=now(),generationModelRequirement=requirement,nextStep=nextStep,inFlightRequests=[],generationStopped=True)
write(ROOT/'production-resume-20261012.json',resume)
for fname in ['progress.json','production-state.json']:
 d=read(ROOT/fname);d.update(updatedAt=now(),currentAdoptedCandidates=items,pendingCandidates=resume['pendingCandidates'],generationModelRequirement=requirement,nextStep=nextStep,inFlight=False,inFlightRequests=[],generationStopped=True,status='local_work_only_new_generation_on_hold_exact_model_requirement')
 if fname=='progress.json':d.update(**counts)
 else:d['counts']=counts
 write(ROOT/fname,d)
for name in ['progress-r08_c11.json','progress-r12_c13.json','progress-r13_c11.json','progress-r13_c13.json','progress-r14_c11.json','progress-r14_c12.json','production-resume-wall-sol-20261012.json','production-resume-right-sol-20261012.json','production-resume-left-sol-r13_c11-20261012.json','production-resume-left-sol-r14_c11-20261012.json']:
 f=ROOT/name
 if not f.exists():continue
 d=read(f)
 if d.get('inFlightRequests'):d['lastInterruptedRequestsBeforeModelHold']=d['inFlightRequests']
 d.update(generationModelRequirement=requirement,nextStep=nextStep,inFlight=False,inFlightRequests=[],activeImageGenCalls=0,inFlightRequestCount=0,updatedAt=now())
 if name=='progress-r08_c11.json':d.update(status='internal_passed_external_pending_new_generation_on_model_hold',fullyCovered4kCount=1,internalPassed4kCount=1,externalPassed4kCount=0,rootReview=str(q/'root-internal-acceptance-20261013.json'))
 else:d['newGenerationStatus']='on_hold_exact_model_requirement'
 write(f,d)
z=read(ROOT/'current-zone-counts-20261013.json');z.update(updatedAtUtc=now(),counts=counts,pendingCandidates=resume['pendingCandidates'],generationModelRequirement=requirement);write(ROOT/'current-zone-counts-20261013.json',z)
h=read(ROOT/'model-requirement-hold-20261013.json');h.update(updatedAtUtc=now(),counts=counts,generationRequirement=requirement,fullCandidatesPendingRepairOrReview=resume['pendingCandidates']);write(ROOT/'model-requirement-hold-20261013.json',h)
print(json.dumps(counts))

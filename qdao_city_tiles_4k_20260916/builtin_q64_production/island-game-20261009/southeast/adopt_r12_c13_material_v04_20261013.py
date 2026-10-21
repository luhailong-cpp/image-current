from workflow import *
q=ROOT/'qa/r12_c13-material-v04-20261013';qa=read(q/'qa-manifest.json');proof=read(q/'source-pixel-proof.json');candidate=Path(proof['candidate']);assert sha(candidate)==proof['candidateSha256'] and proof['mismatchedPixels']==0
review={'tile':'r12_c13','reviewedAt':now(),'candidate':str(candidate),'candidateSha256':sha(candidate),'sourceProof':str(q/'source-pixel-proof.json'),'mismatchedPixels':0,'internalPassed':True,'externalPassed':False,'formalAccepted':False,'changedEvidenceViewed':qa['changed'],'unchangedChecksReused':len(qa['reusedUnchangedFromV03']),'newBoundariesViewed':qa['newSourceBoundaries'],'priorReview':str(ROOT/'qa/r12_c13-floor-ownership-20261013/root-review-resume-20261013.json'),'finding':'Vertical straight wood brightness discontinuity removed; complete T grooves and board bevels retained. All five changed seam/junction views plus four new ownership edges and whole-object view passed; remaining 28 unchanged seam/junction views reused by exact pixel comparison. Minor grain phase retained without physical contour gap.','externalLimit':'Outer candidate pixels unchanged by internal repair; full neighboring-tile and corner acceptance still pending.'}
rf=q/'root-internal-review.json';assert not rf.exists();write(rf,review)
entry={'tile':'r12_c13','candidate':str(candidate),'sha256':sha(candidate),'fullyCovered':True,'internalPassed':True,'externalPassed':False,'localArtworkAcceptanceReady':False,'formalAccepted':False,'sourceProof':str(q/'source-pixel-proof.json'),'review':str(rf),'pending':'complete actual neighboring edges and outer corners'}
r=read(ROOT/'production-resume-20261012.json');adopt=r['currentAdoptedCandidates'];assert not any(x['tile']=='r12_c13' for x in adopt);adopt.append(entry);r['pendingCandidates']=[x for x in r['pendingCandidates'] if x['tile']!='r12_c13']
c=r['counts'];c.update(internalPassed4kCount=sum(bool(x.get('internalPassed')) for x in adopt),fullCandidatePendingRepairOrReviewCount=len(r['pendingCandidates']),generatedNativeCount=len(list((ROOT/'native').glob('*.png'))))
for name in ['production-resume-20261012.json','progress.json','production-state.json','current-zone-counts-20261013.json']:
 d=r if name=='production-resume-20261012.json' else read(ROOT/name)
 if 'counts' in d:d['counts']=dict(c)
 else:d.update(c)
 if 'currentAdoptedCandidates' in d:d['currentAdoptedCandidates']=adopt
 if 'pendingCandidates' in d:d['pendingCandidates']=r['pendingCandidates']
 if 'internalPassedTiles' in d:d['internalPassedTiles']=[e['tile'] for e in adopt if e.get('internalPassed')]
 d.update(updatedAt=now(),updatedAtUtc=now(),status='active_builtin_native_continuation',generationStopped=False)
 write(ROOT/name,d)
p=read(ROOT/'progress-r12_c13.json');p.update(currentCandidate=str(candidate),candidateSha256=sha(candidate),status='internal_passed_external_pending',internalPassed=True,externalPassed=False,inFlight=False,inFlightRequests=[],pendingRepair=None,review=str(rf),updatedAt=now());write(ROOT/'progress-r12_c13.json',p)
print(json.dumps({'tile':'r12_c13','counts':c,'review':str(rf)}))

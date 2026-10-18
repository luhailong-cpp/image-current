from workflow import *
import sys
rf=Path(sys.argv[1]);review=read(rf);tid=review['tile'];candidate=Path(review['candidate']);assert review['internalPassed'] is True and sha(candidate)==review['candidateSha256']
r=read(ROOT/'production-resume-20261012.json');adopt=r['currentAdoptedCandidates'];prior=next((x for x in adopt if x['tile']==tid),None)
entry={'tile':tid,'candidate':str(candidate),'sha256':sha(candidate),'fullyCovered':True,'internalPassed':True,'externalPassed':review.get('externalPassed',False),'localArtworkAcceptanceReady':review.get('localArtworkAcceptanceReady',False),'formalAccepted':False,'sourceProof':review['sourceProof'],'review':str(rf),'pending':review.get('pending','actual neighboring edges and corners')}
if prior:adopt[adopt.index(prior)]=entry
else:adopt.append(entry)
r['pendingCandidates']=[x for x in r.get('pendingCandidates',[]) if x['tile']!=tid]
full=set(x['tile'] for x in adopt+r['pendingCandidates']);r['remainingWithoutFullCandidate']=[f'r{rr:02}_c{cc:02}' for rr in range(8,15) for cc in range(8,15) if f'r{rr:02}_c{cc:02}' not in full]
c=r['counts'];c.update(generatedNativeCount=len(list((ROOT/'native').glob('*.png'))),fullyCovered4kCount=len(full),complete4kCount=len(full),internalPassed4kCount=sum(bool(x.get('internalPassed')) for x in adopt),externalPassed4kCount=sum(bool(x.get('externalPassed')) for x in adopt),localArtworkAcceptanceReadyCount=sum(bool(x.get('localArtworkAcceptanceReady')) for x in adopt),formalAcceptedCount=0,missingNative4kCount=49-len(full),fullCandidatePendingRepairOrReviewCount=len(r['pendingCandidates']))
for name in ['production-resume-20261012.json','progress.json','production-state.json','current-zone-counts-20261013.json']:
 d=r if name=='production-resume-20261012.json' else read(ROOT/name)
 if 'counts' in d:d['counts']=dict(c)
 else:d.update(c)
 if 'currentAdoptedCandidates' in d:d['currentAdoptedCandidates']=adopt
 if 'pendingCandidates' in d:d['pendingCandidates']=r['pendingCandidates']
 if 'remainingWithoutFullCandidate' in d:d['remainingWithoutFullCandidate']=r['remainingWithoutFullCandidate']
 if 'missingNativeTiles' in d:d['missingNativeTiles']=r['remainingWithoutFullCandidate']
 if 'internalPassedTiles' in d:d['internalPassedTiles']=[e['tile'] for e in adopt if e.get('internalPassed')]
 d.update(updatedAt=now(),updatedAtUtc=now(),status='active_builtin_native_continuation',generationStopped=False)
 write(ROOT/name,d)
p=read(ROOT/f'progress-{tid}.json');p.update(currentCandidate=str(candidate),candidateSha256=sha(candidate),status='internal_passed_external_pending',internalPassed=True,externalPassed=entry['externalPassed'],inFlight=False,inFlightRequests=[],pendingRepair={},pendingNew=[],review=str(rf),updatedAt=now())
spec=review.get('nativeSpec')
if spec:p.update(workingVersions=read(Path(spec))['patchVersions'],selectedCoordinateCount=16,generatedNativeCount=len(list((ROOT/'native').glob(tid+'_p*.png'))))
write(ROOT/f'progress-{tid}.json',p)
print(json.dumps({'tile':tid,'counts':c}))

from workflow import *
q=ROOT/'qa/r12_c12-sol-20261012-v01'
f=ROOT/'tiles/r12_c12.candidate-sol-20261012-v01.png';expected='afc8b32555ff1d7b19de32c2e54e446245d62867f6b7ed5490d0ed2dbe0189fc'
assert sha(f)==expected
write(q/'root-visual-review.json',{'reviewedAtUtc':now(),'reviewer':'root','candidate':str(f),'candidateSha256':expected,'junctions':{f'junction_{r}{c}':'pass' for r in range(1,4) for c in range(1,4)},'internalSeams24':'pending independent Sol agent review','overlayReviews':{'16':'all previous actual outer and north joins passed; unchanged accepted native source','17':'left/right/top and NW/NE corners passed; unchanged accepted native source','18':{'left':'pass','top':'pass','bottom':'pass','rightVisible':'pass','rightExternal':'pending actual neighbor','completePlankEndT':'pass','clippedGoldFinialContinuity':'pass'}},'realNorthFullEdge':'pass','realNorthSubjunctions3':'pass','realSouthP11Only':'pass','realSouthFullEdge':'pending','minorFindings':'Fine woodgrain and water ripple phase changes only, no shifted contour, disconnected plank boundary, missing support, filled water gap or extra finial observed in reviewed cuts.','formalAccepted':False})
r=read(ROOT/'production-resume-20261012.json')
pending=[{'tile':'r12_c11','candidate':str(ROOT/'tiles/r12_c11.candidate-sol-20261012-v01.png'),'sha256':'2396f77f0c589db7aeabc42529252a90402cec9fb20d85ab93a1c1760e6753da','fullyCovered':True,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'pending':'one native material join repair and candidate reassembly/independent review'},{'tile':'r12_c12','candidate':str(f),'sha256':expected,'fullyCovered':True,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'pending':'independent 24 internal seam review; east/south external neighbors unfinished','sourceProof':str(q/'source-proof.json')}]
for x in pending:
 cf=Path(x['candidate']);assert sha(cf)==x['sha256'];rec=read(Path(str(cf)+'.generation.json'));assert rec.get('fullCoverage') and rec.get('allContributionsPixelExact')
r['pendingCandidates']=pending
r['counts'].update(generatedNativeCount=len(list((ROOT/'native').glob('*.png'))),fullyCovered4kCount=12,complete4kCount=12,internalPassed4kCount=10)
r['remainingWithoutFullCandidate']=[x for x in r['remainingWithoutFullCandidate'] if x not in ['r12_c11','r12_c12']]
r.update(updatedAtUtc=now(),inFlightRequests=['r13_c12_p12_v01'],nextStep='Finish independent r12_c12 seam QA and neighboring r12 tiles; continue native r13_c12 pier.')
r['pendingRepairs']=[]
write(ROOT/'production-resume-20261012.json',r)
p=read(ROOT/'progress.json');p.update(updatedAt=now(),**r['counts']);p['pendingCandidates']=pending;p['remainingAssigned4kCount']=37;p['rootInFlightCount']=1;p['inFlight']=True;p['currentTile']='r13_c12';p['currentPatch']='r13_c12_p12';p['nextStep']=r['nextStep'];write(ROOT/'progress.json',p)
p=read(ROOT/'production-state.json');p.update(updatedAt=now(),counts=r['counts'],pendingCandidates=pending,rootInFlightCount=1,inFlight=True,nextStep=r['nextStep']);write(ROOT/'production-state.json',p)
p=read(ROOT/'progress-r12_c12.json');p.update(updatedAt=now(),status='full_4k_native_candidate_pending_independent_internal_review',workingVersions=read(ROOT/'r12_c12-native-spec-20261012-v01.json')['patchVersions'],missingPatches=[],pendingRepairs=[],inFlight=False,inFlightRequests=[],generatedNativeCount=len(list((ROOT/'native').glob('r12_c12*.png'))),fullyCovered4kCount=1,internalPassed4kCount=0,candidate=str(f),candidateSha256=expected,sourceProof=str(q/'source-proof.json'));write(ROOT/'progress-r12_c12.json',p)
assert sha(ROOT/'migration-freeze-20261011.json')=='fde0f73f4342364e2d75c54401e9d4b66e378d3583d86ed6b2e3c13368954eeb'
print(json.dumps({'counts':r['counts'],'pendingCandidateCoordinates':[x['tile'] for x in pending]}))

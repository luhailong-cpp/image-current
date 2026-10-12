from workflow import *
import numpy as np

# Recover the only current-run output without an ingested copy. No new network call.
src=Path('C:/Users/luyua/.codex/generated_images/01a13459-b23e-7a80-b4b2-1e079b5884c0/exec-91a6e4f0-f370-4902-ba0b-4efc4c90128f.png')
pid='r13_c13_p24';v='v02';out=ROOT/'native'/f'{pid}_{v}.png';req=read(ROOT/'prompts'/f'{pid}_{v}.request.json')
assert sha(src)=='4ca4682395649a02b7cc237b5d60cf811ccf856bdee93afad0af28e7cc5933ae'
assert not out.exists();shutil.copy2(src,out);assert sha(out)==sha(src)
receipt=ROOT/'receipts'/f'{pid}_{v}.local-recovery-20261013.json'
rec={'savedAt':now(),'operation':'local recovery of already generated original; no new generation','source':str(src),'sha256':sha(src),'actualModel':None,'actualQuality':None,'toolOutputHintAvailable':False,'requestAssociation':'inferred from unique matching prepared p24v02 guide and content among the three in-flight right-side requests; exact matching mast/top anchor and large hull continuing at bottom','originalPreserved':True,'request':str(ROOT/'prompts'/f'{pid}_{v}.request.json'),'status':'native_saved_pending_actual_neighbor_review'}
write(receipt,rec)
write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG','mode':'RGB','tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'recoveredAt':now(),'sourceOutputLastWriteUtc':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'actualModel':None,'actualQuality':None,'prompt':req['promptPath'],'promptSha256':sha(Path(req['promptPath'])),'references':req['references'],'coordinate':patch(pid),'evidence':{'localRecoveryRecord':str(receipt),'returnedFields':None,'requestAssociation':rec['requestAssociation']},'resizedAfterGeneration':False,'status':'recovered_pending_visual_and_seam_review'})
recovery=read(ROOT/'returned-output-check-resume-20261013.json')
for x in recovery['outputs']:
    if x['sha256']==sha(src):x['savedMetadata']=out.name+'.generation.json';x['recoveredAfterAudit']=True
recovery['unmappedCount']=0;recovery['recoveryRecord']=str(receipt);write(ROOT/'returned-output-check-resume-20261013.json',recovery)

# Independent replay and final actual-crop identity check for the newly completed left tile.
q=ROOT/'qa/r13_c11-resume-20261013-v01';proof=read(q/'source-pixel-proof.json');vr=read(q/'left-visual-review.json')
candidate=Path(proof['candidate']);assert sha(candidate)==proof['candidateSha256']==vr['candidateSha256']
im=Image.open(candidate).convert('RGB');a=np.asarray(im);ids=np.asarray(Image.open(proof['sourceIdMap']))
assert sha(Path(proof['sourceIdMap']))==proof['sourceIdMapSha256'];checks=[]
for s in proof['sources']:
    p=Path(s['file']);assert sha(p)==s['sha256'];n=np.asarray(Image.open(p).convert('RGB'))
    y,x=np.where(ids==s['sourceId']);dx,dy=s['destination'];sx,sy=s['sourceCrop'][:2]
    mismatch=int(np.count_nonzero(np.any(a[y,x]!=n[y-dy+sy,x-dx+sx],axis=1)));assert mismatch==0
    checks.append({'source':str(p),'sha256':s['sha256'],'pixels':len(x),'mismatch':mismatch})
assert sum(x['pixels'] for x in checks)==4096*4096
for e in vr['entries']:
    p=Path(e['file']);assert sha(p)==e['sha256']
    if 'sourceCrop' in e:assert np.array_equal(np.asarray(Image.open(p).convert('RGB')),np.asarray(im.crop(e['sourceCrop'])))
for side in ['north','east']:
    neighbor=vr['neighbors'][side];p=Path(neighbor['file']);assert sha(p)==neighbor['sha256'];other=Image.open(p).convert('RGB')
    for i in range(4):
        if side=='north':
            expected=Image.new('RGB',(1024,512));expected.paste(other.crop((i*1024,3840,(i+1)*1024,4096)),(0,0));expected.paste(im.crop((i*1024,0,(i+1)*1024,256)),(0,256))
        else:
            expected=Image.new('RGB',(512,1024));expected.paste(im.crop((3840,i*1024,4096,(i+1)*1024)),(0,0));expected.paste(other.crop((0,i*1024,256,(i+1)*1024)),(256,0))
        assert np.array_equal(np.asarray(expected),np.asarray(Image.open(q/f'{side}{i+1}.png').convert('RGB')))
rootReview={'reviewedAt':now(),'candidate':str(candidate),'candidateSha256':sha(candidate),'sourceIdReplayMismatch':0,'ownedPixels':4096*4096,'sourceChecks':checks,'actualQAEvidenceIdentityVerified':True,'visualReview':'Root viewed all six native seam contact sheets, all nine junctions, complete lower column source boundary, and actual north/east four-segment contacts. Rock contours, waterline, column shaft/base and sea detail remain coherent. Minor native texture phase only.','internalSeamsPassed':24,'junctionsPassed':9,'availableExternalSidesPassed':['north','east'],'internalPassed':True,'externalPassed':False,'formalAccepted':False,'pending':'west and south actual full-tile neighbors and final outer-corner acceptance'}
rp=q/'root-independent-review-resume-20261013.json';assert not rp.exists();write(rp,rootReview)

# Geometry of the saved floor ownership repair improved, but retain visible shade step as not passed.
rq=ROOT/'qa/r12_c13-floor-ownership-20261013';p=read(rq/'candidate-v03-source-id-proof.json');assert sha(Path(p['candidate']))==p['candidateSha256']
repairReview={'reviewedAt':now(),'candidate':p['candidate'],'candidateSha256':p['candidateSha256'],'sourceProof':str(rq/'candidate-v03-source-id-proof.json'),'sourcePixelMismatch':p['mismatchedPixels'],'reviewedSeams':24,'reviewedJunctions':9,'ownershipBoundariesReviewed':6,'geometryFindings':'Complete floor T join restored; top/bottom black grooves continuous. Lowest sail batten physical outer contours connect; internal painted band phase is not a structural break.','internalPassed':False,'formalAccepted':False,'remainingIssue':{'type':'visible_vertical_wood_shade_step','tileX':1024,'approximateTileYRange':[1500,2350],'evidence':str(rq/'candidate-v03-ownership-whole-object.png'),'evidenceSha256':sha(rq/'candidate-v03-ownership-whole-object.png'),'note':'Full object view exposes a straight brightness/texture change across several boards at former core boundary. Keep best v03 geometry, local appearance repair pending.'},'status':'best_saved_geometry_pending_material_repair','nextStep':'When builtin permission restored, local native edit preserving complete T join and board geometry; no programmatic blending or color change.'}
write(rq/'root-review-resume-20261013.json',repairReview)

# This batch uses only current native names and new evidence; no repeated historical image scan.
resume=read(ROOT/'production-resume-20261012.json');adopt=resume['currentAdoptedCandidates'];assert not any(x['tile']=='r13_c11' for x in adopt)
adopt.append({'tile':'r13_c11','candidate':str(candidate),'sha256':sha(candidate),'fullyCovered':True,'internalPassed':True,'externalPassed':False,'localArtworkAcceptanceReady':False,'formalAccepted':False,'sourceProof':str(q/'source-pixel-proof.json'),'review':str(rp),'pending':rootReview['pending']})
pending=[{'tile':'r12_c13','candidate':p['candidate'],'sha256':p['candidateSha256'],'fullyCovered':True,'internalPassed':False,'status':repairReview['status'],'review':str(rq/'root-review-resume-20261013.json'),'pending':repairReview['remainingIssue']}]
counts=resume['counts'];counts.update(generatedNativeCount=len(list((ROOT/'native').glob('*.png'))),fullyCovered4kCount=17,complete4kCount=17,internalPassed4kCount=16,missingNative4kCount=32,fullCandidatePendingRepairOrReviewCount=1)
incident={'recordedAt':now(),'kind':'builtin_authentication_and_permission_failure','rawErrors':{'r14_c14_p12_v01':'image generation failed: http 401 Unauthorized: Missing bearer or basic authentication in header; invalid_request_error','r14_c14_p21_v01':'image generation failed: application network permission was revoked','r14_c14_p14_v02':'image generation failed: http 401 Unauthorized: Missing bearer or basic authentication in header; invalid_request_error','left_resume':'Fatal error: application network permission was revoked','right_resume':'Fatal error: application network permission was revoked','wall_resume':'Fatal error: application network permission was revoked'},'newNetworkRetriesAfterExplicitRevocation':0,'permissionOrCredentialChanges':False,'allCurrentRunReturnedOriginalsPreserved':True,'returnedOutputAudit':str(ROOT/'returned-output-check-resume-20261013.json'),'actualModel':None,'status':'generation_blocked_by_builtin_auth_or_permission; local QA completed','nextAction':'Restore original builtin session permission/authentication through app, then resume saved missing requests; no paid API or bypass.'}
ip=ROOT/'generation-interruption-resume-20261013.json';write(ip,incident)
resume['remainingWithoutFullCandidate']=[t for t in resume['remainingWithoutFullCandidate'] if t!='r13_c11'];resume.update(status='generation_blocked_auth_or_permission',generationStopped=True,inFlight=False,inFlightRequests=[],pendingCandidates=pending,updatedAtUtc=now(),currentInterruption=incident,nextStep=incident['nextAction'])
write(ROOT/'production-resume-20261012.json',resume)
for name in ['progress.json','production-state.json','current-zone-counts-20261013.json']:
    f=ROOT/name;d=read(f)
    if 'counts' in d:d['counts']=dict(counts)
    else:d.update(counts)
    if 'currentAdoptedCandidates' in d:d['currentAdoptedCandidates']=adopt
    if 'missingNativeTiles' in d:d['missingNativeTiles']=resume['remainingWithoutFullCandidate']
    d.update(status=resume['status'],generationStopped=True,inFlight=False,rootInFlightCount=0,inFlightRequests=[],pendingCandidates=pending,currentInterruption=incident,updatedAt=now(),updatedAtUtc=now(),nextStep=incident['nextAction']);write(f,d)
print(json.dumps({'counts':counts,'recovered':str(out),'adopted':'r13_c11','pendingRepair':'r12_c13 visible wood shade step','interruption':str(ip)}))

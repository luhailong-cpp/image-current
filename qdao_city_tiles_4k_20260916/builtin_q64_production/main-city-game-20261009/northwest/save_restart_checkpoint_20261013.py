from pathlib import Path
from datetime import datetime, timezone
import json, os
import numpy as np
from PIL import Image
import production_v2 as p
Z=p.ZONE
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
def write(f,v):p.write_json(f,v,replace=False)
now=datetime.now(timezone.utc).isoformat()
shared=Z/'r07_c05/bridges/shared-east-lower-02'
write(shared/'primary-visual-review.json',{'createdAtUtc':now,'reviewer':'/root','candidate':ref(shared/'trial-native-roi.png'),'reviewedCrops':[ref(shared/n) for n in ['repair-detail.png','upper-perimeter.png','lower-perimeter.png','left-perimeter.png','right-perimeter.png']],'actuallyViewed':True,'status':'local_geometry_passed_pending_independent_review','finding':'The native vertical joint connects the original diagonal endpoints. No locator ink or clipped tips remain in the reviewed ROI. Top/bottom/left/right ROI boundaries were actually viewed. Other defects along the full external edge remain outside this local repair.','fullExternalEdgePassed':False,'formalAccepted':False,'independentReviewBlocker':'Reviewer agent returned Fatal error: application network permission was revoked.'})
# Save both sides as proposals; retain delivered PNG and the pending v07 unchanged.
source=np.asarray(Image.open(shared/'native.png').convert('RGB'))
proposals=[]
for tile,base,box,src in [('r07_c05',Z/'r07_c05/candidate/r07_c05-candidate-native-rois-final-872df04172946ceb/candidate.png',[4059,2673,4096,2796],[590,473,627,596]),('r07_c06',Z/'r07_c06/candidate/r07_c06-candidate-native-roi-v07.png',[0,2673,51,2796],[627,473,678,596])]:
    old=np.asarray(Image.open(base).convert('RGB')); out=old.copy(); x0,y0,x1,y1=box; a,b,c,d=src
    out[y0:y1,x0:x1]=source[b:d,a:c]
    f=shared/(tile+'-shared-lower-proposal-4096.png');Image.fromarray(out).save(f)
    different=np.any(out!=old,axis=2); outside=different.copy();outside[y0:y1,x0:x1]=False
    assert not outside.any() and np.array_equal(out[y0:y1,x0:x1],source[b:d,a:c])
    proposals.append({'tile':tile,'base':ref(base),'candidate':ref(f),'source':ref(shared/'native.png'),'sourceROI':src,'tileROI':box,'nativeOriginXY':[3469,2200] if tile=='r07_c05' else [-627,2200],'allUnchangedPixelsInheritedFromValidatedBase':True,'changedPixels':int(different.sum()),'changedPixelsOutsideROI':int(outside.sum()),'exactSameWorldNativePixels':True,'status':'proposal_pending_independent_review_not_current_delivery'})
write(shared/'two-tile-proposal.json',{'createdAtUtc':now,'proposals':proposals,'sourceResampled':False,'blending':False,'formalAccepted':False})
# The c4 source was copied before its worker lost permission; recover host identity by exact bytes.
D=Z/'r07_c06/repair-batches/c4-upper-material-01'; native=D/'native.png'; digest=p.sha(native)
request=p.read(D/'request.json'); generated_root=Path('C:/Users/luyua/.codex/generated_images'); stamp=native.stat().st_mtime
matches=[];candidates=0
for thread in generated_root.iterdir():
    if not thread.is_dir():continue
    for host in thread.glob('*.png'):
        st=host.stat()
        if abs(st.st_mtime-stamp)>300 or st.st_size!=native.stat().st_size:continue
        candidates+=1
        if p.sha(host)==digest:matches.append(host)
assert len(matches)==1, matches
write(D/'generation-recovered-after-interruption.json',{'createdAtUtc':now,'file':str(native),'sha256':digest,'sourceHostFile':str(matches[0]),'sourceHostSha256':digest,'recoveryMethod':'Exact SHA256 and byte-size match against host output in a five-minute file timestamp window. Original tool receipt was not saved before worker failure.','matchingHostCount':len(matches),'candidateHostCount':candidates,'request':ref(D/'request.json'),'nativePixels':list(Image.open(native).size),'worldBox':request['nativeWorldBox'],'tileOriginXY':request['tileOriginXY'],'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'sourceResampled':False,'status':'saved_native_pending_local_roi_review','formalAccepted':False})
base=Image.open(Z/'r07_c06/candidate/r07_c06-candidate-native-roi-v07.png').convert('RGB');s=Image.open(native).convert('RGB');roi=[115,571,1254,700];box=[2957,853,4096,982]
trial=base.copy();trial.paste(s.crop(roi),(box[0],box[1]));trial.save(D/'trial-upper-band-4096.png')
for name,b in [('upper-band',[2880,810,4096,1025]),('left-band',[2897,823,3027,1022]),('top-band',[2957,823,4096,883]),('bottom-band',[2957,952,4096,1012])]:trial.crop(b).save(D/(name+'.png'))
write(D/'trial-upper-band.json',{'candidate':ref(D/'trial-upper-band-4096.png'),'base':ref(Z/'r07_c06/candidate/r07_c06-candidate-native-roi-v07.png'),'source':ref(native),'sourceROI':roi,'tileROI':box,'status':'pending_visual_review','formalAccepted':False})
cap=Z/'r07_c06/repair-batches/west-cap-material-01'
write(cap/'primary-review-after-interruption.json',{'createdAtUtc':now,'trial':ref(cap/'trial-candidate-4096.png'),'cropActuallyViewed':ref(cap/'trial-detail-native.png'),'reviewer':'/root','status':'needs_repair_not_adopted','finding':'The closed triangular grout cap is intact, but the trial shows conspicuous crossed rectangular texture bands across the upper-left stone field. Material integration is not acceptable; preserve the previous candidate and this native source.','formalAccepted':False})
sel=p.read(Z/'r06_c03/selection.json')
write(Z/'restart-checkpoint-20261013-0835.json',{'createdAtUtc':now,'status':'native_generation_blocked_by_application_network_permission','blockingErrors':[{'agent':'/root/continue_r06_c03','error':'Fatal error: application network permission was revoked'},{'agent':'/root/finish_r07_c06','error':'Fatal error: application network permission was revoked'}],'networkPermissionChangedByAgent':False,'paidAPIUsed':False,'modelSettingsChanged':False,'actualBackendModel':None,'effectiveOwnedTileCount':56,'reservedTilesExcluded':['r01_c04','r01_c05','r02_c04','r02_c05','r03_c04','r03_c05','r04_c04','r04_c05'],'r06_c03Selection':ref(Z/'r06_c03/selection.json'),'sharedLowerRepair':ref(shared/'two-tile-proposal.json'),'r07_c06IndependentInternalReview':ref(Z/'r07_c06/qa/current-v07-native-20261013/independent-internal-review-restart-20261013.json'),'c4SavedNativeRecovery':ref(D/'generation-recovered-after-interruption.json'),'nextSteps':['Resume r06_c03 at s02_04; row1 already selected. Do not regenerate saved row1.','Independently review shared-east-lower-02 ROI and integrate both halves into fresh native source registries.','Inspect c4-upper-material-01 local trial, repair west-cap material as needed, then current affected QA.'],'wholeZoneComplete':False,'historicalDeliveryPackagesUnchanged':True})
print({'sharedProposalCount':len(proposals),'c4NativeSha256':digest,'c4RecoveredHost':str(matches[0]),'checkpoint':str(Z/'restart-checkpoint-20261013-0835.json')})

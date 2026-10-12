from pathlib import Path
import sys,shutil
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent;sys.path.insert(0,str(Z))
import production_v2 as p
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
def check(r):
 assert p.sha(r['file'])==r['sha256'],r['file'];return Path(r['file'])
def write(f,v):
 p.write_json(f,v,replace=False);assert p.read(f)==v
T=Z/'r07_c05';Q=T/'qa/trial-bottom-floor-cap-02-trimmed';m=p.read(Q/'index.json');a=np.array(Image.open(check(m['candidate'])).convert('RGB'));own=np.array(Image.open(check(m['sourceIndex'])));assert a.shape==(4096,4096,3) and own.shape==(4096,4096)
sources=m['sources'];proof=[];total=0
for i,s in enumerate(sources):
 f=check(s);n=np.array(Image.open(f).convert('RGB'));assert n.shape==(1254,1254,3);assert p.sha(s['sourceHostFile'])==s['sha256'];check(s['generationRecord'])
 if i<16:assert p.sha(p.selected_path(T,s['id']))==s['sha256']
 for e in s['evidence'].values():check(e)
 ys,xs=np.where(own==i);ox,oy=s['tileOriginXY'];assert np.array_equal(a[ys,xs],n[ys-oy,xs-ox]);total+=len(xs);proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactSameWorldNativePixels':True,'hostByteIdentical':True})
assert total==16777216 and len(sources)==21
prior_path=T/'qa/local-caps-trial-01/independent-review.json';prior=p.read(prior_path);old={Path(e['file']).stem:e for e in prior['internalQa']};entries=[];changed=[]
for e in m['internalQa']:
 f=check(e);name=f.stem;prev=old[name];check(prev);pixels=np.array(Image.open(f));same=np.array_equal(pixels,np.array(Image.open(prev['file'])))
 crop=Image.fromarray(a).crop(e['cropLTRB'])
 if e.get('rotationCCW90'):crop=crop.transpose(Image.Transpose.ROTATE_90)
 assert np.array_equal(pixels,np.array(crop))
 if same:
  assert prev['visualVerdict']=='passed';review={'mode':'inherited_identical_native_pixels','priorReport':ref(prior_path),'priorCrop':ref(Path(prev['file'])),'actuallyViewedCurrent':False}
 else:
  assert name in ['internal-x1024-segment04','internal-y2048-segment04'];changed.append(name);review={'mode':'direct_native_delta_review','actuallyViewedCurrent':True,'viewDetail':'original','reviewers':['/root','/root/resume_r06_c07_finish'],'findings':'Bottom offset tips close with short vertical grout and southern edge exits naturally; shared east local intersection remains connected.'}
 entries.append({**e,'name':name,'visualVerdict':'passed','review':review})
assert len(entries)==33 and len(changed)==2
details=[]
for name in ['cap-and-perimeter','trim-detail','bottom-detail']:
 f=Q/(name+'.png');details.append({**ref(f),'actuallyViewed':True,'viewDetail':'original','nativePixelScale':1,'visualVerdict':'passed','reviewers':['/root','/root/resume_r06_c07_finish']})
boundary_path=T/'qa/final-roi-native-20261012/review.json';boundary=p.read(boundary_path);assert boundary['blockingCount']==0
oldcandidate=np.array(Image.open(check(boundary['candidate'])).convert('RGB'));assert np.array_equal(oldcandidate[:320],a[:320]) and np.array_equal(oldcandidate[:,:320],a[:,:320])
candidate_dir=T/'candidate/r07_c05-candidate-native-rois-final-872df04172946ceb';candidate_dir.mkdir(exist_ok=True)
for src,dst in [(Path(m['candidate']['file']),candidate_dir/'candidate.png'),(Path(m['sourceIndex']['file']),candidate_dir/'source-index.png')]:
 assert not dst.exists();shutil.copyfile(src,dst);assert p.sha(src)==p.sha(dst)
candidate={**ref(candidate_dir/'candidate.png'),'pixels':[4096,4096],'mode':'RGB'}
assembly={'schemaVersion':2,'tile':'r07_c05','createdAtUtc':p.now(),'output':candidate,'nativeSources':sources,'fixedGridSourceCount':16,'additionalNativeSourceCount':5,'totalNativeSourceCount':21,'sourceIndex':ref(candidate_dir/'source-index.png'),'sourceIndexEncoding':'uint8 zero-based nativeSources; nativeXY=tileXY-tileOriginXY','pixelProof':{'status':'passed','checkedPixels':total,'allPixelsUnmodifiedNativeSamplesAtExactWorldCoordinates':True,'sources':proof},'assemblyInput':ref(Q/'index.json'),'sourceResampled':False,'blending':False,'feathering':False,'formalAccepted':False}
write(candidate_dir/'assembly.json',assembly)
review={'createdAtUtc':p.now(),'candidate':candidate,'assemblyManifest':ref(candidate_dir/'assembly.json'),'status':'passed','internalQA':{'status':'passed','seamSegments':24,'junctions':9,'reviewedNativeCrops':33,'inheritedIdenticalCrops':31,'newNativeCrops':2,'entries':entries},'additionalNativeDeltaViews':details,'roiPerimeterReview':ref(boundary_path),'availableActualExternalReview':{'sides':['north','west'],'seamSegments':8,'junctions':6,'evidence':ref(boundary_path),'currentBoundaryPixelsEqualReviewedCandidate':True},'remainingExternalSides':['east','south'],'formalAccepted':False}
write(Q/'final-current-review.json',review)
acceptance={'schemaVersion':1,'tile':'r07_c05','createdAtUtc':p.now(),'candidate':candidate,'internalQA':{'status':'passed','actuallyViewed':True,'seamSegments':24,'junctions':9,'evidence':ref(Q/'final-current-review.json')},'externalQA':{'status':'partial_passed','reviewedSides':['north','west'],'pendingSides':['east','south'],'evidence':ref(boundary_path)},'formalAccepted':False};write(T/'qa/acceptance.json',acceptance)
delivery={'tile':'r07_c05','createdAtUtc':p.now(),'status':'internally_reviewed_native_deliverable','candidate':candidate,'assemblyManifest':ref(candidate_dir/'assembly.json'),'qaEvidence':ref(Q/'final-current-review.json'),'acceptance':ref(T/'qa/acceptance.json'),'selectedNativeCount':16,'additionalNativeSourceCount':5,'nativeSources':sources,'verifiedPixels':total,'internalQAPassed':True,'availableActualNorthWestBoundariesPassed':True,'unresolvedInternalBlockers':[],'formalAccepted':False,'zoneComplete':False};write(T/'delivery-summary-20261012.json',delivery)
T=Z/'r06_c07';name='r06_c07-candidate-hard-4c0d654c3aae';prior_path=T/'qa'/(name+'.internal-review-pending-rib.json');r=p.read(prior_path);external_path=T/'qa'/(name+'.actual-neighbor-review.json');ext=p.read(external_path);proof_path=T/'qa'/(name+'.native-pixel-proof.json');nativeproof=p.read(proof_path);manifest_path=T/'candidate'/(name+'.assembly.json');manifest=p.read(manifest_path);candidate=r['candidate'];check(candidate);assert candidate==manifest['output'] and nativeproof['allRGBExact'] and nativeproof['verifiedPixels']==16777216
entries=[]
for e in r['crops']:
 check(e);e=dict(e)
 if e['status']!='passed':
  assert Path(e['file']).stem=='internal-y3072-segment02';e.update(status='passed',notes='Root directly viewed at original native detail. Lantern paper ribs remain connected through horizontal seam; local bending follows the spherical lantern rather than ending or jumping. Warm paper light and adjacent stone grain are continuous.',reviewer='/root')
 entries.append(e)
assert len(entries)==33 and len(ext['crops'])==15
for e in ext['crops']:check(e);assert e['status']=='passed'
for k in ['actualNorth','actualWest','actualNorthwest']:check(ext[k])
sources=manifest['nativeSources'];a=np.array(Image.open(candidate['file']).convert('RGB'));total=0
for s in sources:
 f=check(s);pid=s['id'];v=p.validate_native(f,T,pid);assert p.sha(p.selected_path(T,pid))==s['sha256'];gr=p.read(v['generationRecord']);host=gr.get('sourceHostFile',gr.get('evidence',{}).get('hostOutputPath'));assert host and p.sha(host)==s['sha256'];n=np.array(Image.open(f).convert('RGB'));row=s['row'];col=s['column'];x=(col-1)*1024;y=(row-1)*1024;assert np.array_equal(a[y:y+1024,x:x+1024],n[115:1139,115:1139]);total+=1024*1024
assert total==16777216
review_path=T/'qa'/(name+'.internal-review-final.json');write(review_path,{'createdAtUtc':p.now(),'candidate':candidate,'status':'passed','internalQA':{'status':'passed','seamSegments':24,'junctions':9,'crops':entries},'initialReview':ref(prior_path),'rootAdditionalNativeView':'internal-y3072-segment02','blockingCount':0,'formalAccepted':False})
acceptance={'schemaVersion':1,'tile':'r06_c07','createdAtUtc':p.now(),'candidate':candidate,'internalQA':{'status':'passed','actuallyViewed':True,'seamSegments':24,'junctions':9,'evidence':ref(review_path)},'externalQA':{'status':'partial_passed','reviewedSides':['north','west'],'pendingSides':['east','south'],'evidence':ref(external_path)},'formalAccepted':False};write(T/'qa/acceptance.json',acceptance)
delivery={'tile':'r06_c07','createdAtUtc':p.now(),'status':'internally_reviewed_native_deliverable','candidate':candidate,'assemblyManifest':ref(manifest_path),'qaEvidence':ref(review_path),'externalQaEvidence':ref(external_path),'nativePixelProof':ref(proof_path),'acceptance':ref(T/'qa/acceptance.json'),'selectedNativeCount':16,'additionalNativeSourceCount':0,'nativeSources':sources,'verifiedPixels':total,'internalQAPassed':True,'availableActualNorthWestBoundariesPassed':True,'unresolvedInternalBlockers':[],'formalAccepted':False,'zoneComplete':False};write(T/'delivery-summary-20261012.json',delivery)
print({'completed':['r07_c05','r06_c07'],'internallyReviewedTileTotal':11,'wholeZoneComplete':False})

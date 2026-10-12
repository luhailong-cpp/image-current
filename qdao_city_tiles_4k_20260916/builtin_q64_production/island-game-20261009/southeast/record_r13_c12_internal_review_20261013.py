from workflow import *
from PIL import Image
import numpy as np
tid='r13_c12';q=ROOT/'qa/r13_c12-sol-20261013-v01';candidate=ROOT/'tiles/r13_c12.candidate-sol-20261013-v01.png';im=Image.open(candidate).convert('RGB');proof=read(q/'source-proof.json');assert sha(candidate)==proof['candidateSha256'] and proof['sourceReplayMismatch']==0
seams=read(q/'seams.json')
for e in seams['entries']:
 assert np.array_equal(np.array(im.crop(e['sourceCrop'])),np.array(Image.open(e['file']).convert('RGB')))
 e.update(status='passed_root_actual_visual',reviewedAtUtc=now(),note='Actual native-scale crop reviewed, including unchanged-pixel contact sheets; physical contours continuous. Minor water ripple/texture phase retained.')
seams.update(status='passed_root_actual_visual',internalSeamPassedCount=24,formalAccepted=False);write(q/'seams.json',seams)
junctions=[]
for r in range(1,4):
 for c in range(1,4):
  f=q/f'junction_{r}{c}.png';b=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];assert np.array_equal(np.array(im.crop(b)),np.array(Image.open(f).convert('RGB')));junctions.append({'file':str(f),'sha256':sha(f),'sourceCrop':b,'status':'passed_root_actual_visual'})
overlay=read(q/'overlay-qa-cuts.json')
for e in overlay['cuts']:
 assert np.array_equal(np.array(im.crop(e['sourceCrop'])),np.array(Image.open(e['file']).convert('RGB')))
 e['status']='passed_root_actual_visual'
for side in ['left','top']:
 assert np.array_equal(np.array(Image.open(q/f'overlay-16-{side}.png')),np.array(Image.open(ROOT/f'qa/r13-stair-cross-v02-wide/{side}.png')))
overlay.update(status='passed_root_actual_visual',formalAccepted=False);write(q/'overlay-qa-cuts.json',overlay)
review={'candidate':str(candidate),'candidateSha256':sha(candidate),'reviewer':'root','status':'passed_internal_actual_visual','sourcePixelReplayMismatch':0,'internalSeamPassedCount':24,'junctionPassedCount':9,'overlayOuterJoinPassedCount':4,'junctions':junctions,'viewedEvidence':['preview.png','h11.png','h12.png','h13.png','h21.png','h22.png','h23.png','v11.png','v12.png','v13.png','v14.png','contact-row2-v.png','contact-water-h.png','contact-water-v.png','contact-junctions.png','overlay-16-right.png','overlay-16-bottom.png','../r13-stair-cross-v02-wide/left.png','../r13-stair-cross-v02-wide/top.png'],'finding':'Complete two broad physical stair landings and column bodies/feet connected. Upper tapering plank groove ends at actual front beam, not within flat board. Full-width whole-source adoption retains complete object. Slight blue water texture/ripple phase changes recorded as minor differences.','externalAccepted':False,'formalAccepted':False,'updatedAtUtc':now()};write(q/'root-visual-review.json',review)
manifest=read(ROOT/'proposed-overlay-r13_c12-stair-20261012-v02.json');manifest.update(status='adopted_after_full_candidate_internal_review',review=str(q/'root-visual-review.json'),sourceProof=str(q/'source-proof.json'),adoptedAtUtc=now(),formalAccepted=False);write(ROOT/'adopted-overlay-r13_c12-stair-20261013-v02.json',manifest)
selected=read(ROOT/'selected-native-r13_c12-sol-20261013-v01.json');selected.update(internalAccepted=True,externalAccepted=False,formalAccepted=False,review=str(q/'root-visual-review.json'),adoptedOverlayManifest=str(ROOT/'adopted-overlay-r13_c12-stair-20261013-v02.json'));write(ROOT/'selected-native-r13_c12-sol-20261013-v01.json',selected)
p=read(ROOT/'progress-r13_c12.json');p.update(updatedAt=now(),status='full_candidate_internal_passed_external_neighbors_pending',fullyCovered4kCount=1,complete4kCount=1,internalPassed4kCount=1,externalPassed4kCount=0,formalAcceptedCount=0,candidate=str(candidate),candidateSha256=sha(candidate),sourceProof=str(q/'source-proof.json'),review=str(q/'root-visual-review.json'),pendingRepairs=[],inFlight=False,inFlightRequests=[]);write(ROOT/'progress-r13_c12.json',p)
resume=read(ROOT/'production-resume-20261012.json');items=[x for x in resume['currentAdoptedCandidates'] if x['tile']!=tid];items.append({'tile':tid,'candidate':str(candidate),'sha256':sha(candidate),'fullyCovered':True,'internalPassed':True,'externalPassed':False,'localArtworkAcceptanceReady':False,'formalAccepted':False,'sourceProof':str(q/'source-proof.json'),'review':str(q/'root-visual-review.json'),'pending':'Whole actual external west/east/south neighbors are unfinished; north actual candidate join is being checked separately.'});resume.update(currentAdoptedCandidates=items,updatedAtUtc=now());write(ROOT/'production-resume-20261012.json',resume)
ni=Image.open(ROOT/'tiles/r12_c12.candidate-sol-20261012-v01.png').convert('RGB');contact=Image.new('RGB',(2048,1024));entries=[]
for c in range(4):
 strip=Image.new('RGB',(1024,512));strip.paste(ni.crop((c*1024,3840,(c+1)*1024,4096)),(0,0));strip.paste(im.crop((c*1024,0,(c+1)*1024,256)),(0,256));f=q/f'actual-north-{c+1}.png';strip.save(f);contact.paste(strip,((c%2)*1024,(c//2)*512));entries.append({'file':str(f),'sha256':sha(f),'status':'pending_actual_north_review'})
contact.save(q/'contact-actual-north.png');write(q/'actual-north.json',{'candidate':str(candidate),'candidateSha256':sha(candidate),'northCandidate':str(ROOT/'tiles/r12_c12.candidate-sol-20261012-v01.png'),'northSha256':sha(ROOT/'tiles/r12_c12.candidate-sol-20261012-v01.png'),'entries':entries,'formalAccepted':False})
print(json.dumps({'candidate':str(candidate),'internalSeams':24,'junctions':9,'sourceMismatch':0,'internalAccepted':True,'formalAccepted':False}))

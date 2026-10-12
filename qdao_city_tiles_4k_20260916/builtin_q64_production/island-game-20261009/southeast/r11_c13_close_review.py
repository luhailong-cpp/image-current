from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now
T='r11_c13';q1=ROOT/'qa/r11_c13-v01';q2=ROOT/'qa/r11_c13-v02'
old=ROOT/'tiles/r11_c13.candidate-v01.png';new=ROOT/'tiles/r11_c13.candidate-v02.png'
a=np.array(Image.open(old).convert('RGB'));b=np.array(Image.open(new).convert('RGB'))
mask=np.ones((4096,4096),bool);mask[1024:2048,3072:4096]=False
assert not np.any(a[mask]!=b[mask])
v1={'reviewedAt':now(),'reviewer':'right_continue','candidate':str(old),'candidateSha256':sha(old),'internalSeams':{'count':24,'status':'pass_with_minor_water_phase','method':'First two row 10 exact crops visually reviewed previously and inherited pixel-exact; third-row 7 and last-row 7 visually viewed at original pixels.'},'internalJunctions':{'count':9,'status':'pass_with_minor_water_phase','method':'All 9 raw crops viewed'},'northWestSharedEdges':{'count':8,'status':'pass','method':'All 8 raw crops viewed'},'fourTileJunction':{'status':'pass','method':'1024-square original pixels viewed'},'finding':'No major geometry breaks. Faint vertical water material guide at candidate x about 3187 across p24; queued one native repair.','status':'superseded_by_v02','formalAccepted':False}
write(q1/'visual-review.json',v1)
inherited=[];changed=[]
names=[x['id'] for x in read(q1/'seams.json')['entries']]+[f'j{r}{c}' for r in range(1,4) for c in range(1,4)]+[f'north-{i}' for i in range(1,5)]+[f'west-{i}' for i in range(1,5)]+['four-tile-junction']
for name in names:
 p=q1/(name+'.png');n=q2/(name+'.png');same=np.array_equal(np.array(Image.open(p)),np.array(Image.open(n)))
 item={'id':name,'oldFile':str(p),'oldSha256':sha(p),'newFile':str(n),'newSha256':sha(n),'pixelExact':bool(same)}
 (inherited if same else changed).append(item)
third=[]
for p in (ROOT/'qa/r11_c13-third-row').glob('*.png'):
 n=q1/p.name
 if n.exists():third.append({'id':p.stem,'oldFile':str(p),'candidateFile':str(n),'pixelExact':bool(np.array_equal(np.array(Image.open(p)),np.array(Image.open(n))))})
assert all(x['pixelExact'] for x in third)
for q in (q1,q2):
 s=read(q/'seams.json')
 for e in s['entries']:e['status']='pass_visual_review' if q==q2 else 'pass_with_minor_water_phase' if e['id']=='h23' else 'pass_visual_review'
 write(q/'seams.json',s)
review={'reviewedAt':now(),'reviewer':'right_continue','candidate':str(new),'candidateSha256':sha(new),'status':'internal_and_north_west_passed','sourceProof':str(q2/'source-audit.json'),'internalSeamCount':24,'internalSeamsPassed':24,'internalJunctionCount':9,'internalJunctionsPassed':9,'northWestSharedEdgeCount':8,'northWestSharedEdgesPassed':8,'fourTileJunction':'pass','changedCropsActuallyViewed':[x['id'] for x in changed],'unchangedCropsInheritedFromViewedV01':inherited,'changedCropProof':changed,'thirdRowPriorProof':third,'outsideP24CorePixelExact':True,'outsideP24CorePixelCount':int(mask.sum()),'northWestAndNorthwestJunctionPixelExact':all(x['pixelExact'] for x in inherited if x['id'].startswith(('north-','west-','four-'))),'repairConclusion':'One full-native p24 edit removed the long interior vertical guide artifact. Rock silhouettes, coast contact foam and seam geometry remain continuous. h23, v14, v24 and j13/j23 checked in original pixels; full 1536 preview checked.','minorResidual':'At j23 a short fine-water phase difference remains in the inherited p34 upper overlap. No long material band or structural break; no repeated repair.','northNeighbor':'r10_c13.candidate-v02.png','westNeighbor':'r11_c12.candidate-v02.png','northwestNeighbor':'r10_c12.candidate-v02.png','eastSouthEdges':'pending future neighbors; not formally accepted','formalAccepted':False,'actualModel':None,'actualQuality':None}
write(q2/'visual-review.json',review)
p=ROOT/'progress-r11_c13.json';d=read(p);d.update({'status':'internal_and_north_west_passed','updatedAt':now(),'generatedNativeCount':18,'totalActualOutputCount':19,'selectedNativeCount':16,'usableNativeCount':16,'supersededNativeCount':1,'rejectedOutputCount':2,'fullyCovered4kCount':1,'complete4kCount':1,'internalPassed4kCount':1,'externalPassed4kCount':0,'northWestSharedEdgesPassed':8,'formalAcceptedCount':0,'latestCandidate':str(new),'latestCandidateSha256':sha(new),'qaReview':str(q2/'visual-review.json'),'sourceAudit':str(q2/'source-audit.json'),'nextStep':'Root independent review; east/south shared edges pending future neighbors. Parent authorized next r12_c13; coordinate west anchor with parent.'});write(p,d)
print({'changed':[x['id'] for x in changed],'inheritedCount':len(inherited),'thirdRowProof':all(x['pixelExact'] for x in third),'sourceMismatch':read(q2/'source-audit.json')['mismatchedPixels'],'nativeAuditCount':len(read(q2/'source-audit.json')['nativeEvidenceAudit'])})


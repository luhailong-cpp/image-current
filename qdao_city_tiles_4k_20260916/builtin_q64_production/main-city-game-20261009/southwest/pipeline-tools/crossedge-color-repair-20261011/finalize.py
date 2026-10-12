import repair,json
from PIL import Image
import numpy as np
R=repair.R
names=['wood-upper-v01','wood-middle-v01','wood-lower-v01','east-stone-v01','east-stone-left-v01']
proposals=[]
for name in ('wood-combined','east-combined'):
 p=R/name/'proposal.json';r=repair.read(p)
 for field,hashfield in [('premixed','premixedSha256'),('copyMask','copyMaskSha256'),('input','inputSha256')]:assert repair.sha(r[field])==r[hashfield]
 a=np.array(Image.open(r['input']));b=np.array(Image.open(r['premixed']));m=np.array(Image.open(r['copyMask']))>0
 assert np.array_equal(a[~m],b[~m])
 for s in r['sourceCrops']:assert repair.sha(s['file'])==s['sha256'],'candidate changed since snapshot'
 proposals.append({'id':name,'file':str(p),'sha256':repair.sha(p),'worldBox':r['worldBox'],'premixed':r['premixed'],'premixedSha256':r['premixedSha256'],'copyMask':r['copyMask'],'copyMaskSha256':r['copyMaskSha256'],'input':r['input'],'inputSha256':r['inputSha256'],'maskPixelCount':int(m.sum()),'outsideMaskUnchanged':True})
ctx=repair.SW/'r10_c06/repairs-20261011/output/r10_c06.repaired.candidate.context.png'
cand=repair.SOURCES['r10_c06'][0]
assert np.array_equal(np.array(Image.open(ctx))[115:4211,115:4211],np.array(Image.open(cand)))
qa={'reviewedAtUtc':repair.now(),'localRepairsReviewed':True,'woodTargetFindings':'Wood boundary colour cut and plank groove notches improved through upper/middle/lower wood. Native detail 4 segments reviewed, including ivory arcs and combined overlaps.','eastTargetFindings':'Main pedestal front and adjacent left bevel/stone face no longer show the rectangular stripe at y40960/y41075 in the 1914-wide review crop. Genuine pedestal boundaries and foliage retained.','remainingIssues':[{'id':'north-stair-tone','worldBox':[20300,39514,20760,40960],'finding':'Existing vertical light/dark cut remains in stone stairs below the wooden fascia. It is explicitly excluded from this wood repair.'},{'id':'outside-current-mask','finding':'All areas outside sparse proposal masks retain source pixels, including north outermost rows, pillar/drum fragments and existing missing-object concerns. No whole-edge or whole-tile approval.'}],'formalAccepted':False,'wholeNorthEdgeVisualPassed':False,'wholeEastEdgeVisualPassed':False,'requiresParentIntegrationReview':True,'evidence':[str(R/'wood-combined'/('review-segment'+str(i)+'.png'))for i in range(1,5)]+[str(R/'east-combined/review-band.png')]}
repair.write(R/'visual-review.json',qa)
manifest={'status':'stable_two_combined_proposals_ready_for_parent_merge','createdAtUtc':repair.now(),'writeScope':str(R),'newSuccessfulBuiltinCalls':5,'newNativeImages':5,'actualNativePixels':[1254,1254],'rejectedImages':0,'failedBuiltinCalls':0,'actualModel':None,'actualQuality':None,'sourceResampling':False,'maximumFeatherRadiusPixels':2,'proposals':proposals,'individualProposalsSupersededForMerge':True,'mergeInstructions':'Apply only the two combined proposals. Copy premixed RGB once where the binary copy-mask is nonzero. Each proposal is world-coordinate aligned. Validate original pixels under the mask against input.png. Do not apply individual patches again and do not blend premixed pixels again. Root owns candidate/context updates.','generationRecords':[str(R/n/'generation.json')for n in names],'promptFiles':[str(R/n/'prompt.txt')for n in names],'receiptFiles':[str(R/n/'receipt.json')for n in names],'toolReturnFiles':[str(R/n/'tool-return.json')for n in names],'latestR10c06ContextVerification':{'context':str(ctx),'sha256':repair.sha(ctx),'centralCoreEqualsLatestCandidate':True,'candidate':str(cand),'candidateSha256':repair.sha(cand)},'sourceCandidatesUnchanged':True,'visualReview':str(R/'visual-review.json'),'formalAccepted':False,'inFlightCalls':0}
repair.write(R/'manifest.json',manifest)
print(json.dumps({'manifest':str(R/'manifest.json'),'manifestSha256':repair.sha(R/'manifest.json'),'proposals':proposals},ensure_ascii=False))


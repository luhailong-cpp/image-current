from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
Q=Z/'qa/r04_c02_v9_internal_review'
def info(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
index=json.loads((Q/'qa_index.json').read_text(encoding='utf-8-sig'))
replay=json.loads((Q/'strict-replay.json').read_text(encoding='utf-8-sig'))
assert replay['proof']['fullNativeCoverage'] and replay['proof']['verifiedPixelCount']==4096**2 and replay['proof']['priorRepairCount']==8
a=np.array(Image.open(Z/'tiles/r04_c02_candidate-v1_4096.png'));b=np.array(Image.open(Z/'tiles/r04_c02_candidate-v9_4096.png'));d=np.any(a!=b,axis=2)
edges={}
for name,p in [('north',d[0,:]),('south',d[-1,:]),('west',d[:,0]),('east',d[:,-1])]:
 idx=np.where(p)[0];edges[name]={'changedPixelCount':len(idx),'changedSpanHalfOpen':[int(idx.min()),int(idx.max()+1)] if len(idx) else None}
review={'schemaVersion':1,'tileId':'r04_c02','candidate':info(Z/'tiles/r04_c02_candidate-v9_4096.png'),'record':info(Z/'tiles/r04_c02_candidate-v9_4096.native-repair.json'),'owner':'west_closure','ownerReview':'PASS','nativeScale100Percent':True,'standardCropCount':33,'standardCrops':[dict(x,ownerVisualResult='PASS') for x in index['seamAndJunctionCrops']],'extraBoundaries':[dict(info(Q/n),ownerVisualResult='PASS',nativeScale100Percent=True) for n in ['eastupper_lower_boundary_100pct.png','eastroof_lower_boundary_100pct.png','wallscroll_upper_boundary_100pct.png','full_east_mid_100pct.png','north_paving_tip_100pct.png']],'findings':'Stone joints/coping and engraved panels remain connected; tree branches/leaves/petals cross source paths without clipping; cobalt roof barrels and gold/red eaves remain continuous. No open internal geometry or selected repair boundary defect observed. Natural painted stone pattern remains stylized rather than photographic.','strictNativeReplay':info(Q/'strict-replay.json'),'replayVerifiedPixels':4096**2,'nativeSources':16,'selectedRepairCount':8,'outerEdgeChangesVsV1':edges,'macroReviewNote':'Root approved s01c03 a01 following the existing r03c02 sword pedestal ground height; its height differs from the blurred overview. a02 duplicate pedestal rejected. Connected macro review remains required; do not duplicate/extend the sword pedestal.','nextTileNorthAnchor':'Use actual final r04c02 v9 core plus verified original halo; westwalk repair changed south edge, so original row4 native alone is stale.','independentReview':'pending root 12 vertical +9 junction and connected_closure 12 horizontal','internalClosurePassed':False,'externalSeamsReviewed':False,'formalAccepted':False,'formalAcceptedCount':0,'progressModified':False}
(Q/'owner-review.json').write_text(json.dumps(review,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps({'review':info(Q/'owner-review.json'),'edges':edges}))


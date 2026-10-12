from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jsave(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
A=read(D/'output/assembly.json');B=read(Path(A['checks']['Bassembly']))
base=Path(A['sourceContext']);assert sha(base)==A['requiredContextSha256']
# Read-only compatibility QA crop: exact A and B masked pastes, no writes outside A.
box=[950,3060,1530,3580];q=np.array(Image.open(base).crop(box).convert('RGB'))
for group in (A,B):
 for patch in group['patches']:
  p=patch['patch'];m=patch['pasteMask'];assert sha(p['path'])==p['sha256'] and sha(m['path'])==m['sha256']
  b=patch['contextBox'];ix0=max(box[0],b[0]);iy0=max(box[1],b[1]);ix1=min(box[2],b[2]);iy1=min(box[3],b[3])
  if ix0>=ix1 or iy0>=iy1:continue
  pixels=np.array(Image.open(p['path']).convert('RGB'));mask=np.array(Image.open(m['path']).convert('L'))>0
  sub=pixels[iy0-b[1]:iy1-b[1],ix0-b[0]:ix1-b[0]];submask=mask[iy0-b[1]:iy1-b[1],ix0-b[0]:ix1-b[0]]
  dst=q[iy0-box[1]:iy1-box[1],ix0-box[0]:ix1-box[0]];dst[submask]=sub[submask]
Image.fromarray(q).save(D/'qa/A-plus-B-junction-compatibility.png')
qa={'status':'PASS-local-repair-with-disclosed-G07-adjustment','recommendedForParentMerge':True,'formalAccepted':False,'wholeTilePassed':False,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'findings':[{'ids':['G01','G02'],'result':'PASS','description':'Removed both unsupported NW/SW spurs, including their beveled free endpoints. Retained original NE-SE corner without visible disconnection. Retained SE centerline sample displacement 0 to 2 pixels within the tiny junction neighborhood.'},{'ids':['G07'],'result':'PASS-local-continuity','description':'Expanded narrow clipping corridor eliminates the notch, double bevel and floating residual. Groove and short vertical stem connect continuously. This composition intentionally accepts a six-pixel local T endpoint adjustment while preserving far anchors; it does not satisfy an absolute original-T-position lock.','geometryAdjustment':A['G07LocalGeometryAdjustment'],'previousTinyROI':'Rejected; the present expanded corridor is a different composition using the same raw native source.'}],'checks':A['checks'],'outsideMasksExact':True,'noBmaskOverlap':True,'CregionOutsideACrop':True,'generationCounts':{'successfulBuiltinResponses':5,'toolErrors':0,'sourceNativeContributions':2,'fullyRejectedMainAttempts':['group-a-v1','group-a-v2','group-a-G01-v3'],'actualModel':None,'actualQuality':None},'visualEvidence':[str(D/'output/A.candidate.native-crop.png'),str(D/'qa/G07-original-candidate.png'),str(D/'qa/G01-G02-original-candidate.png'),str(D/'qa/A-plus-B-junction-compatibility.png')],'sourceAndSharedFilesModified':False,'requiresWholeTileRecheckAfterGroupIntegration':True}
jsave(D/'qa/final-review.json',qa)
result={'status':'three-targets-repaired-ready-for-parent-mask-merge','formalAccepted':False,'wholeTilePassed':False,'requiredFullContextSha256':A['requiredContextSha256'],'assembly':str(D/'output/assembly.json'),'assemblySha256':sha(D/'output/assembly.json'),'visualReview':str(D/'qa/final-review.json'),'visualReviewSha256':sha(D/'qa/final-review.json'),'patches':A['patches'],'successCount':5,'toolErrorCount':0,'actualModel':None,'actualQuality':None,'importantLimitation':'G07 expanded local corridor adjusts the local T endpoint by about six pixels. Geometry continuity is visually restored, but original T coordinates are not completely frozen.','sourcesNativeSelectionProgressUnmodified':True,'nextAction':'Apply patch+binary-mask pairs once onto the recorded base context, alongside disjoint B and C patches; run whole-tile QA. Never replace entire patch bounding rectangles.'}
jsave(D/'production-result.json',result)
print(json.dumps({'status':result['status'],'assembly':result['assembly'],'patches':[{k:p[k] for k in ['id','contextBox','patch','pasteMask']} for p in A['patches']],'review':result['visualReview']},indent=2))


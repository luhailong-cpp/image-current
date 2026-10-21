from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013';Q.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
A=T/'qa/core-baseline/27e3b54a79fea64ed866/assembly.json';a=read(A)
base=next(x for x in a['artifacts'] if x['kind']=='complete-4k-candidate-unreviewed');B=Path(base['file']);im=Image.open(B).convert('RGB');assert im.size==(4096,4096)
plan=[{'id':'wall-leaves','origin':[1250,480],'finding':'P2 flat rectangular wall/leaf cutoff across y1024, including right-of-gable shadow cutoff and nearby clipped leaves.'},{'id':'leaf-bands','origin':[2700,650],'finding':'P2 short horizontal/vertical clipped foliage at first/second-row junction and native p24 context strip boundaries.'},{'id':'roof-corner','origin':[450,2350],'finding':'P2 rectangular material/tone steps around four-core junction x1024,y3072; rib geometry mostly aligned.'},{'id':'rock-corner','origin':[2450,2450],'finding':'P2 rectangular rock texture and tone step around four-core junction x3072,y3072.'}]
for p in plan:
 x,y=p['origin'];target=Q/(p['id']+'-input-v1.png');assert not target.exists();im.crop((x,y,x+1254,y+1254)).save(target)
 p.update({'input':str(target),'inputSha256':sha(target),'crop':[x,y,x+1254,y+1254],'attempt':1,'status':'prepared'})
save(Q/'repair-plan-v1.json',{'baseCandidate':base,'baseAssembly':str(A),'operation':'1254 native pixel integer crops only','repairs':plan})
review={'tile':T.name,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':str(B),'candidateSha256':base['sha256'],'readyInternalPairsReviewed':24,'completeIntersectionsReviewed':9,'quickReviewsReused':['qa/first-row-v20261013/visual-review.json','qa/quick-native-joins/row2-first-half-review.json','qa/quick-native-joins/row2-second-half-review.json','qa/quick-native-joins/row3-first-three-review.json'],'newSeamWindows':['p24-p34','p33-p34','p31-p41','p32-p42','p33-p43','p34-p44','p41-p42','p42-p43','p43-p44'],'newCornerWindows':[str(A.parent/('intersection-r%d-c%d-100pct.png'%(r,c))) for r in range(1,4) for c in range(1,4)],'p2Issues':plan,'p3Notes':['Minor painterly grain variation away from repair regions.'],'status':'complete_native_candidate_local_repairs_pending','internalPassed4kCount':0,'formalAcceptedCount':0,'sourceShaVerification':'Assembly validates all 16 actual sources, receipts and attached reference hashes. No altered sources since quick checks.'}
save(Q/'baseline-review-v1.json',review)
p=read(T/'tile-progress.json');p.update({'status':'complete_native_candidate_local_repairs_pending','candidate':str(B),'candidateSha256':base['sha256'],'selectedCoreCount':16,'remainingCoreCount':0,'completeCandidateCount':1,'internalPassed4kCount':0,'formalAcceptedCount':0,'fullInternalReview':str(Q/'baseline-review-v1.json'),'pendingRepairs':[x['id'] for x in plan],'nextPatch':None});save(T/'tile-progress.json',p)
print(json.dumps({'candidate':base,'repairPlan':str(Q/'repair-plan-v1.json')}))

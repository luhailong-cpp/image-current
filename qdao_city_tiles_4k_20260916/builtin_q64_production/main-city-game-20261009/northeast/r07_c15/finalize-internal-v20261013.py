from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Z=T.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();q=T/'qa/local-repair-20261013'
composition=read(q/'local-repairs-composition-v1.json')
candidate=Path(composition['candidate']);baseline=Path(composition['baseCandidate'])
a=Image.open(baseline).convert('RGB');b=Image.open(candidate).convert('RGB')
diff=ImageChops.difference(a,b)
for layer in composition['layers']:
    x,y=layer['targetOrigin'];l,t,r,bt=layer['crop'];diff.paste((0,0,0),(x+l,y+t,x+r,y+bt))
assert diff.getbbox() is None
report={'tile':'r07_c15','reviewedAtUtc':now,'candidate':str(candidate),'candidateSha256':sha(candidate),'status':'internal_seam_review_passed_shared_world_edges_pending','internalPassed4kCount':1,'formalAcceptedCount':0,'readyInternalPairsReviewed':24,'completeIntersectionsReviewed':9,'priorReviewReused':str(T/'qa/model-pause-20261012/visual-review.json'),'newCoreReview':str(q/'baseline-review.json'),'repairedFindings':[{'id':'P2-wood-post-start-r1c3','status':'resolved','reviewImage':str(q/'post-composed-review-v2.png'),'finding':'Support now connects continuously to existing eave; interrupted gold/red post cap removed. Lantern/roof alignment retained.'},{'id':'P2-stair-plinth-notch-r3c1','status':'resolved','reviewImage':str(q/'stair-composed-review-v1.png'),'finding':'Stone cheek joins platform with continuous supported faces; rectangular notch removed. Stair count and width retained.'}],'p2Issues':[],'p3Notes':['Small local redwood grain and wall tonal differences retained; no geometry break observed.'],'sourceProof':composition,'outsideRepairRectanglesByteIdenticalToReviewedBaseline':True,'westSharedEdgeReviewReused':'All repair rectangles interior; previously reviewed west edge pixels unchanged.','northEastSouthSharedEdges':'Pending joint review with unfinished adjacent tiles; not formal acceptance'}
save(q/'internal-review-v1.json',report)
save(Path(str(candidate)+'.generation.json'),{'file':str(candidate),'sha256':sha(candidate),'nativeSize':[4096,4096],'assetRole':'assembled 16 native cores plus two local native AI repairs','operation':'integer crop/paste only; no resampling','assembly':str(T/'qa/core-baseline/4310c2993aead148fef7/assembly.json'),'localComposition':str(q/'local-repairs-composition-v1.json'),'visualReview':str(q/'internal-review-v1.json'),'formalAcceptedCount':0})
p=read(T/'tile-progress.json');p.update({'candidate':str(candidate),'candidateSha256':sha(candidate),'status':'complete_native_candidate_internal_review_passed','internalPassed4kCount':1,'formalAcceptedCount':0,'pendingP2RepairCount':0,'generationStopped':False,'blocker':None,'fullInternalReview':str(q/'internal-review-v1.json'),'updatedAt':now,'nextStep':'Shared edges await adjacent-tile completion; root continues its untransferred upper tiles.'});save(T/'tile-progress.json',p)
prog=read(Z/'progress.json')
for r in prog['tiles']:
    if r['tile']=='r07_c15':r.update({'candidate':str(candidate),'candidateSha256':sha(candidate),'internalPassed4kCount':1,'workerStatus':p['status'],'generatedNativeCount':18})
prog.update({'updatedAt':now,'internalPassed4kCount':sum(x['internalPassed4kCount'] for x in prog['tiles']),'completeTilesPendingInternalReviewCount':sum(x['fullyCovered4kCount'] and not x['internalPassed4kCount'] for x in prog['tiles']),'nextStep':'Continue current assigned missing cores; root r07_c15 internal repairs passed.','generationStopped':False})
save(Z/'progress.json',prog)
print(json.dumps({'tile':'r07_c15','candidate':str(candidate),'sha256':sha(candidate),'internalPassed':1,'formalAccepted':0,'rootNextTiles':['r02_c13','r02_c14','r01_c13','r01_c14']}))

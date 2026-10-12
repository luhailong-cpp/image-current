from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;T=D.parents[1];C=T/'candidates/r08_c13.candidate.png'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ev(p):return {'file':str(p),'sha256':sha(p)}
names=['road-junction-v1','stone-cut-v1']
findings=[
 {'id':'P2-road-junction','priority':2,'status':'resolved','tileBox':[1671,2915,2421,3605],'worldBox':[50823,31587,51573,32277],'before':'Blue paving turn contained extra horizontal trough, wedge notch and second kink.','after':'Native redraw rebuilt complete fitted bend and border; no short dead-end wedge. Applied 1:1 crop visually inspected including all four binary-mask boundaries.','evidence':ev(D/'review/road-after-100pct.png'),'repairRecord':str(D/'records/road-junction-v1.json')},
 {'id':'P2-stone-cut','priority':2,'status':'resolved','tileBox':[2555,2400,3360,3084],'worldBox':[51707,31072,52512,31756],'before':'Vertical core cut at tile x3072 interrupted two diamond stone corners and bevel lines.','after':'Complete intersected slabs restored; diagonal joints continuous. Applied 1:1 crop visually inspected including mask boundaries; horizontal blue road pixels outside mask retained.','evidence':ev(D/'review/stone-after-100pct.png'),'repairRecord':str(D/'records/stone-cut-v1.json')}
]
for name in names:
 p=D/'records'/(name+'.json');r=read(p);r['reviewStatus']='passed applied source1254 and mask boundaries at native1:1';save(p,r)
replay=read(D/'replay.json')
for op in replay['operations']:op['record']['sha256']=sha(op['record']['file'])
save(D/'replay.json',replay)
wins=read(D/'review/final-window-manifest.json')
report={'tile':'r08_c13','createdAt':datetime.now(timezone.utc).isoformat(),'candidate':ev(C),'status':'internal_passed_with_recorded_P3_material_variation','completeCandidateCount':1,'internalPassed4kCount':1,'formalAcceptedCount':0,'nativeCoreCount':16,'repairCount':2,'internalReview':{'baselineSeamPairsVisuallyInspectedAt1to1':24,'baselineIntersectionsVisuallyInspectedAt1to1':9,'finalWindowCount':33,'finalWindowsPixelIdenticalToReviewedBaseline':23,'finalChangedWindows':10,'changedWindowMethod':'All differences are inside the two inspected native1254 repair application crops; unaffected content inherits the previous1:1 baseline review. Final window manifest retains each baseline/final SHA. Do not construe this as separately viewing all33 final windows.','manifest':ev(D/'review/final-window-manifest.json')},'repairs':findings,'remainingFindings':[{'priority':3,'status':'recorded not expanded','description':'Minor shifts in stone mineral texture density, paint illumination and fitted grout shapes across native patches; no remaining observed P2 geometry break in reviewed internal windows.'}],'northSeams':ev(D/'review/north-final-review.json'),'otherExternalEdges':'Await completed adjacent candidates and parent group-level review.','sourceReplay':str(D/'apply.py'),'sourceReplayRecord':ev(D/'replay.json'),'actualModel':None,'actualQuality':None,'limits':'Internal geometry review plus four north windows; no formal acceptance, runtime or capacity validation claimed.'}
save(T/'qa/internal-review-20261011.json',report)
side=read(str(C)+'.generation.json')
side.update({'assetRole':'complete4kCandidate; internal geometry review passed; external group review pending','visualReview':str(T/'qa/internal-review-20261011.json'),'visualReviewSha256':sha(T/'qa/internal-review-20261011.json'),'pixelReplayVerified':False,'recipeSha256':sha(D/'replay.json')})
save(str(C)+'.generation.json',side)
p=T/'tile-progress.json';state=read(p)
state.update({'updatedAt':datetime.now(timezone.utc).isoformat(),'status':'complete_4k_candidate_internal_and_north_seams_reviewed','nativePatchCount':16,'selectedCoreCount':16,'remainingCoreCount':0,'completeCandidateCount':1,'fullyCovered4kCount':1,'internalPassed4kCount':1,'internalReviewed4kCount':1,'externalPassed4kCount':0,'formalAcceptedCount':0,'selectedRepairCount':2,'candidate':str(C),'candidateSha256':sha(C),'review':str(T/'qa/internal-review-20261011.json'),'sourceReplay':str(D/'apply.py'),'sourceReplayVerification':str(D/'verification.json'),'northSeamReview':str(D/'review/north-final-review.json'),'inflightGeneration':None,'nextPatch':None,'nextStep':'Parent completes adjacent candidate and connected-group external review; r08_c13 generation and internal QA complete.','actualModel':None,'actualQuality':None})
save(p,state)
print(json.dumps({'candidateSha256':sha(C),'internalPassed4kCount':1,'formalAcceptedCount':0,'remainingCoreCount':0}))


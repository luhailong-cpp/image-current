from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):Path(p).parent.mkdir(exist_ok=True,parents=True);Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sel=rd(R/'selected-patches.json');checks=[];cv=Image.new('RGB',(4096,1024))
for pid,rel in sorted(sel['patches'].items()):
 p=R/rel;g=rd(str(p)+'.generation.json');assert Image.open(p).size==(1254,1254) and sha(p)==g['sha256']
 assert g['actualModel'] is None and g['actualQuality'] is None
 for _,path,hs in [('prompt',g['prompt'],g['promptSha256']),('request',g['evidence']['request'],g['evidence']['requestSha256']),('receipt',g['evidence']['receipt'],g['evidence']['receiptSha256'])]:assert sha(path)==hs
 for ref in g['references']:assert sha(ref['path'])==ref['sha256']
 x=(int(pid[2])-1)*1024;cv.paste(Image.open(p).crop((115,115,1139,1139)),(x,0))
 checks.append({'patch':pid,'file':str(p),'sha256':sha(p),'nativeSize':[1254,1254],'generationRecord':str(p)+'.generation.json','allEvidenceHashesValid':True,'corePixels':1048576})
cp=R/'candidate/r09_c09-bottom-row-native-4096x1024.png';cp.parent.mkdir(exist_ok=True);cv.save(cp)
internal=[R/'qa/resume-pass'/n for n in ['p41--p42.png','p42--p43.png','p43--p44.png']]
ext=R.parent/'seam-qa/r09_c09'
paths=internal+[ext/f'south-segment-{i}-100pct.png' for i in range(1,5)]+[ext/f'intersection-x{x}-y36864-100pct.png' for x in [33792,34816,35840]]
ev=[{'file':str(p),'sha256':sha(p)} for p in paths]
review={'tile':R.name,'reviewer':'south09_resume','status':'partial_native_geometry_pass_color_review_pending','formalAccepted':False,'internalReady':False,'internalSeamsInspected':3,'externalSouthSegmentsInspected':4,'externalSouthCrossingsInspected':3,'geometryBlockingFindings':[],'colorNotes':['Mild same-material exposure/texture changes on south roof/wood joins remain for later bounded low-frequency matching; no geometric displacement was concealed.'],'evidence':ev,'selectedSources':checks}
wr(R/'qa/resume-pass/owner-review.json',review)
d={'tile':R.name,'status':'local_only_after_parent_network_revoked_stop','generatedNativeCount':5,'selectedPatchCount':4,'usableNativeCount':4,'complete4kCandidateCount':0,'internalReady4kCount':0,'formalAcceptedCount':0,'exactCoreCoverage':4194304,'fullTilePixels':16777216,'coverageFraction':0.25,'selectedSources':checks,'rejectedNative':['native/p43-v1.png'],'failureAttempts':[{'file':'p42-v1.attempt-1-error.json','actualImageOutput':False}],'firstActualOutputAfterRestore':{'file':'native/p42-v1.png','sha256':sha(R/'native/p42-v1.png'),'receipt':'p42-v1.receipt.json'},'partialArtifact':{'file':str(cp),'sha256':sha(cp),'dimensions':[4096,1024],'description':'exact bottom row only, not complete tile','resampling':False},'remainingPositions':[f'p{r}{c}' for r in range(1,4) for c in range(1,5)],'nextStep':'After explicit network restoration, view prepared p31-native-conditioned.png then write prompt/request and generate p31; thereafter row3 left to right, row2, row1. Do not regenerate saved bottom row.','preparedGuide':'layout-only/p31-native-conditioned.png','localReview':str(R/'qa/resume-pass/owner-review.json'),'limitations':['No full4096 candidate or internal acceptance','No changes to frozen r10_c09','Git/index/migration untouched'],'updatedAt':datetime.now(timezone.utc).isoformat()}
wr(R/'progress.json',d);wr(R/'local-handoff-20261011.json',d)
print(json.dumps({'tile':R.name,'nativeGenerated':5,'selected':4,'coverage':4194304,'firstRestoreOutput':'p42-v1','hashAudit':'all passed','localReviewEvidence':len(ev),'partialArtifact':str(cp)}))

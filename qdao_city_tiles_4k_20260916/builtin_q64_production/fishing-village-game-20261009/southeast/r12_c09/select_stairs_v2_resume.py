from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=rd(R/'selected-patches.json');prov=rd(R/'processed/joint-stairs/provisional-selection.json')
review=R.parent/'seam-qa/independent-20261010/r12_c09-c10-weststairs-v2-independent.json'
audit=rd(review);assert audit['allEvidenceAndSourceHashesVerified'] and audit['c10CurrentSelectedWestPixelsEqualReviewedPreview']
snap=R/'selected-before-stairs-v2-20261011.json'
if not snap.exists():shutil.copy2(R/'selected-patches.json',snap)
for pid,rel in prov['replacements'].items():
 p=R/rel;rec=rd(str(p)+'.derivation.json');assert sha(p)==rec['sha256']
 assert Image.open(p).size==(1254,1254)
 old['patches'][pid]=rel
cv=Image.new('RGB',(4096,4096));sources=[]
for pid,rel in sorted(old['patches'].items()):
 p=R/rel;im=Image.open(p).convert('RGB');xy=((int(pid[2])-1)*1024,(int(pid[1])-1)*1024);cv.paste(im.crop((115,115,1139,1139)),xy)
 sources.append({'patch':pid,'path':str(p),'sha256':sha(p),'crop':[115,115,1139,1139],'destination':[xy[0],xy[1],xy[0]+1024,xy[1]+1024]})
cp=R/'candidate/r12_c09-stairs-v2-internal-ready-4096.png';cv.save(cp)
now=datetime.now(timezone.utc).isoformat()
d={'tile':R.name,'status':'internal_ready_external_pending','internalReady':True,'formalAccepted':False,'candidate':str(cp),'candidateSha256':sha(cp),'sources':sources,'replacements':prov['replacements'],'independentReview':str(review),'independentReviewSha256':sha(review),'priorSelection':str(snap),'coordinateShift':[0,0],'resampling':False,'imageBlur':False,'pixelBlending':False,'colorCorrectionApplied':False,'ownerReview':'Four changed internal/adoption strips rechecked at100%; no blocking internal geometry. Mild external right material tones remain pending c10 full candidate color review. Prior unchanged internal checks remain valid.','updatedAt':now}
wr(str(cp)+'.derivation.json',d);wr(R/'qa/stairs-v2-adoption-review.json',d)
old.update(candidate=str(cp),candidateSha256=sha(cp),status=d['status'],internalReady=True,formalAccepted=False,jointAdoptionReview=str(R/'qa/stairs-v2-adoption-review.json'),updatedAt=now);wr(R/'selected-patches.json',old)
pr=rd(R/'progress.json');pr.update(candidate=str(cp),candidateSha256=sha(cp),status=d['status'],internalReady4kCount=1,formalAcceptedCount=0,jointAdoptionReview=str(R/'qa/stairs-v2-adoption-review.json'),externalColorReviewPending=True,updatedAt=now);wr(R/'progress.json',pr)
print(json.dumps({'candidate':str(cp),'sha256':sha(cp),'selectedReplacements':3,'internalReady':True,'formalAccepted':False}))

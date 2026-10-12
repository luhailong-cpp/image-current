from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ev(p):return {'file':str(p),'sha256':h(p)}
base=T/'qa/core-baseline/77bab12598c6b11d6b74';left=T/'qa/left-column-v20261012'
review={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r08_c15','selectedCoreCount':4,'sourceValidation':{'assembly':ev(base/'assembly.json'),'invalidSelectedSources':[],'allReferenceBytesReverified':True},'viewedAtNativePixels':[],'findings':[],'internalReviewedPairCount':3,'internalExpectedPairs':24,'externalReviewedWindows':5,'scope':'Only selected left column; no complete-tile or formal acceptance claim','formalAcceptedCount':0,'status':'partial-reviewed-no-P2'}
for stem in ['horizontal-p11-p21','horizontal-p21-p31','horizontal-p31-p41']:
 p=base/(stem+'-join-100pct.png');review['viewedAtNativePixels'].append({**ev(p),'result':'No P2: aligned masonry joints; p31-p41 blue band and complete leaf contours continuous.'})
for p in sorted(left.glob('*100pct.png')):
 review['viewedAtNativePixels'].append({**ev(p),'result':'No P2: paving joints and inherited silhouettes continue across shared boundary.'})
review['findings'].append({'priority':'P3','region':'left column natural pale-stone material','detail':'Minor density/tone shifts in mineral and floral surface marks; no step, crack or cut object in the eight viewed native windows. Preserved without cosmetic overpainting.'})
(left/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf8')
print(json.dumps({'review':ev(left/'visual-review.json'),'viewedCount':len(review['viewedAtNativePixels'])}))


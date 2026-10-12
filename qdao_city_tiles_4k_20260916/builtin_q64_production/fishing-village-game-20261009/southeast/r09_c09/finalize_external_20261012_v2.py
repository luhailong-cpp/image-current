from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parent; Q=R/'qa/external-resume-20261012-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
s=read(Q/'external-seam-summary.json');records=[]
for item in [z for e in s['edges'] for z in e['segments']]+s['intersections']:
    if not item['sourceComplete']:continue
    review=dict(status='view_image_reviewed_100percent',reviewedAt=datetime.now(timezone.utc).isoformat(),structuralBlockers=[],colorOnlyRisks=['Small source-tone difference on existing blue roof; no contour disconnection'] if item['id'] in ['south-segment-3','intersection-x35840-y36864'] else [],candidateUsable=True,formalAccepted=False,note='Latest selected core pixels only. All four south strips and three available south crossings viewed after internal color pass; missing outer neighbors remain pending.')
    item['visualReview']=review;rp=Path(item['report']);d=read(rp);d['visualReview']=review;write(rp,d);records.append(item)
assert len(records)==7
s.update(availableVisualReviewedCount=7,availableGeometryUsable=True,formalAccepted=False,reviewStatus='All currently available segments and intersections reviewed; missing sources pending')
write(Q/'external-seam-summary.json',s)
write(Q/'owner-review.json',dict(tile='r09_c09',availableCount=7,allAvailableViewed=True,records=records,formalAccepted=False))
for name in ['progress.json','local-handoff-20261012.json']:
    p=R/name;d=read(p);d.update(externalQa=str(Q/'external-seam-summary.json'),externalQaSha256=sha(Q/'external-seam-summary.json'),availableExternalQaViewed=7,formalAccepted=False);write(p,d)
print(json.dumps(dict(availableExternalQaViewed=7,formalAccepted=False)))

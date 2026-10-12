"""Record actual root observations supplied in a per-direction evidence file."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
from contact_validation import validate_contact
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
d=sys.argv[1];preview=read(R/'audit'/f'root-{d}-preview-observations.json');assert preview['direction']==d
assert preview['normal']['played'] and preview['quarterSpeed']['played']
assert preview['normal']['cycleMs']==1200 and preview['quarterSpeed']['cycleMs']==4800
assert preview['paused480pxFrames'] and preview['observations']
now=datetime.now(timezone.utc).isoformat();c=validate_contact(R,d,require_preview=False)
preview['reviewedAt']=now;c.update(status='passed_offline_four_spatial_pairs',rootPreview=preview,reviewedAt=now)
save(R/'audit'/f'contact-{d}-review.json',c)
root=read(R/'audit/bamboo-root-acceptance.json');root['directions'][d]={'status':'accepted_offline_after_user_feedback','reviewedAt':now,'frames':c['frames'],'method':preview['method'],'notes':[preview['observations']],'contactReview':f'audit/contact-{d}-review.json','rootPreview':preview,'clientValidated':False}
save(R/'audit/bamboo-root-acceptance.json',root);validate_contact(R,d)
print(d+' actual preview accepted')


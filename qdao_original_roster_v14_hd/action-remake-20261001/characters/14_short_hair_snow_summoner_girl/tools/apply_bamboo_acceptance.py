"""Apply explicit hash-bound root reviews; never infer visual approval from technical validity."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
from contact_validation import validate_contact
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('directions',nargs='+',choices=['N','NE','E','SE','S','SW','W','NW']);args=a.parse_args()
root=read(R/'audit/bamboo-root-acceptance.json')['directions'];reviews=read(R/'review.json');base=read(R/'audit/bamboo-baseline.json')['frames']
for d in args.directions:
 contact=validate_contact(R,d)
 approval=root[d]
 assert approval['status']=='accepted_offline_after_user_feedback'
 assert len(approval['frames'])==16
 for f in approval['frames']:assert sha(R/f['file'])==f['sha256'],'Accepted artwork changed since review'
 phasepath=R/'run'/d/'grounding-review.json';phase=read(phasepath)
 if 'previousFeedbackReview' not in phase:
  phase['previousFeedbackReview']={k:v for k,v in phase.items() if k not in {'previousFeedbackReview','frames'}}
 phase.update({'status':'passed_offline_after_bamboo_reference_review','reviewedAt':approval['reviewedAt'],'selectedCycleMs':1200,'durationsMs':[75]*16,'independentReview':'See audit/bamboo-*-review.json and root SHA-bound acceptance','rootReview':'audit/bamboo-root-acceptance.json','remainingChecks':['Client world velocity, world-root and shadow/event validation after integration'],'clientValidated':False})
 phase.pop('fourFrameContactReview',None)
 phase['spatialContactReview']=f'audit/contact-{d}-review.json'
 phase['contactSpans']=contact['contacts']
 phase['positionPairs']=contact['positionPairs']
 for n,f in enumerate(approval['frames'],1):
  slot=f['file'][:-4];meta=read(R/(f['file']+'.generation.json'))
  reviews[slot]={**reviews.get(slot,{}),'sha256':f['sha256'],'previousFeedbackSha256':base[slot]['sha256'],'visualStatus':'passed','reviewedAt':approval['reviewedAt'],'reviewer':'root; direction-specific static evidence in contact review','scope':approval['method'],'notes':approval['notes'],'rootAcceptance':'audit/bamboo-root-acceptance.json','clientValidated':False}
  row=phase['frames'][n-1]
  row.update({'file':f['file'],'frame':n,'sha256':f['sha256'],'selectedNative':meta['derivedFrom']['file'],'durationMs':75,'reviewStatus':'passed_offline_after_bamboo_reference_review'})
  pair=contact['positionPairs'][(n-1)//2]
  row.update({'phase':pair['position'],'supportLeg':pair['supportLeg'],'observation':pair['observations'],'contactMaintained':True})
  meta['review']={'status':'passed_offline','reviewedAt':approval['reviewedAt'],'source':'review.json','sha256':f['sha256'],'clientValidated':False}
  save(R/(f['file']+'.generation.json'),meta)
 save(phasepath,phase)
save(R/'review.json',reviews)
print(json.dumps({'acceptedDirections':args.directions,'acceptedFrames':len(args.directions)*16}))

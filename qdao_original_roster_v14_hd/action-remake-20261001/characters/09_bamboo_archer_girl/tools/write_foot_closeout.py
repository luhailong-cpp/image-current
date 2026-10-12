from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((ROOT/'review.json').read_text(encoding='utf-8-sig'))
assert len(review['frames'])==196 and not review['staleReviews']
rows=[]
for r in review['frames']:
 p=ROOT/'runtime'/(r['slot']+'.png')
 assert r['sha256']==sha(p),str(p)
 rows.append({'slot':r['slot'],'sha256':r['sha256'],'reviewFile':r['sourceReviewFile'],'evidence':r.get('footOrientation') or r.get('toeKneeAnkleEvidence') or r.get('toeAxisEvidence') or r.get('evidence'),'overallStaticStatus':r.get('status'),'dynamicApproval':False})
out={'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'09_bamboo_archer_girl only: eight run directions plus E/W hit, attack, cast','actualRuntimePng':196,'currentRunDefaultMs':1200,'oldRunBaselineMs':480,'perFrameRunMs':75,'newPromptTemplateAssumedCorrect':False,'referenceNote':'Each current direction assessed independently; another character is not an automatic approval template.','reviewScope':'Current full-body contact sheets and original images; current paired-position evidence in audit/eight-direction-paired-grounding.json. No mechanical leg narrowing or frame translation.','pairedGroundingReview':{'file':'audit/eight-direction-paired-grounding.json','sha256':sha(ROOT/'audit/eight-direction-paired-grounding.json')},'historicalFootReview':{'file':'audit/foot-axis-20261003.md','scope':'Historical only: does not apply to changed frame hashes.'},'dynamicVisualAcceptance':False,'clientIntegration':'not_integrated','clientRuntimeAcceptance':'not_tested','frames':rows,'reviewFiles':[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'review-parts').glob('*.json'))]}
video=ROOT/'audit/video-axis-current-closeout.json'
if video.exists():out['latestVideoAxisReview']={'file':video.relative_to(ROOT).as_posix(),'sha256':sha(video),'dynamicVisualAcceptance':False}
limbs=ROOT/'audit/full-limb-current-closeout.json'
if limbs.exists():out['latestFullLimbReview']={'file':limbs.relative_to(ROOT).as_posix(),'sha256':sha(limbs),'dynamicVisualAcceptance':False}
(ROOT/'audit/foot-grounding-closeout.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'framesBoundToCurrentSha':len(rows),'reviewSequences':len(review['sequences']),'dynamicApproval':False}))

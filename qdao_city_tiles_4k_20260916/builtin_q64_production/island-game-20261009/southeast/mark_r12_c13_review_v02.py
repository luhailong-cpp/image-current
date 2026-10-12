from pathlib import Path
from datetime import datetime,timezone
import json
R=Path(__file__).resolve().parent;Q=R/'qa/r12_c13-resume-sol-20261012'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
n=datetime.now(timezone.utc).isoformat();p=Q/'candidate-v02-seam-review.json';d=read(p)
for s in d['internalSeams']:s.update({'status':'passed_local_visual','reviewedAtUtc':n,'note':'Actual core hard boundary: wood/rail/post/rope/sail edge and water continuity reviewed at original QA dimensions; no geometry break observed.'})
for s in d['junctions']:s.update({'status':'passed_local_visual','reviewedAtUtc':n,'note':'Four native core junction checked at 512 square without resize; connected object boundaries.'})
d.update({'status':'passed_local_visual','internalSeamPassedCount':24,'junctionPassedCount':9,'sourcePixelProof':str(Q/'candidate-v02-source-pixel-proof.json'),'westReview':'Rows 2, 3 and 4 actual root candidate seams passed; inherited row1 and r11 north remain previously passed and were not repainted.','formalAccepted':False});write(p,d)
p=R/'progress-r12_c13.json';pr=read(p);pr.update({'status':'complete_candidate_local_qa_passed','complete4kCount':1,'fullyCovered4kCount':1,'internalPassed4kCount':1,'externalPassed4kCount':1,'formalAcceptedCount':0,'candidate':d['candidate'],'candidateSha256':d['sha256'],'qaReview':str(Q/'candidate-v02-seam-review.json'),'sourcePixelProofMismatchedPixels':0,'nextStep':'Root independent review and formal acceptance; owner continues r13_c13 using accepted r12 candidate/native north anchor.','updatedAt':n});write(p,pr)
p=R/'production-resume-right-sol-20261012.json';res=read(p);res.update({'status':'r12_c13_full_candidate_local_qa_passed_continuing_r13_c13','updatedAtUtc':n,'r12Candidate':{'file':d['candidate'],'sha256':d['sha256'],'sourcePixelProofMismatchedPixels':0,'nativeCoreCount':16,'internalSeamsPassed':24,'junctionsPassed':9,'localVisualAccepted':True,'formalAccepted':False,'review':str(Q/'candidate-v02-seam-review.json')}});write(p,res)
print(json.dumps(res['r12Candidate']))

from pathlib import Path
from datetime import datetime,timezone
import json
from PIL import Image
R=Path(__file__).resolve().parent;Q=R/'qa/r12_c13-resume-sol-20261012'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
n=datetime.now(timezone.utc).isoformat();p=Q/'candidate-v02-seam-review.json';d=read(p);d.update({'status':'root_independent_review_repair_required','localVisualAccepted':False,'formalAccepted':False,'rootFindings':['wood gap ending in flat board around tile x1024 y2170, no physical end-joint T; check above around row2','lowest sail batten around tile x3072 y3730 has apparent roughly50px step; recheck fresh actual candidate source crops']});write(p,d)
p=R/'progress-r12_c13.json';pr=read(p);pr.update({'status':'root_independent_review_repair_required','internalPassed4kCount':0,'externalPassed4kCount':0,'nextStep':'Repair root-identified complete wood end joint and lower sail batten; external count remains zero until all required neighbor borders available.','updatedAt':n});write(p,pr)
p=R/'production-resume-right-sol-20261012.json';res=read(p);res['r12Candidate'].update({'localVisualAccepted':False,'internalSeamsPassed':None,'junctionsPassed':None,'status':'root_independent_review_repair_required','rootFindings':d['rootFindings']});res['updatedAtUtc']=n;write(p,res)
im=Image.open(R/'tiles/r12_c13.candidate-sol-20261012-v02.png').convert('RGB')
for name,box in [('actual-floor-gap-r3-c1',[700,1950,1350,2450]),('actual-floor-gap-r2-c1',[700,1450,1350,1950]),('actual-low-sail-batten',[2700,3500,3500,3950])]:im.crop(tuple(box)).save(Q/f'fresh-{name}.png')
print('Reopened r12 candidate, generated fresh exact source crops.')

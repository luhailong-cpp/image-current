from pathlib import Path
import json,hashlib
Q=Path(__file__).resolve().parent/'r05_c03_v8_internal_closure'
p=Q/'review_pending.json';data=json.loads(p.read_text(encoding='utf8'))
names=data['changedStandardCrops'];assert len(names)==19
report=dict(reviewer='/root/connected_closure',candidate=data['candidate'],method='Independent original-resolution view_image inspection of every listed changed standard crop',status='all_19_changed_standard_crops_passed',checks=[dict(path=str(Q/name),sha256=hashlib.sha256((Q/name).read_bytes()).hexdigest(),visualPassed=True) for name in names],notes=['Stair contours and baseline are continuous.','Door wing and window sill repairs preserve adjacent structures.','Paving repairs retain continuous beveled joints without the prior short L spur.'],formalAccepted=False)
out=Q/'connected_agent_standard_review.json'
with out.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(out)

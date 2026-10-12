from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent.parent
q=Z/'qa/r04_c02_v9_internal_review/qa_index.json'
d=json.loads(q.read_text());items=[x for x in d['seamAndJunctionCrops'] if 'left-right_' in Path(x['path']).name or 'junction_' in Path(x['path']).name]
assert len(items)==21
for x in items:
 p=Path(x['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
 x.update(independentRootNativeVisualStatus='PASS',reviewNote='Viewed at native100percent: continuous stone courses/grout, flowers/branches, blue tile rows and gold/red eaves; no tile seam cut visible.')
out=Z/'qa/r04_c02_v9_independent_root_21_review_20261012.json'
with out.open('x',encoding='utf-8') as f:json.dump({'candidate':{'path':(Z/'tiles/r04_c02_candidate-v9_4096.png').as_posix(),'sha256':'2c846183dfad3630e5640d54b606e1e8e3353f3d0f8dd2a3c1689d93f09368de'},'qaIndex':{'path':q.as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()},'nativeScale100Percent':True,'cropCount':21,'independentRootReviewedOnlyThisSubset':True,'other12HorizontalIndependentReviewOwner':'connected_closure','formalAccepted':False,'items':items},f,ensure_ascii=False,indent=2)
print(out.as_posix(),hashlib.sha256(out.read_bytes()).hexdigest())

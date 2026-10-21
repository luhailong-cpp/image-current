import json,hashlib
from pathlib import Path
z=Path(__file__).resolve().parent
q=z/'qa/assembly_r07_c04_candidate-v1_4096'
j=json.loads((q/'qa_index.json').read_text(encoding='utf-8'))
pending={
'left-right_r01_c03-c04_100pct.png':'rear cap rectangular paving intrusion and stepped front lip near (3070,1050)',
'left-right_r02_c01-c02_100pct.png':'detached oversized floral groove / hard tone join near (1050,2000)',
'left-right_r02_c03-c04_100pct.png':'same rear cap intrusion near (3070,1050)',
'left-right_r03_c01-c02_100pct.png':'wall-foot step and coarse paving blind-end near x1000,y2500..3000',
'left-right_r04_c01-c02_100pct.png':'coarse paving blind-end near (944,3299)',
'left-right_r04_c02-c03_100pct.png':'coarse paving blind-end near (2128,3147)',
'junction_r01-r02_c03-c04_100pct.png':'rear cap intrusion',
'junction_r02-r03_c01-c02_100pct.png':'orphan floral arc and wall-foot step',
'junction_r03-r04_c01-c02_100pct.png':'coarse grout step / blind-end',
'junction_r03-r04_c02-c03_100pct.png':'coarse grout blind-end'
}
items=[]
for x in j['seamAndJunctionCrops']:
 n=Path(x['path']).name
 if not(n.startswith('left-right_') or n.startswith('junction_')):continue
 p=Path(x['path']);h=hashlib.sha256(p.read_bytes()).hexdigest()
 assert h==x['sha256']
 items.append({**x,'reviewer':'right_continuation','visualReview':'actual native 100 percent image viewed','status':'repair_required' if n in pending else 'pass','note':pending.get(n,'Continuous geometry and texture, no blocking join defect visible in this crop.')})
assert len(items)==21
assert sum(x['status']=='repair_required' for x in items)==10
out={'tile':'r07_c04','candidate':str(z/'tiles/r07_c04_candidate-v1_4096.png'),'candidateSha256':'ec6f5430e9259f8e8dbda52b532f493f618dc170226903e62a521fd03f3cfdc3','reviewScope':'12 left-right and 9 junction crops; 12 top-bottom delegated to parent','passCount':11,'repairRequiredCount':10,'internalClosurePassed':False,'formalAccepted':False,'strictNativeReplayObserved':{'result':'pass','fullPixelCoverage':16777216,'rawNativeSources':16,'repairs':0,'planesSha256':'e5b7a024cd705c3c83f550e65d8a59b593f6a34961e6afac30b80fdb0afcac88','note':'Observed strict apply_native_tile_repair.py --validate-base-only success before this review record; not repeated.'},'items':items}
dest=q/'right_native21_review_20261013.json'
with dest.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(str(dest));print(hashlib.sha256(dest.read_bytes()).hexdigest())


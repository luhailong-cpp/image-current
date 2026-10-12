from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent.parent
def info(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
q=Z/'qa/assembly_r05_c02_candidate-v1_4096/qa_index.json'
data=json.loads(q.read_text(encoding='utf-8-sig'))
bad={
'left-right_r02_c02-c03':'Lower medallion gold ring ends and steps near bottom of crop.',
'left-right_r02_c03-c04':'Gold ring small offset and hard texture cut near local y1040.',
'left-right_r03_c02-c03':'Gold ring discontinuity at top, large erroneous triangular bronze projection below body at local y600..1100.',
'left-right_r03_c03-c04':'Gold ring discontinuity visible at very top; remainder continuous.',
'left-right_r04_c01-c02':'Multiple southwest paving grout blind ends and diagonal mismatched slab/shadow cuts.',
'left-right_r04_c02-c03':'Erroneous bronze projection at top and abrupt diagonal paving/shadow segment.',
'top-bottom_r02-r03_x0000-1024':'Left foot top is cropped horizontally near local x620,y355.',
'top-bottom_r02-r03_x2048-3072':'Both gold ring arcs and dark medallion field have hard patch boundaries.',
'top-bottom_r03-r04_x1024-2048':'Middle foot gold moulding offset around local x470,y355 and paving wedge left.',
'top-bottom_r03-r04_x2048-3072':'Foot left contour cropped/stepped near local x110,y340; projection and paving wedge at left.',
'junction_r02-r03_c02-c03':'Medallion lower-left ring stepped at local 280,325.',
'junction_r02-r03_c03-c04':'Medallion right ring offset at local 175,145.',
'junction_r03-r04_c01-c02':'Paving mismatch at lower-right diagonal transition.',
'junction_r03-r04_c02-c03':'Erroneous bronze projection above ground and mismatched paving shadow transition.'}
items=[]
for c in data['seamAndJunctionCrops']:
 key=Path(c['path']).stem.replace('_100pct','')
 items.append({**c,'viewedNative100Percent':True,'status':'REPAIR' if key in bad else 'PASS','note':bad.get(key,'Native contour and material transition continuous; no visible structural cut in this crop.')})
out=Z/'qa/r05_c02_v1_owner_native33_review_20261013.json'
assert not out.exists()
review={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'west_resume','tileId':'r05_c02','candidate':info(Z/'tiles/r05_c02_candidate-v1_4096.png'),'record':info(Z/'tiles/r05_c02_candidate-v1_4096.assembly.json'),'qaIndex':info(q),'status':'native33_reviewed_repairs_pending','nativeViewed':33,'passed':33-len(bad),'repair':len(bad),'internalClosurePassed':False,'formalAccepted':False,'items':items}
out.write_text(json.dumps(review,indent=2)+'\n',encoding='utf8')
s=Z/'west-current-selection-20261012.json';sel=json.loads(s.read_text(encoding='utf-8-sig'))
sel['currentTile']={'tileId':'r05_c02','candidate':review['candidate'],'record':review['record'],'qaIndex':info(q),'internalReview':info(out),'assembled4k':True,'internalClosurePassed':False,'formalAccepted':False,'status':'16_native_assembled_19_PASS_14_repair'}
sel['updatedAtUtc']=review['reviewedAtUtc'];s.write_text(json.dumps(sel,indent=2)+'\n',encoding='utf8')
print(json.dumps({'review':info(out),'passed':review['passed'],'repair':review['repair']}))

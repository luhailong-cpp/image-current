from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast');i='r04_c12_p04_04_v3'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rec=read(z/'native'/f'{i}.png.generation.json')
checks=[]
for ref in rec['references']:
 for source in [ref]+ref.get('sources',[]):
  p=Path(source['file']);checks.append({'path':p.as_posix(),'recordedSha256':source['sha256'],'actualSha256':sha(p),'matches':sha(p)==source['sha256']})
native=z/'native'/f'{i}.png';orig=Path(rec['evidence']['originalToolPath']);im=Image.open(native);assert im.size==(1254,1254);assert all(c['matches'] for c in checks);assert sha(native)==sha(orig)
im.crop((115,115,1139,1139)).save(z/'qa'/f'{i}.core-100pct.png')
audit={'id':i,'nativeSha256':sha(native),'status':'passed_internal_native_upper_left_and_cross','upper':'r04_c12_p03_04_v5','left':'r04_c12_p04_03','geometry':'Continuous down-right blue roof ribs and staggered curved tile joints; matching both sharp anchors. Gold border only in bottom-right planned area. Native, two core joins and cross visually inspected at1:1, passed.','visualEvidence':['r04_c12_p03_04_v5__r04_c12_p04_04_v3.join-100pct.png','r04_c12_p04_03__r04_c12_p04_04_v3.join-100pct.png','cross_r04_c12_p04_04_v3.png'],'originalToolReplayHashMatches':True,'referenceHashChecks':checks,'actualModel':None,'actualQuality':None,'nativeSize':[1254,1254],'coreCrop':[115,115,1139,1139],'resized':False,'feathered':False,'independentReview':'pending parent and south','rightJoin':'delegated to southeast using frozen native','bottomJoin':'perimeter of current connected scope, no new bottom tile requested','reviewedAtUtc':datetime.now(timezone.utc).isoformat()}
write(z/'qa'/f'{i}.audit.json',audit);rec['status']='passed_internal_native_upper_left_and_cross';rec['internalSeams']='upper_left_and_cross_passed';rec['qa']=str(z/'qa'/f'{i}.audit.json');write(native.with_suffix('.png.generation.json'),rec)
p=z/'qa'/'r04_c12_p03_04_v5.audit.json';q=read(p);q['bottomJoin']='passed with r04_c12_p04_04_v3; source and exact core seam inspected at1:1';write(p,q)
for sid in ['r04_c12_p03_03__r04_c12_p03_04_v5','r04_c12_p02_04_v3__r04_c12_p03_04_v5','r04_c12_p03_04_v5__r04_c12_p04_04_v3','r04_c12_p04_03__r04_c12_p04_04_v3']:
 p=z/'qa'/f'{sid}.json';q=read(p);q['status']='passed_visual_geometry_color';q['geometryChecks']={'nativeCoreBoundaryViewedAt100Percent':True,'geometryContinuous':True,'colorContinuous':True,'noVShape':True};q['reviewedAtUtc']=audit['reviewedAtUtc'];write(p,q)
final={'scope':'r04_c12 column4 roof direction correction','status':'completed_internal_qa','finalCores':[{'id':'r04_c12_p02_04_v3','sha256':'31386da8814a038337fbc6d605625276c300145846f6aa07bd6c2a3c4e184314','decision':'retained original core, blue defect only in discarded halo; root independently accepted true core seam/cross'},{'id':'r04_c12_p03_04_v5','sha256':'0a6c92995d611c4f39cbb197fe41a4d3a096d397b8ec733914626eb737b440d9'},{'id':i,'sha256':sha(native)}],'failedAlternativesPreserved':['r04_c12_p02_04_v4','r04_c12_p02_04_v5','r04_c12_p02_04_v6','r04_c12_p03_04_v3','r04_c12_p03_04_v4'],'auditFiles':['r04_c12_p02_04-retained-core-audit.json','r04_c12_p03_04_v5.audit.json',f'{i}.audit.json'],'actualModel':None,'actualQuality':None,'nativeCropPolicy':'1254 native /1024 core/115 halo, no resampling or feathering','selectionAndTilesModified':False,'sourcesFrozenForNeighbors':True}
write(z/'qa'/'r04_c12_p04_04_v3.column-completion.json',final)
print(json.dumps({'id':i,'sha256':sha(native),'refsAllMatch':True,'originalNativeReplay':True,'status':audit['status']}))


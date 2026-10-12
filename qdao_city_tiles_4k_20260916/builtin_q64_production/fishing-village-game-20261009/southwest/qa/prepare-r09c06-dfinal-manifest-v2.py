import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
old=rd(Z/'qa/repair-r09_c06-v1.manifest.json')
post=next(r for r in old['repairs'] if r['id']=='d-front-post-band');post['repairBounds']=[420,320,750,860];post['margin']=45
floor={'id':'d-paving-joint-v2','finding':'F09','tileContextBox':[2600,2840,3854,4094],'contextBox':[2715,2955,3969,4209],'repairBounds':[285,560,875,1180],'margin':45,'source':ref(Z/'qa/repair-r09_c06-d-floor-source-native-v2.png'),'repair':ref(Z/'native/r09_c06_repair_d_floor_v2.png'),'generationRecord':ref(Z/'native/r09_c06_repair_d_floor_v2.png.generation.json')}
m={'schemaVersion':1,'outputPrefix':'repair-r09_c06-dfinal-v2','baseAssembly':old['baseAssembly'],'expectedBaseCandidateSha256':old['expectedBaseCandidateSha256'],'repairs':[post,floor],'scope':'D front post plus new lower floor repair only; other failed v1 regions deliberately absent','nativePixelsResampled':False}
p=Z/'qa/repair-r09_c06-dfinal-v2.manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(ref(p))

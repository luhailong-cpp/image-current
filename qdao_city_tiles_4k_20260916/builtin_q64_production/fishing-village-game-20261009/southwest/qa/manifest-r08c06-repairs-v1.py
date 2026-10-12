import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:{'path':p.as_posix(),'sha256':sha(p)}
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
spec=[
('a_lantern','v1',[180,215,845,1120],40),
('b_rightsign','v1',[720,30,1235,1090],15),
('c_canopyleft','v2',[250,50,1254,1254],50),
('d_canopyright','v3',[0,80,1180,1254],60),
('e_frontcanopy','v1',[280,820,820,1150],50),
('f_goldedge','v1',[420,340,1030,750],55),
('g_woodplane','v1',[470,90,1100,880],60)]
asm=Z/'qa/full-tile-r08_c06-assembly.json';a=rd(asm)
m={'schemaVersion':1,'outputPrefix':'repair-r08_c06-internal-v1','baseAssembly':ref(asm),'expectedBaseCandidateSha256':a['output']['sha256'],'repairs':[]}
for rid,v,b,margin in spec:
 stem='r08_c06_repair_'+rid+'_'+v;j=rd(Z/'native'/(stem+'.request.json'));rp=Z/'native'/(stem+'.png')
 original=j.get('sourceCrop',j['references'][0]);src=Path(original['path'])
 item={'id':rid,'tileContextBox':j['coordinates']['tileContextBox'],'source':ref(src),'repair':ref(rp),'generationRecord':ref(Path(str(rp)+'.generation.json')),'repairBounds':b,'margin':margin}
 m['repairs'].append(item)
p=Z/'qa/repair-r08_c06-internal-v1.manifest.json';p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');print(p)


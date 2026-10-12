import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:{'path':p.as_posix(),'sha256':sha(p)}
m=rd(Z/'qa/repair-r08_c06-internal-v1.manifest.json');m['outputPrefix']='repair-r08_c06-internal-v2'
for r in m['repairs']:
 if r['id']=='a_lantern':r['repairBounds']=[180,215,900,1120];r['margin']=25
 if r['id']=='b_rightsign':
  r['clipPolygon']=[[744,35],[1208,35],[1214,837],[1200,884],[1172,910],[1127,923],[1116,970],[1095,1000],[1040,1025],[1020,1056],[1000,1080],[954,1080],[929,1058],[916,1038],[870,1012],[856,975],[835,938],[799,925],[768,897],[748,865]]
 if r['id']=='e_frontcanopy':
  r['repairBounds']=[280,815,820,1120];r['margin']=20;r['clipPolygon']=[[290,1040],[819,817],[819,908],[290,1110]]
 if r['id']=='f_goldedge':
  p=Z/'native/r08_c06_repair_f_goldedge_v2.png';r['repair']=ref(p);r['generationRecord']=ref(Path(str(p)+'.generation.json'));r['repairBounds']=[500,420,710,630];r['margin']=20
 if r['id']=='g_woodplane':
  r['repairBounds']=[0,0,1140,1000];r['margin']=25;r['clipPolygon']=[[480,0],[515,0],[1120,240],[1120,700],[980,760],[780,784],[348,985],[0,875],[0,625],[460,536],[474,450],[492,250]]
j=rd(Z/'native/r08_c06_repair_h_upperpaving_v1.request.json');p=Z/'native/r08_c06_repair_h_upperpaving_v1.png'
h={'id':'h_upperpaving','tileContextBox':j['coordinates']['tileContextBox'],'source':ref(Path(j['references'][0]['path'])),'repair':ref(p),'generationRecord':ref(Path(str(p)+'.generation.json')),'repairBounds':[500,0,970,740],'margin':40,'clipPolygon':[[500,0],[970,0],[970,215],[760,215],[682,260],[682,336],[838,369],[838,430],[785,470],[785,515],[718,554],[672,610],[642,685],[603,741],[500,741]]}
# H first; A remains final authority over the lantern and front canopy.
m['repairs'].insert(0,h)
(Z/'qa/repair-r08_c06-internal-v2.manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')


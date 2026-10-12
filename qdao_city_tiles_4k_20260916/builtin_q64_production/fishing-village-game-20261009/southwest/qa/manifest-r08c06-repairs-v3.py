import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
qa=Path(__file__).resolve().parent
m=json.loads((qa/'repair-r08_c06-internal-v2.manifest.json').read_text(encoding='utf-8-sig'))
m['outputPrefix']='repair-r08_c06-internal-v3'
for r in m['repairs']:
 if r['id']=='h_upperpaving':
  r['repairBounds']=[0,0,1120,980];r['margin']=30;r.pop('clipPolygon',None)
 if r['id']=='b_rightsign':
  r['repairBounds']=[720,30,1235,1120]
  r['clipPolygon']=[[744,35],[1208,35],[1214,837],[1200,884],[1172,910],[1127,923],[1116,970],[1095,1000],[1070,1065],[1035,1090],[954,1090],[929,1058],[916,1038],[870,1012],[856,975],[835,938],[799,925],[768,897],[748,865]]
 if r['id']=='e_frontcanopy':
  r['repairBounds']=[220,730,950,1254];r['margin']=30;r.pop('clipPolygon',None)
 if r['id']=='f_goldedge':
  r['repairBounds']=[225,270,900,755];r['margin']=30;r.pop('clipPolygon',None)
p=qa/(m['outputPrefix']+'.manifest.json')
with p.open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
print(p)


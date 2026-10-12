import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
q=Path(__file__).resolve().parent
m=json.loads((q/'pair-r08c06-r09c06-v2.manifest.json').read_text(encoding='utf-8-sig'));m['outputPrefix']='pair-r08c06-r09c06-v3'
for r in m['repairs']:
 if r['id']=='south_canopy':
  r['clipPolygon']=[[295,390],[450,335],[1199,335],[1199,1060],[910,910],[630,751],[440,631],[325,550],[295,520]]
 else:
  r['clipPolygon']=[[914,0],[988,0],[990,24],[1023,47],[1048,82],[1055,101],[1150,144],[1225,194],[1253,224],[1253,893],[1110,938],[1036,962],[999,989],[874,989],[871,944],[811,911],[793,856],[727,825],[669,767],[623,692],[599,607],[583,513],[586,428],[603,343],[640,271],[695,204],[773,158],[821,129],[822,92],[840,50],[882,22],[913,15]]
with (q/(m['outputPrefix']+'.manifest.json')).open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)


import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
q=Path(__file__).resolve().parent
m=json.loads((q/'pair-r08c06-r09c06-v3.manifest.json').read_text(encoding='utf-8-sig'));m['outputPrefix']='pair-r08c06-r09c06-v4'
r=m['repairs'][1]
r['clipPolygon']=[[914,0],[988,0],[990,24],[1023,47],[1048,82],[1055,101],[1150,144],[1225,194],[1253,224],[1253,825],[1210,846],[1130,869],[1064,884],[1064,918],[1013,951],[886,951],[849,944],[811,915],[811,879],[800,850],[727,825],[669,767],[623,692],[599,607],[583,513],[586,428],[603,343],[640,271],[695,204],[773,158],[821,129],[822,92],[840,50],[882,22],[913,15]]
with (q/(m['outputPrefix']+'.manifest.json')).open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)


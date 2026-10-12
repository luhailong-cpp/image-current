import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1];Q=Z/'qa'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rep=[]
def add(i,src,stem,box,bounds,margin,poly=None):
 a={'id':i,'source':ref(Q/src),'repair':ref(Z/'native'/(stem+'.png')),'generationRecord':ref(Z/'native'/(stem+'.png.generation.json')),'contextBox':box,'repairBounds':bounds,'margin':margin}
 if poly:a['clipPolygon']=poly
 rep.append(a)
upper=[3640,500,4894,1754]
add('upper-beam','pair-r09c06-c07-upperwood-source-native-v2.png','r09_c06_c07_upperwood_repair_v1',upper,[375,15,707,245],15)
add('rear-plank','pair-r09c06-c07-upperwood-source-native-v2.png','r09_c06_c07_upperwood_repair_v1',upper,[500,415,710,1240],10,[[523,497],[687,427],[687,1216],[523,1117]])
add('red-fish','pair-r09c06-c07-redfish-source-native-v1.png','r09_c06_c07_redfish_repair_v1',[3620,1500,4874,2754],[420,565,1110,1060],35)
lower=[3650,2940,4904,4194]
add('lower-beam','pair-r09c06-c07-lowerwood-floor-source-native-v1.png','r09_c06_c07_lowerwood_floor_repair_v1',lower,[465,402,975,690],25)
add('floor-corner','pair-r09c06-c07-lowerwood-floor-source-native-v1.png','r09_c06_c07_floor_corner_repair_v2',lower,[560,820,1110,1100],40)
m={'schemaVersion':1,'outputPrefix':'pair-r09c06-c07-repair-trial-v1','basePairTrace':ref(Q/'pair-r09c06-c07-v1-trace.json'),'repairs':rep}
p=Q/(m['outputPrefix']+'.manifest.json');p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');print(p)


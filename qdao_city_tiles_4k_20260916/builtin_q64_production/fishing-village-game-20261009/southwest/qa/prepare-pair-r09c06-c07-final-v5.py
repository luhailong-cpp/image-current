import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Q=Path(__file__).resolve().parent;Z=Q.parent
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m=json.loads((Q/'pair-r09c06-c07-final-v4.manifest.json').read_text());m['outputPrefix']='pair-r09c06-c07-final-v5';s=Z/'native/r09_c06_c07_southfloor_repair_v1.png'
m['repairs'].append({'id':'south-floor-corner','source':ref(Q/'pair-r09c06-c07-southfloor-source-native-v1.png'),'repair':ref(s),'generationRecord':ref(Path(str(s)+'.generation.json')),'contextBox':[3650,3072,4904,4326],'repairBounds':[555,1000,1110,1235],'margin':35})
(Q/(m['outputPrefix']+'.manifest.json')).write_text(json.dumps(m,indent=2)+'\n')


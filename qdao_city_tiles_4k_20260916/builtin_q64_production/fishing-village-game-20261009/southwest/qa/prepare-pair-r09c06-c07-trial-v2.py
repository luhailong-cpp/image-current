import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
Q=Path(__file__).resolve().parent
m=json.loads((Q/'pair-r09c06-c07-repair-trial-v1.manifest.json').read_text())
m['outputPrefix']='pair-r09c06-c07-repair-trial-v2'
m['repairs'][0]['clipPolygon']=[[407,36],[688,106],[688,223],[405,157]]
m['repairs'][1]['repairBounds']=[412,408,708,1245]
m['repairs'][1]['clipPolygon']=[[429,546],[687,426],[687,1221],[429,1076]]
p=Q/(m['outputPrefix']+'.manifest.json');p.write_text(json.dumps(m,indent=2)+'\n');print(p)


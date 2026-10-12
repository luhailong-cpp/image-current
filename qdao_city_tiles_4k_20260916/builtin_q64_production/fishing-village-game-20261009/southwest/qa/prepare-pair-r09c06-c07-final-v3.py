import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1];Q=Z/'qa'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m=json.loads((Q/'pair-r09c06-c07-repair-trial-v2.manifest.json').read_text());m['outputPrefix']='pair-r09c06-c07-final-v3'
a=m['repairs'][3];p=Z/'native/r09_c06_c07_lowerbeam_repair_v2.png';a['repair']=ref(p);a['generationRecord']=ref(Path(str(p)+'.generation.json'));a['repairBounds']=[435,385,980,697];a['margin']=20
p=Q/(m['outputPrefix']+'.manifest.json');p.write_text(json.dumps(m,indent=2)+'\n');print(p)


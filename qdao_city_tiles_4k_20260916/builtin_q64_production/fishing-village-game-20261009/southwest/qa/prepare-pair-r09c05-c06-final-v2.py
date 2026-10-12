import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1];QA=Z/'qa';ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m={'schemaVersion':1,'outputPrefix':'pair-r09c05-c06-final-v2','basePairTrace':ref(QA/'pair-r09c05-c06-v1-trace.json'),'source':ref(QA/'pair-r09c05-c06-floor-source-native-v1.png'),'repair':ref(Z/'native/r09_c05_c06_floor_join_repair_v2.png'),'generationRecord':ref(Z/'native/r09_c05_c06_floor_join_repair_v2.png.generation.json'),'contextBox':[3585,2305,4839,3559],'repairBounds':[320,285,915,870],'margin':45,'notes':'v1 native floor repair rejected for displaced corners. v2 surgical repair passed native closed-mask trial; select v2 only.'}
p=QA/'pair-r09c05-c06-final-v2.manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');print(ref(p))

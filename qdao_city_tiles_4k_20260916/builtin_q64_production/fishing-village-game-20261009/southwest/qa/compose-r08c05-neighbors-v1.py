import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,subprocess
Q=Path(__file__).resolve().parent
def ref(p):
 p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,d):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
def run(script,p):subprocess.run([sys.executable,'-B',str(Q/script),'--manifest',str(p)],check=True)
m={'outputPrefix':'pair-r08c05-c06-v1','inputs':[{'tile':'r08_c05','context':ref(Q/'repair-r08_c05-internal-v4-context-native.png')},{'tile':'r08_c06','context':ref(Q/'r08c06-south-final-v7-r08_c06-context-native.png')}],'provenance':[ref(Q/'repair-r08_c05-internal-v4-trace.json'),ref(Q/'r08c06-south-final-v7-root-adoption-audit.json')]}
p=Q/'pair-r08c05-c06-v1.manifest.json';save(p,m);run('native-pair-compose.py',p)
m={'schemaVersion':1,'outputPrefix':'block2x2-r08r09c05c06-v1','globalContextBox':[16269,28557,24691,36979],'tiles':['r08_c05','r08_c06','r09_c05','r09_c06'],'topJoint':ref(Q/'pair-r08c05-c06-v1-context-native.png'),'southwest':ref(Q/'pair-r09c05-c06-northupdate-v1-r09_c05-context-native.png'),'southeast':ref(Q/'r08c06-south-final-v7-r09_c06-context-native.png'),'provenance':[ref(Q/'pair-r08c05-c06-v1-trace.json')]}
p=Q/'block2x2-r08r09c05c06-v1.manifest.json';save(p,m);run('block2x2-generic-compose.py',p)

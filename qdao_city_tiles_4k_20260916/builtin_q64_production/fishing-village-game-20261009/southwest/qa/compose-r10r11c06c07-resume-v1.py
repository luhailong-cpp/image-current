import sys
sys.dont_write_bytecode=True
import json, hashlib, subprocess
from pathlib import Path
Z=Path(__file__).resolve().parent.parent; Q=Z/'qa'
def ref(p):
 p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(name,m):
 p=Q/name;assert not p.exists();p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
inputs=[{'tile':'r10_c06','context':ref(Q/'pair-r10r11c06-final-v5-r10_c06-context-native.png')},{'tile':'r10_c07','context':ref(Q/'block2x2-r09r10c06c07-v2-r10_c07-context-native.png')}]
provenance=[ref(Q/'pair-r10r11c06-final-v5-trace.json'),ref(Q/'block2x2-r09r10c06c07-v2-trace.json')]
p=write('pair-r10c06c07-resume-v1.manifest.json',{'outputPrefix':'pair-r10c06c07-resume-v1','inputs':inputs,'provenance':provenance})
subprocess.run([sys.executable,'-B',str(Q/'native-pair-compose.py'),'--manifest',str(p)],check=True)
m={'outputPrefix':'block2x2-r10r11c06c07-v1','topJoint':ref(Q/'pair-r10c06c07-resume-v1-context-native.png'),'southwest':ref(Q/'pair-r10r11c06-final-v5-r11_c06-context-native.png'),'southeast':ref(Q/'repair-r11_c07-internal-v1-context-native.png'),'provenance':provenance+[ref(Q/'r11_c07-internal-visual-audit-v1.json'),ref(Q/'repair-r11_c07-internal-v1-trace.json'),ref(Q/'pair-r10c06c07-resume-v1-trace.json')],'globalContextBox':[20365,36749,28787,45171],'tiles':['r10_c06','r10_c07','r11_c06','r11_c07']}
p=write('block2x2-r10r11c06c07-v1.manifest.json',m)
subprocess.run([sys.executable,'-B',str(Q/'block2x2-generic-compose.py'),'--manifest',str(p)],check=True)

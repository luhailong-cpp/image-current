import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
m=read(z/'qa/pair-r10r11c06-v1.manifest.json');m['outputPrefix']='pair-r10r11c06-current-v4';m['inputs'][0]['context']=ref(z/'qa/block2x2-r09r10c06c07-v2-r10_c06-context-native.png');m['provenance'].append(ref(z/'qa/block2x2-r09r10c06c07-v2-trace.json'))
p=z/'qa/pair-r10r11c06-current-v4.manifest.json';assert not p.exists();prod.write(p,m)
subprocess.run([sys.executable,'-B',str(z/'qa/native-pair-compose.py'),'--manifest',str(p)],check=True)
m=read(z/'qa/pair-r10r11c06-final-v3.manifest.json');m['outputPrefix']='pair-r10r11c06-final-v5';m['basePairTrace']=ref(z/'qa/pair-r10r11c06-current-v4-trace.json')
r=m['repairs'][0];r['clipPolygon']=[[365,65],[510,65],[545,155],[610,185],[710,230],[795,320],[845,460],[885,610],[910,780],[885,900],[840,995],[750,1040],[640,1065],[630,1130],[360,1130],[355,1070],[280,1030],[230,965],[195,855],[190,690],[210,510],[240,360],[300,245],[360,185]]
r['note']='Final adoption follows full lantern silhouette, excludes the wooden post and exposed rear rail; preserves latest c06/c07 block source.'
p=z/'qa/pair-r10r11c06-final-v5.manifest.json';assert not p.exists();prod.write(p,m)
subprocess.run([sys.executable,'-B',str(z/'qa/native-pair-multi-repair-compose.py'),'--manifest',str(p)],check=True)

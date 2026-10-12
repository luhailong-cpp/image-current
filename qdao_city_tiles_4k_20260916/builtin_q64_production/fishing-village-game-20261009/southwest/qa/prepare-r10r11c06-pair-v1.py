import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
m={'outputPrefix':'pair-r10r11c06-v1','inputs':[{'tile':'r10_c06','context':ref(z/'qa/block2x2-r09r10c05c06-v1-r10_c06-context-native.png')},{'tile':'r11_c06','context':ref(z/'qa/repair-r11_c06-internal-v2-context-native.png')}],'provenance':[ref(z/'qa/block2x2-r09r10c05c06-v1-trace.json'),ref(z/'qa/repair-r11_c06-internal-v2-trace.json'),ref(z/'qa/r11_c06-internal-visual-audit-v2.json')]}
p=z/'qa/pair-r10r11c06-v1.manifest.json';assert not p.exists();prod.write(p,m)
subprocess.run([sys.executable,'-B',str(z/'qa/native-pair-compose.py'),'--manifest',str(p)],check=True)

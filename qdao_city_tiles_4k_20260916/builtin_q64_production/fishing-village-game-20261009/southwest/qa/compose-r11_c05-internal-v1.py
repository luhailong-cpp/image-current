import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
a=read(z/'qa/full-tile-r11_c05-assembly.json')
m={'schemaVersion':1,'outputPrefix':'repair-r11_c05-internal-v1','baseAssembly':ref(z/'qa/full-tile-r11_c05-assembly.json'),'expectedBaseCandidateSha256':a['output']['sha256'],'repairs':[{'id':'cylinder-foot','tileContextBox':[1390,1580,2644,2834],'contextBox':[1505,1695,2759,2949],'repairBounds':[360,350,760,780],'margin':60,'source':ref(z/'qa/r11_c05-cylinder-foot-repair-v1-source-native.png'),'repair':ref(z/'native/r11_c05_cylinder_foot_repair_v1.png'),'generationRecord':ref(z/'native/r11_c05_cylinder_foot_repair_v1.png.generation.json')}]}
p=z/'qa/repair-r11_c05-internal-v1.manifest.json';assert not p.exists();prod.write(p,m)
subprocess.run([sys.executable,'-B',str(z/'qa/repair-compose.py'),'--manifest',str(p)],check=True)
p=z/'qa/repair-r11_c05-internal-v1-cylinder-foot-after-100pct.png'
assert not p.exists();Image.open(z/'qa/repair-r11_c05-internal-v1-context-native.png').crop((1505,1695,2759,2949)).save(p)
progress=read(z/'progress.json');progress['status']='art_production_in_progress';progress['currentTile']='r11_c05';progress['currentPatch']='internal-localrepair';progress['nextStep']='Verify repaired cylinder native crop, then north/east four-tile join; continue r11c04.'
for e in progress.get('errors',[]):
 if e.get('status')=='current_network_permission_denied':e['status']='observed_agent_error_root_builtin_now_succeeded';e['rootRecoveryEvidence']=ref(z/'native/r11_c05_cylinder_foot_repair_v1.receipt.json')
prod.write(z/'progress.json',progress)


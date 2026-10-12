import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
m=read(z/'qa/repair-r11_c06-internal-v1-manifest-v2.json');m['outputPrefix']='repair-r11_c06-internal-v2'
for r in m['repairs']:
 if r['id']=='d':r['repairBounds']=[450,15,870,1239];r['margin']=70
p=z/'qa/repair-r11_c06-internal-v2.manifest.json';assert not p.exists();prod.write(p,m)
subprocess.run([sys.executable,'-B',str(z/'qa/repair-compose.py'),'--manifest',str(p)],check=True)
c=Image.open(z/'qa/repair-r11_c06-internal-v2-context-native.png');b=[2165,565,3419,1819];q=z/'qa/repair-r11_c06-internal-v2-D-result-native.png';assert not q.exists();c.crop(b).save(q)
print(q.as_posix())

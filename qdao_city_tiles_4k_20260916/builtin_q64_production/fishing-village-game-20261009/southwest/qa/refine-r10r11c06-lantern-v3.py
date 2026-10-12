import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
p=z/'qa/pair-r10r11c06-final-v2.manifest.json';m=json.loads(p.read_text(encoding='utf-8-sig'));m['outputPrefix']='pair-r10r11c06-final-v3'
r=m['repairs'][0];r['clipPolygon']=[[190,90],[840,90],[840,480],[885,680],[900,850],[875,960],[820,1035],[670,1080],[650,1160],[340,1160],[340,1080],[250,1030],[205,920],[195,700]]
r['note']='Retain the coherent original wooden post after full native review; repair only lantern and natural silhouette to avoid a new post endpoint band.'
p=z/'qa/pair-r10r11c06-final-v3.manifest.json';assert not p.exists();prod.write(p,m)
subprocess.run([sys.executable,'-B',str(z/'qa/native-pair-multi-repair-compose.py'),'--manifest',str(p)],check=True)

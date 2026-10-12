import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parents[1];source=Z/'qa/repair-r09_c06-dfinal-v2-context-native.png';im=Image.open(source)
items=[('post',[2460,2520,3714,3774]),('floor',[2600,2840,3854,4094]),('floor-target',[2830,3360,3530,4060])]
records=[]
for name,box in items:
 p=Z/'qa'/('repair-r09_c06-dfinal-v2-'+name+'-after-100pct.png');assert not p.exists();im.crop(tuple(v+115 for v in box)).save(p);records.append({'file':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tileBox':box,'operation':'exact native crop only'})
p=Z/'qa/repair-r09_c06-dfinal-v2-after-crops.json';assert not p.exists();p.write_text(json.dumps({'source':source.as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'crops':records},indent=2)+'\n',encoding='utf-8')
print(json.dumps(records))

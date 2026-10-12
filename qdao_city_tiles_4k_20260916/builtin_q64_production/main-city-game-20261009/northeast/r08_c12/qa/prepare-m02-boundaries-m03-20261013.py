from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12');q=p/'qa/repair-resume-20261013';src=p/'candidates/r08_c12.m02-south-v1.png';im=Image.open(src).convert('RGB')
boxes={'m02-north-left':[1380,0,1620,1000],'m02-north-right':[1790,0,2030,1000],'m02-south-left':[1130,1000,1370,2254],'m02-south-right':[2384,1000,2624,2254],'m02-south-top':[1250,880,2504,1120],'m02-south-bottom':[1250,2134,2504,2374],'m03-context-lines-target-v1':[1933,1933,3187,3187]}
for n,b in boxes.items():
 o=q/(n+'.png');assert not o.exists();im.crop(b).save(o)
(q/'qa-and-m03-crop-evidence.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'boxes':boxes,'operation':'integer native crop, no pixel resizing or editing'},indent=2),encoding='utf-8')

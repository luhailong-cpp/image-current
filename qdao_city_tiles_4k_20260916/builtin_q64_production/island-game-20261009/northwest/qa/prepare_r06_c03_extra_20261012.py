from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1]
B=Z/'tiles/r06_c03_candidate-v1_4096.png'
D=Z/'qa/r06_c03_v1_extra_20261012';D.mkdir(exist_ok=False)
boxes={'whole_stone_pillar_and_courses':[2842,600,4096,1854],'whole_roof_curl_and_boundary':[1250,1950,2504,3204],'paving_material_transition':[1450,0,2704,1254],'last_roof_edge_join':[2450,2842,3704,4096]}
im=Image.open(B);out=[]
for n,b in boxes.items():
 p=D/(n+'.png');im.crop(b).save(p);out.append({'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cropBox':b,'nativeScale100Percent':True,'resized':False})
(D/'index.json').write_text(json.dumps({'base':{'path':B.as_posix(),'sha256':hashlib.sha256(B.read_bytes()).hexdigest()},'operation':'exact native coordinate crops only','crops':out},indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))

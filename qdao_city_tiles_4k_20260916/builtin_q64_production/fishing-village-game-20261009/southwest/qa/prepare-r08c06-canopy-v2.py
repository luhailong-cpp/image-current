import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for rid,x in [('c_canopyleft',1520),('d_canopyright',2544)]:
 s='r08_c06_repair_'+rid
 j=json.loads((Z/'native'/(s+'_v1.request.json')).read_text(encoding='utf-8'))
 b=[x,1300,x+1254,2554];cb=[v+115 for v in b]
 src=Z/'qa'/('repair-r08_c06-'+rid+'-v2-source-1254.png')
 Image.open(Z/'qa/full-tile-r08_c06-context-native.png').crop(cb).save(src)
 p=(Z/'native'/(s+'_v1.prompt.txt')).read_text(encoding='utf-8').replace('particularly a 100px outer border','particularly the outer border except the broken blue surface at the overlap edge')
 pp=Z/'native'/(s+'_v2.prompt.txt');pp.write_text(p,encoding='utf-8')
 j.update(stem=s+'_v2',prompt=pp.as_posix())
 j['coordinates']['tileContextBox']=b;j['coordinates']['contextBox']=cb
 j['references']=[{'path':src.as_posix(),'sha256':sha(src),'dimensions':[1254,1254],'role':'exact native edit target'}]
 j['submittedParameters']['referenced_image_paths']=[src.as_posix()]
 (Z/'native'/(s+'_v2.request.json')).write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')


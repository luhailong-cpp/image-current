import json,hashlib
from pathlib import Path
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest");q=z/'qa'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m=json.loads((q/'repair-r09_c06-salvage-v2.manifest.json').read_text(encoding='utf-8-sig'))
m['outputPrefix']='repair-r09_c06-objects-v3'
source=q/'repair-r09_c06-a-complete-upper-posts-source-native-v3.png'
native=z/'native/r09_c06_repair_a_complete_posts_v3.png'
for name,bounds,margin in [('a-entire-red-post',[340,20,570,1254],25),('a-entire-rear-post',[620,840,795,1230],20)]:
 m['repairs'].append({'id':name,'tileContextBox':[260,-40,1514,1214],'contextBox':[375,75,1629,1329],'repairBounds':bounds,'margin':margin,'source':ref(source),'repair':ref(native),'generationRecord':ref(Path(str(native)+'.generation.json'))})
m['notes']='Six visually checked salvage subregions plus two naturally terminated upper posts. Central complete post integrated next via its separate native long-object source map.'
(q/'repair-r09_c06-objects-v3.manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


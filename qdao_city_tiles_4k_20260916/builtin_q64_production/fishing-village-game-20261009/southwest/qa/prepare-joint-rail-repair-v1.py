import json,hashlib
from pathlib import Path
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest")
p=z/'qa/joint-r09c04-c05-repair-v1.manifest.draft.json'
m=json.loads(p.read_text(encoding='utf-8-sig'))
m.pop('draftStatus',None)
m['outputPrefix']='joint-r09c04-c05-repair-v1'
art=z/'native/r09_c04_c05_repair_rail_v1.png'
rec=Path(str(art)+'.generation.json')
for k,f in [('repair',art),('generationRecord',rec)]:
 m['repairs'][0][k]={'path':f.as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(z/'qa/joint-r09c04-c05-repair-v1.manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


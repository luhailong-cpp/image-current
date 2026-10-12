import json
from pathlib import Path
from datetime import datetime,timezone
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
p=z/'records/r06_c14.local-continuation-20261011.json'
d=json.loads(p.read_text(encoding='utf-8'))
n=z/'native/r06_c14_p11-v1.png'
r=json.loads(Path(str(n)+'.generation.json').read_text(encoding='utf-8'))
d.update({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'resumedBuiltinRequest':'success','firstSuccessfulNative':{'path':str(n),'sha256':r['sha256'],'nativeSize':r['nativeSize'],'source':r['source'],'receipt':r['receipt'],'references':r['references']},'actualNewNativeCount':1,'missingCoordinates':[x for x in d['missingCoordinates'] if x!='r06_c14_p11']})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(p))


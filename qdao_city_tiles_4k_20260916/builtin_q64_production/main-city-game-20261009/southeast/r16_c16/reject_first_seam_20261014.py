from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent
p=T/'active-native-map.json';m=json.loads(p.read_text());v=m['p01_01']
assert v=='p01_01_v20261014T000935_8a825786'
native=T/'native'/f'{v}.png'
r={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':'p01_01','version':v,'native':str(native),'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'status':'not_adopted_geometry_failed','issue':'New horizontal grout at y~128 cuts off all upward-right diagonal joints in north native anchor; direction reset at anchor boundary. Original retained; no child anchors prepared.','formalAccepted':False}
with (T/'records'/f'{v}.quick-qa.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
del m['p01_01'];p.write_text(json.dumps(m,indent=2),encoding='utf-8')
q=T/'local-content.json';d=json.loads(q.read_text())
d['p01_01']+=' CRITICAL JOIN GEOMETRY: the LEFT main stone wall face has long grout lines rising steeply toward the right (about 45 degrees), exactly visible in TOP native115 band. Extend every one of these diagonal joints smoothly DOWN AND LEFT from its endpoint at y115; keep the same grid orientation over the full main wall face. Do not reset them to horizontal courses. In particular DO NOT draw any horizontal joint across the whole image at y115, y128, y230 or anywhere just below the top reference band. TOP is seamless art continuing into this crop, not a separate row of decorative stones or coping. Preserve the main inside corner at x~950 from TOP; its right wall has its own consistent perspective plane. Large slabs, no new structure.'
q.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(r))

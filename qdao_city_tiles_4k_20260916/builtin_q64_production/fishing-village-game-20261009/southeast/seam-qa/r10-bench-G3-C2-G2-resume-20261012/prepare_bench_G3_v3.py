from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent
source=D/'bench-G3-left-conditioned-v2-bounded-preview-native1254.png'
im=Image.open(source).convert('RGBA');box=[620,380,850,920];im.paste((255,255,255,0),box)
p=D/'bench-G3-left-conditioned-v3-right-clear-hole-guide-native1254.png';assert not p.exists();im.save(p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(source),'sourceSha256':sha(source),
 'guide':str(p),'guideSha256':sha(p),'localGuideBox':box,'localWorldBox':[31170,40580,31400,41120],
 'operation':'Native clear guide hole only; no generated art drawn mechanically.','resampling':False,'canonicalModified':False}
(D/'bench-G3-left-conditioned-v3-guide-provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')

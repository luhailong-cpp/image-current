from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach');q=b/'r05_c10/qa'
names=['vertical-x3072-y3072.png','horizontal-y3072-x2048.png','horizontal-y3072-x3072.png']
items=[{'file':str(q/n),'sha256':hashlib.sha256((q/n).read_bytes()).hexdigest(),'status':'PASS','nativeScaleViewed':True} for n in names]
(b/'extension-20261011/root-c10-bottom-review.json').write_text(json.dumps({'reviewedAt':datetime.now(timezone.utc).isoformat(),'items':items,'finding':'Lantern metal foot, knot, tassel, dark timber, sand and paving geometry continue. No blocking issue in these three cuts.','formalAccepted':False},indent=2)+'\n',encoding='utf-8')


from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
def ref(p):return {'path':str(p).replace(chr(92),'/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
sel=json.loads((z/'records/r06_c14.selection-proposed-v1.json').read_text(encoding='utf-8'))
co=json.loads((z/'records/r06_c14.coordinates.json').read_text(encoding='utf-8'))
d={'tile':'r06_c14','createdAtUtc':datetime.now(timezone.utc).isoformat(),'origin':[53248,20480],'corePixels':[4096,4096],'actualGeneratedNativeCount':18,'selectedCoreCount':16,'candidate':ref(z/'tiles/r06_c14.candidate-v1.png'),'selection':ref(z/'records/r06_c14.selection-proposed-v1.json'),'coordinateRecord':ref(z/'records/r06_c14.coordinates.json'),'selectedSources':sel['patches'],'coordinates':co['patches'],'qaManifest':ref(z/'qa/r06_c14-v1/manifest.json'),'selfReview':ref(z/'qa/r06_c14-v1/r06_c14-self-review.json'),'validation':ref(z/'qa/r06_c14-v1/r06_c14-provenance-validation.json'),'formalAccepted':False,'status':'internal_self_review_passed_root_independent_review_pending','actualModel':None,'actualQuality':None,'progressModified':False}
(z/'records/r06_c14.handoff-v1.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=z/'records/r06_c14.local-continuation-20261011.json';x=json.loads(p.read_text(encoding='utf-8'));x['status']=d['status'];x['handoff']=ref(z/'records/r06_c14.handoff-v1.json');p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(z/'records/r06_c14.handoff-v1.json'))


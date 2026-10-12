from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/r08_c09')
d=json.loads((T/'p34-v2.request.json').read_text())
n=str(T/'native/p33-v1.png')
d['referenced_image_paths'].append(n)
d['referenceRoles']['5']='Actual left neighbor native detail and paving scale only; do not copy pedestal'
d['referenceEvidence'].append(dict(path=n,sha256=hashlib.sha256(Path(n).read_bytes()).hexdigest(),role=d['referenceRoles']['5']))
(T/'p34-v2.request.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
(T/'p34-v1-rejection.json').write_text(json.dumps(dict(status='rejected_layout_wrong',selected=False,source='raw/p34-v1-builtin.png',reason='Invented circular fish-relief plaza and steps from independent material reference; intended target is only empty flat paving.'),indent=2),encoding='utf-8')


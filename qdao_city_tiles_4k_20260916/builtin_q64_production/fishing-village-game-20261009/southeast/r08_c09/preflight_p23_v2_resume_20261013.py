from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/r08_c09')
d=json.loads((T/'p23-v2.request.json').read_text());n=str(T/'native/p33-v1.png')
d['referenced_image_paths'].append(n);d['referenceRoles']['5']='Actual patch immediately BELOW; only its topmost CORE strip is shown at bottom115 of target, do not fit its whole base here'
d['referenceEvidence'].append(dict(path=n,sha256=hashlib.sha256(Path(n).read_bytes()).hexdigest(),role=d['referenceRoles']['5']))
(T/'p23-v2.request.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
(T/'p23-v1-rejection.json').write_text(json.dumps(dict(status='rejected_geometry',selected=False,source='raw/p23-v1-builtin.png',reason='Pedestal ground contact lifted into target; lower contour does not continue to the exact native p33 base, would duplicate complete pedestal.'),indent=2),encoding='utf-8')


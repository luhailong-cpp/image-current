from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/r08_c09')
d=json.loads((T/'p24-v1.request.json').read_text());n=str(T/'native/p34-v2.png')
d['referenced_image_paths'].append(n);d['referenceRoles']['5']='Actual lower neighbor material and scale only'
d['referenceEvidence'].append(dict(path=n,sha256=hashlib.sha256(Path(n).read_bytes()).hexdigest(),role=d['referenceRoles']['5']))
(T/'p24-v1.request.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
(T/'p23-v2-rejection.json').write_text(json.dumps(dict(status='rejected_geometry_deferred',selected=False,source='raw/p23-v2-builtin.png',reason='Ground contact still lifted and round collar is too high versus lower fixed core; keep best candidate but do independent patches after second attempt.'),indent=2),encoding='utf-8')


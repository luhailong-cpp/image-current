from pathlib import Path
import json,hashlib
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
d={'schemaVersion':1,'tile':'r06_c14','status':'candidate_self_review_pending','patches':{}}
for r in range(1,5):
 for c in range(1,5):
  p=f'r06_c14_p{r}{c}';v='v3' if p.endswith('34') else 'v1';f=z/'native'/f'{p}-{v}.png';d['patches'][p]={'path':str(f).replace(chr(92),'/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
out=z/'records/r06_c14.selection-proposed-v1.json';assert not out.exists();out.write_text(json.dumps(d,indent=2),encoding='utf-8');print(str(out))


from pathlib import Path
import json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/r08_c09');p=T/'p31-v4.request.json';d=json.loads(p.read_text());d['referenced_image_paths'][0]=str(T/'layout-only/p31-true-core-conditioned-resume-20261013-v4.png');p.write_text(json.dumps(d,indent=2),encoding='utf-8')


from pathlib import Path
import json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/r08_c09')
p=T/'p33-v1.request.json'
d=json.loads(p.read_text())
d['prompt']=d['prompt'].replace('Open empty gray-blue stone paving only. Keep selected lower and left native slab grout positions and diagonal directions exact. Use broad cool daylight painterly slabs. No new props, foliage or objects.','The EXISTING partial dark wooden lantern-post pedestal occupies upper center and is cut off by top edge exactly as in the target. Preserve its sole footprint and contour, do not remove it or add another. Rest is open natural gray-blue stone paving. Keep selected lower and left native slab grout endpoints exact. Render the post base and stone only at supplied positions.')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
(T/'p33-v1.prompt.txt').write_text(d['prompt'],encoding='utf-8')


from pathlib import Path
from PIL import Image
import json,re
roots=[Path(r'E:\work\image'),Path(r'E:\work\output\imagegen'),Path(r'E:\work\mmorpg-client\Assets\Art')]
exclude=r'(character|roster|pets|sprite|walk|run|idle|frames|strip|attack|direction|portrait|cutout|transparen|alpha|mask|ui_|ui/|/ui/|headband|recut|slices|/tiles/|refined|guides|gait|contact|qdao_festival_refinement|style-repair|style-audit|/review/|/qa/|/icons/|/originals/|/mattes/|/processing/|/catalog/|/temp/|/tmp/)'
rows=[]
for root in roots:
 for p in root.rglob('*'):
  if p.suffix.lower() not in ['.png','.jpg','.webp'] or re.search(exclude,p.as_posix(),re.I): continue
  try:
   with Image.open(p) as im: w,h=im.size
  except Exception: continue
  if min(w,h)>=1000 and .75<=w/h<=1.5: rows.append({'path':str(p),'width':w,'height':h})
Path(r'E:\work\image\qdao_large_city_maps_20260912\catalog\dimension-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))

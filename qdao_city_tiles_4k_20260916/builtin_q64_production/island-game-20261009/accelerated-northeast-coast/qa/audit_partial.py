from pathlib import Path
from PIL import Image
import json,hashlib,re
from datetime import datetime,timezone
z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast');q=z/'qa'
selected={}
for r in range(1,5):
 for c in range(1,5):
  choices=list((z/'native').glob(f'r02_c13_p{r:02}_{c:02}*.png'))
  choices.sort(key=lambda p: int(re.search(r'_v(\d+)\.png$',p.name).group(1)) if re.search(r'_v(\d+)\.png$',p.name) else 1)
  if choices:selected[(r,c)]=choices[-1]
refs=[]
for (r,c),a in selected.items():
 if r==4:continue
 imA=Image.open(a).convert('RGB');assert imA.size==(1254,1254)
 for side,key in [('south',(r+1,c)),('east',(r,c+1))]:
  if key not in selected:continue
  b=selected[key];imB=Image.open(b).convert('RGB');assert imB.size==(1254,1254)
  if side=='south':
   j=Image.new('RGB',(1024,512));j.paste(imA.crop((115,883,1139,1139)),(0,0));j.paste(imB.crop((115,115,1139,371)),(0,256))
  else:
   j=Image.new('RGB',(512,1024));j.paste(imA.crop((883,115,1139,1139)),(0,0));j.paste(imB.crop((115,115,371,1139)),(256,0))
  out=q/f'audit-{a.stem}__{b.stem}-{side}-100pct.png';j.save(out) if not out.exists() else None
  refs.append({'a':a.as_posix(),'aSha256':hashlib.sha256(a.read_bytes()).hexdigest(),'b':b.as_posix(),'bSha256':hashlib.sha256(b.read_bytes()).hexdigest(),'side':side,'evidence':out.as_posix()})
(q/'audit-new-rows-sources.json').write_text(json.dumps({'generatedAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'unscaled native core seam strips;512px total width across seam','seams':refs},indent=2),encoding='utf-8')
print(json.dumps(refs))

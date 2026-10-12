from pathlib import Path
from PIL import Image
import json, hashlib, re
from datetime import datetime,timezone
z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast');q=z/'qa';q.mkdir(exist_ok=True)
south=z.parent/'northeast/native'
selected=[]
for r in range(1,5):
 line=[]
 for c in range(1,5):
  choices=list((z/'native').glob(f'r02_c13_p{r:02}_{c:02}*.png'))
  choices.sort(key=lambda p: int(re.search(r'_v(\d+)\.png$',p.name).group(1)) if re.search(r'_v(\d+)\.png$',p.name) else 1)
  line.append(choices[-1] if choices else None)
 selected.append(line)
sources=[]; outputs=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for r,line in enumerate(selected):
 if not all(line):continue
 ims=[Image.open(p).convert('RGB') for p in line]
 assert all(im.size==(1254,1254) for im in ims)
 for p in line:sources.append({'file':p.as_posix(),'sha256':sha(p)})
 native=Image.new('RGB',(4096,1024))
 for c,im in enumerate(ims): native.paste(im.crop((115,115,1139,1139)),(c*1024,0))
 p=q/f'audit-row{r+1}-native.png';native.save(p);outputs.append(p.as_posix())
 for c in range(1,4):
  p=q/f'audit-row{r+1}-internal-{c}-{c+1}-100pct.png';native.crop((c*1024-256,0,c*1024+256,1024)).save(p);outputs.append(p.as_posix())
 lower=selected[r+1] if r<3 else [south/f'r03_c13_p01_{c:02}.png' for c in range(1,5)]
 if all(lower):
  for c,(im,b) in enumerate(zip(ims,lower)):
   bot=Image.open(b).convert('RGB');j=Image.new('RGB',(1024,512));j.paste(im.crop((115,883,1139,1139)),(0,0));j.paste(bot.crop((115,115,1139,371)),(0,256))
   p=q/f'audit-row{r+1}-south-{c+1}-100pct.png';j.save(p);outputs.append(p.as_posix());sources.append({'file':b.as_posix(),'sha256':sha(b)})
(q/'audit-selected-sources.json').write_text(json.dumps({'generatedAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'unscaled native core crops and adjacent core seam strips only','sources':sources,'outputs':outputs,'selected':[[p.name if p else None for p in line] for line in selected]},indent=2),encoding='utf-8')
print(json.dumps({'selected':[[p.name if p else None for p in line] for line in selected],'outputs':outputs}))

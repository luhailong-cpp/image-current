from pathlib import Path
from PIL import Image
import json
R=Path(r'D:/work/image/designs/creature-combat-20261005/pets/02-jiangling')
rows=[]
for a,n in [('hit',6),('attack',12)]:
 for i in range(1,n+1):
  p=R/'runtime'/a/'W'/f'{i:02}.png'; im=Image.open(p); al=im.getchannel('A')
  counts={}; boxes={}
  for t in [1,8,16,64,128]:
   m=al.point(lambda v:255 if v>=t else 0)
   boxes[str(t)]=m.getbbox()
   counts[str(t)]=sum(1 for x in range(1024) if al.getpixel((x,0))>=t)+sum(1 for x in range(1024) if al.getpixel((x,1023))>=t)+sum(1 for y in range(1,1023) if al.getpixel((0,y))>=t)+sum(1 for y in range(1,1023) if al.getpixel((1023,y))>=t)
  rows.append({'file':p.relative_to(R).as_posix(),'thresholdBoxes':boxes,'edgePixelCounts':counts})
(R/'qa'/'W-edge-check.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([x for x in rows if x['edgePixelCounts']['1']],ensure_ascii=False))


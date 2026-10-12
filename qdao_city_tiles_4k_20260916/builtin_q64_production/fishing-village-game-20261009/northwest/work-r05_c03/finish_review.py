from pathlib import Path
from PIL import Image
import json,hashlib
W=Path(__file__).resolve().parent;B=W.parent;F=W/'final-v1';im=Image.open(F/'r05_c03.candidate.png')
for y in range(4):
 for x in range(4):im.crop((x*1024,y*1024,(x+1)*1024,(y+1)*1024)).save(F/f'qa/core-{y+1}-{x+1}.100pct.png')
for name,box in [('net-corner',[9580,16750,10834,18004]),('cream-edge',[9000,18000,10254,19254])]:im.crop(tuple(v-([8192,16384][i%2]) for i,v in enumerate(box))).save(F/f'qa/{name}-whole-after.100pct.png')
n=Image.open(B/'delivery-2x2/stage-v3/r04_c03.png');band=Image.new('RGB',(4096,600));band.paste(n.crop((0,3796,4096,4096)),(0,0));band.paste(im.crop((0,0,4096,300)),(0,300));band.save(F/'qa/north-whole.100pct.png')
for j in range(4):band.crop((j*1024,0,(j+1)*1024,600)).save(F/f'qa/north-{j+1}.100pct.png')
print('Native review crops saved')

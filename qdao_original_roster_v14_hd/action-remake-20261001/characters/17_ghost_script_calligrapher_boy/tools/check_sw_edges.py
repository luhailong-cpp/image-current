from pathlib import Path
from PIL import Image
import json
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy');rows=[]
for p in sorted((B/'staging').glob('run-SW-*.png')):
 a=Image.open(p).getchannel('A');w,h=a.size
 edge={name:sum(v>128 for v in a.crop(box).getdata()) for name,box in [('left',(0,0,1,h)),('right',(w-1,0,w,h)),('top',(0,0,w,1)),('bottom',(0,h-1,w,h))]}
 if any(edge.values()):rows.append({'file':p.name,'edgeOpaquePixels':edge})
(B/'review/reference09-SW/edge-diagnostic.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows))


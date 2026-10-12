from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
data={}
for d in ['E','W']:
 s=json.loads((R/f'review/run-{d}-selection.json').read_text(encoding='utf-8-sig'))
 data[d]=s
 for size in [128,256]:
  ims=[Image.open(R/f'candidate/run/{d}/{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.LANCZOS) for i in range(1,17)]
  ims[0].save(R/f'preview/run-{d}-paired-1x-{size}.webp',save_all=True,append_images=ims[1:],duration=[75]*16,loop=0,lossless=True)
(R/'review/run-EW-position-data.js').write_text('window.EW_DATA='+json.dumps(data,ensure_ascii=False)+';\n',encoding='utf-8')
print('E/W player data and 4 complete 1x WebP files refreshed')


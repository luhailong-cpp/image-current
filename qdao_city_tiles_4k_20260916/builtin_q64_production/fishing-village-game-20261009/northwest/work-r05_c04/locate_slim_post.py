from pathlib import Path
from PIL import Image
import json
W=Path(__file__).resolve().parent;B=W.parent
c=json.loads((B.parent/'production-contract.json').read_text(encoding='utf-8-sig'));ref=Image.open(c['layoutReference'])
for y in [15000,15600,16269]:
 box=[15245,y,16499,y+1254];ref.transform((1254,1254),Image.Transform.EXTENT,tuple(z*1254/57344 for z in box),resample=Image.Resampling.BICUBIC).save(W/f'guides/slim-post-layout-{y}.png')


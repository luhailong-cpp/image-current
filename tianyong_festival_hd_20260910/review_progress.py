from pathlib import Path
import json, sys, importlib.util
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root))
import seam_helpers as seam
records=[]
thumb=192
sheet=Image.new('RGB',(thumb*6,thumb*6),(35,40,40))
for r in range(1,7):
 for c in range(1,7):
  name=f'city_r{r:02d}_c{c:02d}.png'
  guide=Image.open(root/'guides'/name).convert('RGB')
  p=root/'refined'/name
  if p.exists():
   try:
    raw=Image.open(p).convert('RGB'); raw.load()
   except OSError:
    continue
   a=np.asarray(raw.resize((1254,1254)).filter(ImageFilter.GaussianBlur(12)),dtype=np.float32)
   b=np.asarray(guide.filter(ImageFilter.GaussianBlur(12)),dtype=np.float32)
   records.append({'name':name,'nativeSize':list(raw.size),'layoutLowFrequencyRms':round(float(np.sqrt(np.mean((a-b)**2))),2)})
   im=raw.crop((115,115,1139,1139)).resize((thumb,thumb),Image.Resampling.LANCZOS)
  else:
   im=guide.crop((115,115,1139,1139)).resize((thumb,thumb),Image.Resampling.LANCZOS).point(lambda x:int(x*.3))
  sheet.paste(im,((c-1)*thumb,(r-1)*thumb))
qa=root/'qa';qa.mkdir(exist_ok=True)
sheet.save(qa/'progress-contact.jpg',quality=85)
(qa/'progress.json').write_text(json.dumps({'completed':len(records),'total':36,'note':'RMS is a layout drift screening measure, not a pass/fail image-quality score. Dark cells are unfinished guide placeholders only.','patches':sorted(records,key=lambda v:v['layoutLowFrequencyRms'],reverse=True)},indent=2),encoding='utf-8')
print(json.dumps({'completed':len(records),'total':36,'highestLayoutDrift':sorted(records,key=lambda v:v['layoutLowFrequencyRms'],reverse=True)[:5]}))

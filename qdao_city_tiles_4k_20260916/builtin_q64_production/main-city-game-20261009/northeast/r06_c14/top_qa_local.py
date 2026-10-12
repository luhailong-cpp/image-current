from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
Q=T/'qa'/'top-half';Q.mkdir(parents=True,exist_ok=True)
out=Image.new('RGB',(4096,2048))
sources=[]
for r in (1,2):
 for c in range(1,5):
  p=T/'native'/f'p{r}{c}.png'
  im=Image.open(p).convert('RGB')
  out.paste(im.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
  sources.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out.save(Q/'top-half.png')
for r in (1,2):
 montage=Image.new('RGB',(1152,1024))
 for c in range(1,4):
  crop=out.crop((c*1024-192,(r-1)*1024,c*1024+192,r*1024))
  crop.save(Q/f'v-{r}-{c}.png');montage.paste(crop,((c-1)*384,0))
 montage.save(Q/f'v-row{r}-100pct.png')
north=Image.open(T.parent/'r05_c14'/'candidates'/'r05_c14.candidate.png').convert('RGB')
for c in range(1,5):
 crop=out.crop(((c-1)*1024,832,c*1024,1216));crop.save(Q/f'h-{c}-100pct.png')
 ext=Image.new('RGB',(1024,384));ext.paste(north.crop(((c-1)*1024,3904,c*1024,4096)),(0,0));ext.paste(out.crop(((c-1)*1024,0,c*1024,192)),(0,192));ext.save(Q/f'north-{c}-100pct.png')
 forr=0
(Q/'manifest.json').write_text(json.dumps({'selectedNative':sources,'dimensions':[4096,2048],'resized':False},indent=2),encoding='utf-8')


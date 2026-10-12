from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach');d=b/'r05_c11/repairs/ground-halo-v1';d.mkdir(parents=True,exist_ok=True)
canvas=Image.new('RGBA',(4096,4096))
sources=[]
for r in range(1,5):
 for c in range(1,5):
  sp=b/'r05_c11/records'/f'p{r}{c}.selection.json'
  if sp.exists():
   s=json.loads(sp.read_text(encoding='utf-8-sig'));p=Path(s['file']);canvas.paste(Image.open(p).convert('RGBA').crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024));sources.append({'core':f'p{r}{c}','file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
box=[1305,1900,2559,3154];im=canvas.crop(box);assert im.size==(1254,1254) and im.getchannel('A').getextrema()==(255,255)
p=d/'target-native.png';im.convert('RGB').save(p)
(d/'target-derivation.json').write_text(json.dumps({'tile':'r05_c11','tileLocalBox':box,'globalPixelBox':[40960+box[0],16384+box[1],40960+box[2],16384+box[3]],'sources':sources,'operation':'Unscaled native selected core assembly and crop','nativePixelsResized':False,'targetSha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
print(str(p))


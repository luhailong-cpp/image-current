from pathlib import Path
from PIL import Image
import json,hashlib
O=Path(__file__).resolve().parent
I=json.loads((O/'inventory.json').read_text(encoding='utf-8'))
T={t['tileId']:t for t in I['tiles']}
a,b='r08_c04','r09_c04'
im=Image.new('RGB',(2048,1024));boxes=[]
with Image.open(T[a]['file']) as ia,Image.open(T[b]['file']) as ib:
 for j in range(4):
  part=Image.new('RGB',(1024,512));part.paste(ia.crop((j*1024,3840,(j+1)*1024,4096)),(0,0));part.paste(ib.crop((j*1024,0,(j+1)*1024,256)),(0,256));x=(j%2)*1024;y=(j//2)*512;im.paste(part,(x,y));boxes.append({'upperTileCrop':[j*1024,3840,(j+1)*1024,4096],'lowerTileCrop':[j*1024,0,(j+1)*1024,256],'montageBox':[x,y,x+1024,y+512]})
p=O/'seams-100pct/r08_c04-r09_c04-horizontal-native100-v01.png';im.save(p)
m=json.loads((O/'assembly-review-manifest.json').read_text(encoding='utf-8'));m['seams'].append({'file':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':[2048,1024],'pair':[a,b],'axis':'horizontal','scale':'1:1 exact pixels; unscaled montage','panels':boxes,'inputHashes':{a:T[a]['sha256'],b:T[b]['sha256']},'status':'pending_actual_view_image'});(O/'assembly-review-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')

from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy")
pairs=[("cast-W-03-v2","cast-W-03-v3"),("cast-W-04-v2","cast-W-04-v3"),("cast-E-01-v2","cast-E-01-v3"),("cast-W-02-v2","cast-W-02-v3"),("cast-E-10-v3","cast-E-10-v5")]
rows=[]
for key in dict.fromkeys(k for pair in pairs for k in pair):
 p=B/"staging"/(key+".png"); im=Image.open(p); a=np.asarray(im.convert("RGBA")); mask=a[:,:,3]>=128
 y,x=np.where(mask); bb=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
 rows.append(dict(key=key,file=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=list(im.size),mode=im.mode,alphaRange=[int(a[:,:,3].min()),int(a[:,:,3].max())],alpha128BBox=bb,alpha128BBoxRatio=(bb[2]-bb[0])/(bb[3]-bb[1]),visibleRedPixelCount=int(np.sum((a[:,:,3]>16)&(a[:,:,0]>210)&(a[:,:,1]<85)&(a[:,:,2]<85)))))
p=B/"staging"/"cast-E-10-v4.png";im=Image.open(p)
rows.append(dict(key=p.stem,file=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=list(im.size),mode=im.mode))
(B/"review"/"combat-limb-fixes-metadata.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
canvas=Image.new("RGB",(5*280,2*310),(225,225,225));draw=ImageDraw.Draw(canvas)
for col,pair in enumerate(pairs):
 for row,key in enumerate(pair):
  im=Image.open(B/"staging"/(key+".png")).convert("RGBA");im.thumbnail((280,280))
  x=col*280+(280-im.width)//2;y=row*310+24
  canvas.paste(im,(x,y),im)
  draw.text((col*280+5,row*310+5),key+" "+("BEFORE" if row==0 else "AFTER"),fill=(0,0,0))
canvas.save(B/"review"/"combat-limb-fixes-comparison.png")
print(json.dumps(rows,ensure_ascii=False))

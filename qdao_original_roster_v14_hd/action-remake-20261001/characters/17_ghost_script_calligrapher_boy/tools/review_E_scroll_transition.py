from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy")
keys=["run-E-03-v5","run-E-03-v6","run-E-11-v7","run-E-11-v8"]
canvas=Image.new("RGB",(960,264),(220,220,220));d=ImageDraw.Draw(canvas);rows=[]
for i,k in enumerate(keys):
 p=B/"staging"/(k+".png");im=Image.open(p).convert("RGBA");rows.append(dict(key=k,file=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=list(im.size),mode=im.mode))
 im=im.resize((240,240),Image.Resampling.LANCZOS);canvas.paste(im,(i*240,24),im);d.text((i*240+4,4),k,fill=(0,0,0))
canvas.save(B/"review"/"run-E-scroll-transition-240px.png")
print(json.dumps(rows))

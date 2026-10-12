from pathlib import Path
from PIL import Image,ImageDraw
import json
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy");keys=["run-E-02-v2","run-E-03-v6","run-E-04-v3","run-E-10-v4","run-E-11-v8","run-E-12-v8"]
c=Image.new("RGB",(960,688),(215,215,215));d=ImageDraw.Draw(c);rows=[]
for i,k in enumerate(keys):
 p=B/"staging"/(k+".png");im=Image.open(p).convert("RGBA");rows.append(dict(key=k,size=im.size))
 x=i%3*320;y=i//3*344;d.text((x+5,y+5),k,fill=(0,0,0));v=im.resize((320,320),Image.Resampling.LANCZOS);c.paste(v,(x,y+24),v)
c.save(B/"review/E-head-size-independent-contact.png");print(json.dumps(rows))


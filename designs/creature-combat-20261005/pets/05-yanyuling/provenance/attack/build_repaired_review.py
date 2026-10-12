from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
B=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling");out=Image.new("RGB",(1536,2*546),(232,228,215));dr=ImageDraw.Draw(out);F=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",20);sources=[]
for ix,n in enumerate([6,7,8,10,11,12]):
 p=B/"runtime"/"attack"/"E"/f"{n:02d}.png";im=Image.open(p).convert("RGBA").resize((512,512),Image.Resampling.LANCZOS)
 x=(ix%3)*512;y=(ix//3)*546;out.paste(im,(x,y+34),im);dr.text((x+8,y+7),f"E/{n:02d}"+(" repaired" if n in (7,11) else ""),font=F,fill=(20,30,35));sources.append({"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
out.save(B/"provenance"/"attack"/"continuity-repair-06-08-10-12.png")
(B/"provenance"/"attack"/"continuity-repair-06-08-10-12.sources.json").write_text(json.dumps(sources,indent=2),encoding="utf-8")


from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib,json
B=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling");O=B/"provenance"/"attack";F=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",20)
def sheet(files,name,cols,size):
 rows=(len(files)+cols-1)//cols
 out=Image.new("RGB",(cols*size,rows*(size+34)),(232,228,215));dr=ImageDraw.Draw(out)
 sources=[]
 for idx,p in enumerate(files):
  im=Image.open(p).convert("RGBA").resize((size,size),Image.Resampling.LANCZOS);x=(idx%cols)*size;y=(idx//cols)*(size+34)
  out.paste(im,(x,y+34),im);dr.text((x+8,y+7),p.parent.name+"/"+p.stem,font=F,fill=(30,35,40))
  sources.append({"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
 out.save(O/name)
 (O/(name+".sources.json")).write_text(json.dumps(sources,indent=2),encoding="utf-8")
sheet([B/"runtime"/"attack"/"E"/f"{n:02d}.png" for n in range(1,13)],"static-review-E-all.png",4,384)
sheet([B/"runtime"/"attack"/"W"/f"{n:02d}.png" for n in range(1,7)],"static-review-W-first6.png",3,384)
sheet([B/"runtime"/"attack"/"E"/f"{n:02d}.png" for n in (6,7,8)],"static-review-E-06-08.png",3,600)
sheet([B/"runtime"/"attack"/d/"01.png" for d in ("E","W")],"static-review-anchor-first.png",2,1024)


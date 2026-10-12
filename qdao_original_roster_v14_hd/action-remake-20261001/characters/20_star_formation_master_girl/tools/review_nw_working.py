from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
versions={i:(f"{i:02}-v1" if i not in (1,9) else ("01-v3" if i==1 else "01-v2")) for i in range(1,17)}
versions.update({i:f"{i:02}-v2" for i in range(12,17)})
versions.update({15:"15-v3",16:"16-v3"})
frames=[]
contact=Image.new("RGB",(1120,1248),"#e7e4dc");draw=ImageDraw.Draw(contact);font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",18)
for i,v in versions.items():
 p=ROOT/f"generation/run/NW/{v}.png";im=Image.open(p);im.load()
 art=im.resize((280,280),Image.Resampling.LANCZOS);x=(i-1)%4*280;y=(i-1)//4*312;contact.paste(art,(x,y),art);draw.text((x+8,y+280),f"NW{i:02} source {v}",font=font,fill="#25423d")
 frames.append({"action":"run","direction":"NW","frame":i,"source":p.relative_to(ROOT).as_posix(),"generationRecord":p.relative_to(ROOT).as_posix()+".generation.json","sourceSha256":hashlib.sha256(p.read_bytes()).hexdigest(),"status":"candidate_static_review","visualReview":"root_reviewing"})
contact.save(ROOT/"preview/run-NW-working-contact.png")
(ROOT/"provenance/run-NW-working-slots.json").write_text(json.dumps({"frames":frames},ensure_ascii=False,indent=2),encoding="utf-8")
print("NW working contact built")

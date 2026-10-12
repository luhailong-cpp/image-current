"""Build review contact sheets and real-frame APNG from a direction selection."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument("direction");args=a.parse_args();d=args.direction
rows=json.loads((ROOT/f"grounding4/{d}/selected.json").read_text(encoding="utf-8-sig"))
full=Image.new("RGB",(1024,1100),(227,226,219));feet=Image.new("RGB",(1440,1040),(227,226,219))
fd=ImageDraw.Draw(full);gd=ImageDraw.Draw(feet);seq=[]
for row in rows:
 n=row["frame"];p=ROOT/row["exportFile"];im=Image.open(p).convert("RGBA")
 assert im.size==(1024,1024)
 row["sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
 x=((n-1)%4)*256;y=((n-1)//4)*275
 s=im.resize((256,256));full.paste(s,(x,y+19),s);fd.text((x+5,y+3),f"{d}{n:02} {p.name}",fill="black")
 crop=im.crop((0,620,1024,1024)).resize((360,142));x=((n-1)%4)*360;y=((n-1)//4)*260
 feet.paste(crop,(x,y+24),crop);gd.text((x+5,y+4),f"{d}{n:02} {p.name}",fill="black")
 # Reference is visual only, never reposition source.
 gd.line((x,y+24+int((922-620)*142/404),x+360,y+24+int((922-620)*142/404)),fill=(180,180,180))
 seq.append(s)
dest=ROOT/f"grounding4/{d}"
full.save(dest/"selected-contact.jpg",quality=94);feet.save(dest/"selected-feet.jpg",quality=94)
seq[0].save(dest/"selected-normal.png",save_all=True,append_images=seq[1:],duration=75,loop=0,disposal=1,blend=0)
seq[0].save(dest/"selected-slow.png",save_all=True,append_images=seq[1:],duration=300,loop=0,disposal=1,blend=0)
(dest/"selected.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(d,len(rows))


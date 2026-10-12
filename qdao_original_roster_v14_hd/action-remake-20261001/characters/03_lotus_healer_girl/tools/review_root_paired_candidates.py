from pathlib import Path
import json, hashlib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[1]
changes={"NE":{3:"03-paired-v1",4:"04-ground4-v1",5:"05-paired-v1",6:"06-paired-v1",7:"07-paired-v1",8:"08-paired-v1",11:"11-paired-v1",12:"12-paired-v1",13:"13-paired-v2",14:"14-paired-v2",15:"15-paired-v1",16:"16-paired-v2"},"S":{i:f"{i:02d}-paired-v1" for i in (5,6,7,8,13,14,15,16)}}
for d,mapping in changes.items():
 data=json.loads((B/f"review/run-{d}-sequence-input.json").read_text(encoding="utf-8-sig"))
 for fr in data["frames"]:
  n=fr.get("slot",fr.get("frame"))
  if n in mapping:fr["source"]=f"generation/{d}/{mapping[n]}.png"
 out=Image.new("RGB",(1280,1440),(239,239,236));draw=ImageDraw.Draw(out)
 lower=Image.new("RGB",(1600,800),(239,239,236));ld=ImageDraw.Draw(lower)
 for i,fr in enumerate(data["frames"]):
  p=Path(fr["source"]);p=p if p.is_absolute() else B/p
  im=Image.open(p).convert("RGBA")
  thumb=im.resize((310,310),Image.Resampling.LANCZOS)
  x=(i%4)*320;y=(i//4)*360
  out.paste(thumb,(x,y+35),thumb);draw.text((x+5,y+5),f"{d} {i+1:02d} {p.stem}",fill=(10,10,10))
  crop=im.crop((330,780,980,1230)).resize((200,139),Image.Resampling.LANCZOS)
  lx=(i%8)*200;ly=(i//8)*400
  lower.paste(crop,(lx,ly+50),crop)
  ld.text((lx+5,ly+10),f"{d} {i+1:02d}",fill=(10,10,10))
 out.save(B/f"review/root-paired-{d}-candidate.jpg")
 lower.save(B/f"review/root-paired-{d}-feet.jpg")
 (B/f"review/root-paired-{d}-candidate.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("wrote NE/S candidate contact sheets; authoritative inputs unchanged")


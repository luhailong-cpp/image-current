import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
r=Path("D:/work/image/designs/creature-combat-20261005/pets/04-guideng")
rows=[]; thumbs=[]
for action,count in [("hit",6),("attack",8)]:
 for i in range(1,count+1):
  p=r/"runtime"/action/"E"/f"{i:02}.png"
  rec=json.loads((r/"records"/("E-"+action)/f"{i:02}.generation.json").read_text(encoding="utf-8"))
  im=Image.open(p)
  a=im.getchannel("A")
  bbox8=a.point(lambda x:255 if x>=8 else 0).getbbox()
  sha=hashlib.sha256(p.read_bytes()).hexdigest()
  rows.append({"action":action,"frame":i,"size":list(im.size),"mode":im.mode,"shaMatches":sha==rec["sha256"],"sha256":sha,"alphaRange":list(a.getextrema()),"bboxAlpha8":bbox8,"refsExist":all(Path(z["path"]).exists() for z in rec["references"]),"promptExists":Path(rec["prompt"]).exists()})
  tile=Image.new("RGBA",(256,280),(42,49,46,255));tile.alpha_composite(im.resize((256,256),Image.Resampling.LANCZOS),(0,24));ImageDraw.Draw(tile).text((8,6),f"E {action} {i:02}",fill="white");thumbs.append(tile)
sheet=Image.new("RGBA",(7*256,2*280),(22,28,25,255))
for j,t in enumerate(thumbs):sheet.alpha_composite(t,((j%7)*256,(j//7)*280))
sheet.convert("RGB").save(r/"records/E-attack/contact-first14.jpg",quality=93)
out={"scope":"E hit01-06 and E attack01-08","count":len(rows),"uniqueShaCount":len(set(x["sha256"] for x in rows)),"rows":rows,"allTechnicalPassed":all(x["size"]==[1024,1024] and x["mode"]=="RGBA" and x["shaMatches"] and x["refsExist"] and x["promptExists"] and x["alphaRange"]==[0,255] for x in rows),"reviewNotes":"Individual images all inspected via tool images and saved view_image. Continuous-playback verification delegated to root. Native canvas scaling only; low alpha noise unmodified for root unified handling."}
(r/"records/E-attack/technical-first14.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=False))


from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=B/"r13_c06/pipeline/output/d22f5458cef890fe/assembly.json";a=read(ap)
im=Image.open(a["output"]["file"]).convert("RGB");assert im.size==(4096,4096)
q=ap.parent/"root-full-native-qa";q.mkdir(exist_ok=False)
for row in range(4):
 panel=Image.new("RGB",(840,1048),"white");d=ImageDraw.Draw(panel)
 for k,x in enumerate([1024,2048,3072]):
  panel.paste(im.crop((x-128,row*1024,x+128,(row+1)*1024)),(k*280,24));d.text((k*280+3,3),f"V{k+1} row{row+1}",fill="black")
 panel.save(q/f"V-row{row+1}.png")
for k,y in enumerate([1024,2048,3072]):
 panel=Image.new("RGB",(1024,1120),"white");d=ImageDraw.Draw(panel)
 for col in range(4):
  panel.paste(im.crop((col*1024,y-128,(col+1)*1024,y+128)),(0,col*280+24));d.text((3,col*280+3),f"H{k+1} col{col+1}",fill="black")
 panel.save(q/f"H{k+1}.png")
e=read(B/"current-candidates.json")["tiles"]["r13_c05"]["candidate"];assert sha(e["file"])==e["sha256"]
left=Image.open(e["file"]).convert("RGB");panel=Image.new("RGB",(1120,1048),"white");d=ImageDraw.Draw(panel)
for row in range(4):
 part=Image.new("RGB",(256,1024));part.paste(left.crop((3968,row*1024,4096,(row+1)*1024)),(0,0));part.paste(im.crop((0,row*1024,128,(row+1)*1024)),(128,0));panel.paste(part,(row*280,24));d.text((row*280+3,3),f"LEFT row{row+1}",fill="black")
panel.save(q/"left-native-boundary.png")
manifest={"assembly":str(ap),"assemblySha256":sha(ap),"candidate":a["output"],"context":a["context"],"leftNeighbor":e,"nativePanelsResampled":False,"formalAccepted":False,"images":[{"file":str(p),"sha256":sha(p)} for p in q.glob("*.png")],"priorTopAndRow1Review":"r13_c06/pipeline/output/97b324e1ddc5dff2/root-row1-native-qa/root-review.json","topReviewReuse":"Same row1 selected inputs; source hash equivalence must be verified before reusing prior failure evidence."}
(q/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(q)


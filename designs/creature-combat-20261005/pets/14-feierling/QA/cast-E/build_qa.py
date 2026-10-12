from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
from datetime import datetime,timezone
ROOT=Path("D:/work/image/designs/creature-combat-20261005/pets/14-feierling")
GEN=ROOT/"generation/cast/E"
OUT=ROOT/"runtime/cast/E"
QA=ROOT/"QA/cast-E"
QA.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for n in range(1,17):
 p=OUT/f"{n:02}.png"
 im=Image.open(p)
 a=im.getchannel("A")
 g=GEN/f"{n:02}.generation.json"
 data=json.loads(g.read_text(encoding="utf-8"))
 rows.append({"frame":n,"file":p.relative_to(ROOT).as_posix(),"size":list(im.size),"mode":im.mode,"sha256":sha(p),"pixelSha256":hashlib.sha256(im.tobytes()).hexdigest(),"alphaExtrema":list(a.getextrema()),"transparentPixels":a.histogram()[0],"opaquePixels":a.histogram()[255],"alphaBBox":a.getbbox(),"record":g.relative_to(ROOT).as_posix(),"recordSHAAgrees":data["sha256"]==sha(p),"promptExists":(ROOT/data["prompt"]).exists(),"receiptExists":(ROOT/data["evidence"]["receipt"]).exists(),"nativeSize":[data["native"]["width"],data["native"]["height"]]})
good=all(r["size"]==[1024,1024] and r["mode"]=="RGBA" and r["alphaExtrema"]==[0,255] and r["transparentPixels"]>0 and r["recordSHAAgrees"] and r["promptExists"] and r["receiptExists"] for r in rows)
report={"scope":"cast E only; initial whole-canvas 1254-to-1024 export, before parent final directional export","checkedAt":datetime.now(timezone.utc).isoformat(),"expectedFrames":16,"actualFrames":len(rows),"uniqueFileHashes":len({x["sha256"] for x in rows}),"uniquePixelHashes":len({x["pixelSha256"] for x in rows}),"technicalPass":good and len({x["pixelSha256"] for x in rows})==16,"rows":rows,"clientValidated":False,"visualReview":"Each returned final native frame actually viewed at full resolution in generation tool; contact sheet follows; playback pending browser review."}
(QA/"technical-check.pre-final-export.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
for page in range(2):
 sheet=Image.new("RGB",(4*340,2*370),(232,230,224))
 d=ImageDraw.Draw(sheet)
 for j in range(8):
  n=page*8+j+1
  im=Image.open(OUT/f"{n:02}.png").convert("RGBA").resize((330,330),Image.Resampling.LANCZOS)
  x=(j%4)*340+5;y=(j//4)*370+26
  sheet.paste(im,(x,y),im)
  d.text((x,y-20),f"CAST E {n:02} / 45 ms",fill=(26,49,40))
 sheet.save(QA/f"contact-{page+1}.png")
# Fix first receipt with exact path inputs recorded for the first generation.
p=GEN/"01.receipt.json";r=json.loads(p.read_text(encoding="utf-8"))
r["referenced_image_paths"]=["D:/work/image/designs/pets-xianling-20260924/source/14-feierling-E.png","D:/work/image/designs/pets-xianling-20260924/source/14-feierling-W.png","D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png"]
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
# Preserve reject provenance truthfully before parent removes unused pixels.
for n in [6,11,15]:
 p=GEN/f"{n:02}.rejected-a.generation.json"
 r=json.loads(p.read_text(encoding="utf-8"));r["status"]="rejected"
 r["file"]=None
 r["native"]["file"]=f"generation/cast/E/{n:02}.rejected-a.native.png"
 r["prompt"]=f"generation/cast/E/{n:02}.rejected-a.prompt.txt"
 r["evidence"]["receipt"]=f"generation/cast/E/{n:02}.rejected-a.receipt.json"
 r["rejectionReasonFile"]=f"generation/cast/E/{n:02}.rejected-a.reason.json"
 r["runtimeOverwriteNote"]="The earlier provisional runtime was replaced by a new AI generation; sha256 retains that rejected export checksum."
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"technicalPass":report["technicalPass"],"frames":len(rows),"uniquePixels":report["uniquePixelHashes"],"contactSheets":2}))


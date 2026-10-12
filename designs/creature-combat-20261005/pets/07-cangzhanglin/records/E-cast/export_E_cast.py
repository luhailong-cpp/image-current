from pathlib import Path
from PIL import Image
import json, hashlib, sys, shutil
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/07-cangzhanglin")
payload=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
num=payload["frame"]
n=f"{num:02d}"
if payload.get("actualPrompt"):
    (base/"prompts"/("cast-E-"+n+".txt")).write_text(payload["actualPrompt"],encoding="utf-8")
source=Path(payload["source"])
stage=base/"staging"/"cast"/"E"/(n+".png")
stage.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,stage)
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(stage);im.load()
if im.mode!="RGBA": raise RuntimeError(f"Expected native RGBA; got {im.mode}")
native={"width":im.width,"height":im.height,"format":"PNG","mode":im.mode,"sha256":sha(stage)}
if im.width!=im.height: raise RuntimeError("Expected square native canvas")
out=Image.new("RGBA",(1024,1024),(0,0,0,0))
out.alpha_composite(im.resize((960,960),Image.Resampling.LANCZOS),(32,6))
dest=base/"runtime"/"cast"/"E"/(n+".png")
dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
record={
 "file":str(dest.relative_to(base)).replace("\\","/"),"sha256":sha(dest),
 "generatedAt":payload["finishedAt"],"startedAt":payload["startedAt"],
 "width":1024,"height":1024,"format":"PNG","mode":"RGBA",
 "tool":"image_gen.imagegen","route":"builtin",
 "configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8")),
 "submittedParameters":{"model":None,"quality":None,"transparent_background":True},
 "actualModel":None,"actualQuality":None,
 "evidence":{"receipt":f"records/E-cast/{n}.receipt.json","fields":"output_hint; tool did not disclose model or quality"},
 "unverifiedReason":"宿主管理，工具未披露 model/quality 参数或可核实模型元数据。",
 "prompt":f"prompts/cast-E-{n}.txt","references":payload["references"],
 "native":native,"derivedFrom":{"path":str(stage.relative_to(base)).replace("\\","/"),"sha256":native["sha256"],"sourceHostPath":str(source),"retention":"pending final verified cleanup"},
 "operation":{"type":"uniform whole-canvas export","sourceCanvas":[im.width,im.height],"resize":[960,960],"resample":"LANCZOS","pasteOffset":[32,6],"targetCanvas":[1024,1024],"perFrameAlignment":False,"crop":False},
 "animation":{"direction":"E","action":"cast","frame":num,"durationMs":45,"pivot":[0.5,0.08],"groundAnchor":[512,942],"event":"cast" if num==10 else None},
 "visualReview":payload.get("visualReview","pending"),
 "alpha":{"extrema":list(out.getchannel("A").getextrema()),"bbox":list(out.getbbox()) if out.getbbox() else None}}
rpath=base/"records"/"E-cast"/(n+".generation.json");rpath.parent.mkdir(parents=True,exist_ok=True)
rpath.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
(base/"records"/"E-cast"/(n+".receipt.json")).write_text(json.dumps(payload["receipt"],ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frame":num,"native":native,"file":record["file"],"sha256":record["sha256"],"alpha":record["alpha"]},ensure_ascii=False))

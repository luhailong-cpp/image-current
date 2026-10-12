import json,hashlib,sys
from pathlib import Path
from PIL import Image
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/13-yalingtong")
n=sys.argv[1]
req=json.loads((root/f"evidence/cast/W/{n}.request.json").read_text(encoding="utf-8"))
(root/f"prompts/cast/W/{n}.txt").write_text(req["submittedParameters"]["prompt"],encoding="utf-8")
source=Path(req["sourcePath"])
native=Image.open(source)
raw_sha=hashlib.sha256(source.read_bytes()).hexdigest()
out=root/f"runtime/cast/W/{n}.png"
out.parent.mkdir(parents=True,exist_ok=True)
native.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS).save(out)
im=Image.open(out)
a=im.getchannel("A")
refs=[{"path":p,"role":r,"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p,r in zip(req["submittedParameters"]["referenced_image_paths"],["canonical E identity","canonical W rear identity and camera","primary approved painted style"])]
record={"file":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"generatedAt":req["generatedAt"],"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":req["submittedParameters"],"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露模型或质量选择器，无可核实返回字段","evidence":{"receipt":f"evidence/cast/W/{n}.request.json","output_hint":req["output_hint"]},"prompt":f"prompts/cast/W/{n}.txt","references":refs,"native":{"path":str(source),"sha256":raw_sha,"width":native.width,"height":native.height,"mode":native.mode,"format":native.format},"operation":{"type":"uniform-full-canvas-resize","sourceSize":[native.width,native.height],"targetSize":[1024,1024],"filter":"Lanczos","perFrameTranslation":False,"createsPose":False},"width":1024,"height":1024,"format":"PNG","mode":im.mode,"alphaExtrema":a.getextrema(),"alphaBBox":a.getbbox(),"action":"cast","direction":"W","frame":int(n),"durationMs":45,"pivot":[0.5,0.08],"event":"release" if n=="10" else None}
(root/f"evidence/cast/W/{n}.generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:record[k] for k in ["file","sha256","alphaBBox","alphaExtrema"]},ensure_ascii=False))

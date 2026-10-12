import sys,json,hashlib
from pathlib import Path
from PIL import Image
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/13-yalingtong")
n=sys.argv[1]; request_name=sys.argv[2]
e=root/"evidence/cast/W"; req=json.loads((e/request_name).read_text(encoding="utf-8"))
source=Path(req["sourcePath"]); native=Image.open(source)
out=root/f"runtime/cast/W/{n}.png"
refs=[{"path":p,"role":role,"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest(),"historicalPixels":str(Path(p).resolve())==str(out.resolve())} for p,role in zip(req["submittedParameters"]["referenced_image_paths"],req["referenceRoles"])]
history=e/"history"; history.mkdir(exist_ok=True)
prior=e/f"{n}.generation.json"
old=json.loads(prior.read_text(encoding="utf-8"))
h=history/f"{n}.{old['sha256'][:12]}.generation.json"
h.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding="utf-8")
(history/f"{n}.{old['sha256'][:12]}.prompt.txt").write_text((root/f"prompts/cast/W/{n}.txt").read_text(encoding="utf-8"),encoding="utf-8")
native.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS).save(out)
im=Image.open(out); a=im.getchannel("A")
rec={"file":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"generatedAt":req["generatedAt"],"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":req["submittedParameters"],"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露模型或质量选择器，无可核实返回字段","evidence":{"receipt":f"evidence/cast/W/{request_name}","output_hint":req["output_hint"]},"prompt":f"prompts/cast/W/{n}.txt","references":refs,"aiEditedFrom":{"priorRecord":str(h),"priorSha256":old["sha256"],"priorPixelsRetained":False},"native":{"path":str(source),"sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"width":native.width,"height":native.height,"mode":native.mode,"format":native.format},"operation":{"type":"uniform-full-canvas-resize","sourceSize":[native.width,native.height],"targetSize":[1024,1024],"filter":"Lanczos","perFrameTranslation":False,"createsPose":False},"width":1024,"height":1024,"format":"PNG","mode":im.mode,"alphaExtrema":a.getextrema(),"alphaBBox":a.getbbox(),"action":"cast","direction":"W","frame":int(n),"durationMs":45,"pivot":[0.5,0.08],"event":"release" if n=="10" else None,"visualDecision":req.get("visualDecision")}
prior.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
(root/f"prompts/cast/W/{n}.txt").write_text(req["submittedParameters"]["prompt"],encoding="utf-8")
print(json.dumps({"file":str(out),"sha256":rec["sha256"],"source":str(source),"alphaBBox":a.getbbox()},ensure_ascii=False))


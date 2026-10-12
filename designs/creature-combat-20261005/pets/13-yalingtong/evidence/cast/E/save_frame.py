import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/13-yalingtong")
src=Path(sys.argv[1]); n=sys.argv[2]; started=sys.argv[3]
out=base/"runtime"/"cast"/"E"/(n+".png")
out.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src); im.load()
native={"width":im.width,"height":im.height,"format":im.format,"mode":im.mode,"sha256":hashlib.sha256(src.read_bytes()).hexdigest()}
if im.mode!="RGBA": raise ValueError("Expected native RGBA transparent output")
im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
final=Image.open(out); alpha=final.getchannel("A")
refs=[
{"path":r"D:/work/image/designs/pets-original-20260924/source/13-yalingtong-E.png","role":"native E identity master"},
{"path":r"D:/work/image/designs/pets-original-20260924/source/13-yalingtong-W.png","role":"native W anatomy and clothing master"},
{"path":r"D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png","role":"primary approved painting/style reference"}]
if len(sys.argv)>5:
    refs.extend(json.loads(sys.argv[5]))
if len(sys.argv)>6 and sys.argv[6]=='replace':
    refs=json.loads(sys.argv[5])
for ref in refs: ref["sha256"]=hashlib.sha256(Path(ref["path"]).read_bytes()).hexdigest()
record={
"file":"runtime/cast/E/"+n+".png","sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
"action":"cast","direction":"E","frame":int(n),"durationMs":45,"event":"release" if n=="10" else None,
"generatedAt":started,"recordedAt":datetime.now(timezone.utc).isoformat(),
"tool":"image_gen.imagegen","route":"builtin",
"configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),
"submittedParameters":{"model":None,"quality":None,"prompt":"prompts/cast/E/"+n+".txt","referenced_image_paths":[r["path"] for r in refs],"transparent_background":True},
"actualModel":None,"actualQuality":None,
"unverifiedReason":"Host-managed builtin tool exposes no model or quality selector and returns image_url/output_hint only; no reliable model/quality receipt was disclosed.",
"evidence":"evidence/cast/E/"+n+".receipt.txt",
"prompt":"prompts/cast/E/"+n+".txt","references":refs,
"native":native,"derivedFrom":{"path":str(src),"sha256":native["sha256"],"retained":True},
"operation":{"kind":"uniform-full-canvas-resize","from":[im.width,im.height],"to":[1024,1024],"resampler":"Pillow LANCZOS","translation":[0,0],"crop":None,"mirror":False},
"export":{"width":1024,"height":1024,"format":"PNG","mode":"RGBA","alphaExtrema":list(alpha.getextrema()),"alphaBBox":list(alpha.getbbox())},
"visualStatus":"individually-reviewed","visualNotes":sys.argv[4] if len(sys.argv)>4 else ""}
(base/"evidence"/"cast"/"E"/(n+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frame":n,"native":native,"export":record["export"],"sha256":record["sha256"]}))

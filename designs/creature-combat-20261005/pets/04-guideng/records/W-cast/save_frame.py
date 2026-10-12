import sys,json,hashlib,datetime
from pathlib import Path
from PIL import Image
base=Path("D:/work/image/designs/creature-combat-20261005/pets/04-guideng")
job=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
i=job["index"]; label=f"{i:02d}"
src=Path(job["source"]); dst=base/"runtime/cast/W"/(label+".png")
dst.parent.mkdir(parents=True,exist_ok=True)
if dst.exists(): raise RuntimeError("Refusing overwrite")
im=Image.open(src).convert("RGBA"); native=im.size; sourceSha=hashlib.sha256(src.read_bytes()).hexdigest()
if im.size != (1024,1024): im=im.resize((1024,1024),Image.Resampling.LANCZOS)
im.save(dst)
record={**job,"file":str(dst),"sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),"generatedAt":job["completedAt"],"nativeSize":list(native),"exportSize":[1024,1024],"format":"PNG","sourceSha256":sourceSha,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":job["references"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"Host-managed tool exposes no model/quality selector or result metadata","operation":"Whole-canvas uniform resize to 1024x1024 using Lanczos; no crop, alignment, translation, mirroring, interpolation between frames, or synthetic pose","derivedFrom":{"path":str(src),"sha256":sourceSha,"nativeSize":list(native)},"durationMs":45,"pivot":[0.5,0.08],"virtualAnchor":[512,942],"alphaExtrema":list(im.getchannel("A").getextrema()),"alphaBBox":list(im.getchannel("A").getbbox()),"visualReview":job.get("visualReview","")}
(base/"records/W-cast"/(label+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(dst),"native":native,"alpha":record["alphaExtrema"],"sha256":record["sha256"]}))


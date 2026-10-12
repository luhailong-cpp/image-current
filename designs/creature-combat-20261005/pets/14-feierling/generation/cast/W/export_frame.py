import json,sys,hashlib
from pathlib import Path
from PIL import Image
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/14-feierling")
g=base/"generation/cast/W"
j=Path(sys.argv[1])
d=json.loads(j.read_text(encoding="utf-8-sig"))
src=Path(d["nativeFile"])
im=Image.open(src); im.load()
native={"file":str(src),"sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"width":im.width,"height":im.height,"mode":im.mode,"format":im.format}
if im.width!=im.height: raise SystemExit("Non-square native requires review; no auto crop")
if im.mode!="RGBA": raise SystemExit("Native has no RGBA; no fake alpha")
out=base/"runtime/cast/W"/(d["frame"]+".png");out.parent.mkdir(parents=True,exist_ok=True)
export=im.resize((1024,1024),Image.Resampling.LANCZOS) if im.size!=(1024,1024) else im.copy()
export.save(out)
alpha=export.getchannel("A")
d.update({"file":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"width":1024,"height":1024,"format":"PNG","mode":"RGBA","native":native,"derivedFrom":{"file":str(src),"sha256":native["sha256"],"operation":"whole-canvas proportional LANCZOS resize to 1024x1024; no crop, translation, bottom alignment, pose synthesis or interpolation"},"alpha":{"extrema":alpha.getextrema(),"bbox":alpha.getbbox(),"transparentPixels":alpha.histogram()[0],"opaquePixels":alpha.histogram()[255]},"durationMs":45,"pivot":[0.5,0.08]})
j.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frame":d["frame"],"output":str(out),"native":native,"alpha":d["alpha"]}))


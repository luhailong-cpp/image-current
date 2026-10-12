from pathlib import Path
from PIL import Image
import json, hashlib, sys, shutil
BASE=Path(r"D:/work/image/designs/creature-combat-20261005/pets/01-zhuling")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
j=Path(sys.argv[1]); rec=json.loads(j.read_text(encoding="utf-8"))
src=Path(rec["sourcePath"]); d=rec["direction"]; n=rec["frame"]
out=BASE/"runtime"/"attack"/d/f"{n:02d}.png"; out.parent.mkdir(parents=True, exist_ok=True)
with Image.open(src) as native:
    native.load(); rec["native"]={"width":native.width,"height":native.height,"mode":native.mode,"format":native.format,"sha256":sha(src)}
    if native.width != native.height: raise ValueError("non-square output")
    im=native.convert("RGBA")
    im=im.resize((820,820),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(1024,1024),(0,0,0,0)); canvas.alpha_composite(im,(102,102)); im=canvas
    im.save(out)
alpha=im.getchannel("A")
rec["file"]=out.relative_to(BASE).as_posix(); rec["sha256"]=sha(out); rec["width"]=rec["height"]=1024
rec["alphaExtrema"]=alpha.getextrema(); rec["alphaBBox"]=alpha.getbbox()
rec["operation"]="Fixed transform shared across all 68 frames: full native square canvas resized to 820x820 and alpha-composited at (102,102) onto transparent 1024 canvas. No crop/bbox fitting/per-frame alignment; preserve generated alpha."
rec["derivedFrom"]={"path":str(src),"sha256":rec["native"]["sha256"]}
rec["durationMs"]=30; rec["pivot"]=[0.5,0.08]; rec["event"]="impact" if n==7 else None
record=BASE/"records"/"attack"/d/f"{n:02d}.generation.json"; record.parent.mkdir(parents=True,exist_ok=True)
record.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
j.unlink()
print(json.dumps({"file":str(out),"native":rec["native"],"alpha":rec["alphaExtrema"],"bbox":rec["alphaBBox"],"sha256":rec["sha256"]}))

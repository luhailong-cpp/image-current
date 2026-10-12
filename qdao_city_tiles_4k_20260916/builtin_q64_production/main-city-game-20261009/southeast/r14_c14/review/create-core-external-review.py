from PIL import Image
from pathlib import Path
import json,hashlib
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast")
q=b/"r14_c14/review/assembly-8ff54f4e9ec7de483b1a/core-only-external"
q.mkdir(exist_ok=True)
specs={}
for tile in ("r13_c14","r14_c13","r14_c14"):
    d=json.loads((b/tile/"candidate/latest-assembly.json").read_text(encoding="utf-8"))
    specs[tile]=d["candidate"]
p=b/"r13_c13/candidate/r13_c13-4k-candidate-repaired.png"
specs["r13_c13"]={"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size":[4096,4096]}
ims={}
for k,s in specs.items():
    p=Path(s["path"])
    assert hashlib.sha256(p.read_bytes()).hexdigest()==s["sha256"]
    ims[k]=Image.open(p).convert("RGB")
    assert ims[k].size==(4096,4096)
a=Image.new("RGB",(4096,512))
a.paste(ims["r13_c14"].crop((0,3840,4096,4096)),(0,0))
a.paste(ims["r14_c14"].crop((0,0,4096,256)),(0,256))
for start in (0,2048):a.crop((start,0,start+2048,512)).save(q/f"north-core-seam-x{start:04d}-{start+2048:04d}.png")
c=Image.new("RGB",(512,4096))
c.paste(ims["r14_c13"].crop((3840,0,4096,4096)),(0,0))
c.paste(ims["r14_c14"].crop((0,0,256,4096)),(256,0))
for start in (0,2048):c.crop((0,start,512,start+2048)).save(q/f"west-core-seam-y{start:04d}-{start+2048:04d}.png")
d=Image.new("RGB",(900,900))
d.paste(ims["r13_c13"].crop((3646,3646,4096,4096)),(0,0))
d.paste(ims["r13_c14"].crop((0,3646,450,4096)),(450,0))
d.paste(ims["r14_c13"].crop((3646,0,4096,450)),(0,450))
d.paste(ims["r14_c14"].crop((0,0,450,450)),(450,450))
d.save(q/"four-core-corner-900.png")
(q/"source-manifest.json").write_text(json.dumps({"sources":specs,"method":"actual formal4096 core crops only; no halo, resizing, blending or painting; source files untouched","tileR14C14OriginInCorner":[450,450],"coreSeamCoordinate":256},indent=2),encoding="utf-8")
print(str(q))


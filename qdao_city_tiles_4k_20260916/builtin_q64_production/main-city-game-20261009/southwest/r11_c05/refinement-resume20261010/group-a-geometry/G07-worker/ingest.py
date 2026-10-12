from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, shutil
root=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c05/refinement-resume20261010/group-a-geometry/G07-worker")
req=json.loads((root/"request.json").read_text())
receipt=json.loads((root/"receipt.json").read_text())
for d in ["native","qa","output"]: (root/d).mkdir(exist_ok=True)
src=Path(receipt["sourceOutput"])
raw=root/"native/G07-v1.raw.png"
shutil.copyfile(src,raw)
base=Image.open(req["referenced_image_paths"][0]).convert("RGB")
new=Image.open(raw).convert("RGB")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
box=(390,255,660,480)
base.crop(box).save(root/"qa/original-joint.png")
new.crop(box).save(root/"qa/generated-joint.png")
a=np.array(base);b=np.array(new)
anchors=[(420,439),(450,418),(480,396),(495,386),(515,372),(535,374),(555,361),(575,347),(595,334),(620,316),(650,296),(750,225),(850,155)]
measure=[]
for x,y in anchors:
    lo=max(0,y-25);hi=min(1254,y+26)
    ra=a[lo:hi,x-1:x+2].mean(axis=(1,2));rb=b[lo:hi,x-1:x+2].mean(axis=(1,2))
    ya=int(lo+np.argmin(ra));yb=int(lo+np.argmin(rb))
    measure.append({"x":x,"sourceDarkestY":ya,"generatedDarkestY":yb,"shiftY":yb-ya})
data={"rawPath":str(raw),"rawSha256":sha(raw),"sourceToolOutputSha256":sha(src),"rawSize":list(new.size),"rawMode":new.mode,"actualModel":None,"actualQuality":None,"inputs":req["inputs"],"promptSha256":req["promptSha256"],"anchorMeasurements":measure,"measurementNote":"Darkest RGB mean in 3-column strip within expected y +/-25; visual inspection remains necessary."}
(root/"native/G07-v1.raw.png.generation.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
print(json.dumps(data))


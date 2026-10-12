from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c04")
oldname="r05_c04-candidate-minimum-error-fc35358c1e27"
newname="r05_c04-candidate-minimum-error-6b0f7ef07937"
old=json.loads((B/"candidate"/(oldname+".assembly.json")).read_text(encoding="utf-8-sig"))
new=json.loads((B/"candidate"/(newname+".assembly.json")).read_text(encoding="utf-8-sig"))
oldmap={x["id"]:x["sha256"] for x in old["nativeSources"]}
sourcechanges=[{"id":x["id"],"oldSha256":oldmap.get(x["id"]),"newSha256":x["sha256"]} for x in new["nativeSources"] if oldmap.get(x["id"])!=x["sha256"]]
changed=[];same=[]
for p in sorted((B/"qa"/newname).glob("*.png")):
 op=B/"qa"/oldname/p.name
 a=np.array(Image.open(p));b=np.array(Image.open(op))
 if np.array_equal(a,b): same.append(str(p))
 else: changed.append({"file":str(p),"prior":str(op),"changedPixelCount":int(np.any(a!=b,axis=2).sum())})
data={"sourceChanges":sourcechanges,"unchangedSourceCount":16-len(sourcechanges),"changedQa":changed,"pixelIdenticalQa":same}
(B/"qa/s04_02_joint01-selection-replay.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
print(json.dumps(data,indent=2))


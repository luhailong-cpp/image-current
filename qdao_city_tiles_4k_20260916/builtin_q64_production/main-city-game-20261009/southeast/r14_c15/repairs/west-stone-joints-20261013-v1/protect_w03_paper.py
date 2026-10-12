from pathlib import Path
from PIL import Image
import json,hashlib
import numpy as np
d=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c15/repairs/west-stone-joints-20261013-v1");p=d/"W03"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
prep=json.loads((p/"preparation.json").read_text());r=prep["nativeCrop"]
a=np.array(Image.open(p/"alpha-crop.png"));yy,xx=np.indices(a.shape);xx=xx+r[0];yy=yy+r[1]
dx=np.maximum(0,800-xx);dy=np.maximum(0,800-yy);dist=np.sqrt(dx*dx+dy*dy)
a=np.minimum(a,np.rint(np.clip(dist/24,0,1)*255).astype(np.uint8));a[(xx>=800)&(yy>=800)]=0
mask=np.zeros((1254,1254),np.uint8);mask[r[1]:r[3],r[0]:r[2]]=255;mask[800:920,800:915]=0
full=np.zeros_like(mask);full[r[1]:r[3],r[0]:r[2]]=a
for path,arr in [("alpha-crop.png",a),("alpha-native-1254.png",full),("edit-mask-native-1254.png",mask)]:Image.fromarray(arr).save(p/path)
target=np.array(Image.open(p/"reference-core-join-native-1254.png").convert("RGB"));target[mask>0]=(255,0,255);Image.fromarray(target).save(p/"edit-target-native-1254.png")
prompt=(p/"prompt.txt").read_text();prompt+="The lower-right notch excludes the existing red paper fragment; keep that paper and its shadow pixel-aligned and never cover it with paving.\n";(p/"prompt.txt").write_text(prompt)
req=json.loads((p/"request.json").read_text());req["submittedParameters"]["prompt"]=prompt;(p/"request.json").write_text(json.dumps(req,ensure_ascii=False,indent=2)+"\n")
prep.update(target=info(p/"edit-target-native-1254.png"),references=[info(p/"edit-target-native-1254.png"),info(p/"reference-core-join-native-1254.png")],savedMask=info(p/"edit-mask-native-1254.png"),alpha=info(p/"alpha-crop.png"),fullAlpha=info(p/"alpha-native-1254.png"),prompt=info(p/"prompt.txt"),request=info(p/"request.json"),protectedRedPaperBoxInTarget=[800,800,915,920])
prep["alphaRule"]+=" Lower-right notch [800,800,915,920] additionally has alpha zero with a 24px inward taper around its boundary to protect existing red paper."
(p/"preparation.json").write_text(json.dumps(prep,ensure_ascii=False,indent=2)+"\n")
ready=json.loads((d/"ready-requests.json").read_text())
for j in ready["jobs"]:
 if j["id"]=="W03":
  for k,fn in [("request","request.json"),("preparation","preparation.json"),("target","edit-target-native-1254.png"),("mask","edit-mask-native-1254.png"),("alpha","alpha-crop.png")]:j[k]=info(p/fn)
  j["protectedRedPaperBoxInTarget"]=[800,800,915,920]
(d/"ready-requests.json").write_text(json.dumps(ready,indent=2)+"\n")
print(json.dumps({"ready":info(d/"ready-requests.json"),"W03":info(p/"preparation.json")}))

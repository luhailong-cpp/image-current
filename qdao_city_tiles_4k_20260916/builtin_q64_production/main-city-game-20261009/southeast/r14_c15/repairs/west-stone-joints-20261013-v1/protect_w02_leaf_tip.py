from pathlib import Path
from PIL import Image
import json,hashlib
import numpy as np
d=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c15/repairs/west-stone-joints-20261013-v1");p=d/"W02"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
prep=json.loads((p/"preparation.json").read_text());r=prep["nativeCrop"]
a=np.array(Image.open(p/"alpha-crop.png"))
yy,xx=np.indices(a.shape);xx=xx+r[0];yy=yy+r[1]
# Keep the existing pointed leaf entering at lower-left exactly.
dx=np.maximum(0,xx-712);dy=np.maximum(0,810-yy)
dist=np.sqrt(dx*dx+dy*dy)
a=np.minimum(a,np.rint(np.clip(dist/24,0,1)*255).astype(np.uint8))
a[(xx<712)&(yy>=810)]=0
mask=np.zeros((1254,1254),np.uint8);mask[r[1]:r[3],r[0]:r[2]]=255;mask[810:880,640:712]=0
full=np.zeros_like(mask);full[r[1]:r[3],r[0]:r[2]]=a
Image.fromarray(a).save(p/"alpha-crop.png");Image.fromarray(full).save(p/"alpha-native-1254.png");Image.fromarray(mask).save(p/"edit-mask-native-1254.png")
target=np.array(Image.open(p/"reference-core-join-native-1254.png").convert("RGB"));target[mask>0]=(255,0,255);Image.fromarray(target).save(p/"edit-target-native-1254.png")
prompt=(p/"prompt.txt").read_text();prompt+="The lower-left notch of the magenta mask protects the real existing green leaf tip; retain that leaf and its precise silhouette, never replace it with paving.\n";(p/"prompt.txt").write_text(prompt)
req=json.loads((p/"request.json").read_text());req["submittedParameters"]["prompt"]=prompt;(p/"request.json").write_text(json.dumps(req,ensure_ascii=False,indent=2)+"\n")
prep.update(target=info(p/"edit-target-native-1254.png"),references=[info(p/"edit-target-native-1254.png"),info(p/"reference-core-join-native-1254.png")],savedMask=info(p/"edit-mask-native-1254.png"),alpha=info(p/"alpha-crop.png"),fullAlpha=info(p/"alpha-native-1254.png"),prompt=info(p/"prompt.txt"),request=info(p/"request.json"),protectedLeafTipBoxInTarget=[640,810,712,880])
prep["alphaRule"]+=" Lower-left notch [640,810,712,880] additionally has alpha zero with a 24px inward taper around its boundary to protect the existing leaf tip."
(p/"preparation.json").write_text(json.dumps(prep,ensure_ascii=False,indent=2)+"\n")
ready=json.loads((d/"ready-requests.json").read_text())
for j in ready["jobs"]:
 if j["id"]=="W02":
  for k,fn in [("request","request.json"),("preparation","preparation.json"),("target","edit-target-native-1254.png"),("mask","edit-mask-native-1254.png"),("alpha","alpha-crop.png")]:j[k]=info(p/fn)
  j["protectedLeafTipBoxInTarget"]=[640,810,712,880]
(d/"ready-requests.json").write_text(json.dumps(ready,indent=2)+"\n")
print(json.dumps({"ready":info(d/"ready-requests.json"),"W02":info(p/"preparation.json")}))

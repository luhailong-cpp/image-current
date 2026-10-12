from pathlib import Path
import json,hashlib,copy,sys
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parents[1];D=B/"refinement";SW=B.parent
sys.path.insert(0,str(SW));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=B/"native/p02_01.png"
a=np.array(Image.open(source).convert("RGB"));seed=a.copy()
# Exact native crops only: elongate a quiet stone course, preserving the first groove.
# The source strip contains no grout and is copied 1:1, never scaled.
seed[882:1154]=a[530:802]
# Existing second groove and lower-course native geometry shifted exactly +192px.
seed[1142:1254]=a[950:1062]
# Two-pixel mechanical transition only, away from either joint.
for y in range(880,884):
 w=(y-880)/3
 seed[y]=np.rint(a[y]*(1-w)+a[y-352]*w).astype(np.uint8)
target=D/"p02_01.geometry-v02.native-crop-seed.png"
assert not target.exists()
Image.fromarray(seed).save(target)
der={"source":str(source),"sourceSha256":sha(source),"operation":"two exact native source crops, no source scaling, no painted texture; provisional edit target only","copies":[{"sourceBox":[0,530,1254,802],"targetBox":[0,882,1254,1154]},{"sourceBox":[0,950,1254,1062],"targetBox":[0,1142,1254,1254]}],"maximumBlendWidth":4,"maximumFeatherRadiusPixels":2,"geometryExpected":{"horizontalGroovesY":[863,1152]},"gameArt":False,"requiresVisualReview":True}
atomic_json(Path(str(target)+".derivation.json"),der)
req=json.loads((D/"p02_01.geometry-v01.request.json").read_text())
prompt="""Use case: precise-object-edit. Edit IMAGE1 only. It already has the correct sparse stone geometry: the first horizontal grout is near y863, the second near y1152, with a broad uninterrupted middle course between them, and only two clipped vertical joints near x314 and x938 below y1152. Do not move, remove, add, duplicate, thicken or redraw any grout line. Preserve exactly the large stones, upper-right diagonal groove, close framing and1254x1254 scale. Refine ONLY stone face material to natural quiet pale-gray broad softly painted stone like the reference, removing tiny woven crosshatching/cellular marks. Keep broad soft light and volume, no blur. No added objects, scene, architecture, props, ornament or red paper. References2-4 are style/geometry context only and must contribute no depicted objects. Keep top230 neighbor strip pixel-registered and retain the same tones."""
pp=D/"p02_01.geometry-v02.prompt.txt";rp=D/"p02_01.geometry-v02.request.json"
assert not pp.exists() and not rp.exists()
pp.write_text(prompt,encoding="utf-8")
req.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp))
req["references"][0]={"file":str(target),"sha256":sha(target),"role":"edit target mechanically assembled from source-native crops, provisional geometry guide not final"}
req["referenced_image_paths"]=[r["file"] for r in req["references"]]
req["refinementOf"]={"file":str(source),"sha256":sha(source),"derivation":str(target)+".derivation.json"}
atomic_json(rp,req)
print(json.dumps({"request":str(rp),"seed":str(target)}))

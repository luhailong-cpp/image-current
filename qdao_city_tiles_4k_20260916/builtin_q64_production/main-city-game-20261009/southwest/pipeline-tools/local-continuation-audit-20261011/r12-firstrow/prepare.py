import json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
O=Path(__file__).parent;S=O.parents[2]
A=S/"r12_c05/pipeline/output/a5704019021dd0ee/assembly.json"
a=json.loads(A.read_text(encoding="utf-8"));im=Image.open(a["output"]["file"]).convert("RGB")
north=Image.open(S/"integrated-20261011/v2/r11_c05.candidate.png").convert("RGB")
p02=Image.open(S/"r12_c05/native/p02_01.png").convert("RGB")
ref=Image.open(S.parents[1]/"parallel_20261005/daylight-only-20261009/tianyong/tianyong-natural-stone-detail-v1.png").convert("RGB")
meta=[]
for j in range(4):
 x=j*1024
 pair=Image.new("RGB",(1024,512));pair.paste(north.crop((x,3840,x+1024,4096)),(0,0));pair.paste(im.crop((x,0,x+1024,256)),(0,256))
 name=f"north-shared-segment-{j+1}.png";pair.save(O/name)
 meta.append({"file":name,"resized":False,"worldBox":[16384+x,44800,16384+x+1024,45312],"seamAtImageY":256})
for j,x in enumerate([1024,2048,3072],1):
 name=f"firstrow-internal-{j}.png";im.crop((x-256,0,x+256,1024)).save(O/name)
 meta.append({"file":name,"resized":False,"tileBox":[x-256,0,x+256,1024],"boundaryAtImageX":256})
p=Image.new("RGB",(1024,512));p.paste(im.crop((0,768,1024,1024)),(0,0));p.paste(p02.crop((115,115,1139,371)),(0,256));p.save(O/"p02_01-top-boundary.png")
meta.append({"file":"p02_01-top-boundary.png","resized":False,"worldBox":[16384,45824,17408,46336],"seamAtImageY":256,"note":"direct core boundary preview, not a final multirow quilt"})
for name,box in [("ref-stone-context",[477,865,773,989]),("ref-stone-face",[523,920,741,978]),("ref-right-paving",[1183,500,1254,865])]:
 ref.crop(box).save(O/(name+".png"));meta.append({"file":name+".png","source":"approved detail v1","sourceBox":box,"resized":False})
p02.crop((0,800,1254,1254)).save(O/"p02_01-lower-course.png")
im.resize((2048,512),Image.Resampling.LANCZOS).save(O/"firstrow-preview-resized-2048.png")
meta.append({"file":"firstrow-preview-resized-2048.png","resized":True,"previewOnly":True,"nativeSize":list(im.size),"outputSize":[2048,512]})
(O/"crop-manifest.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
# Dark seam minima on the lower native crop, verify reported line positions.
arr=np.array(p02);gray=np.mean(arr,axis=2)
for x in [100,500,800,1150]:
 series=gray[780:1220,x]
 ids=np.argsort(series)[:8]+780
 print(x,sorted(ids.tolist()))
print("artifacts",len(meta))


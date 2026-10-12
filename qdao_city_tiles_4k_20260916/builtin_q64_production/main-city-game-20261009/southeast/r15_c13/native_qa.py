from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
idx=read(T/"candidate/latest-assembly.json")
m=read(idx["manifest"]["path"])
q=T/"review/native-qa-20261011"
q.mkdir(exist_ok=True)
outputs=[]
def save(name,im,boxes,source):
 p=q/(name+".png")
 if p.exists():
  assert np.array_equal(np.asarray(Image.open(p)),np.asarray(im))
 else: im.save(p)
 outputs.append({"path":str(p),"sha256":sha(p),"size":list(im.size),"resized":False,"source":source,"sourceBoxes":boxes})
final=Image.open(m["candidate"]["path"]).convert("RGB")
for i in range(4):
 panel=Image.new("RGB",(1536,1024))
 boxes=[]
 for j,x in enumerate((1024,2048,3072)):
  box=(x-256,i*1024,x+256,(i+1)*1024);boxes.append(box)
  panel.paste(final.crop(box),(j*512,0))
 save(f"vertical-seams-quarter-{i+1}",panel,boxes,m["candidate"])
 panel=Image.new("RGB",(1024,1536));boxes=[]
 for j,y in enumerate((1024,2048,3072)):
  box=(i*1024,y-256,(i+1)*1024,y+256);boxes.append(box)
  panel.paste(final.crop(box),(0,j*512))
 save(f"horizontal-seams-quarter-{i+1}",panel,boxes,m["candidate"])
north=Image.open(T.parent/"r14_c13/candidate/r14_c13-4k-north-v6.png").convert("RGB")
assert sha(T.parent/"r14_c13/candidate/r14_c13-4k-north-v6.png")=="f1d683133fa23f466621f492375b55848d2a8c5775e039f10c2c86bc3860fda5"
for i in range(4):
 panel=Image.new("RGB",(1024,800))
 panel.paste(north.crop((i*1024,3696,(i+1)*1024,4096)),(0,0))
 panel.paste(final.crop((i*1024,0,(i+1)*1024,400)),(0,400))
 save(f"north-joint-quarter-{i+1}",panel,[[i*1024,3696,(i+1)*1024,4096],[i*1024,0,(i+1)*1024,400]],"r14_c13 immutable v6 above; r15_c13 candidate below")
for i in range(4):
 panel=Image.new("RGB",(1024,1280))
 panel.paste(final.crop((i*1024,0,(i+1)*1024,256)),(0,0))
 panel.paste(final.crop((i*1024,3840,(i+1)*1024,4096)),(0,256))
 panel.paste(final.crop((0,i*1024,256,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90),(0,512))
 panel.paste(final.crop((3840,i*1024,4096,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90),(0,768))
 save(f"four-edges-quarter-{i+1}",panel,[],"top=north;second=south;third=west90ccw;fourth=east90ccw; bottom256 blank")
masks=np.load(m["seamPathsAndAlpha"]["path"],allow_pickle=False)
active=m["activeNativeMapSnapshot"]
natives=[]
for r in range(1,5):
 for c in range(1,5):
  p=f"p{r:02d}_{c:02d}";f=T/"native"/(active[p]+".png")
  rec=read(str(f)+".generation.json")
  assert sha(f)==rec["sha256"]
  assert rec["actualModel"] is None and rec["actualQuality"] is None
  im=Image.open(f).convert("RGB");assert im.size==(1254,1254)
  natives.append(np.asarray(im))
def join(a,b,key):
 w=masks[key+"_alpha"].astype(np.uint32)[...,None]
 blend=((a[:,-230:].astype(np.uint32)*(255-w)+b[:,:230].astype(np.uint32)*w+127)//255).astype(np.uint8)
 return np.concatenate((a[:,:-230],blend,b[:,230:]),axis=1)
strips=[]
for r in range(4):
 a=natives[r*4]
 for c in range(1,4): a=join(a,natives[r*4+c],f"row{r+1:02d}_c{c:02d}_c{c+1:02d}")
 strips.append(a)
a=strips[0].transpose(1,0,2)
for r in range(1,4): a=join(a,strips[r].transpose(1,0,2),f"rows_r{r:02d}_r{r+1:02d}")
replay=a.transpose(1,0,2)
assert np.array_equal(replay,np.asarray(Image.open(m["context"]["path"]).convert("RGB")))
assert np.array_equal(replay[115:4211,115:4211],np.asarray(final))
result={"checkedAt":datetime.now(timezone.utc).isoformat(),"tile":"r15_c13","candidate":m["candidate"],"context":m["context"],"manifest":idx["manifest"],"nativeCount":16,"allNative1254NoResize":True,"actualModelQualityUnknown":True,"savedAlphaIndependentReplay":{"contextPixelExact":True,"candidatePixelExact":True},"reviewImages":outputs,"visualQA":"pending"}
(q/"verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps({k:result[k] for k in ["candidate","context","manifest","savedAlphaIndependentReplay"]},indent=2))


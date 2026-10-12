"""One-shot p13/p14 bridge target, native crop/paste only; does not alter sources."""
from pathlib import Path
from PIL import Image
import hashlib,json,datetime
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=Z/"native/r06_c12_p13-v2.png";b=Z/"native/r06_c12_p14-v3.png"
ar=json.loads(Path(str(a)+".generation.json").read_text(encoding="utf-8-sig"))
br=json.loads(Path(str(b)+".generation.json").read_text(encoding="utf-8-sig"))
assert sha(a)==ar["sha256"] and sha(b)==br["sha256"]
ga=ar["coordinates"]["nativeGlobalBox"];gb=br["coordinates"]["nativeGlobalBox"]
assert gb[0]-ga[0]==1024 and ga[1]==gb[1]
with Image.open(a)as ia,Image.open(b)as ib:
 assert ia.size==ib.size==(1254,1254)
 out=Image.new("RGB",(1254,1254))
 out.paste(ia.crop((512,0,1139,1254)),(0,0))
 out.paste(ib.crop((115,0,742,1254)),(627,0))
p=Z/"guides/p13-p14-bridge-target.png"
assert not p.exists()
out.save(p)
data={"file":str(p),"sha256":sha(p),"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"purpose":"Native 1:1 edit target for a single joint stone-seam repair validation; not accepted game art",
"pixels":[1254,1254],"nativeGlobalBox":[ga[0]+512,ga[1],ga[0]+1766,ga[3]],"joinLocalX":627,
"operation":"Opaque native crop/paste only; no resize, drawing, feathering or blending",
"derivedFrom":[{"path":str(a),"sha256":sha(a),"sourceBox":[512,0,1139,1254],"targetBox":[0,0,627,1254],"generationRecord":str(a)+".generation.json"},
{"path":str(b),"sha256":sha(b),"sourceBox":[115,0,742,1254],"targetBox":[627,0,1254,1254],"generationRecord":str(b)+".generation.json"}],
"configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),
"formalAccepted":False}
Path(str(p)+".derived.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(data))


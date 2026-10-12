from pathlib import Path
import argparse,json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=argparse.ArgumentParser();q.add_argument("name");q.add_argument("side",choices=["left","top"]);q.add_argument("a");q.add_argument("b");x=q.parse_args()
assert x.name.startswith("r07_c13")
ap=Z/"native"/x.a;bp=Z/"native"/x.b;a=Image.open(ap);b=Image.open(bp);assert a.size==b.size==(1254,1254)
im=Image.new("RGB",(256,1254)if x.side=="left"else(1254,256))
if x.side=="left":im.paste(a.crop((1011,0,1139,1254)),(0,0));im.paste(b.crop((115,0,243,1254)),(128,0))
else:im.paste(a.crop((0,1011,1254,1139)),(0,0));im.paste(b.crop((0,115,1254,243)),(0,128))
p=Z/"qa"/(x.name+".png");assert not p.exists();im.save(p)
Path(str(p)+".derived.json").write_text(json.dumps({"file":str(p),"sha256":sha(p),"sourceImages":[{"path":str(a),"sha256":sha(a)}for a in [ap,bp]],"operation":"native integer crop and paste only","seamLocalCoordinate":128,"seamAxis":"x"if x.side=="left"else"y","formalAccepted":False},indent=2),encoding="utf-8")
print(str(p))


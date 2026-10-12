from pathlib import Path
from PIL import Image
import json, hashlib
B=Path(__file__).resolve().parent.parent;W=B/"work-r06_c02"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
left=B/"native/r06_c02_s01_s02_v02.png";right=B/"native/r06_c02_s01_s03_v02.png"
# Exact native crop centered on the original neighboring core boundary x6144.
out=Image.new("RGB",(1254,1254))
out.paste(Image.open(left).crop((512,0,1139,1254)),(0,0))
out.paste(Image.open(right).crop((115,0,742,1254)),(627,0))
p=W/"guides/r06_c02_roof_joint_12_v01.authoritative.png"
assert not p.exists()
out.save(p)
rec={"file":str(p),"sha256":sha(p),"globalNativeBox":[5517,20365,6771,21619],"globalCoreBox":[5632,20480,6656,21504],"purpose":"Exact native-cut repair guide; no resizing, interpolation, manual painting or generated final pixels","sources":[{"file":str(left),"sha256":sha(left),"crop":[512,0,1139,1254],"destination":[0,0]},{"file":str(right),"sha256":sha(right),"crop":[115,0,742,1254],"destination":[627,0]}]}
Path(str(p)+".derivation.json").write_text(json.dumps(rec,indent=2),encoding="utf-8")
print(json.dumps(rec))


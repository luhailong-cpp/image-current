from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent;T="r07_c13"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((Z/"records"/f"{T}.working-selection.json").read_text())
im=Image.new("RGB",(1024,4096));sources=[]
for r in range(1,5):
 p=Z/"native"/s[f"{T}_p{r}1"];a=Image.open(p);assert a.size==(1254,1254)
 im.paste(a.crop((115,115,1139,1139)),(0,(r-1)*1024));sources.append({"path":str(p),"sha256":sha(p),"sourceCropBox":[115,115,1139,1139],"destinationBox":[0,(r-1)*1024,1024,r*1024]})
out=Z/"qa"/f"{T}-first-column.native-1to1.png";assert not out.exists();im.save(out)
Path(str(out)+".derived.json").write_text(json.dumps({"file":str(out),"sha256":sha(out),"pixels":[1024,4096],"globalBox":[49152,24576,50176,28672],"sources":sources,"operation":"Four exact1024 native core crops pasted opaque vertically, no scaling","partialCoverage":True,"formalAccepted":False},indent=2),encoding="utf-8")
print(str(out))


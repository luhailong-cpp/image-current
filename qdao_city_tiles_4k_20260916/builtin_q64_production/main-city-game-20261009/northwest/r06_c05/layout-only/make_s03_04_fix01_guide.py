from PIL import Image
from pathlib import Path
import production_v2 as p
b=p.ZONE/"r06_c05"
source=b/"native/s03_04.png"
anchor=b/"layout-only/s03_04.continuation-guide.png"
out=b/"layout-only/s03_04_fix01.native-repair-guide.png"
if out.exists(): raise FileExistsError(out)
im=Image.open(source).convert("RGB")
guide=Image.open(anchor).convert("RGB")
boxes=[[0,0,1254,230],[0,1024,1254,1254]]
for box in boxes: im.paste(guide.crop(box),(box[0],box[1]))
im.save(out)
p.write_json(Path(str(out)+".derivation.json"),{"kind":"layout-only native repair guide","notProductionArt":True,"operation":"unscaled exact pixel crop/paste only","source":{"file":str(source),"sha256":p.sha(source)},"anchors":{"file":str(anchor),"sha256":p.sha(anchor)},"boxesReplacedFromGuide":boxes,"output":{"file":str(out),"sha256":p.sha(out)}})
print(out)

from PIL import Image
from pathlib import Path
import production_v2 as p
b=p.ZONE/"r06_c05"
src=b/"native/s04_03_roadalign02.png"
north=b/"native/s03_03.png"
out=b/"layout-only/s04_03_bluealign03.native-guide.png"
im=Image.open(src).convert("RGB")
raw=im.copy()
# This is reference preparation only. No production image is edited.
im.paste(raw.crop((524,0,1046,1254)),(499,0))
im.paste(raw.crop((1046,0,1071,1254)),(1021,0))
im.paste(Image.open(north).convert("RGB").crop((0,1024,1254,1254)),(0,0))
im.save(out)
p.write_json(Path(str(out)+".derivation.json"),{"kind":"layout-only native mechanical reference; NOT production art","operation":"exact unscaled crop-paste to show desired whole-road alignment; new production image must come from imagegen","source":{"file":str(src),"sha256":p.sha(src)},"northAnchor":{"file":str(north),"sha256":p.sha(north),"sourceCrop":[0,1024,1254,1254],"destinationXY":[0,0]},"guideOperations":[{"sourceCrop":[524,0,1046,1254],"destinationXY":[499,0]},{"sourceCrop":[1046,0,1071,1254],"destinationXY":[1021,0]}],"output":{"file":str(out),"sha256":p.sha(out)}})

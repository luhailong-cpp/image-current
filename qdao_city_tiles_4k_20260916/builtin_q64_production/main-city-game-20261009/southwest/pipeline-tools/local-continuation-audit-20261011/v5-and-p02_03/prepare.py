from pathlib import Path
from PIL import Image,ImageDraw
import json
O=Path(__file__).parent;S=O.parents[2]
f=S.parents[1]/"parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png"
im=Image.open(f)
meta=[]
for name,box,scale in [("wholecity-local-original",[300,820,430,950],1),("wholecity-local-nearest6",[300,820,430,950],6),("wholecity-patch-original",[350,879,375,904],1),("wholecity-patch-nearest24",[350,879,375,904],24),("wholecity-tile-region-nearest8",[309,857,400,933],8)]:
 c=im.crop(box)
 if scale!=1:c=c.resize((c.width*scale,c.height*scale),Image.Resampling.NEAREST)
 c.save(O/(name+".png"));meta.append({"file":name+".png","sourceBox":box,"scaleForReview":scale,"resizedPreviewOnly":scale!=1})
# Actual nearest seed and exact top+left source native crops
for nm,f,box in [("p01_03-bottom230",S/"r12_c05/native/p01_03.png",[0,1024,1254,1254]),("p02_02-right230",S/"r12_c05/native/p02_02.png",[1024,0,1254,1254])]:
 Image.open(f).crop(box).save(O/(nm+".png"))
(O/"crop-manifest.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
print(im.size)


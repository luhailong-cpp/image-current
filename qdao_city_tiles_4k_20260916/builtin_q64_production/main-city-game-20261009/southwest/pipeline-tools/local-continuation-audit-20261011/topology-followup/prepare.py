from PIL import Image,ImageDraw
from pathlib import Path
import json
O=Path(__file__).parent;S=O.parents[2]
f=S.parents[1]/"parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png"
im=Image.open(f)
for name,box in [("p01_03",[347,856,378,888]),("p02_02",[327,876,359,907])]:
 x0,y0,x1,y1=box;s=30;c=im.crop(box).resize(((x1-x0)*s,(y1-y0)*s),Image.Resampling.NEAREST)
 o=Image.new("RGB",(c.width+40,c.height+40),"white");o.paste(c,(40,40));d=ImageDraw.Draw(o)
 for x in range(x0,x1):d.text((40+(x-x0)*s,15),str(x),fill="black")
 for y in range(y0,y1):d.text((0,40+(y-y0)*s),str(y),fill="black")
 o.save(O/(name+"-source-pixel-coordinates.png"))
# Wider native source, nearest inspection only.
im.crop((305,830,395,925)).resize((900,950),Image.Resampling.NEAREST).save(O/"coupled-source-nearest10.png")


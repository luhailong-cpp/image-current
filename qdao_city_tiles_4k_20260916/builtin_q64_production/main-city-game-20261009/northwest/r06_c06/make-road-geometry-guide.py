from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
d=Path(__file__).resolve().parent
src=d/"layout-only/s01_04.continuation-guide.png"
im=Image.open(src).convert("RGB")
base=im.copy()
draw=ImageDraw.Draw(im)
# Layout-only flat polygons and lines; never used as production pixels.
draw.rectangle((230,230,1253,1253),fill=(230,226,217))
s=.747
upper=lambda x:955-s*x
lower=lambda x:1345-s*x
middle=lambda x:1115-s*x
poly=lambda a,b:[(230,a(230)),(1254,a(1254)),(1254,b(1254)),(230,b(230))]
draw.polygon(poly(lambda x:upper(x)-80,lambda x:lower(x)+80),fill=(231,224,208))
draw.polygon(poly(upper,lower),fill=(133,165,189))
for fn in [lambda x:upper(x)-80,upper,middle,lower,lambda x:lower(x)+80]:
    draw.line([(230,fn(230)),(1254,fn(1254))],fill=(92,89,83),width=3)
draw.line([(230,359),(690,359)],fill=(141,133,119),width=3)
for x in (489,894):
    end=min(359,upper(x)-80)
    if end>230:draw.line([(x,230),(x,end)],fill=(141,133,119),width=3)
# Reapply exact top and left native anchor strips from immutable registered guide.
im.paste(base.crop((0,0,1254,230)),(0,0))
im.paste(base.crop((0,0,230,1254)),(0,0))
dest=d/"layout-only/s01_04_fix02.geometry-only-guide.png"
p.save_png(dest,im)
p.write_json(dest.with_suffix(".png.derivation.json"),{"role":"layout-only geometry polygons plus unchanged native anchors; NOT production artwork","source":{"file":str(src),"sha256":p.sha(src)},"nativeAnchorPixelsPreserved":["top230","left230"],"geometry":{"upperBlue":"y=955-0.747x","middleJoint":"y=1115-0.747x","lowerBlue":"y=1345-0.747x"},"productionArt":False})
print(dest)


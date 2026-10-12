from PIL import Image,ImageDraw
from pathlib import Path
import production_v2 as p
b=p.ZONE/"r06_c05"
src=b/"layout-only/s03_04_fix01.native-repair-guide.png"
out=b/"layout-only/s03_04_grid02.layout-guide.png"
im=Image.open(src).convert("RGB")
d=ImageDraw.Draw(im)
d.rectangle((22,636,1253,1023),fill=(226,222,214))
lines=[]
for cross in [-402,-58,286,630,968,1310,1652]:
    for slope in [1.043,-1.105]:
        p1=(round(cross+slope*(636-1070)),636)
        p2=(round(cross+slope*(1024-1070)),1024)
        lines.append([p1,p2])
        d.line([p1,p2],fill=(141,121,97),width=3)
# keep far-left actual path edge as the guide's geometric terminator
d.rectangle((0,636,21,1023),fill=(228,224,216))
d.line([(20,636),(20,1024)],fill=(141,121,97),width=3)
# actual bottom anchor remains untouched
im.save(out)
p.write_json(Path(str(out)+".derivation.json"),{"kind":"layout-only geometric guidance, NOT production art","source":{"file":str(src),"sha256":p.sha(src)},"operation":"coordinate guide replaces only known-wrong paving geometry y636..1023; top and bottom original native anchors preserved","guideLineEndpoints":lines,"nativeSouthAnchorUntouched":[0,1024,1254,1254],"output":{"file":str(out),"sha256":p.sha(out)}})

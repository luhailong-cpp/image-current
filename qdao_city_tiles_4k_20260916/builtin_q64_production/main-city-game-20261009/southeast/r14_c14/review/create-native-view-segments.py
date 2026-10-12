from PIL import Image
from pathlib import Path
import json
q=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14/review/assembly-8ff54f4e9ec7de483b1a")
out=q/"native-view-segments"
out.mkdir(exist_ok=True)
items=[]
for p in q.glob("*.png"):
    if not (p.name.startswith(("vertical-","horizontal-","edge-"))): continue
    with Image.open(p) as im:
        w,h=im.size
        vertical=h>w
        length=h if vertical else w
        for start in range(0,length,2048):
            end=min(start+2048,length)
            box=(0,start,w,end) if vertical else (start,0,end,h)
            dst=out/(p.stem+f"-part{start:04d}-{end:04d}.png")
            im.crop(box).save(dst)
            items.append({"source":str(p),"crop":box,"path":str(dst),"resized":False})
(out/"manifest.json").write_text(json.dumps(items,indent=2),encoding="utf-8")
print(json.dumps({"count":len(items),"directory":str(out)}))


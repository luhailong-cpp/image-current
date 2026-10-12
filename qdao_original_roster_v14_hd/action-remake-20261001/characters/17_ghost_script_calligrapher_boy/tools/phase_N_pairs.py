from pathlib import Path
from PIL import Image,ImageDraw
import json
b=Path(__file__).resolve().parents[1];out=b/"review"/"phase-N";out.mkdir(parents=True,exist_ok=True)
v2={1,3,4,5,6,8,9}
files={n:b/"staging"/f"run-N-{n:02}-v{2 if n in v2 else 1}.png" for n in range(1,17)}
for group,nums in enumerate([[1,9,2,10],[3,11,4,12],[5,13,6,14],[7,15,8,16]],1):
    sheet=Image.new("RGB",(2308,1510),(27,34,37));d=ImageDraw.Draw(sheet)
    for i,n in enumerate(nums):
        p=files[n];im=Image.open(p).convert("RGBA");crop=im.crop((50,530,1204,1254))
        panel=Image.new("RGBA",crop.size,(27,34,37,255));panel.alpha_composite(crop)
        x=(i%2)*1154;y=(i//2)*755+30;sheet.paste(panel.convert("RGB"),(x,y));d.text((x+12,y-22),p.stem,fill=(255,238,180))
        for gy in (1000,1100,1200):
            sy=y+gy-530;d.line((x,sy,x+1154,sy),fill=(75,65,65));d.text((x+2,sy-14),str(gy),fill=(200,180,170))
    sheet.save(out/f"pairs-{group}.jpg",quality=94)
(out/"selection-before.json").write_text(json.dumps([str(files[n]) for n in range(1,17)],indent=2),encoding="utf-8")
print(str(out))


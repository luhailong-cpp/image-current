from pathlib import Path
from PIL import Image, ImageDraw
import json
b=Path(__file__).resolve().parents[1]; out=b/"review"/"grounding-W"; out.mkdir(parents=True,exist_ok=True)
files=[]
for n in range(1,17):
    paths=list((b/"staging").glob(f"run-W-{n:02}-v*.png"))
    files.append(max(paths,key=lambda p:int(p.stem.rsplit("v",1)[1])))
for start in range(0,16,4):
    sheet=Image.new("RGB",(1800,1100),(30,35,37)); draw=ImageDraw.Draw(sheet)
    for i,path in enumerate(files[start:start+4]):
        im=Image.open(path).convert("RGBA")
        # QA-only crop at fixed coordinates for comparing shoes. Originals unchanged.
        crop=im.crop((150,700,1050,1220))
        rgb=Image.new("RGBA",crop.size,(30,35,37,255)); rgb.alpha_composite(crop)
        x=(i%2)*900;y=(i//2)*550+30
        sheet.paste(rgb.convert("RGB"),(x,y));draw.text((x+12,y-22),path.stem,fill=(250,240,200))
        for gy in (1100,1155,1200):
            sy=y+gy-700;draw.line((x,sy,x+900,sy),fill=(130,80,60),width=1);draw.text((x+2,sy-14),str(gy),fill=(220,180,130))
        for gx in (300,500,700,900):
            sx=x+gx-150;draw.line((sx,y,sx,y+520),fill=(55,60,60),width=1);draw.text((sx+3,y+2),str(gx),fill=(170,180,180))
    sheet.save(out/f"legs-{start+1:02}-{start+4:02}.png")
(out/"selection.json").write_text(json.dumps([str(p) for p in files],indent=2),encoding="utf-8")
print(str(out))


from pathlib import Path
from PIL import Image,ImageDraw
import json
b=Path(__file__).resolve().parents[1];out=b/"review"/"phase-N"
r=json.loads((b/"review-run-N.json").read_text(encoding="utf-8"))
files={f["n"]:b/f["file"] for f in r["frames"]}
for group,nums in enumerate([[3,4,5,6],[11,12,13,14],[14,15,16,1],[5,6,7,8],[7,15,8,9]],1):
    sheet=Image.new("RGB",(2308,1510),(27,34,37));d=ImageDraw.Draw(sheet)
    for i,n in enumerate(nums):
        p=files[n];im=Image.open(p).convert("RGBA");crop=im.crop((50,530,1204,1254))
        panel=Image.new("RGBA",crop.size,(27,34,37,255));panel.alpha_composite(crop)
        x=(i%2)*1154;y=(i//2)*755+30;sheet.paste(panel.convert("RGB"),(x,y));d.text((x+12,y-22),p.stem,fill=(255,238,180))
        for gy in (1000,1100,1200):
            sy=y+gy-530;d.line((x,sy,x+1154,sy),fill=(75,65,65));d.text((x+2,sy-14),str(gy),fill=(200,180,170))
    sheet.save(out/f"current-continuity-{group}.jpg",quality=94)
sheet=Image.new("RGB",(1360,1472),(220,226,221));d=ImageDraw.Draw(sheet)
for i,n in enumerate(range(1,17)):
    im=Image.open(files[n]).convert("RGBA");im.thumbnail((330,330),Image.Resampling.LANCZOS)
    x=(i%4)*340;y=(i//4)*368;sheet.paste(im,(x,y),im);d.text((x+10,y+337),files[n].stem,fill=(15,25,25))
sheet.save(out/"current-overview.jpg",quality=94)
(out/"selection-current.json").write_text(json.dumps([{"file":f["file"],"sha256":f["sha256"]} for f in r["frames"]],indent=2),encoding="utf-8")
print(str(out))


from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy")
m=json.loads((B/"preview/manifest-preview.json").read_text(encoding="utf-8-sig"))
rows=[]
for s in m["slots"]:
 if s["action"]=="run" and s["direction"]=="E":
  q=s["selected"];p=(B/"preview"/q["path"]).resolve();im=Image.open(p)
  rows.append(dict(slot=s["slot"],key=q["key"],file=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=list(im.size),mode=im.mode))
out=B/"review"
(out/"grounding-E-independent-latest-selection.json").write_text(json.dumps(dict(manifestBuiltAt=m["built_at"],selection=rows),ensure_ascii=False,indent=2),encoding="utf-8")
def contact(keys,size,cols,name):
 sheet=Image.new("RGB",(cols*size,((len(keys)+cols-1)//cols)*(size+24)),(220,220,220));d=ImageDraw.Draw(sheet)
 for j,k in enumerate(keys):
  r=next(x for x in rows if x["key"]==k);im=Image.open(r["file"]).convert("RGBA");im=im.resize((size,size),Image.Resampling.LANCZOS)
  x=(j%cols)*size;y=(j//cols)*(size+24);d.text((x+4,y+4),k,fill=(10,10,10));sheet.paste(im,(x,y+24),im)
 sheet.save(out/name)
contact([r["key"] for r in rows],240,4,"grounding-E-independent-latest-240px.png")
contact([rows[i-1]["key"] for i in [2,3,4,10,11,12]],420,3,"grounding-E-independent-latest-support.png")
print(json.dumps(dict(manifestBuiltAt=m["built_at"],selection=rows),ensure_ascii=True))

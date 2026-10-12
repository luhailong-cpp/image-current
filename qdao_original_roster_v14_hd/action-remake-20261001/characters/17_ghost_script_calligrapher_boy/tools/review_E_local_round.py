from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy")
keys=["run-E-10-v3","run-E-10-v4","run-E-12-v3","run-E-12-v5","run-E-12-v6","run-E-03-v6","run-E-11-v8"]
rows=[]
for k in keys:
 p=B/"staging"/(k+".png");im=Image.open(p)
 rows.append(dict(key=k,file=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=list(im.size),mode=im.mode))
seq=[["run-E-10-v3","run-E-11-v8","run-E-12-v3"],["run-E-10-v4","run-E-11-v8","run-E-12-v5"],["run-E-10-v4","run-E-11-v8","run-E-12-v6"]]
c=Image.new("RGB",(720,792),(218,218,218));d=ImageDraw.Draw(c)
for ri,r in enumerate(seq):
 for ci,k in enumerate(r):
  im=Image.open(B/"staging"/(k+".png")).convert("RGBA").resize((240,240),Image.Resampling.LANCZOS)
  c.paste(im,(ci*240,ri*264+24),im);d.text((ci*240+4,ri*264+4),k,fill=(0,0,0))
c.save(B/"review"/"grounding-E-local-round-comparison.png")
print(json.dumps(rows))

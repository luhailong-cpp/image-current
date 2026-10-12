from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy")
rows=[]
keys=["run-E-11-v8","run-E-12-v6","run-E-12-v8","run-E-13-v2"]
for k in keys:
 p=B/"staging"/(k+".png");im=Image.open(p);rows.append(dict(key=k,file=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=list(im.size),mode=im.mode))
seq=[["run-E-11-v8","run-E-12-v6","run-E-13-v2"],["run-E-11-v8","run-E-12-v8","run-E-13-v2"]]
canvas=Image.new("RGB",(720,528),(220,220,220));d=ImageDraw.Draw(canvas)
for ri,r in enumerate(seq):
 for ci,k in enumerate(r):
  im=Image.open(B/"staging"/(k+".png")).convert("RGBA").resize((240,240),Image.Resampling.LANCZOS)
  canvas.paste(im,(ci*240,ri*264+24),im);d.text((ci*240+4,ri*264+4),k,fill=(0,0,0))
canvas.save(B/"review"/"grounding-E-12v8-independent-comparison.png")
print(json.dumps(rows))

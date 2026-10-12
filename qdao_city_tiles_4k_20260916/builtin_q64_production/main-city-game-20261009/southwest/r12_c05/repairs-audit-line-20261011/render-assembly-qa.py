from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,sys
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011"/sys.argv[2];D.mkdir(exist_ok=True)
A=json.loads((B/"pipeline/output"/sys.argv[1]/"assembly.json").read_text())
I=Image.open(A["contextOutput"]["file"]);P=I.resize((1082,1082));P.save(D/"context-preview-resized.png")
J=ImageDraw.Draw(P)
for p in [115,1139,2163,3187,4211]:
 q=round(p*1082/4326);J.line([(q,0),(q,1081)],fill=(255,0,0));J.line([(0,q),(1081,q)],fill=(255,0,0))
P.save(D/"context-preview-grid-resized.png")
for r in range(1,4):
 for c in range(4):
  y=115+1024*r;x=115+1024*c;I.crop((x,y-180,x+1024,y+180)).save(D/("H"+str(r)+"-"+str(c+1)+".png"))
for c in range(1,4):
 for r in range(4):
  x=115+1024*c;y=115+1024*r;I.crop((x-180,y,x+180,y+1024)).save(D/("V"+str(c)+"-"+str(r+1)+".png"))
(D/"manifest.json").write_text(json.dumps({"source":A["contextOutput"],"assembly":str(B/"pipeline/output"/sys.argv[1]/"assembly.json"),"previewResized":True,"seamCropsResized":False},indent=2))
print(str(D))


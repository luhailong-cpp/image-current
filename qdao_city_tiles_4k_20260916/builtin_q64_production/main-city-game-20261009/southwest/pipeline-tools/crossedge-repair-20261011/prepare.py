from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
P=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/pipeline-tools/crossedge-repair-20261011")
P.mkdir(parents=True,exist_ok=True)
S=P.parent.parent
a=S/"r11_c05/refinement-resume20261010/integrated-v2/r11_c05.repaired-v2.candidate.png"
b=S/"r11_c06/pipeline/output/94ddb3ea62a89ee2/r11_c06.candidate.png"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
box=[19853,42413,21107,43667]
im=Image.new("RGB",(1254,1254))
im.paste(Image.open(a).crop((3469,1453,4096,2707)),(0,0))
im.paste(Image.open(b).crop((0,1453,627,2707)),(627,0))
out=P/"south-crossedge.v1.target.png";im.save(out)
c=json.loads((S.parent/"production-contract.json").read_text(encoding="utf-8-sig"))
refs=[{"file":str(out),"sha256":sha(out),"role":"edit target, exact 1254 square crop of current candidates"}]
for key in ["layoutReference","detailStyleReference","primaryStyleReference"]:
 p=Path(c[key]);refs.append({"file":str(p),"sha256":sha(p),"role":key})
r={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"worldBox":box,"pixels":[1254,1254],"resized":False,"sources":[{"file":str(a),"sha256":sha(a),"crop":[3469,1453,4096,2707],"target":[0,0,627,1254]},{"file":str(b),"sha256":sha(b),"crop":[0,1453,627,2707],"target":[627,0,1254,1254]}],"references":refs,"actualModel":None,"actualQuality":None}
(P/"source-evidence.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(r))


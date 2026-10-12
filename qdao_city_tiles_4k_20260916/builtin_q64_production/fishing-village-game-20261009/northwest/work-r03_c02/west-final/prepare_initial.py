from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");D=R/"work-r03_c02/west-final";D.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rp=lambda p:Path(p) if Path(p).is_absolute() else R/p
wm=read(R/"work-r03_c02/tiles/r03_c02.candidate.assembly.json");em=read(R/"work-r03_c03/joint-final/joint-assembly.json")
wpath=R/"work-r03_c02/tiles/r03_c02.candidate.png";epath=Path(em["candidate"]["file"])
west=np.asarray(Image.open(wpath)).copy();east=np.asarray(Image.open(epath)).copy()
wi=np.asarray(Image.open(R/"work-r03_c02/tiles/r03_c02.candidate.source-id.png")) if (R/"work-r03_c02/tiles/r03_c02.candidate.source-id.png").exists() else None
print("westkeys",list(wm.keys()),"eastkeys",list(em.keys()),"westid",wm.get("sourceIdMap"),"westartifacts",wm.get("artifacts"))
print("eastsources",[(s["jointSourceId"],Path(s["file"]).name) for s in em["sources"]])
pair=np.concatenate([west,east],axis=1);Image.fromarray(pair).save(D/"initial-pair.png")
crops=[]
for i in range(4):
 b=[8192-400,8192+1024*i,8192+400,8192+1024*(i+1)]
 p=D/f"initial-seam-{i+1}.png";Image.fromarray(pair[b[1]-8192:b[3]-8192,b[0]-4096:b[2]-4096]).save(p);crops.append(str(p))
for name,b in [("G1",[4415,8835,5265,9585]),("M1",[4500,8192,5500,8850]),("M2",[5800,9600,7100,11200])]:
 Image.fromarray(pair[b[1]-8192:b[3]-8192,b[0]-4096:b[2]-4096]).save(D/("initial-"+name+".png"))
(D/"initial-inputs.json").write_text(json.dumps({"west":str(wpath),"westSHA256":sha(wpath),"east":str(epath),"eastSHA256":sha(epath),"globalBox":[4096,8192,12288,12288],"crops":crops},indent=2))


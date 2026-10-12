import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest")
sys.path.insert(0,str(B));import assemble_native as a
O=B/"r06_c04"/"qa"
def row(tile,r):
 d=json.loads((B/tile/"selection.json").read_text(encoding="utf-8-sig"))
 ps=[]
 for c in range(1,5):
  pid=f"s{r:02}_{c:02}";p=Path(d.get(pid,str(B/tile/"native"/(pid+".png"))));ps.append(np.asarray(Image.open(p).convert("RGB")))
 out=ps[0]
 for q in ps[1:]:out,_=a.append_with_minimum_seam(out,q)
 return out
north=row("r05_c04",4);south=row("r06_c04",1)
actual=np.concatenate([north[909:1139,115:4211],south[115:345,115:4211]],axis=0)
stats=[]
for c in range(4):
 im=Image.fromarray(actual[:,c*1024:(c+1)*1024]);path=O/f"subagent-audit-actual-external-c{c+1}.png";im.save(path)
 edge=np.abs(actual[229,c*1024:(c+1)*1024].astype(float)-actual[230,c*1024:(c+1)*1024])
 stats.append({"column":c+1,"path":str(path),"edgeMeanRGBAbsDifference":float(edge.mean()),"edgeP95":float(np.percentile(edge,95)),"worldBox":[12288+c*1024,20250,13312+c*1024,20710],"nativeScale":1})
(O/"subagent-audit-actual-external.json").write_text(json.dumps(stats,indent=2),encoding="utf-8")
print(json.dumps(stats,indent=2))


import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest")
sys.path.insert(0,str(B))
import assemble_native as a
O=B/"r06_c04"/"qa"
O.mkdir(exist_ok=True)
sel=json.loads((B/"r06_c04"/"selection.json").read_text(encoding="utf-8-sig"))
selN=json.loads((B/"r05_c04"/"selection.json").read_text(encoding="utf-8-sig"))
def get(tile,pid):
    d=sel if tile=="r06_c04" else selN
    p=Path(d.get(pid,str(B/tile/"native"/(pid+".png"))))
    return np.asarray(Image.open(p).convert("RGB")),p
pairs=[]
for c in range(1,4): pairs.append(("internal-row1-c"+str(c),("r06_c04",f"s01_{c:02}"),("r06_c04",f"s01_{c+1:02}"),"x"))
pairs.append(("internal-row2-c1",("r06_c04","s02_01"),("r06_c04","s02_02"),"x"))
for c in range(1,3): pairs.append(("internal-y1024-c"+str(c),("r06_c04",f"s01_{c:02}"),("r06_c04",f"s02_{c:02}"),"y"))
for c in range(1,5): pairs.append(("external-north-c"+str(c),("r05_c04",f"s04_{c:02}"),("r06_c04",f"s01_{c:02}"),"y"))
reports=[]
for name,left,right,axis in pairs:
    A,pa=get(*left); C,pc=get(*right)
    if axis=="y": A,C=A.transpose(1,0,2),C.transpose(1,0,2)
    hard=np.concatenate((A[:,115:1139],C[:,115:1139]),axis=1)
    minimum,sp=a.append_with_minimum_seam(A,C)
    h=Image.fromarray(hard[115:1139,794:1254].transpose(1,0,2))
    m=Image.fromarray(minimum[115:1139,909:1369].transpose(1,0,2))
    # y joins display in world orientation. x joins transpose: original y runs left to right.
    canvas=Image.new("RGB",(1024,956),"#202020")
    canvas.paste(h,(0,24));canvas.paste(m,(0,496))
    d=ImageDraw.Draw(canvas);d.text((5,5),name+" | HARD, seam at strip y230",fill="white");d.text((5,480),"MINIMUM-ERROR | native pixels, no scale or blend",fill="white")
    output=O/("subagent-audit-"+name+".png");canvas.save(output)
    reports.append({"name":name,"sources":[str(pa),str(pc)],"sha256":[a.sha(pa),a.sha(pc)],"axis":axis,"output":str(output),"sourceResampled":False,"seamRange":[int(sp.min()),int(sp.max())],"meanOverlapDifference":float(np.abs(A[:,-230:].astype(float)-C[:,:230]).mean())})
(O/"subagent-audit-sources.json").write_text(json.dumps(reports,indent=2),encoding="utf-8")
print(json.dumps(reports,indent=2))

